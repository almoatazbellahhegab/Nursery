"""STAFF-UNIT scenarios exercise opaque decisions, not staff-policy approval."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import cast
from uuid import UUID

import pytest

from nursery_api.attendance.models import (
    AttendanceAction,
    AttendanceTarget,
    VerifiedAttendanceGrant,
)
from nursery_api.staff_attendance.presence import (
    StaffAction,
    StaffAttendanceCode,
    StaffAttendanceError,
    StaffCommand,
    StaffDecision,
    StaffIdentity,
    StaffReceipt,
    StaffSnapshot,
    StaffTarget,
    VerifiedStaffGrant,
    decide_staff_attendance,
)

NOW = datetime(2026, 10, 24, 7, tzinfo=UTC)
IDENTITY = StaffIdentity(UUID(int=301), UUID(int=302))
TARGET = StaffTarget(IDENTITY, UUID(int=303))
STATE = StaffSnapshot(IDENTITY)
COMMAND = StaffCommand(TARGET, UUID(int=304), StaffAction.CHECK_IN, NOW, 0)
GRANT = VerifiedStaffGrant(
    TARGET, UUID(int=305), StaffAction.CHECK_IN, True, NOW + timedelta(hours=8)
)


def present() -> StaffSnapshot:
    return decide_staff_attendance(COMMAND, STATE, GRANT, recorded_at=NOW).snapshot


def test_staff_unit_001_checkin_proposes_one_open_session_with_branch_and_trusted_actor() -> None:
    result = decide_staff_attendance(COMMAND, STATE, GRANT, recorded_at=NOW)
    assert result.snapshot.identity == IDENTITY
    assert result.snapshot.open_branch_id == TARGET.branch_id
    assert result.snapshot.open_session_id == result.event.session_id
    assert result.snapshot.version == result.event.version == 1
    assert result.event.target == TARGET
    assert result.event.actor_id == GRANT.actor_id
    assert result.event.operation_id == COMMAND.operation_id
    assert result.event.occurred_at == result.event.recorded_at == NOW
    assert STATE.open_session_id is None and STATE.version == 0
    with pytest.raises(FrozenInstanceError):
        setattr(result.snapshot, "open_session_id", None)
    with pytest.raises(FrozenInstanceError):
        setattr(result.event, "actor_id", UUID(int=999))


@pytest.mark.parametrize("other_branch", [False, True])
def test_staff_unit_002_open_session_blocks_duplicate_at_same_or_other_branch(
    other_branch: bool,
) -> None:
    target = replace(TARGET, branch_id=UUID(int=999)) if other_branch else TARGET
    command = replace(COMMAND, target=target, expected_version=1, operation_id=UUID(int=306))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(command, present(), replace(GRANT, target=target), recorded_at=NOW)
    assert error.value.code == StaffAttendanceCode.ALREADY_PRESENT


def test_staff_unit_003_checkout_closes_original_session_and_retains_its_branch() -> None:
    current = present()
    command = replace(
        COMMAND,
        action=StaffAction.CHECK_OUT,
        expected_version=1,
        occurred_at=NOW + timedelta(hours=1),
        operation_id=UUID(int=306),
    )
    result = decide_staff_attendance(
        command,
        current,
        replace(GRANT, action=StaffAction.CHECK_OUT),
        recorded_at=command.occurred_at,
    )
    assert result.snapshot.open_session_id is None and result.snapshot.open_branch_id is None
    assert result.event.session_id == current.open_session_id
    assert result.event.target.branch_id == TARGET.branch_id
    assert result.snapshot.version == 2
    assert current.open_session_id is not None
    next_result = decide_staff_attendance(
        replace(
            COMMAND,
            operation_id=UUID(int=307),
            expected_version=2,
            occurred_at=command.occurred_at,
        ),
        result.snapshot,
        GRANT,
        recorded_at=command.occurred_at,
    )
    assert next_result.event.session_id != result.event.session_id


def test_staff_unit_004_checkout_without_open_session_is_rejected() -> None:
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            replace(COMMAND, action=StaffAction.CHECK_OUT),
            STATE,
            replace(GRANT, action=StaffAction.CHECK_OUT),
            recorded_at=NOW,
        )
    assert error.value.code == StaffAttendanceCode.NOT_PRESENT


def test_staff_unit_005_checkout_at_another_branch_cannot_close_an_open_session() -> None:
    target = replace(TARGET, branch_id=UUID(int=999))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            replace(COMMAND, target=target, action=StaffAction.CHECK_OUT, expected_version=1),
            present(),
            replace(GRANT, target=target, action=StaffAction.CHECK_OUT),
            recorded_at=NOW,
        )
    assert error.value.code == StaffAttendanceCode.BRANCH_CONFLICT


@pytest.mark.parametrize(
    "case", ["organization", "employee", "branch", "action", "inactive", "expired"]
)
def test_staff_unit_006_denied_grants_hide_state_and_version_details(case: str) -> None:
    grant = GRANT
    if case == "organization":
        grant = replace(
            grant, target=replace(TARGET, identity=replace(IDENTITY, organization_id=UUID(int=999)))
        )
    elif case == "employee":
        grant = replace(
            grant, target=replace(TARGET, identity=replace(IDENTITY, employee_id=UUID(int=999)))
        )
    elif case == "branch":
        grant = replace(grant, target=replace(TARGET, branch_id=UUID(int=999)))
    elif case == "action":
        grant = replace(grant, action=StaffAction.CHECK_OUT)
    elif case == "inactive":
        grant = replace(grant, employee_active=False)
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            replace(COMMAND, expected_version=99),
            present(),
            grant,
            recorded_at=grant.expires_at if case == "expired" else NOW,
        )
    assert error.value.code == StaffAttendanceCode.ACCESS_DENIED
    assert str(error.value) == "staff_attendance_access_denied"


@pytest.mark.parametrize("field", ["organization_id", "employee_id"])
def test_staff_unit_007_other_employees_state_is_denied(field: str) -> None:
    identity = replace(IDENTITY, **{field: UUID(int=999)})
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(COMMAND, StaffSnapshot(identity), GRANT, recorded_at=NOW)
    assert error.value.code == StaffAttendanceCode.ACCESS_DENIED


def test_staff_unit_008_stale_version_is_rejected_before_presence_conflict() -> None:
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(COMMAND, present(), GRANT, recorded_at=NOW)
    assert error.value.code == StaffAttendanceCode.VERSION_CONFLICT


@pytest.mark.parametrize("case", ["future_event", "past_event", "past_recording"])
def test_staff_unit_009_future_and_backwards_instants_are_rejected(case: str) -> None:
    current = present()
    occurred = NOW + timedelta(seconds=1) if case == "future_event" else NOW
    recorded = NOW
    if case == "past_event":
        occurred = NOW - timedelta(seconds=1)
    elif case == "past_recording":
        current = replace(current, last_recorded_at=NOW + timedelta(seconds=1))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            replace(
                COMMAND, action=StaffAction.CHECK_OUT, expected_version=1, occurred_at=occurred
            ),
            current,
            replace(GRANT, action=StaffAction.CHECK_OUT),
            recorded_at=recorded,
        )
    assert error.value.code == StaffAttendanceCode.CHRONOLOGY_CONFLICT


@pytest.mark.parametrize("offset", [-5, 0, 3])
def test_staff_unit_010_equivalent_offsets_store_one_utc_instant(offset: int) -> None:
    instant = NOW.astimezone(timezone(timedelta(hours=offset)))
    result = decide_staff_attendance(
        replace(COMMAND, occurred_at=instant), STATE, GRANT, recorded_at=instant
    )
    assert result.event.occurred_at == NOW and result.event.occurred_at.tzinfo is UTC
    assert result.snapshot.last_recorded_at == NOW


@pytest.mark.parametrize("field", ["occurred", "recorded", "expiry"])
def test_staff_unit_011_naive_instants_are_rejected(field: str) -> None:
    naive = NOW.replace(tzinfo=None)
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        command = replace(COMMAND, occurred_at=naive) if field == "occurred" else COMMAND
        grant = replace(GRANT, expires_at=naive) if field == "expiry" else GRANT
        decide_staff_attendance(
            command, STATE, grant, recorded_at=naive if field == "recorded" else NOW
        )


@pytest.mark.parametrize("version", [-1, True])
def test_staff_unit_012_invalid_versions_are_rejected(version: int) -> None:
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        replace(COMMAND, expected_version=version)


@pytest.mark.parametrize("case", ["branch_only", "session_only", "version_zero", "future_record"])
def test_staff_unit_013_inconsistent_stored_presence_is_rejected(case: str) -> None:
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        if case == "branch_only":
            replace(present(), open_session_id=None)
        elif case == "session_only":
            replace(present(), open_branch_id=None)
        elif case == "version_zero":
            replace(present(), version=0)
        else:
            replace(present(), last_recorded_at=NOW - timedelta(seconds=1))


def test_staff_unit_014_child_grants_and_actions_cannot_be_used_as_staff_authority() -> None:
    child = AttendanceTarget(
        IDENTITY.organization_id, TARGET.branch_id, UUID(int=310), UUID(int=311)
    )
    grant = VerifiedAttendanceGrant(child, GRANT.actor_id, GRANT.expires_at)
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        decide_staff_attendance(COMMAND, STATE, cast(VerifiedStaffGrant, grant), recorded_at=NOW)
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        replace(COMMAND, action=cast(StaffAction, AttendanceAction.CHECK_IN))


def original_checkin() -> StaffDecision:
    return decide_staff_attendance(COMMAND, STATE, GRANT, recorded_at=NOW)


@pytest.mark.parametrize("offset", [-5, 0, 3])
def test_staff_unit_015_exact_retry_preserves_original_session_and_fact(offset: int) -> None:
    saved = original_checkin()
    command = replace(COMMAND, occurred_at=NOW.astimezone(timezone(timedelta(hours=offset))))
    replay = decide_staff_attendance(
        command,
        saved.snapshot,
        GRANT,
        recorded_at=NOW + timedelta(minutes=1),
        receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
    )
    assert replay.replayed and not saved.replayed
    assert replay.event is saved.event
    assert replay.snapshot is saved.snapshot
    assert replay.event.session_id == saved.event.session_id


def test_staff_unit_016_retry_after_checkout_does_not_reopen_or_roll_back_state() -> None:
    saved = original_checkin()
    checkout = replace(
        COMMAND,
        action=StaffAction.CHECK_OUT,
        expected_version=1,
        operation_id=UUID(int=312),
        occurred_at=NOW + timedelta(minutes=5),
    )
    later = decide_staff_attendance(
        checkout,
        saved.snapshot,
        replace(GRANT, action=StaffAction.CHECK_OUT),
        recorded_at=checkout.occurred_at,
    )
    replay = decide_staff_attendance(
        COMMAND,
        later.snapshot,
        GRANT,
        recorded_at=NOW + timedelta(minutes=10),
        receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
    )
    assert replay.replayed and replay.snapshot.open_session_id == saved.event.session_id
    assert later.snapshot.version == 2 and later.snapshot.open_session_id is None


@pytest.mark.parametrize("field", ["version", "operation", "action", "time"])
def test_staff_unit_017_reused_receipt_with_changed_command_fails(field: str) -> None:
    saved = original_checkin()
    if field == "version":
        changed = replace(COMMAND, expected_version=1)
    elif field == "operation":
        changed = replace(COMMAND, operation_id=UUID(int=999))
    elif field == "action":
        changed = replace(COMMAND, action=StaffAction.CHECK_OUT)
    else:
        changed = replace(COMMAND, occurred_at=NOW + timedelta(seconds=1))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            changed,
            saved.snapshot,
            replace(GRANT, action=changed.action),
            recorded_at=NOW + timedelta(minutes=1),
            receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert error.value.code == StaffAttendanceCode.OPERATION_CONFLICT


@pytest.mark.parametrize("case", ["actor", "branch", "employee", "organization"])
def test_staff_unit_018_other_actor_or_target_receipt_is_denied_before_payload(case: str) -> None:
    saved = original_checkin()
    receipt_actor = UUID(int=999) if case == "actor" else GRANT.actor_id
    target = TARGET
    if case == "branch":
        target = replace(target, branch_id=UUID(int=999))
    elif case == "employee":
        target = replace(target, identity=replace(IDENTITY, employee_id=UUID(int=999)))
    elif case == "organization":
        target = replace(target, identity=replace(IDENTITY, organization_id=UUID(int=999)))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            replace(COMMAND, expected_version=99),
            saved.snapshot,
            GRANT,
            recorded_at=NOW,
            receipt=StaffReceipt(replace(COMMAND, target=target), receipt_actor, saved),
        )
    assert error.value.code == StaffAttendanceCode.ACCESS_DENIED


@pytest.mark.parametrize("case", ["inactive", "expired", "action"])
def test_staff_unit_019_retry_rechecks_current_grant_before_receipt_conflicts(case: str) -> None:
    saved = original_checkin()
    grant = GRANT
    if case == "inactive":
        grant = replace(grant, employee_active=False)
    elif case == "action":
        grant = replace(grant, action=StaffAction.CHECK_OUT)
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            replace(COMMAND, expected_version=99),
            saved.snapshot,
            grant,
            recorded_at=grant.expires_at if case == "expired" else NOW,
            receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert error.value.code == StaffAttendanceCode.ACCESS_DENIED


@pytest.mark.parametrize(
    "part",
    [
        "actor",
        "operation",
        "action",
        "target",
        "session",
        "branch",
        "version",
        "occurred",
        "recorded",
        "identity",
        "replayed",
    ],
)
def test_staff_unit_020_inconsistent_saved_receipt_parts_cannot_claim_success(part: str) -> None:
    original = original_checkin()
    saved = original
    if part == "actor":
        saved = replace(saved, event=replace(saved.event, actor_id=UUID(int=999)))
    elif part == "operation":
        saved = replace(saved, event=replace(saved.event, operation_id=UUID(int=999)))
    elif part == "action":
        saved = replace(saved, event=replace(saved.event, action=StaffAction.CHECK_OUT))
    elif part == "target":
        saved = replace(
            saved, event=replace(saved.event, target=replace(TARGET, branch_id=UUID(int=999)))
        )
    elif part == "session":
        saved = replace(saved, snapshot=replace(saved.snapshot, open_session_id=UUID(int=999)))
    elif part == "branch":
        saved = replace(saved, snapshot=replace(saved.snapshot, open_branch_id=UUID(int=999)))
    elif part == "version":
        saved = replace(saved, event=replace(saved.event, version=2))
    elif part == "occurred":
        saved = replace(saved, event=replace(saved.event, occurred_at=NOW - timedelta(seconds=1)))
    elif part == "recorded":
        saved = replace(saved, event=replace(saved.event, recorded_at=NOW + timedelta(seconds=1)))
    elif part == "identity":
        saved = replace(
            saved,
            snapshot=replace(saved.snapshot, identity=replace(IDENTITY, employee_id=UUID(int=999))),
        )
    else:
        saved = replace(saved, replayed=True)
    # Most cases also supply the corrupt snapshot as current, proving that
    # agreeing copies cannot hide contradictions with the recorded event.
    current = original.snapshot if part == "identity" else saved.snapshot
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            COMMAND,
            current,
            GRANT,
            recorded_at=NOW + timedelta(minutes=1),
            receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert error.value.code == StaffAttendanceCode.OPERATION_CONFLICT


@pytest.mark.parametrize(
    "case", ["older", "same_version_other_session", "later_older_time", "future"]
)
def test_staff_unit_021_contradictory_current_state_is_not_hidden_by_receipt(case: str) -> None:
    saved = original_checkin()
    if case == "older":
        current = STATE
    elif case == "same_version_other_session":
        current = replace(saved.snapshot, open_session_id=UUID(int=999))
    elif case == "later_older_time":
        current = replace(
            saved.snapshot,
            version=2,
            last_occurred_at=NOW - timedelta(seconds=1),
            last_recorded_at=NOW - timedelta(seconds=1),
        )
    else:
        current = replace(saved.snapshot, version=2, last_recorded_at=NOW + timedelta(seconds=1))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            COMMAND,
            current,
            GRANT,
            recorded_at=NOW,
            receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert error.value.code == StaffAttendanceCode.OPERATION_CONFLICT


def test_staff_unit_022_checkout_replay_preserves_closed_state_and_original_session() -> None:
    initial = original_checkin()
    command = replace(
        COMMAND,
        action=StaffAction.CHECK_OUT,
        expected_version=1,
        operation_id=UUID(int=312),
        occurred_at=NOW + timedelta(minutes=1),
    )
    grant = replace(GRANT, action=StaffAction.CHECK_OUT)
    saved = decide_staff_attendance(
        command, initial.snapshot, grant, recorded_at=command.occurred_at
    )
    receipt = StaffReceipt(command, grant.actor_id, saved)
    replay = decide_staff_attendance(
        command, saved.snapshot, grant, recorded_at=command.occurred_at, receipt=receipt
    )
    assert replay.replayed and replay.event is saved.event
    assert replay.event.session_id == initial.event.session_id
    assert replay.snapshot.open_session_id is None
    corrupt = replace(
        saved,
        snapshot=replace(
            saved.snapshot, open_session_id=saved.event.session_id, open_branch_id=TARGET.branch_id
        ),
    )
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            command,
            saved.snapshot,
            grant,
            recorded_at=command.occurred_at,
            receipt=replace(receipt, decision=corrupt),
        )
    assert error.value.code == StaffAttendanceCode.OPERATION_CONFLICT


@pytest.mark.parametrize("version", [0, -1, True])
def test_staff_unit_023_receipt_events_require_positive_nonboolean_versions(version: int) -> None:
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        replace(original_checkin().event, version=version)


def test_staff_unit_024_event_recording_cannot_precede_occurrence() -> None:
    with pytest.raises(StaffAttendanceError, match="^staff_attendance_invalid_value$"):
        replace(original_checkin().event, recorded_at=NOW - timedelta(seconds=1))


def test_staff_unit_025_future_recorded_receipt_cannot_be_replayed_early() -> None:
    saved = decide_staff_attendance(COMMAND, STATE, GRANT, recorded_at=NOW + timedelta(seconds=1))
    with pytest.raises(StaffAttendanceError) as error:
        decide_staff_attendance(
            COMMAND,
            saved.snapshot,
            GRANT,
            recorded_at=NOW,
            receipt=StaffReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert error.value.code == StaffAttendanceCode.OPERATION_CONFLICT
