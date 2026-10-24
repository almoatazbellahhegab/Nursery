"""Shared transaction-bound receipts and minimal immutable mutation audit."""

import hashlib
import json
from typing import Any
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from psycopg.types.json import Jsonb

from .api import Actor, ApiError, StrictModel, now_utc


def fingerprint(action: str, resource: UUID | None, body: StrictModel) -> str:
    return hashlib.sha256(
        json.dumps([action, str(resource), body.model_dump(mode="json")], sort_keys=True).encode()
    ).hexdigest()


def replay(actor: Actor, operation: UUID, command_hash: str) -> dict[str, Any] | None:
    actor.connection.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
        (f"command:{actor.organization_id}:{actor.user_id}:{operation}",),
    )
    row = actor.connection.execute(
        "SELECT fingerprint,response FROM app.command_receipts WHERE organization_id=%s "
        "AND actor_id=%s AND operation_id=%s",
        (actor.organization_id, actor.user_id, operation),
    ).fetchone()
    if row is None:
        return None
    if row["fingerprint"] != command_hash:
        raise ApiError(409, "operation_conflict")
    return dict(row["response"], replayed=True)


def complete(
    actor: Actor,
    operation: UUID,
    command_hash: str,
    result: dict[str, Any],
    action: str,
    resource: UUID,
    details: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = jsonable_encoder(dict(result, replayed=False))
    actor.connection.execute(
        "INSERT INTO app.command_receipts VALUES(%s,%s,%s,%s,%s,%s)",
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
            Jsonb(details),
        ),
    )
    return payload
