"""ADM-APPT: opaque calendar decisions, not a production scheduling integration."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from nursery_api.admissions.appointments import (
    AppointmentAction,
    AppointmentCalendar,
    AppointmentCommand,
    AppointmentError,
    AppointmentErrorCode,
    AppointmentKind,
    AppointmentScope,
    AppointmentSnapshot,
    AppointmentStatus,
    HostSlot,
    decide_appointment,
)
from nursery_api.admissions.stages import (
    AdmissionsError,
    AdmissionsErrorCode,
    LeadScope,
    VerifiedAdmissionsGrant,
)

NOW = datetime(2026, 10, 24, 7, tzinfo=UTC)
LEAD = LeadScope(UUID(int=201), UUID(int=202), UUID(int=203))
SCOPE = AppointmentScope(LEAD, UUID(int=204))
HOST = UUID(int=205)
SLOT = HostSlot(HOST, NOW + timedelta(hours=2), NOW + timedelta(hours=3))
GRANT = VerifiedAdmissionsGrant(LEAD.organization_id, LEAD.branch_id, UUID(int=206), SLOT.ends_at)
CALENDAR = AppointmentCalendar(
    LEAD.organization_id,
    LEAD.branch_id,
    (HostSlot(HOST, NOW + timedelta(hours=1), NOW + timedelta(hours=6)),),
    (),
    frozenset({"SYNTHETIC_RESCHEDULE", "SYNTHETIC_CANCEL"}),
)
COMMAND = AppointmentCommand(
    SCOPE, UUID(int=207), 0, AppointmentAction.SCHEDULE, AppointmentKind.VISIT, SLOT
)


def scheduled() -> AppointmentSnapshot:
    return decide_appointment(COMMAND, None, GRANT, CALENDAR, changed_at=NOW).snapshot


def change_command(action: AppointmentAction) -> AppointmentCommand:
    return replace(
        COMMAND,
        operation_id=UUID(int=208),
        expected_version=1,
        action=action,
        slot=None
        if action == AppointmentAction.CANCEL
        else replace(SLOT, starts_at=SLOT.ends_at, ends_at=SLOT.ends_at + timedelta(hours=1)),
        reason_code="SYNTHETIC_CANCEL"
        if action == AppointmentAction.CANCEL
        else "SYNTHETIC_RESCHEDULE",
    )


def other_booking(
    *,
    host: UUID = HOST,
    start: datetime = SLOT.starts_at,
    end: datetime = SLOT.ends_at,
    branch: UUID = LEAD.branch_id,
    status: AppointmentStatus = AppointmentStatus.SCHEDULED,
) -> AppointmentSnapshot:
    scope = AppointmentScope(replace(LEAD, branch_id=branch, lead_id=UUID(int=209)), UUID(int=210))
    return AppointmentSnapshot(
        scope, AppointmentKind.TRIAL, HostSlot(host, start, end), status, 1, NOW
    )


@pytest.mark.parametrize("kind", list(AppointmentKind))
def test_adm_appt_001_visit_and_trial_record_host_scope_and_immutable_history(
    kind: AppointmentKind,
) -> None:
    result = decide_appointment(replace(COMMAND, kind=kind), None, GRANT, CALENDAR, changed_at=NOW)
    assert result.snapshot.scope == SCOPE
    assert result.snapshot.kind == kind
    assert result.snapshot.slot == SLOT
    assert result.snapshot.version == 1
    assert result.snapshot.status == AppointmentStatus.SCHEDULED
    assert result.history.previous is None
    assert result.history.snapshot is result.snapshot
    assert result.history.actor_id == GRANT.actor_id
    assert result.history.operation_id == COMMAND.operation_id
    assert result.history.action == AppointmentAction.SCHEDULE
    assert result.history.reason_code is None
    assert CALENDAR.appointments == ()
    with pytest.raises(FrozenInstanceError):
        setattr(result.snapshot, "version", 2)
    with pytest.raises(FrozenInstanceError):
        setattr(result.history, "actor_id", UUID(int=999))


@pytest.mark.parametrize("offset", [-5, 0, 3])
def test_adm_appt_002_offsets_compare_as_instants_and_store_utc(offset: int) -> None:
    zone = timezone(timedelta(hours=offset))
    slot = HostSlot(HOST, SLOT.starts_at.astimezone(zone), SLOT.ends_at.astimezone(zone))
    result = decide_appointment(
        replace(COMMAND, slot=slot), None, GRANT, CALENDAR, changed_at=NOW.astimezone(zone)
    )
    assert result.snapshot.slot == SLOT
    assert result.snapshot.slot.starts_at.tzinfo is UTC
    assert result.snapshot.changed_at == NOW and result.snapshot.changed_at.tzinfo is UTC


@pytest.mark.parametrize("end", [SLOT.starts_at, SLOT.starts_at - timedelta(seconds=1)])
def test_adm_appt_003_nonpositive_slots_are_rejected(end: datetime) -> None:
    with pytest.raises(AdmissionsError, match="^admissions_invalid_value$"):
        replace(SLOT, ends_at=end)


@pytest.mark.parametrize("field", ["start", "end", "now"])
def test_adm_appt_004_naive_instants_are_rejected(field: str) -> None:
    with pytest.raises(AdmissionsError, match="^admissions_invalid_value$"):
        slot = HostSlot(
            HOST,
            SLOT.starts_at.replace(tzinfo=None) if field == "start" else SLOT.starts_at,
            SLOT.ends_at.replace(tzinfo=None) if field == "end" else SLOT.ends_at,
        )
        decide_appointment(
            replace(COMMAND, slot=slot),
            None,
            GRANT,
            CALENDAR,
            changed_at=NOW.replace(tzinfo=None) if field == "now" else NOW,
        )


@pytest.mark.parametrize(
    "case", ["org", "branch", "calendar", "calendar_org", "expired", "current"]
)
def test_adm_appt_005_access_denial_precedes_version_and_calendar_disclosure(case: str) -> None:
    grant = (
        replace(GRANT, organization_id=UUID(int=999))
        if case == "org"
        else (replace(GRANT, branch_id=UUID(int=999)) if case == "branch" else GRANT)
    )
    calendar = replace(CALENDAR, availability=())
    if case == "calendar":
        calendar = replace(calendar, branch_id=UUID(int=999))
    elif case == "calendar_org":
        calendar = replace(calendar, organization_id=UUID(int=999))
    current = (
        replace(scheduled(), scope=replace(SCOPE, appointment_id=UUID(int=999)))
        if (case == "current")
        else None
    )
    with pytest.raises(AdmissionsError) as error:
        decide_appointment(
            replace(COMMAND, expected_version=99),
            current,
            grant,
            calendar,
            changed_at=GRANT.expires_at if case == "expired" else NOW,
        )
    assert error.value.code == AdmissionsErrorCode.ACCESS_DENIED
    assert str(error.value) == "admissions_access_denied"


@pytest.mark.parametrize("case", ["empty", "unknown_host", "before_open", "after_close", "gap"])
def test_adm_appt_006_requires_full_containment_in_supplied_host_availability(case: str) -> None:
    windows: tuple[HostSlot, ...] = ()
    if case == "unknown_host":
        windows = (replace(SLOT, host_id=UUID(int=999)),)
    elif case == "before_open":
        windows = (replace(SLOT, starts_at=SLOT.starts_at + timedelta(seconds=1)),)
    elif case == "after_close":
        windows = (replace(SLOT, ends_at=SLOT.ends_at - timedelta(seconds=1)),)
    elif case == "gap":
        windows = (
            replace(SLOT, ends_at=SLOT.starts_at + timedelta(minutes=20)),
            replace(SLOT, starts_at=SLOT.starts_at + timedelta(minutes=40)),
        )
    with pytest.raises(AppointmentError) as error:
        decide_appointment(
            COMMAND, None, GRANT, replace(CALENDAR, availability=windows), changed_at=NOW
        )
    assert error.value.code == AppointmentErrorCode.OUTSIDE_AVAILABILITY


@pytest.mark.parametrize("offset_minutes", [-30, 0, 30])
@pytest.mark.parametrize("other_branch", [False, True])
def test_adm_appt_007_same_host_overlaps_conflict_including_another_branch(
    offset_minutes: int,
    other_branch: bool,
) -> None:
    offset = timedelta(minutes=offset_minutes)
    booking = other_booking(
        start=SLOT.starts_at + offset,
        end=SLOT.ends_at + offset,
        branch=UUID(int=999) if other_branch else LEAD.branch_id,
    )
    with pytest.raises(AppointmentError) as error:
        decide_appointment(
            COMMAND, None, GRANT, replace(CALENDAR, appointments=(booking,)), changed_at=NOW
        )
    assert error.value.code == AppointmentErrorCode.HOST_CONFLICT
    assert str(error.value) == "admissions_appointment_host_conflict"


@pytest.mark.parametrize("case", ["previous", "following", "another_host", "cancelled"])
def test_adm_appt_008_adjacent_other_host_and_cancelled_slots_do_not_conflict(case: str) -> None:
    booking = (
        other_booking(start=SLOT.starts_at - timedelta(hours=1), end=SLOT.starts_at)
        if case == "previous"
        else other_booking(start=SLOT.ends_at, end=SLOT.ends_at + timedelta(hours=1))
        if case == "following"
        else other_booking(host=UUID(int=999))
        if case == "another_host"
        else other_booking(status=AppointmentStatus.CANCELLED)
    )
    result = decide_appointment(
        COMMAND,
        None,
        GRANT,
        replace(CALENDAR, availability=(SLOT,), appointments=(booking,)),
        changed_at=NOW,
    )
    assert result.snapshot.slot == SLOT


def test_adm_appt_009_reschedule_preserves_original_and_records_reason_actor_and_version() -> None:
    original = scheduled()
    command = change_command(AppointmentAction.RESCHEDULE)
    result = decide_appointment(
        command,
        original,
        GRANT,
        replace(CALENDAR, appointments=(original,)),
        changed_at=NOW + timedelta(minutes=1),
    )
    assert result.snapshot.slot == command.slot
    assert result.snapshot.version == 2
    assert result.history.previous is original
    assert result.history.reason_code == "SYNTHETIC_RESCHEDULE"
    assert result.history.actor_id == GRANT.actor_id
    assert result.history.snapshot is result.snapshot
    assert original.slot == SLOT and original.version == 1


def test_adm_appt_010_reschedule_cannot_move_into_another_booking() -> None:
    command = change_command(AppointmentAction.RESCHEDULE)
    assert command.slot is not None
    calendar = replace(
        CALENDAR,
        appointments=(other_booking(start=command.slot.starts_at, end=command.slot.ends_at),),
    )
    with pytest.raises(AppointmentError) as error:
        decide_appointment(command, scheduled(), GRANT, calendar, changed_at=NOW)
    assert error.value.code == AppointmentErrorCode.HOST_CONFLICT


def test_adm_appt_011_reschedule_excludes_only_its_unchanged_current_calendar_row() -> None:
    original = scheduled()
    command = replace(
        change_command(AppointmentAction.RESCHEDULE),
        slot=replace(SLOT, starts_at=SLOT.starts_at + timedelta(minutes=15)),
    )
    result = decide_appointment(
        command, original, GRANT, replace(CALENDAR, appointments=(original,)), changed_at=NOW
    )
    assert result.snapshot.version == 2
    corrupt_row = replace(original, slot=replace(SLOT, host_id=UUID(int=999)))
    with pytest.raises(AdmissionsError) as error:
        decide_appointment(
            command, original, GRANT, replace(CALENDAR, appointments=(corrupt_row,)), changed_at=NOW
        )
    assert error.value.code == AdmissionsErrorCode.OPERATION_CONFLICT


def test_adm_appt_012_cancel_preserves_slot_and_history_without_needing_open_hours() -> None:
    original = scheduled()
    result = decide_appointment(
        change_command(AppointmentAction.CANCEL),
        original,
        GRANT,
        replace(CALENDAR, availability=(), appointments=(original, other_booking())),
        changed_at=NOW,
    )
    assert result.snapshot.status == AppointmentStatus.CANCELLED
    assert result.snapshot.slot == SLOT
    assert result.snapshot.version == 2
    assert result.history.previous is original
    assert result.history.reason_code == "SYNTHETIC_CANCEL"
    assert original.status == AppointmentStatus.SCHEDULED


@pytest.mark.parametrize("action", [AppointmentAction.RESCHEDULE, AppointmentAction.CANCEL])
@pytest.mark.parametrize("reason", [None, "", "UNAPPROVED"])
def test_adm_appt_013_changes_require_a_reason_from_supplied_configuration(
    action: AppointmentAction,
    reason: str | None,
) -> None:
    with pytest.raises(AppointmentError) as error:
        decide_appointment(
            replace(change_command(action), reason_code=reason),
            scheduled(),
            GRANT,
            CALENDAR,
            changed_at=NOW,
        )
    assert error.value.code == AppointmentErrorCode.INVALID_REASON


@pytest.mark.parametrize("action", [AppointmentAction.RESCHEDULE, AppointmentAction.CANCEL])
def test_adm_appt_014_cancelled_appointments_cannot_be_mutated(action: AppointmentAction) -> None:
    current = replace(scheduled(), status=AppointmentStatus.CANCELLED)
    with pytest.raises(AppointmentError) as error:
        decide_appointment(change_command(action), current, GRANT, CALENDAR, changed_at=NOW)
    assert error.value.code == AppointmentErrorCode.INVALID_STATE


@pytest.mark.parametrize("case", ["create_existing", "change_missing", "kind_change"])
def test_adm_appt_015_creation_and_changes_require_consistent_existing_state(case: str) -> None:
    current = None if case == "change_missing" else scheduled()
    command = (
        replace(COMMAND, expected_version=1)
        if case == "create_existing"
        else (
            replace(change_command(AppointmentAction.RESCHEDULE), expected_version=0)
            if case == "change_missing"
            else replace(change_command(AppointmentAction.RESCHEDULE), kind=AppointmentKind.TRIAL)
        )
    )
    with pytest.raises(AppointmentError) as error:
        decide_appointment(command, current, GRANT, CALENDAR, changed_at=NOW)
    assert error.value.code == AppointmentErrorCode.INVALID_STATE


def test_adm_appt_016_stale_versions_and_backwards_history_are_rejected() -> None:
    original = scheduled()
    command = change_command(AppointmentAction.RESCHEDULE)
    with pytest.raises(AdmissionsError) as error:
        decide_appointment(
            replace(command, expected_version=0), original, GRANT, CALENDAR, changed_at=NOW
        )
    assert error.value.code == AdmissionsErrorCode.VERSION_CONFLICT
    with pytest.raises(AdmissionsError) as error:
        decide_appointment(
            command, original, GRANT, CALENDAR, changed_at=NOW - timedelta(seconds=1)
        )
    assert error.value.code == AdmissionsErrorCode.CHRONOLOGY_CONFLICT


def test_adm_appt_017_noop_reschedule_creates_no_new_history() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_appointment(
            replace(change_command(AppointmentAction.RESCHEDULE), slot=SLOT),
            scheduled(),
            GRANT,
            CALENDAR,
            changed_at=NOW,
        )
    assert error.value.code == AdmissionsErrorCode.NO_CHANGE


@pytest.mark.parametrize("version", [-1, True])
def test_adm_appt_018_invalid_versions_are_rejected(version: int) -> None:
    with pytest.raises(AdmissionsError, match="^admissions_invalid_value$"):
        replace(COMMAND, expected_version=version)


def test_adm_appt_019_untrusted_calendar_rows_and_duplicate_ids_are_rejected() -> None:
    booking = other_booking()
    with pytest.raises(AdmissionsError, match="^admissions_invalid_value$"):
        replace(CALENDAR, appointments=(booking, booking))
    with pytest.raises(AdmissionsError, match="^admissions_invalid_value$"):
        replace(
            CALENDAR,
            appointments=(
                replace(
                    booking,
                    scope=replace(
                        booking.scope,
                        lead=replace(booking.scope.lead, organization_id=UUID(int=999)),
                    ),
                ),
            ),
        )


def test_adm_appt_020_same_id_calendar_row_cannot_hide_creation_collision() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_appointment(
            COMMAND, None, GRANT, replace(CALENDAR, appointments=(scheduled(),)), changed_at=NOW
        )
    assert error.value.code == AdmissionsErrorCode.OPERATION_CONFLICT


@pytest.mark.parametrize("case", ["contains", "contained", "one_microsecond"])
def test_adm_appt_021_containment_and_minimal_overlap_are_still_host_conflicts(case: str) -> None:
    if case == "contains":
        booking = other_booking(
            start=SLOT.starts_at - timedelta(minutes=10),
            end=SLOT.ends_at + timedelta(minutes=10),
        )
    elif case == "contained":
        booking = other_booking(
            start=SLOT.starts_at + timedelta(minutes=10),
            end=SLOT.ends_at - timedelta(minutes=10),
        )
    else:
        booking = other_booking(
            start=SLOT.ends_at - timedelta(microseconds=1),
            end=SLOT.ends_at + timedelta(minutes=10),
        )
    with pytest.raises(AppointmentError) as error:
        decide_appointment(
            COMMAND, None, GRANT, replace(CALENDAR, appointments=(booking,)), changed_at=NOW
        )
    assert error.value.code == AppointmentErrorCode.HOST_CONFLICT


@pytest.mark.parametrize("case", ["missing_slot", "cancel_with_slot", "create_with_reason"])
def test_adm_appt_022_command_shape_cannot_silently_discard_requested_fields(case: str) -> None:
    with pytest.raises(AdmissionsError, match="^admissions_invalid_value$"):
        if case == "missing_slot":
            replace(COMMAND, slot=None)
        elif case == "cancel_with_slot":
            replace(change_command(AppointmentAction.CANCEL), slot=SLOT)
        else:
            replace(COMMAND, reason_code="SYNTHETIC_RESCHEDULE")
