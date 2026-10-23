"""Immutable attendance values using opaque identifiers and UTC instants only."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID


class AttendanceErrorCode(StrEnum):
    """Stable domain codes; transport adapters translate these to safe messages."""

    ACCESS_DENIED = "attendance_access_denied"
    INVALID_VALUE = "attendance_invalid_value"
    VERSION_CONFLICT = "attendance_version_conflict"
    ALREADY_PRESENT = "attendance_already_present"
    NOT_PRESENT = "attendance_not_present"
    CHRONOLOGY_CONFLICT = "attendance_chronology_conflict"
    OPERATION_CONFLICT = "attendance_operation_conflict"


class AttendanceError(Exception):
    """Reject a decision without exposing identifiers or modifying any state."""

    def __init__(self, code: AttendanceErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


def utc_instant(value: datetime) -> datetime:
    """Normalize an aware instant to UTC; reject ambiguous naive timestamps."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)
    return value.astimezone(UTC)


def require_version(value: int) -> None:
    """Reject negative versions and booleans masquerading as integers."""
    if type(value) is not int or value < 0:
        raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)


class AttendanceAction(StrEnum):
    """Approved basic transitions; correction and QR policies remain separate."""

    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


class Presence(StrEnum):
    """Physical presence only; not an absence, sickness or lateness category."""

    NOT_PRESENT = "not_present"
    PRESENT = "present"


@dataclass(frozen=True)
class AttendanceTarget:
    """Bind one child to an organization, branch and classroom resolved by server."""

    organization_id: UUID
    branch_id: UUID
    classroom_id: UUID
    child_id: UUID

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, UUID)
            for value in (self.organization_id, self.branch_id, self.classroom_id, self.child_id)
        ):
            raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)


@dataclass(frozen=True)
class AttendanceCommand:
    """Retryable client intent; never contains an asserted actor identity or role."""

    operation_id: UUID
    target: AttendanceTarget
    action: AttendanceAction
    occurred_at: datetime
    expected_version: int

    def __post_init__(self) -> None:
        if not isinstance(self.operation_id, UUID) or not isinstance(self.action, AttendanceAction):
            raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)
        require_version(self.expected_version)
        object.__setattr__(self, "occurred_at", utc_instant(self.occurred_at))


@dataclass(frozen=True)
class AttendanceSnapshot:
    """Authoritatively loaded child presence; version zero has no attendance yet."""

    target: AttendanceTarget
    presence: Presence = Presence.NOT_PRESENT
    version: int = 0
    last_occurred_at: datetime | None = None

    def __post_init__(self) -> None:
        require_version(self.version)
        if not isinstance(self.presence, Presence):
            raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)
        if self.version == 0:
            if self.presence != Presence.NOT_PRESENT or self.last_occurred_at is not None:
                raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)
        elif self.last_occurred_at is None:
            raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)
        if self.last_occurred_at is not None:
            object.__setattr__(self, "last_occurred_at", utc_instant(self.last_occurred_at))


@dataclass(frozen=True)
class VerifiedAttendanceGrant:
    """Trusted adapter input, never deserialized from an HTTP request.

    Creating this value does not authenticate anyone. Before each decision the
    server must validate identity, active organization, memberships, assignments,
    child/branch state and revocation against authoritative storage. Exact child
    scope avoids embedding an unapproved role or sensitive-field policy here.
    """

    target: AttendanceTarget
    actor_id: UUID
    expires_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.actor_id, UUID):
            raise AttendanceError(AttendanceErrorCode.INVALID_VALUE)
        object.__setattr__(self, "expires_at", utc_instant(self.expires_at))


@dataclass(frozen=True)
class AttendanceEvent:
    """Append-only attendance fact; actor comes exclusively from the trusted grant."""

    event_id: UUID
    operation_id: UUID
    target: AttendanceTarget
    actor_id: UUID
    action: AttendanceAction
    occurred_at: datetime
    recorded_at: datetime
    version: int


@dataclass(frozen=True)
class AttendanceDecision:
    """Proposed immutable result; a replay must never be written over current state."""

    snapshot: AttendanceSnapshot
    event: AttendanceEvent
    replayed: bool = False


@dataclass(frozen=True)
class AttendanceReceipt:
    """Trusted durable receipt to load under organization, actor and operation ID.

    It must be saved atomically with the corresponding state/event by a future
    PostgreSQL adapter. In-memory decisions alone do not make retries durable.
    """

    command: AttendanceCommand
    actor_id: UUID
    decision: AttendanceDecision
