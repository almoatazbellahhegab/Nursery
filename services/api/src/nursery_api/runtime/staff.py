"""Transactional staff attendance API with current scope, immutable audit and retries.

Implementation defaults under the explicit review waiver: teachers act/read only
for themselves; assigned managers and organization admins manage branch staff.
Managers/admins may correct another employee's times within seven days, with a
reason and timeline-order validation. No payroll/overtime policy is inferred.
"""

import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta
from typing import Annotated, Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Header, Query
from fastapi.encoders import jsonable_encoder
from psycopg.types.json import Jsonb
from pydantic import AwareDatetime, Field, StrictInt

from nursery_api.staff_attendance.presence import (
    StaffAction,
    StaffAttendanceError,
    StaffCommand,
    StaffIdentity,
    StaffSnapshot,
    StaffTarget,
    VerifiedStaffGrant,
    decide_staff_attendance,
)

from .api import Actor, ApiError, Authenticated, CommittedRoute, StrictModel, now_utc

router = APIRouter(
    prefix="/api/v1/staff-attendance", tags=["Staff attendance"], route_class=CommittedRoute
)
Operation = Annotated[UUID, Header(alias="Idempotency-Key")]


class Transition(StrictModel):
    employee_id: UUID
    branch_id: UUID
    action: StaffAction
    expected_version: Annotated[StrictInt, Field(ge=0)]
    occurred_at: AwareDatetime | None = None


class Correction(StrictModel):
    employee_id: UUID
    branch_id: UUID
    event_id: UUID
    expected_version: Annotated[StrictInt, Field(ge=1)]
    corrected_at: AwareDatetime
    reason: str = Field(min_length=3, max_length=500)


def authorize_employee(
    actor: Actor, employee_id: UUID, branch_id: UUID, *, write: bool
) -> dict[str, Any]:
    if actor.role not in {"administrator", "branch_manager", "teacher"}:
        raise ApiError(403, "staff_access_denied")
    branch = actor.connection.execute(
        "SELECT id FROM app.branches WHERE id=%s AND (active OR NOT %s)", (branch_id, write)
    ).fetchone()
    if branch is None:
        raise ApiError(404, "staff_not_found")
    employee = actor.connection.execute(
        "SELECT e.id,e.user_id,e.active,e.display_name FROM app.employees e "
        "JOIN app.employee_assignments a ON a.organization_id=e.organization_id AND a.employee_id=e.id "
        "WHERE e.organization_id=%s AND e.id=%s AND a.branch_id=%s AND a.starts_at<=%s "
        "AND (a.ends_at IS NULL OR a.ends_at>%s)",
        (actor.organization_id, employee_id, branch_id, now_utc(), now_utc()),
    ).fetchone()
    if employee is None or (actor.role == "teacher" and employee["user_id"] != actor.user_id):
        raise ApiError(404, "staff_not_found")
    if write and not employee["active"]:
        raise ApiError(409, "employee_inactive")
    return employee


def fingerprint(kind: str, body: StrictModel) -> str:
    payload = body.model_dump(mode="json")
    for key in ("occurred_at", "corrected_at"):
        value = getattr(body, key, None)
        if value is not None:
            payload[key] = value.astimezone(UTC).isoformat()
    return hashlib.sha256(
        json.dumps([kind, payload], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def replay(actor: Actor, operation: UUID, command_hash: str) -> dict[str, Any] | None:
    # Serialize the operation even when its first receipt row does not yet exist.
    actor.connection.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
        (f"{actor.organization_id}:{actor.user_id}:{operation}",),
    )
    row = actor.connection.execute(
        "SELECT fingerprint,response FROM app.staff_receipts WHERE organization_id=%s AND actor_id=%s AND operation_id=%s",
        (actor.organization_id, actor.user_id, operation),
    ).fetchone()
    if row is None:
        return None
    if row["fingerprint"] != command_hash:
        raise ApiError(409, "operation_conflict")
    result: dict[str, Any] = row["response"]
    return dict(result, replayed=True)


def save_result(
    actor: Actor,
    operation: UUID,
    command_hash: str,
    result: dict[str, Any],
    action: str,
    resource: UUID,
) -> dict[str, Any]:
    payload: dict[str, Any] = jsonable_encoder(dict(result, replayed=False))
    actor.connection.execute(
        "INSERT INTO app.staff_receipts VALUES(%s,%s,%s,%s,%s,%s)",
        (actor.organization_id, actor.user_id, operation, command_hash, Jsonb(payload), now_utc()),
    )
    actor.connection.execute(
        "INSERT INTO app.audit VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (
            actor.organization_id,
            uuid4(),
            actor.user_id,
            action,
            resource,
            now_utc(),
            Jsonb(payload),
        ),
    )
    return payload


