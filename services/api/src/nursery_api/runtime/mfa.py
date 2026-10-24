"""Encrypted TOTP enrollment, one-use recovery and session-bound retry receipts.

Five failed verifications per five-minute user window; a consumed TOTP counter
cannot authorize a different operation. Ciphertext retry receipts expire after
ten minutes. No OTP, seed or recovery code is written into audit or logs.
"""

import hashlib
import hmac
import json
import secrets
from dataclasses import replace
from datetime import timedelta
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse
from psycopg.types.json import Jsonb
from pydantic import Field

from .api import (
    Actor,
    ApiError,
    CommittedRoute,
    LimitedAuthenticated,
    StrictModel,
    now_utc,
    profile,
)
from .security import digest

router = APIRouter(prefix="/api/v1/auth/mfa", tags=["Account security"], route_class=CommittedRoute)
Operation = Annotated[UUID, Header(alias="Idempotency-Key")]


class Verification(StrictModel):
    code: str = Field(min_length=6, max_length=80, repr=False)
    kind: Literal["totp", "recovery"] = "totp"


class Empty(StrictModel):
    pass


def cipher(request: Request) -> Fernet:
    value: Fernet | None = request.app.state.mfa_cipher
    if value is None:
        raise ApiError(503, "account_security_unavailable")
    return value


def locked_enrollment(actor: Actor) -> dict[str, Any]:
    actor.connection.execute(
        "INSERT INTO app.mfa_enrollments(user_id) VALUES(%s) ON CONFLICT DO NOTHING",
        (actor.user_id,),
    )
    row = actor.connection.execute(
        "SELECT * FROM app.mfa_enrollments WHERE user_id=%s FOR UPDATE",
        (actor.user_id,),
    ).fetchone()
    assert row is not None
    current = actor.connection.execute(
        "SELECT token_hash FROM app.sessions WHERE token_hash=%s AND user_id=%s AND NOT revoked AND expires_at>%s",
        (digest(actor.token), actor.user_id, now_utc()),
    ).fetchone()
    if current is None:
        raise ApiError(401, "authentication_required")
    return row


def audit(actor: Actor, action: str) -> None:
    actor.connection.execute(
        "INSERT INTO app.audit VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (
            actor.organization_id,
            uuid4(),
            actor.user_id,
            action,
            actor.user_id,
            now_utc(),
            Jsonb({}),
        ),
    )


def limited(row: dict[str, Any], actor: Actor) -> bool:
    if now_utc() - row["window_started_at"] >= timedelta(minutes=5):
        actor.connection.execute(
            "UPDATE app.mfa_enrollments SET failures=0,window_started_at=%s WHERE user_id=%s",
            (now_utc(), actor.user_id),
        )
        row["failures"] = 0
    return bool(row["failures"] >= 5)


def deny(actor: Actor) -> JSONResponse:
    # Return a response, rather than raising through the transaction dependency,
    # so failed-attempt counters and the minimal security audit commit.
    actor.connection.execute(
        "UPDATE app.mfa_enrollments SET failures=failures+1 WHERE user_id=%s", (actor.user_id,)
    )
    audit(actor, "mfa.verification_denied")
    return JSONResponse(
        status_code=403,
        content={"code": "invalid_mfa_verification", "correlation_id": str(uuid4())},
    )


def matching_counter(secret: str, code: str, previous: int) -> int | None:
    if len(code) != 6 or not code.isascii() or not code.isdigit():
        return None
    otp = pyotp.TOTP(secret)
    counter = otp.timecode(now_utc())
    for value in (counter, counter - 1, counter + 1):
        if value > previous and hmac.compare_digest(otp.generate_otp(value), code):
            return value
    return None


def request_hash(action: str, body: Verification) -> str:
    return hashlib.sha256(
        json.dumps([action, body.model_dump()], sort_keys=True).encode()
    ).hexdigest()


