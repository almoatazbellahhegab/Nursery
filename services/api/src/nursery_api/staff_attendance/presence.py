"""Opaque employee check-in/out groundwork for DEV-FEAT-012-01.

State is keyed by organization and employee, not branch, so an open session at
one branch cannot be bypassed by checking in at another. Trusted grants include
the exact branch/action and current employee activity. They are internal inputs,
not authenticated credentials or a replacement for FEAT-010/FEAT-005.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class StaffAttendanceCode(StrEnum):
    """Non-identifying rejection codes for a future localized transport adapter."""

    INVALID_VALUE = "staff_attendance_invalid_value"
    ACCESS_DENIED = "staff_attendance_access_denied"
    VERSION_CONFLICT = "staff_attendance_version_conflict"
    CHRONOLOGY_CONFLICT = "staff_attendance_chronology_conflict"
    ALREADY_PRESENT = "staff_attendance_already_present"
    NOT_PRESENT = "staff_attendance_not_present"
    BRANCH_CONFLICT = "staff_attendance_branch_conflict"


class StaffAttendanceError(Exception):
    """Reject without changing state or exposing employee/branch details."""

    def __init__(self, code: StaffAttendanceCode) -> None:
        self.code = code
        super().__init__(code.value)


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
    return value.astimezone(UTC)


def _version(value: int) -> None:
    if type(value) is not int or value < 0:
        raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)


class StaffAction(StrEnum):
    """Correction, leave, shifts and payroll are deliberately separate workflows."""

    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


@dataclass(frozen=True)
class StaffIdentity:
    """Organization-wide employee key used to prevent cross-branch duplicates."""

    organization_id: UUID
    employee_id: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.organization_id, UUID) or not isinstance(self.employee_id, UUID):
            raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)


@dataclass(frozen=True)
class StaffTarget:
    """One employee at one branch; cannot substitute a child attendance target."""

    identity: StaffIdentity
    branch_id: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.identity, StaffIdentity) or not isinstance(self.branch_id, UUID):
            raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)


@dataclass(frozen=True)
class StaffCommand:
    """Versioned intent with no actor, employee-status or role claims."""

    target: StaffTarget
    operation_id: UUID
    action: StaffAction
    occurred_at: datetime
    expected_version: int

    def __post_init__(self) -> None:
        _version(self.expected_version)
        if (
            not isinstance(self.target, StaffTarget)
            or not isinstance(self.operation_id, UUID)
            or not isinstance(self.action, StaffAction)
        ):
            raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))


@dataclass(frozen=True)
class VerifiedStaffGrant:
    """Trusted current status/action grant, never created from request-body claims.

    The adapter must validate active identity, employee profile, assignment,
    branch/action authority, revocation and optional-module entitlement per call.
    A grant for child attendance is not accepted as a staff grant.
    """

    target: StaffTarget
    actor_id: UUID
    action: StaffAction
    employee_active: bool
    expires_at: datetime

    def __post_init__(self) -> None:
        if (
            not isinstance(self.target, StaffTarget)
            or not isinstance(self.actor_id, UUID)
            or not isinstance(self.action, StaffAction)
            or type(self.employee_active) is not bool
        ):
            raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
        object.__setattr__(self, "expires_at", _utc(self.expires_at))


@dataclass(frozen=True)
class StaffSnapshot:
    """At most one proposed open session across an organization's branches."""

    identity: StaffIdentity
    version: int = 0
    open_branch_id: UUID | None = None
    open_session_id: UUID | None = None
    last_occurred_at: datetime | None = None
    last_recorded_at: datetime | None = None

    def __post_init__(self) -> None:
        _version(self.version)
        if (
            not isinstance(self.identity, StaffIdentity)
            or (self.open_branch_id is None) != (self.open_session_id is None)
            or (self.open_branch_id is not None and not isinstance(self.open_branch_id, UUID))
            or (self.open_session_id is not None and not isinstance(self.open_session_id, UUID))
        ):
            raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
        if self.version == 0:
            if any(
                value is not None
                for value in (
                    self.open_branch_id,
                    self.open_session_id,
                    self.last_occurred_at,
                    self.last_recorded_at,
                )
            ):
                raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
        else:
            if self.last_occurred_at is None or self.last_recorded_at is None:
                raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
            occurred, recorded = _utc(self.last_occurred_at), _utc(self.last_recorded_at)
            if occurred > recorded:
                raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
            object.__setattr__(self, "last_occurred_at", occurred)
            object.__setattr__(self, "last_recorded_at", recorded)


@dataclass(frozen=True)
class StaffEvent:
    """Proposed immutable presence fact; session links check-in to its checkout."""

    event_id: UUID
    operation_id: UUID
    target: StaffTarget
    actor_id: UUID
    action: StaffAction
    session_id: UUID
    occurred_at: datetime
    recorded_at: datetime
    version: int


@dataclass(frozen=True)
class StaffDecision:
    """Pure state/event result; not a durable receipt or payroll record."""

    snapshot: StaffSnapshot
    event: StaffEvent


def decide_staff_attendance(
    command: StaffCommand,
    current: StaffSnapshot,
    grant: VerifiedStaffGrant,
    *,
    recorded_at: datetime,
) -> StaffDecision:
    """Propose a scoped check-in/out after current active/action/expiry checks.

    The caller must lock the employee's organization-wide state, recheck access,
    enforce operation uniqueness and atomically persist state/event/receipt/audit.
    No actual authentication, cross-process concurrency or retry durability is
    established here. Staff correction/report policy is not inferred from DEC-06.
    """
    now = _utc(recorded_at)
    if (
        not isinstance(command, StaffCommand)
        or not isinstance(current, StaffSnapshot)
        or not isinstance(grant, VerifiedStaffGrant)
    ):
        raise StaffAttendanceError(StaffAttendanceCode.INVALID_VALUE)
    if (
        grant.target != command.target
        or current.identity != command.target.identity
        or grant.action != command.action
        or not grant.employee_active
        or now >= grant.expires_at
    ):
        raise StaffAttendanceError(StaffAttendanceCode.ACCESS_DENIED)
    if command.expected_version != current.version:
        raise StaffAttendanceError(StaffAttendanceCode.VERSION_CONFLICT)
    if (
        command.occurred_at > now
        or (current.last_occurred_at is not None and command.occurred_at < current.last_occurred_at)
        or (current.last_recorded_at is not None and now < current.last_recorded_at)
    ):
        raise StaffAttendanceError(StaffAttendanceCode.CHRONOLOGY_CONFLICT)
    if command.action == StaffAction.CHECK_IN:
        if current.open_session_id is not None:
            raise StaffAttendanceError(StaffAttendanceCode.ALREADY_PRESENT)
        session_id = uuid4()
        branch_id: UUID | None = command.target.branch_id
        open_session_id: UUID | None = session_id
    else:
        if current.open_session_id is None:
            raise StaffAttendanceError(StaffAttendanceCode.NOT_PRESENT)
        if current.open_branch_id != command.target.branch_id:
            raise StaffAttendanceError(StaffAttendanceCode.BRANCH_CONFLICT)
        session_id = current.open_session_id
        branch_id, open_session_id = None, None

    snapshot = StaffSnapshot(
        current.identity,
        current.version + 1,
        branch_id,
        open_session_id,
        command.occurred_at,
        now,
    )
    event = StaffEvent(
        uuid4(),
        command.operation_id,
        command.target,
        grant.actor_id,
        command.action,
        session_id,
        command.occurred_at,
        now,
        snapshot.version,
    )
    return StaffDecision(snapshot, event)