def locked_presence(actor: Actor, employee: UUID) -> StaffSnapshot:
    actor.connection.execute(
        "INSERT INTO app.staff_presence(organization_id,employee_id) VALUES(%s,%s) ON CONFLICT DO NOTHING",
        (actor.organization_id, employee),
    )
    row = actor.connection.execute(
        "SELECT * FROM app.staff_presence WHERE organization_id=%s AND employee_id=%s FOR UPDATE",
        (actor.organization_id, employee),
    ).fetchone()
    assert row is not None
    return StaffSnapshot(
        StaffIdentity(actor.organization_id, employee),
        row["version"],
        row["open_branch_id"],
        row["open_session_id"],
        row["last_occurred_at"],
        row["last_recorded_at"],
    )


@router.get("/employees", summary="List visible staff and current presence at an authorized branch")
def employees(actor: Authenticated, branch_id: UUID, cursor: UUID | None = None) -> dict[str, Any]:
    if actor.role not in {"administrator", "branch_manager", "teacher"}:
        raise ApiError(403, "staff_access_denied")
    if (
        actor.connection.execute("SELECT id FROM app.branches WHERE id=%s", (branch_id,)).fetchone()
        is None
    ):
        raise ApiError(404, "staff_not_found")
    rows = actor.connection.execute(
        "SELECT DISTINCT e.id,e.display_name,e.active,coalesce(p.version,0) AS version,"
        "p.open_branch_id,p.open_session_id,p.last_occurred_at FROM app.employees e "
        "JOIN app.employee_assignments a ON a.organization_id=e.organization_id AND a.employee_id=e.id "
        "LEFT JOIN app.staff_presence p ON p.organization_id=e.organization_id AND p.employee_id=e.id "
        "WHERE e.organization_id=%s AND a.branch_id=%s AND a.starts_at<=%s AND (a.ends_at IS NULL OR a.ends_at>%s) "
        "AND (%s OR e.user_id=%s) AND (%s::uuid IS NULL OR e.id>%s) ORDER BY e.id LIMIT 101",
        (
            actor.organization_id,
            branch_id,
            now_utc(),
            now_utc(),
            actor.role != "teacher",
            actor.user_id,
            cursor,
            cursor,
        ),
    ).fetchall()
    return {"items": rows[:100], "next_cursor": str(rows[99]["id"]) if len(rows) > 100 else None}