def retry(actor: Actor, operation: UUID, command_hash: str, key: Fernet) -> dict[str, Any] | None:
    actor.connection.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
        (f"auth:{actor.user_id}:{digest(actor.token)}:{operation}",),
    )
    row = actor.connection.execute(
        "SELECT fingerprint,response_cipher FROM app.auth_receipts WHERE user_id=%s AND session_hash=%s AND operation_id=%s",
        (actor.user_id, digest(actor.token), operation),
    ).fetchone()
    if row is None:
        return None
    if row["fingerprint"] != command_hash:
        raise ApiError(409, "operation_conflict")
    if actor.mfa_at is None:
        raise ApiError(403, "reauthentication_required")
    try:
        data: dict[str, Any] = json.loads(key.decrypt(row["response_cipher"].encode(), ttl=600))
    except InvalidToken as error:
        raise ApiError(409, "verification_retry_expired") from error
    return dict(data, profile=profile(actor), replayed=True)


def receipt(
    actor: Actor, operation: UUID, command_hash: str, result: dict[str, Any], key: Fernet
) -> dict[str, Any]:
    payload = dict(result, replayed=False)
    encrypted = key.encrypt(json.dumps(payload, default=str).encode()).decode()
    actor.connection.execute(
        "INSERT INTO app.auth_receipts VALUES(%s,%s,%s,%s,%s,%s)",
        (actor.user_id, digest(actor.token), operation, command_hash, encrypted, now_utc()),
    )
    return payload


def upgrade_session(actor: Actor) -> Actor:
    now = now_utc()
    assert actor.authenticated_at is not None
    actor.connection.execute(
        "UPDATE app.sessions SET mfa_at=%s,expires_at=%s WHERE token_hash=%s AND user_id=%s",
        (now, actor.authenticated_at + timedelta(hours=12), digest(actor.token), actor.user_id),
    )
    actor.connection.execute(
        "UPDATE app.mfa_enrollments SET failures=0,window_started_at=%s WHERE user_id=%s",
        (now, actor.user_id),
    )
    return replace(actor, mfa_at=now, mfa_enrolled=True, mfa_required=True)


@router.post(
    "/begin",
    summary="Begin/rotate TOTP enrollment; seed encrypted at rest and bound to this session",
)
def begin(body: Empty, actor: LimitedAuthenticated, request: Request) -> dict[str, str]:
    key = cipher(request)
    row = locked_enrollment(actor)
    if row["activated_at"] is not None and (
        actor.mfa_at is None or now_utc() - actor.mfa_at > timedelta(minutes=15)
    ):
        raise ApiError(403, "reauthentication_required")
    if (
        row["pending_cipher"] is not None
        and row["pending_session_hash"] == digest(actor.token)
        and now_utc() - row["pending_at"] < timedelta(minutes=10)
    ):
        try:
            secret = key.decrypt(row["pending_cipher"].encode(), ttl=600).decode()
        except InvalidToken as error:
            raise ApiError(503, "account_security_unavailable") from error
    else:
        secret = pyotp.random_base32()
        actor.connection.execute(
            "UPDATE app.mfa_enrollments SET pending_cipher=%s,pending_session_hash=%s,pending_at=%s WHERE user_id=%s",
            (key.encrypt(secret.encode()).decode(), digest(actor.token), now_utc(), actor.user_id),
        )
        audit(actor, "mfa.enrollment_started")
    return {
        "secret": secret,
        "otpauth_uri": pyotp.TOTP(secret).provisioning_uri(
            name=str(actor.user_id), issuer_name="Nursery"
        ),
    }


