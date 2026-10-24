"""Versioned branch administration; tenant and branch reads remain RLS scoped."""

from typing import Annotated, Any, Literal
from datetime import timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Header, Query
from pydantic import Field, StrictInt, field_validator

from .api import Actor, ApiError, Authenticated, CommittedRoute, StrictModel, now_utc
from .commands import complete, fingerprint, replay

router = APIRouter(prefix="/api/v1/branches", tags=["Branches"], route_class=CommittedRoute)
Operation = Annotated[UUID, Header(alias="Idempotency-Key")]


class BranchFields(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    timezone: str = Field(default="Africa/Cairo", max_length=80)
    contact_email: str = Field(default="", max_length=254)
    contact_phone: str = Field(default="", max_length=40)
    address: str = Field(default="", max_length=500)
    capacity: Annotated[StrictInt, Field(ge=1, le=10000)] | None = None
    operating_status: Literal["planned", "open", "temporarily_closed"] = "open"
    active: bool = True

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name required")
        return value.strip()

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError("Unknown timezone") from error
        return value

    @field_validator("contact_email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if value and (value.count("@") != 1 or any(c.isspace() for c in value)):
            raise ValueError("Invalid contact email")
        return value.strip().lower()


class BranchUpdate(BranchFields):
    expected_version: Annotated[StrictInt, Field(ge=1)]


class Assignment(StrictModel):
    user_id: UUID
    assigned: bool
    expected_version: Annotated[StrictInt, Field(ge=1)]


def require_admin(actor: Actor) -> None:
    if actor.role != "administrator":
        raise ApiError(403, "branch_administration_denied")
    if actor.mfa_required and (
        actor.mfa_at is None or now_utc() - actor.mfa_at > timedelta(minutes=15)
    ):
        raise ApiError(403, "reauthentication_required")


def branch_row(actor: Actor, branch_id: UUID, *, lock: bool = False) -> dict[str, Any]:
    row = actor.connection.execute(
        "SELECT * FROM app.branches WHERE organization_id=%s AND id=%s"
        + (" FOR UPDATE" if lock else ""),
        (actor.organization_id, branch_id),
    ).fetchone()
    if row is None:
        raise ApiError(404, "branch_not_found")
    return row


@router.get("", summary="List currently authorized branches, including retained inactive branches")
def list_branches(actor: Authenticated, cursor: UUID | None = None) -> dict[str, Any]:
    rows = actor.connection.execute(
        "SELECT * FROM app.branches WHERE organization_id=%s AND (%s::uuid IS NULL OR id>%s) "
        "ORDER BY id LIMIT 101",
        (actor.organization_id, cursor, cursor),
    ).fetchall()
    return {"items": rows[:100], "next_cursor": str(rows[99]["id"]) if len(rows) > 100 else None}


@router.get("/members", summary="Administrator-only member choices for branch assignment")
def list_members(actor: Authenticated, cursor: UUID | None = None) -> dict[str, Any]:
    require_admin(actor)
    rows = actor.connection.execute(
        "SELECT m.user_id,m.role,m.active,u.email FROM app.memberships m JOIN app.users u ON u.id=m.user_id "
        "WHERE m.organization_id=%s AND (%s::uuid IS NULL OR m.user_id>%s) ORDER BY m.user_id LIMIT 101",
        (actor.organization_id, cursor, cursor),
    ).fetchall()
    return {
        "items": rows[:100],
        "next_cursor": str(rows[99]["user_id"]) if len(rows) > 100 else None,
    }


@router.post("", summary="Create a branch with a durable operation receipt and audit")
def create_branch(body: BranchFields, actor: Authenticated, operation: Operation) -> dict[str, Any]:
    require_admin(actor)
    command_hash = fingerprint("branch.create", None, body)
    cached = replay(actor, operation, command_hash)
    if cached is not None:
        return cached
    branch_id = uuid4()
    actor.connection.execute(
        "INSERT INTO app.branches(organization_id,id,name,timezone,contact_email,contact_phone,address,"
        "capacity,operating_status,active) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            actor.organization_id,
            branch_id,
            body.name,
            body.timezone,
            body.contact_email,
            body.contact_phone,
            body.address,
            body.capacity,
            body.operating_status,
            body.active,
        ),
    )
    return complete(
        actor,
        operation,
        command_hash,
        branch_row(actor, branch_id),
        "branch.create",
        branch_id,
        {"version": 1},
    )


@router.get(
    "/{branch_id}", summary="Read a branch within current organization and assignment scope"
)
def get_branch(branch_id: UUID, actor: Authenticated) -> dict[str, Any]:
    return branch_row(actor, branch_id)


@router.post("/{branch_id}", summary="Edit branch metadata/status using an optimistic version")
def edit_branch(
    branch_id: UUID, body: BranchUpdate, actor: Authenticated, operation: Operation
) -> dict[str, Any]:
    require_admin(actor)
    command_hash = fingerprint("branch.edit", branch_id, body)
    cached = replay(actor, operation, command_hash)
    if cached is not None:
        return cached
    original = branch_row(actor, branch_id, lock=True)
    if original["version"] != body.expected_version:
        raise ApiError(409, "branch_version_conflict")
    actor.connection.execute(
        "UPDATE app.branches SET name=%s,timezone=%s,contact_email=%s,contact_phone=%s,address=%s,capacity=%s,"
        "operating_status=%s,active=%s,version=version+1 WHERE organization_id=%s AND id=%s",
        (
            body.name,
            body.timezone,
            body.contact_email,
            body.contact_phone,
            body.address,
            body.capacity,
            body.operating_status,
            body.active,
            actor.organization_id,
            branch_id,
        ),
    )
    return complete(
        actor,
        operation,
        command_hash,
        branch_row(actor, branch_id),
        "branch.edit",
        branch_id,
        {"version": body.expected_version + 1, "active": body.active},
    )


@router.get("/{branch_id}/members", summary="Administrator-only current branch member assignments")
def get_assignments(
    branch_id: UUID, actor: Authenticated, cursor: UUID | None = Query(default=None)
) -> dict[str, Any]:
    require_admin(actor)
    branch_row(actor, branch_id)
    rows = actor.connection.execute(
        "SELECT user_id FROM app.branch_memberships WHERE organization_id=%s AND branch_id=%s "
        "AND (%s::uuid IS NULL OR user_id>%s) ORDER BY user_id LIMIT 101",
        (actor.organization_id, branch_id, cursor, cursor),
    ).fetchall()
    return {
        "items": rows[:100],
        "next_cursor": str(rows[99]["user_id"]) if len(rows) > 100 else None,
    }


@router.post(
    "/{branch_id}/members",
    summary="Assign/remove one active organization member; revoke old branch scope immediately",
)
def assign_member(
    branch_id: UUID, body: Assignment, actor: Authenticated, operation: Operation
) -> dict[str, Any]:
    require_admin(actor)
    command_hash = fingerprint("branch.assignment", branch_id, body)
    cached = replay(actor, operation, command_hash)
    if cached is not None:
        return cached
    original = branch_row(actor, branch_id, lock=True)
    if original["version"] != body.expected_version:
        raise ApiError(409, "branch_version_conflict")
    member = actor.connection.execute(
        "SELECT user_id FROM app.memberships WHERE organization_id=%s AND user_id=%s AND active",
        (actor.organization_id, body.user_id),
    ).fetchone()
    if member is None:
        raise ApiError(404, "member_not_found")
    if body.assigned:
        if not original["active"]:
            raise ApiError(409, "branch_inactive")
        actor.connection.execute(
            "INSERT INTO app.branch_memberships VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
            (actor.organization_id, body.user_id, branch_id),
        )
    else:
        actor.connection.execute(
            "DELETE FROM app.branch_memberships WHERE organization_id=%s AND user_id=%s AND branch_id=%s",
            (actor.organization_id, body.user_id, branch_id),
        )
    actor.connection.execute(
        "UPDATE app.branches SET version=version+1 WHERE organization_id=%s AND id=%s",
        (actor.organization_id, branch_id),
    )
    return complete(
        actor,
        operation,
        command_hash,
        {"user_id": body.user_id, "assigned": body.assigned, "version": body.expected_version + 1},
        "branch.assignment",
        branch_id,
        {"user_id": str(body.user_id), "assigned": body.assigned},
    )