@router.post(
    "/transitions",
    summary="Atomically check staff in/out, with version and durable operation replay",
)
def transition(body: Transition, actor: Authenticated, operation: Operation) -> dict[str, Any]:
    authorize_employee(actor, body.employee_id, body.branch_id, write=True)
    command_hash = fingerprint("transition", body)
    cached = replay(actor, operation, command_hash)
    if cached is not None:
        return cached
    current = locked_presence(actor, body.employee_id)
    now = now_utc()
    target = StaffTarget(current.identity, body.branch_id)
    try:
        decision = decide_staff_attendance(
            StaffCommand(
                target, operation, body.action, body.occurred_at or now, body.expected_version
            ),
            current,
            VerifiedStaffGrant(
                target, actor.user_id, body.action, True, now + timedelta(seconds=10)
            ),
            recorded_at=now,
        )
    except StaffAttendanceError as error:
        raise ApiError(409, error.code.value) from None
    event, snapshot = decision.event, decision.snapshot
    actor.connection.execute(
        "UPDATE app.staff_presence SET version=%s,open_branch_id=%s,open_session_id=%s,last_occurred_at=%s,last_recorded_at=%s "
        "WHERE organization_id=%s AND employee_id=%s",
        (
            snapshot.version,
            snapshot.open_branch_id,
            snapshot.open_session_id,
            snapshot.last_occurred_at,
            snapshot.last_recorded_at,
            actor.organization_id,
            body.employee_id,
        ),
    )
    actor.connection.execute(
        "INSERT INTO app.staff_events VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            actor.organization_id,
            event.event_id,
            body.employee_id,
            body.branch_id,
            actor.user_id,
            operation,
            event.session_id,
            event.action.value,
            event.occurred_at,
            event.recorded_at,
            event.version,
        ),
    )
    return save_result(
        actor,
        operation,
        command_hash,
        {
            "employee_id": body.employee_id,
            "event_id": event.event_id,
            "session_id": event.session_id,
            "action": event.action.value,
            "occurred_at": event.occurred_at,
            "recorded_at": event.recorded_at,
            "version": snapshot.version,
            "present": snapshot.open_session_id is not None,
        },
        "staff." + event.action.value,
        body.employee_id,
    )


def effective_events(
    actor: Actor, employee_id: UUID, branch_id: UUID | None = None
) -> list[dict[str, Any]]:
    rows = actor.connection.execute(
        "SELECT e.*,coalesce(c.corrected_at,e.occurred_at) AS effective_at FROM app.staff_events e "
        "LEFT JOIN LATERAL(SELECT corrected_at FROM app.staff_corrections WHERE organization_id=e.organization_id "
        "AND event_id=e.id ORDER BY version DESC LIMIT 1)c ON true "
        "WHERE e.organization_id=%s AND e.employee_id=%s "
        "AND (%s::uuid IS NULL OR e.branch_id=%s) ORDER BY e.version DESC LIMIT 1001",
        (actor.organization_id, employee_id, branch_id, branch_id),
    ).fetchall()
    return list(reversed(rows))


@router.get(
    "/history", summary="Read bounded staff event/correction history within current branch scope"
)
def history(actor: Authenticated, employee_id: UUID, branch_id: UUID) -> dict[str, Any]:
    authorize_employee(actor, employee_id, branch_id, write=False)
    events = effective_events(actor, employee_id, branch_id)
    corrections: list[dict[str, Any]] = []
    if actor.role in {"administrator", "branch_manager"}:
        corrections = actor.connection.execute(
            "SELECT c.id,c.event_id,c.original_at,c.corrected_at,c.recorded_at,c.reason,c.actor_id,c.version "
            "FROM app.staff_corrections c JOIN app.staff_events e ON e.organization_id=c.organization_id AND e.id=c.event_id "
            "WHERE c.organization_id=%s AND c.employee_id=%s AND e.branch_id=%s ORDER BY c.version DESC LIMIT 100",
            (actor.organization_id, employee_id, branch_id),
        ).fetchall()
    return {"events": events[-1000:], "corrections": corrections, "truncated": len(events) > 1000}