@router.post(
    "/confirm",
    response_model=None,
    summary="Confirm TOTP, issue recovery codes once and revoke other sessions atomically",
)
def confirm(
    body: Verification, actor: LimitedAuthenticated, request: Request, operation: Operation
) -> dict[str, Any] | JSONResponse:
    key = cipher(request)
    command_hash = request_hash("confirm", body)
    cached = retry(actor, operation, command_hash, key)
    if cached is not None:
        return cached
    row = locked_enrollment(actor)
    if limited(row, actor):
        return JSONResponse(
            status_code=429,
            content={"code": "verification_rate_limited", "correlation_id": str(uuid4())},
        )
    if (
        body.kind != "totp"
        or row["pending_cipher"] is None
        or row["pending_session_hash"] != digest(actor.token)
        or now_utc() - row["pending_at"] >= timedelta(minutes=10)
    ):
        return deny(actor)
    try:
        secret = key.decrypt(row["pending_cipher"].encode(), ttl=600).decode()
    except InvalidToken as error:
        raise ApiError(503, "account_security_unavailable") from error
    counter = matching_counter(secret, body.code, -1)
    if counter is None:
        return deny(actor)
    actor.connection.execute(
        "UPDATE app.mfa_enrollments SET secret_cipher=pending_cipher,activated_at=%s,last_counter=%s,"
        "pending_cipher=NULL,pending_session_hash=NULL,pending_at=NULL WHERE user_id=%s",
        (now_utc(), counter, actor.user_id),
    )
    actor.connection.execute(
        "UPDATE app.mfa_recovery_codes SET used_at=%s WHERE user_id=%s AND used_at IS NULL",
        (now_utc(), actor.user_id),
    )
    codes = [secrets.token_hex(10) for _ in range(10)]
    for code in codes:
        actor.connection.execute(
            "INSERT INTO app.mfa_recovery_codes VALUES(%s,%s,%s,NULL)",
            (actor.user_id, digest(str(actor.user_id) + "\0" + code), now_utc()),
        )
    actor.connection.execute(
        "UPDATE app.sessions SET revoked=true WHERE user_id=%s AND token_hash<>%s",
        (actor.user_id, digest(actor.token)),
    )
    upgraded = upgrade_session(actor)
    audit(actor, "mfa.enrollment_confirmed")
    return receipt(
        actor, operation, command_hash, {"profile": profile(upgraded), "recovery_codes": codes}, key
    )


@router.post(
    "/verify",
    response_model=None,
    summary="Verify a fresh TOTP or consume one recovery code; no reusable role proof",
)
def verify(
    body: Verification, actor: LimitedAuthenticated, request: Request, operation: Operation
) -> dict[str, Any] | JSONResponse:
    key = cipher(request)
    command_hash = request_hash("verify", body)
    cached = retry(actor, operation, command_hash, key)
    if cached is not None:
        return cached
    row = locked_enrollment(actor)
    if limited(row, actor):
        return JSONResponse(
            status_code=429,
            content={"code": "verification_rate_limited", "correlation_id": str(uuid4())},
        )
    if row["secret_cipher"] is None:
        return deny(actor)
    if body.kind == "totp":
        try:
            secret = key.decrypt(row["secret_cipher"].encode()).decode()
        except InvalidToken as error:
            raise ApiError(503, "account_security_unavailable") from error
        counter = matching_counter(secret, body.code, row["last_counter"])
        if counter is None:
            return deny(actor)
        actor.connection.execute(
            "UPDATE app.mfa_enrollments SET last_counter=%s WHERE user_id=%s",
            (counter, actor.user_id),
        )
    else:
        normalized = body.code.replace("-", "").replace(" ", "").lower()
        saved = actor.connection.execute(
            "UPDATE app.mfa_recovery_codes SET used_at=%s WHERE user_id=%s AND code_hash=%s AND used_at IS NULL RETURNING code_hash",
            (now_utc(), actor.user_id, digest(str(actor.user_id) + "\0" + normalized)),
        ).fetchone()
        if saved is None:
            return deny(actor)
    upgraded = upgrade_session(actor)
    audit(actor, "mfa.verified" if body.kind == "totp" else "mfa.recovery_used")
    return receipt(actor, operation, command_hash, {"profile": profile(upgraded)}, key)
