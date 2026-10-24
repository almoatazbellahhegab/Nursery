"""Immutable lead-stage decisions; policy edges are explicit, never inferred."""

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class AdmissionsErrorCode(StrEnum):
    """Safe stable codes; transport/message localization is a future adapter."""

    ACCESS_DENIED = "admissions_access_denied"
    INVALID_VALUE = "admissions_invalid_value"
    VERSION_CONFLICT = "admissions_version_conflict"
    NO_CHANGE = "admissions_no_stage_change"
    INVALID_TRANSITION = "admissions_transition_not_allowed"
    CONVERSION_REQUIRED = "admissions_enrollment_conversion_required"
    CHRONOLOGY_CONFLICT = "admissions_chronology_conflict"
    OPERATION_CONFLICT = "admissions_operation_conflict"


class AdmissionsError(Exception):
    """Reject without exposing the lead, branch, actor or workflow contents."""

    def __init__(self, code: AdmissionsErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
    return value.astimezone(UTC)


def _version(value: int, *, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)


class LeadStage(StrEnum):
    """The nine source product stages; enumeration order grants no transition."""

    INQUIRY = "inquiry"
    CONTACTED = "contacted"
    VISIT_SCHEDULED = "visit_scheduled"
    TRIAL_DAY = "trial_day"
    APPLICATION = "application"
    ACCEPTED = "accepted"
    WAITLISTED = "waitlisted"
    ENROLLED = "enrolled"
    LOST = "lost"


@dataclass(frozen=True)
class LeadScope:
    """Opaque resource context; intentionally contains no family/child PII."""

    organization_id: UUID
    branch_id: UUID
    lead_id: UUID

    def __post_init__(self) -> None:
        if not all(
            isinstance(v, UUID) for v in (self.organization_id, self.branch_id, self.lead_id)
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)


@dataclass(frozen=True)
class LeadSnapshot:
    """Authoritatively loaded lead state; this is not a persisted inquiry model."""

    scope: LeadScope
    stage: LeadStage = LeadStage.INQUIRY
    version: int = 0
    last_changed_at: datetime | None = None

    def __post_init__(self) -> None:
        _version(self.version)
        if not isinstance(self.stage, LeadStage):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        if self.version == 0:
            if self.stage != LeadStage.INQUIRY or self.last_changed_at is not None:
                raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        elif self.last_changed_at is None:
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        if self.last_changed_at is not None:
            object.__setattr__(self, "last_changed_at", _utc(self.last_changed_at))


@dataclass(frozen=True)
class VerifiedAdmissionsGrant:
    """Trusted internal input, never built from request-body role or actor claims.

    The future server adapter must validate active organization, branch membership,
    action permission and revocation on each request. This value is not evidence
    that authentication or the policy provider has been implemented.
    """

    organization_id: UUID
    branch_id: UUID
    actor_id: UUID
    expires_at: datetime

    def __post_init__(self) -> None:
        if not all(
            isinstance(v, UUID) for v in (self.organization_id, self.branch_id, self.actor_id)
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        object.__setattr__(self, "expires_at", _utc(self.expires_at))


@dataclass(frozen=True)
class StagePolicy:
    """Versioned explicit edges loaded from trusted, approved configuration.

    No default matrix is provided. A policy UUID is a reference, not proof of
    approval; a future configuration adapter must enforce approval ownership.
    Extra required-field/loss-reason conditions must pass before this decision.
    """

    organization_id: UUID
    policy_id: UUID
    revision: int
    allowed_edges: frozenset[tuple[LeadStage, LeadStage]]

    def __post_init__(self) -> None:
        _version(self.revision, minimum=1)
        if not isinstance(self.organization_id, UUID) or not isinstance(self.policy_id, UUID):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        edges = frozenset(self.allowed_edges)
        if any(
            not isinstance(before, LeadStage) or not isinstance(after, LeadStage) or before == after
            for before, after in edges
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        object.__setattr__(self, "allowed_edges", edges)


@dataclass(frozen=True)
class ChangeLeadStage:
    """Stage intent, including operation ID/version but no asserted actor identity."""

    scope: LeadScope
    operation_id: UUID
    expected_version: int
    new_stage: LeadStage

    def __post_init__(self) -> None:
        _version(self.expected_version)
        if not isinstance(self.operation_id, UUID) or not isinstance(self.new_stage, LeadStage):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)


@dataclass(frozen=True)
class StageHistory:
    """Append-only fact carrying prior/new stage, trusted actor, time and policy."""

    event_id: UUID
    operation_id: UUID
    scope: LeadScope
    previous_stage: LeadStage
    new_stage: LeadStage
    actor_id: UUID
    changed_at: datetime
    version: int
    policy_id: UUID
    policy_revision: int

    def __post_init__(self) -> None:
        _version(self.version, minimum=1)
        _version(self.policy_revision, minimum=1)
        if (
            not isinstance(self.scope, LeadScope)
            or not all(
                isinstance(value, UUID)
                for value in (self.event_id, self.operation_id, self.actor_id, self.policy_id)
            )
            or not isinstance(self.previous_stage, LeadStage)
            or not isinstance(self.new_stage, LeadStage)
            or self.previous_stage == self.new_stage
        ):
            raise AdmissionsError(AdmissionsErrorCode.INVALID_VALUE)
        object.__setattr__(self, "changed_at", _utc(self.changed_at))


@dataclass(frozen=True)
class StageDecision:
    """Proposed state and its history fact; neither is persisted by this package."""

    snapshot: LeadSnapshot
    history: StageHistory
    replayed: bool = False


@dataclass(frozen=True)
class StageReceipt:
    """Trusted stored response, scoped by organization, branch, actor and operation.

    A future adapter must load and commit this atomically with state/history/audit.
    Constructing an in-memory receipt does not establish durable idempotency.
    """

    command: ChangeLeadStage
    actor_id: UUID
    decision: StageDecision


def decide_stage_change(
    command: ChangeLeadStage,
    current: LeadSnapshot,
    grant: VerifiedAdmissionsGrant,
    policy: StagePolicy,
    *,
    changed_at: datetime,
    receipt: StageReceipt | None = None,
) -> StageDecision:
    """Return a valid stage/history pair or raise a safe AdmissionsError.

    Scope/expiry checks precede state/policy details. Only exact configured edges
    are allowed, including any skipping/reopening; no transitions are inferred.
    ENROLLED requires the future atomic onboarding conversion workflow, so this
    stage-edit entry point cannot move into or out of enrollment. The caller
    must lock/compare versions and persist state, history, receipt and audit in
    one tenant-scoped transaction. Operation IDs here do not provide durable
    deduplication. A trusted receipt permits an exact historical retry response,
    marked replayed; never write that response over the current state. Current
    scope/authorization/expiry are checked even on retries. No side effects,
    database reads or sensitive logging occur.
    """
    now = _utc(changed_at)
    if (
        current.scope != command.scope
        or grant.organization_id != command.scope.organization_id
        or grant.branch_id != command.scope.branch_id
        or policy.organization_id != command.scope.organization_id
        or now >= grant.expires_at
    ):
        raise AdmissionsError(AdmissionsErrorCode.ACCESS_DENIED)
    if receipt is not None:
        return _replay_stage_change(command, current, grant, receipt)
    if command.expected_version != current.version:
        raise AdmissionsError(AdmissionsErrorCode.VERSION_CONFLICT)
    if command.new_stage == current.stage:
        raise AdmissionsError(AdmissionsErrorCode.NO_CHANGE)
    # A UI stage edit must never manufacture or undo a real enrollment.
    if LeadStage.ENROLLED in (current.stage, command.new_stage):
        raise AdmissionsError(AdmissionsErrorCode.CONVERSION_REQUIRED)
    if (current.stage, command.new_stage) not in policy.allowed_edges:
        raise AdmissionsError(AdmissionsErrorCode.INVALID_TRANSITION)
    if current.last_changed_at is not None and now < current.last_changed_at:
        raise AdmissionsError(AdmissionsErrorCode.CHRONOLOGY_CONFLICT)

    next_state = LeadSnapshot(
        scope=current.scope,
        stage=command.new_stage,
        version=current.version + 1,
        last_changed_at=now,
    )
    history = StageHistory(
        event_id=uuid4(),
        operation_id=command.operation_id,
        scope=current.scope,
        previous_stage=current.stage,
        new_stage=command.new_stage,
        actor_id=grant.actor_id,
        changed_at=now,
        version=next_state.version,
        policy_id=policy.policy_id,
        policy_revision=policy.revision,
    )
    return StageDecision(snapshot=next_state, history=history)


def _replay_stage_change(
    command: ChangeLeadStage,
    current: LeadSnapshot,
    grant: VerifiedAdmissionsGrant,
    receipt: StageReceipt,
) -> StageDecision:
    """Return one original fact only after checking receipt identity and integrity."""
    if receipt.actor_id != grant.actor_id or receipt.command.scope != command.scope:
        raise AdmissionsError(AdmissionsErrorCode.ACCESS_DENIED)
    if receipt.command != command:
        raise AdmissionsError(AdmissionsErrorCode.OPERATION_CONFLICT)

    saved = receipt.decision
    history = saved.history
    snapshot = saved.snapshot
    # Fail closed on inconsistent stored parts rather than inventing a new success.
    if (
        saved.replayed
        or history.scope != command.scope
        or snapshot.scope != command.scope
        or history.actor_id != grant.actor_id
        or history.operation_id != command.operation_id
        or history.new_stage != command.new_stage
        or history.previous_stage == history.new_stage
        or LeadStage.ENROLLED in (history.previous_stage, history.new_stage)
        or history.version != command.expected_version + 1
        or snapshot.version != history.version
        or snapshot.stage != history.new_stage
        or snapshot.last_changed_at != history.changed_at
        or current.version < snapshot.version
        or (current.version == snapshot.version and current != snapshot)
        or current.last_changed_at is None
        or current.last_changed_at < history.changed_at
    ):
        raise AdmissionsError(AdmissionsErrorCode.OPERATION_CONFLICT)
    return replace(saved, replayed=True)