@router.post(
    "/corrections",
    summary="Append a manager correction with original/new time, actor and mandatory reason",
)
def correct(body: Correction, actor: Authenticated, operation: Operation) -> dict[str, Any]:
    employee = authorize_employee(actor, body.employee_id, body.branch_id, write=True)
    if (
        actor.role not in {"administrator", "branch_manager"}
        or employee["user_id"] == actor.user_id
    ):
        raise ApiError(403, "staff_correction_denied")
    if len(body.reason.strip()) < 3:
        raise ApiError(422, "reason_required")
    command_hash = fingerprint("correction", body)
    cached = replay(actor, operation, command_hash)
    if cached is not None:
        return cached
    current = locked_presence(actor, body.employee_id)
    if current.version != body.expected_version:
        raise ApiError(409, "staff_attendance_version_conflict")
    events = effective_events(actor, body.employee_id)
    event = next(
        (e for e in events if e["id"] == body.event_id and e["branch_id"] == body.branch_id), None
    )
    if event is None:
        raise ApiError(404, "staff_event_not_found")
    now = now_utc()
    corrected = body.corrected_at.astimezone(UTC)
    if corrected > now or now - event["recorded_at"] > timedelta(days=7):
        raise ApiError(409, "staff_correction_window")
    index = events.index(event)
    if (index > 0 and corrected < events[index - 1]["effective_at"]) or (
        index + 1 < len(events) and corrected > events[index + 1]["effective_at"]
    ):
        raise ApiError(409, "staff_correction_chronology")
    if corrected == event["effective_at"]:
        raise ApiError(409, "staff_correction_no_change")
    correction_id = uuid4()
    version = current.version + 1
    actor.connection.execute(
        "INSERT INTO app.staff_corrections VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            actor.organization_id,
            correction_id,
            body.employee_id,
            body.event_id,
            actor.user_id,
            event["effective_at"],
            corrected,
            now,
            body.reason.strip(),
            version,
        ),
    )
    latest_time = corrected if index == len(events) - 1 else current.last_occurred_at
    actor.connection.execute(
        "UPDATE app.staff_presence SET version=%s,last_occurred_at=%s,last_recorded_at=%s WHERE organization_id=%s AND employee_id=%s",
        (version, latest_time, now, actor.organization_id, body.employee_id),
    )
    return save_result(
        actor,
        operation,
        command_hash,
        {
            "correction_id": correction_id,
            "event_id": body.event_id,
            "original_at": event["effective_at"],
            "corrected_at": corrected,
            "actor_id": actor.user_id,
            "recorded_at": now,
            "reason": body.reason.strip(),
            "version": version,
        },
        "staff.correct",
        body.employee_id,
    )


@router.get(
    "/daily", summary="Read branch-local daily staff presence with effective corrected instants"
)
def daily(
    actor: Authenticated, branch_id: UUID, day: Annotated[date | None, Query()] = None
) -> dict[str, Any]:
    employees(
        actor, branch_id
    )  # Establish current role and branch access before historical details.
    branch = actor.connection.execute(
        "SELECT timezone FROM app.branches WHERE organization_id=%s AND id=%s",
        (actor.organization_id, branch_id),
    ).fetchone()
    assert branch is not None
    zone = ZoneInfo(branch["timezone"])
    day = day or now_utc().astimezone(zone).date()
    start = datetime.combine(day, time(), zone).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time(), zone).astimezone(UTC)
    visible = actor.connection.execute(
        "SELECT DISTINCT e.id,e.display_name,p.open_branch_id FROM app.employees e "
        "JOIN app.employee_assignments a ON a.organization_id=e.organization_id AND a.employee_id=e.id "
        "LEFT JOIN app.staff_presence p ON p.organization_id=e.organization_id AND p.employee_id=e.id "
        "WHERE e.organization_id=%s AND a.branch_id=%s AND a.starts_at<%s "
        "AND (a.ends_at IS NULL OR a.ends_at>%s) AND (%s OR e.user_id=%s) ORDER BY e.id LIMIT 201",
        (actor.organization_id, branch_id, end, start, actor.role != "teacher", actor.user_id),
    ).fetchall()
    cutoff = min(now_utc(), end)
    items: list[dict[str, Any]] = []
    for employee in visible[:200]:
        events = effective_events(actor, employee["id"])
        sessions: dict[UUID, dict[str, datetime]] = {}
        for event in events:
            if event["branch_id"] == branch_id:
                sessions.setdefault(event["session_id"], {})[event["action"]] = event[
                    "effective_at"
                ]
        seconds = 0
        for session in sessions.values():
            if "check_in" in session:
                left, right = (
                    max(session["check_in"], start),
                    min(session.get("check_out", cutoff), cutoff),
                )
                seconds += max(0, int((right - left).total_seconds()))
        items.append(
            {
                "employee_id": employee["id"],
                "display_name": employee["display_name"],
                "present": employee["open_branch_id"] == branch_id,
                "seconds_present": seconds,
                "data_truncated": len(events) > 1000,
            }
        )
    return {
        "day": day,
        "timezone": branch["timezone"],
        "start": start,
        "end": end,
        "cutoff": cutoff,
        "items": items,
        "truncated": len(visible) > 200,
    }
