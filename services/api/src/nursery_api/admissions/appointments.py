"""Opaque admissions appointment planning; no invitations, PII model or persistence.

Availability and reason codes are supplied by a trusted adapter, with no default
hours, duration, role matrix or reason list. The adapter must establish current
action/branch/host permissions, load a complete calendar under a transaction and
atomically persist the proposed appointment, history, receipt and audit. These
pure decisions cannot establish concurrent-write safety or durable idempotency.
Planning constraints align with S03-DECISION-PACK revision 3; no role matrix,
production personal-data schema or specialist approval is supplied by this module.
"""

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .stages import (
    AdmissionsError,
    AdmissionsErrorCode,
    LeadScope,
    VerifiedAdmissionsGrant,
    _utc,
    _version,
)


class AppointmentErrorCode(StrEnum):
    """Stable errors with no calendar, resource or actor details."""

    OUTSIDE_AVAILABILITY = "admissions_appointment_outside_availability"
    HOST_CONFLICT = "admissions_appointment_host_conflict"
    INVALID_STATE = "admissions_appointment_invalid_state"
    INVALID_REASON = "admissions_appointment_invalid_reason"


class AppointmentError(Exception):
    """Appointment-specific rejection; common scope/version errors use AdmissionsError."""

    def __init__(self, code: AppointmentErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


class AppointmentKind(StrEnum):
    """Both source admissions appointment kinds share calendar constraints."""

    VISIT = "visit"
    TRIAL = "trial"


class AppointmentAction(StrEnum):
    """Cancellation is terminal; creating a new appointment is a separate operation."""

    SCHEDULE = "schedule"
    RESCHEDULE = "reschedule"
    CANCEL = "cancel"


class AppointmentStatus(StrEnum):
    """Recorded planning state, not attendance or notification delivery."""

    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AppointmentScope:
    """Tenant, branch, lead and appointment identity, with no family details."""

    lead: LeadScope
    appointment_id: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.lead, LeadScope) or not isinstance(self.appointment_id, UUID):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)


@dataclass(frozen=True)
class HostSlot:
    """One host's aware half-open interval [start, end), normalized to UTC."""

    host_id: UUID
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.host_id, UUID):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        start, end = _utc(self.starts_at), _utc(self.ends_at)
        if start >= end:
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        object.__setattr__(self, "starts_at", start)
        object.__setattr__(self, "ends_at", end)


