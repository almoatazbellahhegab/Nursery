"""Pure basic attendance transitions; no SQL, HTTP, logging or policy defaults."""

from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from .models import (
    AttendanceAction,
    AttendanceCommand,
    AttendanceDecision,
    AttendanceError,
    AttendanceErrorCode,
    AttendanceEvent,
    AttendanceReceipt,
    AttendanceSnapshot,
    Presence,
    VerifiedAttendanceGrant,
    utc_instant,
)


def decide_attendance(
    command: AttendanceCommand,
    current: AttendanceSnapshot,
    grant: VerifiedAttendanceGrant,
    *,
    recorded_at: datetime,
    receipt: AttendanceReceipt | None = None,
) -> AttendanceDecision:
    """Propose check-in/out or return the exact earlier result for a valid retry.

    Raises AttendanceError for denied scope/expiry, operation reuse, stale
    versions, impossible presence transitions or out-of-order/future events.
    The caller owns authoritative authorization and a transaction that locks
    the child state, loads its receipt and commits state/event/receipt/audit/
    outbox together. Retried results are historical responses, never fresh
    writes. No authorization, database or multi-client concurrency guarantee
    is established by this pure function. Correction/absence policy is DEC-06.
    """
    now = utc_instant(recorded_at)
    # Check scope before receipts or state conflicts to avoid cross-scope leaks.
    if grant.target != command.target or current.target != command.target:
        raise AttendanceError(AttendanceErrorCode.ACCESS_DENIED)
    if now >= grant.expires_at:
        raise AttendanceError(AttendanceErrorCode.ACCESS_DENIED)

    if receipt is not None:
        return _replay(command, grant, receipt)

    if command.expected_version != current.version:
        raise AttendanceError(AttendanceErrorCode.VERSION_CONFLICT)
    if command.occurred_at > now or (
        current.last_occurred_at is not None and command.occurred_at < current.last_occurred_at
    ):
        raise AttendanceError(AttendanceErrorCode.CHRONOLOGY_CONFLICT)

    if command.action == AttendanceAction.CHECK_IN:
        if current.presence == Presence.PRESENT:
            raise AttendanceError(AttendanceErrorCode.ALREADY_PRESENT)
        presence = Presence.PRESENT
    else:
        if current.presence != Presence.PRESENT:
            raise AttendanceError(AttendanceErrorCode.NOT_PRESENT)
        presence = Presence.NOT_PRESENT

    next_state = AttendanceSnapshot(
        target=current.target,
        presence=presence,
        version=current.version + 1,
        last_occurred_at=command.occurred_at,
    )
    event = AttendanceEvent(
        event_id=uuid4(),
        operation_id=command.operation_id,
        target=current.target,
        actor_id=grant.actor_id,
        action=command.action,
        occurred_at=command.occurred_at,
        recorded_at=now,
        version=next_state.version,
    )
    return AttendanceDecision(snapshot=next_state, event=event)


def _replay(
    command: AttendanceCommand,
    grant: VerifiedAttendanceGrant,
    receipt: AttendanceReceipt,
) -> AttendanceDecision:
    """Preserve receipt scope, payload identity and the original event on retries."""
    saved = receipt.decision
    if receipt.actor_id != grant.actor_id or receipt.command.target != grant.target:
        raise AttendanceError(AttendanceErrorCode.ACCESS_DENIED)
    if receipt.command != command:
        raise AttendanceError(AttendanceErrorCode.OPERATION_CONFLICT)
    # Treat mismatched stored receipt parts as unusable; never synthesize success.
    if (
        saved.replayed
        or saved.event.actor_id != grant.actor_id
        or saved.event.target != command.target
        or saved.snapshot.target != command.target
        or saved.event.operation_id != command.operation_id
        or saved.event.action != command.action
        or saved.event.occurred_at != command.occurred_at
        or saved.event.version != command.expected_version + 1
        or saved.snapshot.version != saved.event.version
        or saved.snapshot.last_occurred_at != saved.event.occurred_at
        or saved.snapshot.presence
        != (
            Presence.PRESENT
            if command.action == AttendanceAction.CHECK_IN
            else Presence.NOT_PRESENT
        )
    ):
        raise AttendanceError(AttendanceErrorCode.OPERATION_CONFLICT)
    return replace(saved, replayed=True)
