"""Server-owned sessions and tenant context for the connected application.

Roles/employee activity are reloaded from PostgreSQL on every request. Browser
mutations require an allowlisted Origin and session-bound CSRF proof. Native
clients use opaque bearer sessions. None of these claims are read from JSON roles.
"""

import hmac
import secrets
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from fastapi.exceptions import RequestValidationError
from psycopg import OperationalError

from .database import Connection, Database, set_context
from .security import csrf_token, digest, password_hash, password_matches

_DUMMY_HASH = password_hash(secrets.token_urlsafe(24))


class ApiError(Exception):
    """Safe external code; no database or identity-existence details."""

    def __init__(self, status: int, code: str) -> None:
        self.status, self.code = status, code


class StrictModel(BaseModel):
    """Unknown input fields fail validation instead of silently becoming claims."""

    model_config = ConfigDict(extra="forbid")


class Login(StrictModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256, repr=False)
    organization_id: UUID | None = None
    native: bool = False


@dataclass(frozen=True)
class Actor:
    """Request context resolved from a current, active database session."""

    user_id: UUID
    organization_id: UUID
    role: str
    token: str = field(repr=False)
    connection: Connection = field(repr=False)


def now_utc() -> datetime:
    return datetime.now(UTC)


def require_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is None or origin not in request.app.state.origins:
        raise ApiError(403, "origin_denied")


def current_actor(request: Request) -> Iterator[Actor]:
    """Resolve identity, active membership and tenant in the same transaction as work."""
    authorization = request.headers.get("authorization", "")
    bearer = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else None
    cookie = request.cookies.get("nursery_session")
    if cookie and bearer and cookie != bearer:
        raise ApiError(401, "authentication_required")
    token = bearer or cookie
    if not token or len(token) > 256:
        raise ApiError(401, "authentication_required")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        if request.headers.get("origin") is not None or not bearer:
            require_origin(request)
        if not bearer and not hmac.compare_digest(
            request.headers.get("x-csrf-token", ""), csrf_token(token)
        ):
            raise ApiError(403, "csrf_required")
    database: Database = request.app.state.database
    with database.transaction() as connection:
        session = connection.execute(
            "SELECT s.user_id,s.organization_id FROM app.sessions s JOIN app.users u ON u.id=s.user_id "
            "WHERE s.token_hash=%s AND NOT s.revoked AND u.active AND s.expires_at>%s "
            "AND s.last_seen_at>%s",
            (digest(token), now_utc(), now_utc() - timedelta(minutes=30)),
        ).fetchone()
        if session is None:
            raise ApiError(401, "authentication_required")
        set_context(connection, session["user_id"], session["organization_id"])
        membership = connection.execute(
            "SELECT role FROM app.memberships WHERE organization_id=%s AND user_id=%s AND active",
            (session["organization_id"], session["user_id"]),
        ).fetchone()
        organization = connection.execute(
            "SELECT id FROM app.organizations WHERE id=%s AND active", (session["organization_id"],)
        ).fetchone()
        if membership is None or organization is None:
            raise ApiError(401, "authentication_required")
        set_context(connection, session["user_id"], session["organization_id"], membership["role"])
        connection.execute(
            "UPDATE app.sessions SET last_seen_at=%s WHERE token_hash=%s",
            (now_utc(), digest(token)),
        )
        yield Actor(
            session["user_id"], session["organization_id"], membership["role"], token, connection
        )


Authenticated = Annotated[Actor, Depends(current_actor)]
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Identity"])


def profile(actor: Actor) -> dict[str, Any]:
    branches = actor.connection.execute(
        "SELECT id,name FROM app.branches WHERE organization_id=%s AND active ORDER BY name,id LIMIT 100",
        (actor.organization_id,),
    ).fetchall()
    organization = actor.connection.execute(
        "SELECT name,timezone FROM app.organizations WHERE id=%s", (actor.organization_id,)
    ).fetchone()
    return {
        "user_id": str(actor.user_id),
        "organization_id": str(actor.organization_id),
        "role": actor.role,
        "organization": organization,
        "branches": branches,
        "csrf_token": csrf_token(actor.token),
    }