@dataclass(frozen=True)
class AppointmentSnapshot:
    """Versioned planning state loaded by an authoritative future adapter."""

    scope: AppointmentScope
    kind: AppointmentKind
    slot: HostSlot
    status: AppointmentStatus
    version: int
    changed_at: datetime

    def __post_init__(self) -> None:
        _version(self.version, minimum=1)
        if (
            not isinstance(self.scope, AppointmentScope)
            or not isinstance(self.kind, AppointmentKind)
            or not isinstance(self.slot, HostSlot)
            or not isinstance(self.status, AppointmentStatus)
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        object.__setattr__(self, "changed_at", _utc(self.changed_at))


@dataclass(frozen=True)
class AppointmentCalendar:
    """Trusted branch availability and organization-wide busy appointments.

    Busy appointments may span branches to catch a shared host's conflicts.
    They are internal facts, never returned to the requesting client. A tuple
    does not prove completeness: a future transaction adapter owns that guarantee.
    """

    organization_id: UUID
    branch_id: UUID
    availability: tuple[HostSlot, ...]
    appointments: tuple[AppointmentSnapshot, ...]
    change_reason_codes: frozenset[str]

    def __post_init__(self) -> None:
        if not isinstance(self.organization_id, UUID) or not isinstance(self.branch_id, UUID):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        slots = tuple(self.availability)
        appointments = tuple(self.appointments)
        reasons = frozenset(self.change_reason_codes)
        if (
            any(not isinstance(slot, HostSlot) for slot in slots)
            or any(
                not isinstance(item, AppointmentSnapshot)
                or item.scope.lead.organization_id != self.organization_id
                for item in appointments
            )
            or any(not isinstance(code, str) or not code.strip() for code in reasons)
            or len({item.scope.appointment_id for item in appointments}) != len(appointments)
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        object.__setattr__(self, "availability", slots)
        object.__setattr__(self, "appointments", appointments)
        object.__setattr__(self, "change_reason_codes", reasons)


@dataclass(frozen=True)
class AppointmentCommand:
    """Versioned scheduling intent; no caller-asserted role or host eligibility."""

    scope: AppointmentScope
    operation_id: UUID
    expected_version: int
    action: AppointmentAction
    kind: AppointmentKind
    slot: HostSlot | None = None
    reason_code: str | None = None

    def __post_init__(self) -> None:
        _version(self.expected_version)
        if (
            not isinstance(self.scope, AppointmentScope)
            or not isinstance(self.operation_id, UUID)
            or not isinstance(self.action, AppointmentAction)
            or not isinstance(self.kind, AppointmentKind)
            or (self.action == AppointmentAction.CANCEL and self.slot is not None)
            or (self.action != AppointmentAction.CANCEL and not isinstance(self.slot, HostSlot))
            or (self.reason_code is not None and not isinstance(self.reason_code, str))
            or (self.action == AppointmentAction.SCHEDULE and self.reason_code is not None)
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)


@dataclass(frozen=True)
class AppointmentHistory:
    """One immutable proposed event; unchanged original facts remain available."""

    event_id: UUID
    operation_id: UUID
    actor_id: UUID
    action: AppointmentAction
    reason_code: str | None
    previous: AppointmentSnapshot | None
    snapshot: AppointmentSnapshot


@dataclass(frozen=True)
class AppointmentDecision:
    """Proposed state/history, without enrollment, stage change or outbound effects."""

    snapshot: AppointmentSnapshot
    history: AppointmentHistory


def decide_appointment(
    command: AppointmentCommand,
    current: AppointmentSnapshot | None,
    grant: VerifiedAdmissionsGrant,
    calendar: AppointmentCalendar,
    *,
    changed_at: datetime,
) -> AppointmentDecision:
    """Validate a schedule, reschedule or cancellation against trusted inputs.

    Scope/expiry denial precedes version, reason and availability details.
    Cancellation requires no free slot or current availability. Only overlapping
    scheduled appointments for the same host conflict, including another branch.
    The adapter must separately verify that the lead/host are active and eligible
    and that the granted actor can perform the specific action.
    """
    now = _utc(changed_at)
    lead = command.scope.lead
    if (
        grant.organization_id != lead.organization_id
        or grant.branch_id != lead.branch_id
        or calendar.organization_id != lead.organization_id
        or calendar.branch_id != lead.branch_id
        or (current is not None and current.scope != command.scope)
        or now >= grant.expires_at
    ):
        raise AdmissionsError(AdmissionsErrorCode.ACCESS_DENIED)

    # A same-ID calendar row must be the current row, never an unrelated booking
    # that can be hidden by excluding the appointment being rescheduled.
    for item in calendar.appointments:
        if item.scope.appointment_id == command.scope.appointment_id and item != current:
            raise AdmissionsError(AdmissionsErrorCode.OPERATION_CONFLICT)

    version = current.version if current is not None else 0
    if command.expected_version != version:
        raise AdmissionsError(AdmissionsErrorCode.VERSION_CONFLICT)
    if current is not None and now < current.changed_at:
        raise AdmissionsError(AdmissionsErrorCode.CHRONOLOGY_CONFLICT)
    if command.action == AppointmentAction.SCHEDULE:
        if current is not None:
            raise AppointmentError(AppointmentErrorCode.INVALID_STATE)
    else:
        if (
            current is None
            or current.status != AppointmentStatus.SCHEDULED
            or command.kind != current.kind
        ):
            raise AppointmentError(AppointmentErrorCode.INVALID_STATE)
        if command.reason_code not in calendar.change_reason_codes:
            raise AppointmentError(AppointmentErrorCode.INVALID_REASON)

    if command.action == AppointmentAction.CANCEL:
        assert current is not None
        snapshot = replace(
            current, status=AppointmentStatus.CANCELLED, version=version + 1, changed_at=now
        )
    else:
        assert command.slot is not None
        if current is not None and command.slot == current.slot:
            raise AdmissionsError(AdmissionsErrorCode.NO_CHANGE)
        _check_slot(command.slot, command.scope, calendar)
        snapshot = AppointmentSnapshot(
            command.scope,
            command.kind,
            command.slot,
            AppointmentStatus.SCHEDULED,
            version + 1,
            now,
        )
    history = AppointmentHistory(
        uuid4(),
        command.operation_id,
        grant.actor_id,
        command.action,
        command.reason_code,
        current,
        snapshot,
    )
    return AppointmentDecision(snapshot, history)


def _check_slot(slot: HostSlot, scope: AppointmentScope, calendar: AppointmentCalendar) -> None:
    """Linear calendar scan with boundary-safe containment and overlap checks."""
    if not any(
        window.host_id == slot.host_id
        and window.starts_at <= slot.starts_at
        and slot.ends_at <= window.ends_at
        for window in calendar.availability
    ):
        raise AppointmentError(AppointmentErrorCode.OUTSIDE_AVAILABILITY)
    if any(
        item.status == AppointmentStatus.SCHEDULED
        and item.scope.appointment_id != scope.appointment_id
        and item.slot.host_id == slot.host_id
        and slot.starts_at < item.slot.ends_at
        and item.slot.starts_at < slot.ends_at
        for item in calendar.appointments
    ):
        raise AppointmentError(AppointmentErrorCode.HOST_CONFLICT)
