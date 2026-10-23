"""ATT-UNIT cases cover domain decisions only, linked to FEAT-011 source UAT."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from nursery_api.attendance.decisions import decide_attendance
from nursery_api.attendance.models import (
    AttendanceAction,
    AttendanceCommand,
    AttendanceDecision,
    AttendanceError,
    AttendanceErrorCode,
    AttendanceReceipt,
    AttendanceSnapshot,
    AttendanceTarget,
    Presence,
    VerifiedAttendanceGrant,
)

NOW = datetime(2026, 10, 23, 9, tzinfo=UTC)
TARGET = AttendanceTarget(UUID(int=1), UUID(int=2), UUID(int=3), UUID(int=4))
GRANT = VerifiedAttendanceGrant(TARGET, UUID(int=5), NOW + timedelta(hours=1))
COMMAND = AttendanceCommand(UUID(int=6), TARGET, AttendanceAction.CHECK_IN, NOW, 0)
EMPTY = AttendanceSnapshot(TARGET)


def check_in() -> AttendanceDecision:
    """Build a deterministic valid input; event UUID uniqueness is incidental."""
    return decide_attendance(COMMAND, EMPTY, GRANT, recorded_at=NOW)


def assert_code(error: pytest.ExceptionInfo[AttendanceError], code: AttendanceErrorCode) -> None:
    """Assert safe stable codes instead of identifier-bearing error details."""
    assert error.value.code == code
    assert str(error.value) == code.value


def test_att_unit_001_check_in_records_scope_actor_and_utc_time() -> None:
    """Partial TC-FEAT-011-01; no persistence or audit is claimed."""
    result = check_in()
    assert result.snapshot.presence == Presence.PRESENT
    assert result.snapshot.version == 1
    assert result.event.target == TARGET
    assert result.event.actor_id == GRANT.actor_id
    assert result.event.operation_id == COMMAND.operation_id
    assert result.event.occurred_at == result.snapshot.last_occurred_at == NOW
    assert result.event.recorded_at == NOW
    assert result.event.version == result.snapshot.version
    assert result.replayed is False
    assert EMPTY.version == 0


def test_att_unit_002_duplicate_check_in_does_not_change_existing_state() -> None:
    """Partial TC-FEAT-011-02; a new operation cannot create another present state."""
    original = check_in().snapshot
    duplicate = replace(COMMAND, operation_id=UUID(int=7), expected_version=1)
    with pytest.raises(AttendanceError) as error:
        decide_attendance(duplicate, original, GRANT, recorded_at=NOW)
    assert_code(error, AttendanceErrorCode.ALREADY_PRESENT)
    assert original.version == 1
    assert original.presence == Presence.PRESENT


def test_att_unit_003_check_out_has_matching_state_and_event_timestamp() -> None:
    """Partial TC-FEAT-011-03; timeline integration is deliberately not asserted."""
    checkout = replace(
        COMMAND,
        operation_id=UUID(int=7),
        action=AttendanceAction.CHECK_OUT,
        expected_version=1,
        occurred_at=NOW + timedelta(minutes=30),
    )
    result = decide_attendance(
        checkout, check_in().snapshot, GRANT, recorded_at=NOW + timedelta(minutes=31)
    )
    assert result.snapshot.presence == Presence.NOT_PRESENT
    assert result.snapshot.version == 2
    assert result.snapshot.last_occurred_at == result.event.occurred_at == checkout.occurred_at


def test_att_unit_004_checkout_without_presence_is_rejected() -> None:
    with pytest.raises(AttendanceError) as error:
        decide_attendance(
            replace(COMMAND, action=AttendanceAction.CHECK_OUT), EMPTY, GRANT, recorded_at=NOW
        )
    assert_code(error, AttendanceErrorCode.NOT_PRESENT)


def test_att_unit_005_exact_retry_returns_original_event_without_a_new_write() -> None:
    """Partial TC-FEAT-011-04; a durable receipt adapter is still required."""
    original = check_in()
    receipt = AttendanceReceipt(COMMAND, GRANT.actor_id, original)
    retry = decide_attendance(
        COMMAND, original.snapshot, GRANT, recorded_at=NOW + timedelta(minutes=1), receipt=receipt
    )
    assert retry.replayed is True
    assert retry.event == original.event
    assert retry.snapshot == original.snapshot
    assert original.replayed is False


def test_att_unit_006_retry_after_later_checkout_returns_historical_response_only() -> None:
    original = check_in()
    checkout = replace(
        COMMAND, operation_id=UUID(int=7), action=AttendanceAction.CHECK_OUT, expected_version=1
    )
    later = decide_attendance(checkout, original.snapshot, GRANT, recorded_at=NOW)
    retry = decide_attendance(
        COMMAND,
        later.snapshot,
        GRANT,
        recorded_at=NOW,
        receipt=AttendanceReceipt(COMMAND, GRANT.actor_id, original),
    )
    assert retry.replayed is True
    assert retry.snapshot.version == 1
    assert later.snapshot.version == 2
    assert later.snapshot.presence == Presence.NOT_PRESENT


@pytest.mark.parametrize("field", ["action", "occurred_at", "expected_version"])
def test_att_unit_007_changed_retry_payload_is_rejected(field: str) -> None:
    changed = {
        "action": replace(COMMAND, action=AttendanceAction.CHECK_OUT),
        "occurred_at": replace(COMMAND, occurred_at=NOW - timedelta(minutes=1)),
        "expected_version": replace(COMMAND, expected_version=1),
    }[field]
    with pytest.raises(AttendanceError) as error:
        decide_attendance(
            changed,
            EMPTY,
            GRANT,
            recorded_at=NOW,
            receipt=AttendanceReceipt(COMMAND, GRANT.actor_id, check_in()),
        )
    assert_code(error, AttendanceErrorCode.OPERATION_CONFLICT)


@pytest.mark.parametrize("field", ["organization_id", "branch_id", "classroom_id", "child_id"])
def test_att_unit_008_other_scope_is_denied_before_state_conflict(field: str) -> None:
    other = replace(TARGET, **{field: UUID(int=99)})
    with pytest.raises(AttendanceError) as error:
        decide_attendance(
            replace(COMMAND, target=other, expected_version=99), EMPTY, GRANT, recorded_at=NOW
        )
    assert_code(error, AttendanceErrorCode.ACCESS_DENIED)


def test_att_unit_009_wrong_snapshot_scope_is_denied() -> None:
    other = AttendanceSnapshot(replace(TARGET, organization_id=UUID(int=99)))
    with pytest.raises(AttendanceError) as error:
        decide_attendance(COMMAND, other, GRANT, recorded_at=NOW)
    assert_code(error, AttendanceErrorCode.ACCESS_DENIED)


@pytest.mark.parametrize("with_receipt", [False, True])
def test_att_unit_010_expired_grant_denies_even_a_previously_successful_retry(
    with_receipt: bool,
) -> None:
    original = check_in()
    with pytest.raises(AttendanceError) as error:
        decide_attendance(
            COMMAND,
            original.snapshot,
            GRANT,
            recorded_at=GRANT.expires_at,
            receipt=AttendanceReceipt(COMMAND, GRANT.actor_id, original) if with_receipt else None,
        )
    assert_code(error, AttendanceErrorCode.ACCESS_DENIED)


def test_att_unit_011_another_actor_cannot_replay_a_receipt() -> None:
    with pytest.raises(AttendanceError) as error:
        decide_attendance(
            COMMAND,
            EMPTY,
            replace(GRANT, actor_id=UUID(int=99)),
            recorded_at=NOW,
            receipt=AttendanceReceipt(COMMAND, GRANT.actor_id, check_in()),
        )
    assert_code(error, AttendanceErrorCode.ACCESS_DENIED)


def test_att_unit_012_stale_concurrent_command_requires_reload() -> None:
    """Optimistic decision only; database compare-and-swap remains an integration test."""
    with pytest.raises(AttendanceError) as error:
        decide_attendance(COMMAND, check_in().snapshot, GRANT, recorded_at=NOW)
    assert_code(error, AttendanceErrorCode.VERSION_CONFLICT)


@pytest.mark.parametrize("minute_delta", [-1, 1])
def test_att_unit_013_out_of_order_or_future_events_are_not_silently_reordered(
    minute_delta: int,
) -> None:
    checkout = replace(
        COMMAND,
        operation_id=UUID(int=7),
        action=AttendanceAction.CHECK_OUT,
        expected_version=1,
        occurred_at=NOW + timedelta(minutes=minute_delta),
    )
    with pytest.raises(AttendanceError) as error:
        decide_attendance(checkout, check_in().snapshot, GRANT, recorded_at=NOW)
    assert_code(error, AttendanceErrorCode.CHRONOLOGY_CONFLICT)


def test_att_unit_014_offset_timestamps_are_normalized_and_retries_compare_as_instants() -> None:
    local = NOW.astimezone(timezone(timedelta(hours=3)))
    command = replace(COMMAND, occurred_at=local)
    original = decide_attendance(command, EMPTY, GRANT, recorded_at=local)
    retry = decide_attendance(
        COMMAND,
        original.snapshot,
        GRANT,
        recorded_at=NOW,
        receipt=AttendanceReceipt(command, GRANT.actor_id, original),
    )
    assert original.event.occurred_at.tzinfo is UTC
    assert original.event.recorded_at.tzinfo is UTC
    assert retry.replayed is True


def test_att_unit_015_naive_time_is_rejected() -> None:
    with pytest.raises(AttendanceError) as error:
        replace(COMMAND, occurred_at=NOW.replace(tzinfo=None))
    assert_code(error, AttendanceErrorCode.INVALID_VALUE)


@pytest.mark.parametrize("version", [-1, True])
def test_att_unit_016_invalid_version_is_rejected(version: int) -> None:
    with pytest.raises(AttendanceError) as error:
        replace(COMMAND, expected_version=version)
    assert_code(error, AttendanceErrorCode.INVALID_VALUE)


def test_att_unit_017_corrupt_receipt_cannot_claim_a_successful_replay() -> None:
    original = check_in()
    corrupt = replace(original, event=replace(original.event, version=42))
    with pytest.raises(AttendanceError) as error:
        decide_attendance(
            COMMAND,
            EMPTY,
            GRANT,
            recorded_at=NOW,
            receipt=AttendanceReceipt(COMMAND, GRANT.actor_id, corrupt),
        )
    assert_code(error, AttendanceErrorCode.OPERATION_CONFLICT)


def test_att_unit_018_event_and_snapshot_are_immutable() -> None:
    original = check_in()
    with pytest.raises(FrozenInstanceError):
        setattr(original.event, "actor_id", UUID(int=99))
    with pytest.raises(FrozenInstanceError):
        setattr(original.snapshot, "presence", Presence.NOT_PRESENT)
