"""ADM-UNIT scenarios use synthetic policy edges, never a default business policy."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from nursery_api.admissions.stages import (
    AdmissionsError,
    AdmissionsErrorCode,
    ChangeLeadStage,
    LeadScope,
    LeadSnapshot,
    LeadStage,
    StagePolicy,
    StageReceipt,
    VerifiedAdmissionsGrant,
    decide_stage_change,
)

NOW = datetime(2026, 10, 24, 9, tzinfo=UTC)
SCOPE = LeadScope(UUID(int=101), UUID(int=102), UUID(int=103))
STATE = LeadSnapshot(SCOPE)
GRANT = VerifiedAdmissionsGrant(
    SCOPE.organization_id, SCOPE.branch_id, UUID(int=104), NOW + timedelta(hours=1)
)
POLICY = StagePolicy(
    SCOPE.organization_id,
    UUID(int=105),
    1,
    frozenset(
        {
            (LeadStage.INQUIRY, LeadStage.CONTACTED),
            (LeadStage.CONTACTED, LeadStage.APPLICATION),
            (LeadStage.LOST, LeadStage.CONTACTED),
            (LeadStage.ACCEPTED, LeadStage.ENROLLED),
            (LeadStage.ENROLLED, LeadStage.LOST),
        }
    ),
)
COMMAND = ChangeLeadStage(SCOPE, UUID(int=106), 0, LeadStage.CONTACTED)


def assert_code(error: pytest.ExceptionInfo[AdmissionsError], code: AdmissionsErrorCode) -> None:
    """Messages must be stable codes without lead or actor identifiers."""
    assert error.value.code == code
    assert str(error.value) == code.value


def test_adm_unit_001_valid_move_records_prior_stage_actor_time_and_policy() -> None:
    """Partial TC-FEAT-030-02; state/history persistence is not exercised."""
    result = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    assert result.snapshot.stage == LeadStage.CONTACTED
    assert result.snapshot.version == result.history.version == 1
    assert result.history.scope == SCOPE
    assert result.history.operation_id == COMMAND.operation_id
    assert result.history.previous_stage == LeadStage.INQUIRY
    assert result.history.new_stage == LeadStage.CONTACTED
    assert result.history.actor_id == GRANT.actor_id
    assert result.snapshot.last_changed_at == result.history.changed_at == NOW
    assert result.history.policy_id == POLICY.policy_id
    assert result.history.policy_revision == POLICY.revision
    assert STATE.stage == LeadStage.INQUIRY


def test_adm_unit_002_missing_policy_edge_is_denied_even_between_adjacent_stages() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND, STATE, GRANT, replace(POLICY, allowed_edges=frozenset()), changed_at=NOW
        )
    assert_code(error, AdmissionsErrorCode.INVALID_TRANSITION)


def test_adm_unit_003_policy_does_not_imply_transitive_stage_skipping() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            replace(COMMAND, new_stage=LeadStage.APPLICATION), STATE, GRANT, POLICY, changed_at=NOW
        )
    assert_code(error, AdmissionsErrorCode.INVALID_TRANSITION)


def test_adm_unit_004_reopening_requires_an_explicit_edge() -> None:
    lost = LeadSnapshot(SCOPE, LeadStage.LOST, 2, NOW)
    command = replace(COMMAND, expected_version=2)
    assert (
        decide_stage_change(command, lost, GRANT, POLICY, changed_at=NOW).snapshot.stage
        == LeadStage.CONTACTED
    )
    without_reopening = replace(
        POLICY, allowed_edges=frozenset({(LeadStage.INQUIRY, LeadStage.CONTACTED)})
    )
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(command, lost, GRANT, without_reopening, changed_at=NOW)
    assert_code(error, AdmissionsErrorCode.INVALID_TRANSITION)


@pytest.mark.parametrize("field", ["organization_id", "branch_id", "lead_id"])
def test_adm_unit_005_other_scope_is_denied_before_stale_version(field: str) -> None:
    other_scope = replace(SCOPE, **{field: UUID(int=999)})
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            replace(COMMAND, scope=other_scope, expected_version=99),
            STATE,
            GRANT,
            POLICY,
            changed_at=NOW,
        )
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


@pytest.mark.parametrize("field", ["organization_id", "branch_id"])
def test_adm_unit_006_unrelated_grant_is_denied(field: str) -> None:
    other_grant = (
        replace(GRANT, organization_id=UUID(int=999))
        if field == "organization_id"
        else replace(GRANT, branch_id=UUID(int=999))
    )
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(COMMAND, STATE, other_grant, POLICY, changed_at=NOW)
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


def test_adm_unit_007_other_organization_policy_is_denied() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND, STATE, GRANT, replace(POLICY, organization_id=UUID(int=999)), changed_at=NOW
        )
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


def test_adm_unit_008_expired_grant_is_denied_at_the_exact_boundary() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=GRANT.expires_at)
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


def test_adm_unit_009_repeated_stale_intent_does_not_return_a_fresh_history_fact() -> None:
    result = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(COMMAND, result.snapshot, GRANT, POLICY, changed_at=NOW)
    assert_code(error, AdmissionsErrorCode.VERSION_CONFLICT)
    assert result.snapshot.version == 1


def test_adm_unit_010_noop_does_not_increment_history() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            replace(COMMAND, new_stage=LeadStage.INQUIRY), STATE, GRANT, POLICY, changed_at=NOW
        )
    assert_code(error, AdmissionsErrorCode.NO_CHANGE)


@pytest.mark.parametrize(
    "before,after",
    [
        (LeadStage.ACCEPTED, LeadStage.ENROLLED),
        (LeadStage.ENROLLED, LeadStage.LOST),
    ],
)
def test_adm_unit_011_stage_edit_cannot_manufacture_or_undo_enrollment(
    before: LeadStage, after: LeadStage
) -> None:
    state = LeadSnapshot(SCOPE, before, 1, NOW)
    command = replace(COMMAND, expected_version=1, new_stage=after)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(command, state, GRANT, POLICY, changed_at=NOW)
    assert_code(error, AdmissionsErrorCode.CONVERSION_REQUIRED)


def test_adm_unit_012_offsets_are_normalized_to_one_history_instant() -> None:
    result = decide_stage_change(
        COMMAND, STATE, GRANT, POLICY, changed_at=NOW.astimezone(timezone(timedelta(hours=3)))
    )
    assert result.snapshot.last_changed_at == result.history.changed_at == NOW
    assert result.history.changed_at.tzinfo is UTC


def test_adm_unit_013_naive_time_is_rejected() -> None:
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW.replace(tzinfo=None))
    assert_code(error, AdmissionsErrorCode.INVALID_VALUE)


def test_adm_unit_014_history_cannot_go_backwards() -> None:
    state = LeadSnapshot(SCOPE, LeadStage.CONTACTED, 1, NOW)
    command = replace(COMMAND, expected_version=1, new_stage=LeadStage.APPLICATION)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(command, state, GRANT, POLICY, changed_at=NOW - timedelta(seconds=1))
    assert_code(error, AdmissionsErrorCode.CHRONOLOGY_CONFLICT)


@pytest.mark.parametrize("version", [-1, True])
def test_adm_unit_015_invalid_command_version_is_rejected(version: int) -> None:
    with pytest.raises(AdmissionsError) as error:
        replace(COMMAND, expected_version=version)
    assert_code(error, AdmissionsErrorCode.INVALID_VALUE)


def test_adm_unit_016_self_transition_policy_is_rejected() -> None:
    with pytest.raises(AdmissionsError) as error:
        replace(POLICY, allowed_edges=frozenset({(LeadStage.INQUIRY, LeadStage.INQUIRY)}))
    assert_code(error, AdmissionsErrorCode.INVALID_VALUE)


def test_adm_unit_017_history_and_state_are_immutable() -> None:
    result = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    with pytest.raises(FrozenInstanceError):
        setattr(result.history, "previous_stage", LeadStage.ACCEPTED)
    with pytest.raises(FrozenInstanceError):
        setattr(result.snapshot, "stage", LeadStage.ENROLLED)


def test_adm_unit_018_exact_retry_preserves_the_original_history_fact() -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    receipt = StageReceipt(COMMAND, GRANT.actor_id, saved)
    replay = decide_stage_change(
        COMMAND,
        saved.snapshot,
        GRANT,
        POLICY,
        changed_at=NOW + timedelta(minutes=1),
        receipt=receipt,
    )
    assert replay.replayed
    assert replay.history is saved.history
    assert replay.snapshot is saved.snapshot
    assert not saved.replayed


def test_adm_unit_019_retry_after_a_later_move_returns_history_without_rolling_state_back() -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    later = decide_stage_change(
        replace(
            COMMAND, operation_id=UUID(int=107), expected_version=1, new_stage=LeadStage.APPLICATION
        ),
        saved.snapshot,
        GRANT,
        POLICY,
        changed_at=NOW + timedelta(minutes=1),
    )
    replay = decide_stage_change(
        COMMAND,
        later.snapshot,
        GRANT,
        POLICY,
        changed_at=NOW + timedelta(minutes=2),
        receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
    )
    assert replay.replayed and replay.snapshot.version == 1
    assert later.snapshot.version == 2 and later.snapshot.stage == LeadStage.APPLICATION
    assert replay.history.event_id == saved.history.event_id


@pytest.mark.parametrize("field", ["expected_version", "new_stage", "operation_id"])
def test_adm_unit_020_receipt_cannot_be_used_with_a_changed_command(field: str) -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    changed = (
        replace(COMMAND, expected_version=1)
        if field == "expected_version"
        else replace(COMMAND, new_stage=LeadStage.APPLICATION)
        if field == "new_stage"
        else replace(COMMAND, operation_id=UUID(int=999))
    )
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            changed,
            saved.snapshot,
            GRANT,
            POLICY,
            changed_at=NOW,
            receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.OPERATION_CONFLICT)


def test_adm_unit_021_another_actor_cannot_replay_a_stored_response() -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND,
            saved.snapshot,
            replace(GRANT, actor_id=UUID(int=999)),
            POLICY,
            changed_at=NOW,
            receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


def test_adm_unit_022_retry_rechecks_expiry_before_receipt_conflicts() -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            replace(COMMAND, expected_version=99),
            saved.snapshot,
            GRANT,
            POLICY,
            changed_at=GRANT.expires_at,
            receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


@pytest.mark.parametrize("field", ["organization_id", "branch_id", "lead_id"])
def test_adm_unit_023_cross_scope_receipts_fail_before_payload_conflicts(field: str) -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    other_command = replace(COMMAND, scope=replace(SCOPE, **{field: UUID(int=999)}))
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND,
            saved.snapshot,
            GRANT,
            POLICY,
            changed_at=NOW,
            receipt=StageReceipt(other_command, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.ACCESS_DENIED)


@pytest.mark.parametrize("part", ["actor", "operation", "stage", "time", "snapshot", "replayed"])
def test_adm_unit_024_inconsistent_receipt_parts_cannot_manufacture_a_success(part: str) -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    history = saved.history
    if part == "actor":
        saved = replace(saved, history=replace(history, actor_id=UUID(int=999)))
    elif part == "operation":
        saved = replace(saved, history=replace(history, operation_id=UUID(int=999)))
    elif part == "stage":
        saved = replace(saved, history=replace(history, new_stage=LeadStage.APPLICATION))
    elif part == "time":
        saved = replace(saved, history=replace(history, changed_at=NOW + timedelta(minutes=1)))
    elif part == "snapshot":
        saved = replace(saved, snapshot=replace(saved.snapshot, stage=LeadStage.APPLICATION))
    else:
        saved = replace(saved, replayed=True)
    current = LeadSnapshot(SCOPE, LeadStage.CONTACTED, 1, NOW)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND,
            current,
            GRANT,
            POLICY,
            changed_at=NOW,
            receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.OPERATION_CONFLICT)


def test_adm_unit_025_receipt_cannot_replay_against_state_older_than_its_result() -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND,
            STATE,
            GRANT,
            POLICY,
            changed_at=NOW,
            receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.OPERATION_CONFLICT)


def test_adm_unit_026_retry_does_not_reapply_new_policy_edges_to_historical_success() -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    new_policy = replace(POLICY, revision=2, allowed_edges=frozenset())
    replay = decide_stage_change(
        COMMAND,
        saved.snapshot,
        GRANT,
        new_policy,
        changed_at=NOW,
        receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
    )
    assert replay.replayed and replay.history.policy_revision == 1


@pytest.mark.parametrize("field", ["version", "policy_revision"])
def test_adm_unit_027_history_rejects_boolean_versions(field: str) -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    with pytest.raises(AdmissionsError) as error:
        if field == "version":
            replace(saved.history, version=True)
        else:
            replace(saved.history, policy_revision=True)
    assert_code(error, AdmissionsErrorCode.INVALID_VALUE)


@pytest.mark.parametrize("later_version", [1, 2])
def test_adm_unit_028_contradictory_current_state_cannot_be_hidden_by_a_receipt(
    later_version: int,
) -> None:
    saved = decide_stage_change(COMMAND, STATE, GRANT, POLICY, changed_at=NOW)
    current = LeadSnapshot(
        SCOPE,
        LeadStage.APPLICATION,
        later_version,
        NOW if later_version == 1 else NOW - timedelta(minutes=1),
    )
    with pytest.raises(AdmissionsError) as error:
        decide_stage_change(
            COMMAND,
            current,
            GRANT,
            POLICY,
            changed_at=NOW,
            receipt=StageReceipt(COMMAND, GRANT.actor_id, saved),
        )
    assert_code(error, AdmissionsErrorCode.OPERATION_CONFLICT)