@auth_router.post(
    "/login", summary="Create an opaque session after password and active-membership verification"
)
def login(body: Login, request: Request, response: Response) -> dict[str, Any]:
    """Rate-limited login; credentials never enter tenant events or response logs."""
    if not body.native or request.headers.get("origin") is not None:
        require_origin(request)
    database: Database = request.app.state.database
    now = now_utc()
    username = body.email.strip().lower()
    ip = request.client.host if request.client else "unknown"
    key = digest(username + "\0" + ip)
    invalid = False
    result: dict[str, Any] = {}
    with database.transaction() as connection:
        connection.execute(
            "INSERT INTO app.login_limits(key_hash,started_at) VALUES(%s,%s) ON CONFLICT DO NOTHING",
            (key, now),
        )
        limit = connection.execute(
            "SELECT failures,started_at FROM app.login_limits WHERE key_hash=%s FOR UPDATE", (key,)
        ).fetchone()
        assert limit is not None
        if now - limit["started_at"] >= timedelta(minutes=15):
            connection.execute(
                "UPDATE app.login_limits SET failures=0,started_at=%s WHERE key_hash=%s", (now, key)
            )
        elif limit["failures"] >= 10:
            raise ApiError(429, "login_rate_limited")
        user = connection.execute(
            "SELECT id,password_hash,active FROM app.users WHERE email=%s", (username,)
        ).fetchone()
        encoded = user["password_hash"] if user else _DUMMY_HASH
        valid = password_matches(body.password, encoded)
        if user is None or not user["active"] or not valid:
            connection.execute(
                "UPDATE app.login_limits SET failures=failures+1 WHERE key_hash=%s", (key,)
            )
            invalid = True
        else:
            set_context(connection, user["id"], UUID(int=0))
            memberships = connection.execute(
                "SELECT organization_id,role FROM app.memberships WHERE user_id=%s AND active "
                "ORDER BY organization_id",
                (user["id"],),
            ).fetchall()
            chosen = [
                m
                for m in memberships
                if body.organization_id is None or m["organization_id"] == body.organization_id
            ]
            if len(chosen) != 1:
                raise ApiError(401, "organization_selection_required")
            membership = chosen[0]
            set_context(connection, user["id"], membership["organization_id"], membership["role"])
            organization = connection.execute(
                "SELECT id FROM app.organizations WHERE active"
            ).fetchone()
            if organization is None:
                raise ApiError(401, "authentication_required")
            token = secrets.token_urlsafe(32)
            connection.execute(
                "INSERT INTO app.sessions VALUES(%s,%s,%s,%s,%s,false)",
                (
                    digest(token),
                    user["id"],
                    membership["organization_id"],
                    now + timedelta(hours=12),
                    now,
                ),
            )
            connection.execute("UPDATE app.login_limits SET failures=0 WHERE key_hash=%s", (key,))
            actor = Actor(
                user["id"], membership["organization_id"], membership["role"], token, connection
            )
            result = profile(actor)
            if body.native:
                result["access_token"] = token
            else:
                response.set_cookie(
                    "nursery_session",
                    token,
                    max_age=43200,
                    httponly=True,
                    secure=request.app.state.secure_cookies,
                    samesite="strict",
                    path="/api/v1",
                )
    if invalid:
        raise ApiError(401, "invalid_credentials")
    return result


@auth_router.get("/me", summary="Reload current role, active organization and visible branches")
def me(actor: Authenticated) -> dict[str, Any]:
    return profile(actor)


@auth_router.post("/logout", status_code=204, summary="Revoke the current server session")
def logout(actor: Authenticated, response: Response) -> None:
    actor.connection.execute(
        "UPDATE app.sessions SET revoked=true WHERE token_hash=%s", (digest(actor.token),)
    )
    response.delete_cookie("nursery_session", path="/api/v1")


def configure_runtime(
    app: FastAPI, database_url: str, origins: list[str], secure_cookies: bool
) -> None:
    """Attach connected routes only when explicitly configured with a database."""
    app.state.database = Database(database_url)
    app.state.origins = frozenset(origins)
    app.state.secure_cookies = secure_cookies
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "Idempotency-Key"],
    )

    @app.exception_handler(ApiError)
    def safe_error(request: Request, error: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status,
            content={"code": error.code, "correlation_id": str(uuid4())},
            headers={"Cache-Control": "no-store"},
        )

    @app.middleware("http")
    async def private_responses(request: Request, call_next: Any) -> Response:
        result: Response = await call_next(request)
        result.headers["Cache-Control"] = "no-store"
        result.headers["X-Content-Type-Options"] = "nosniff"
        return result

    app.include_router(auth_router)

    @app.exception_handler(RequestValidationError)
    def safe_validation(request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": "invalid_input",
                "correlation_id": str(uuid4()),
                "fields": [
                    {"location": list(item["loc"]), "type": item["type"]} for item in error.errors()
                ],
            },
        )

    @app.exception_handler(OperationalError)
    def database_unavailable(request: Request, error: OperationalError) -> JSONResponse:
        return JSONResponse(
            status_code=503, content={"code": "service_unavailable", "correlation_id": str(uuid4())}
        )
