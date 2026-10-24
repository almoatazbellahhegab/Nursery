"""Real API/PostgreSQL source cases and staff concurrency/audit denial regressions."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.errors import InsufficientPrivilege

from conftest import Workspace
from nursery_api.runtime.bootstrap import identifier
from nursery_api.runtime.database import set_context

BRANCH = str(identifier("gardenmaadi"))
EMPLOYEE = str(identifier("teacher@garden.example.test:employee"))


def checkin(workspace: Workspace, *, version: int = 0, operation: str | None = None) -> Any:
    return workspace.client.post(
        "/api/v1/staff-attendance/transitions",
        json={
            "employee_id": EMPLOYEE,
            "branch_id": BRANCH,
            "action": "check_in",
            "expected_version": version,
        },
        headers={"Idempotency-Key": operation or str(uuid4())},
    )


def test_staff_api_001_active_employee_checkin_is_persisted_and_audited(
    workspace: Workspace,
) -> None:
    """TC-FEAT-012-01 at actual API/PostgreSQL integration level."""
    workspace.login("teacher")
    response = checkin(workspace)
    assert response.status_code == 200
    data = response.json()
    assert data["present"] and data["version"] == 1
    with psycopg.connect(workspace.owner_url) as connection:
        assert connection.execute(
            "SELECT count(*) FROM app.staff_presence WHERE open_session_id IS NOT NULL"
        ).fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM app.staff_events").fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM app.staff_receipts").fetchone() == (1,)
        assert connection.execute(
            "SELECT count(*) FROM app.audit WHERE action='staff.check_in'"
        ).fetchone() == (1,)


def test_staff_api_002_duplicate_and_exact_retry_do_not_create_another_open_record(
    workspace: Workspace,
) -> None:
    """TC-FEAT-012-02, including durable duplicate replay."""
    workspace.login("teacher")
    operation = str(uuid4())
    first = checkin(workspace, operation=operation)
    assert first.status_code == 200
    replay = checkin(workspace, operation=operation)
    assert replay.status_code == 200 and replay.json()["replayed"]
    assert replay.json()["event_id"] == first.json()["event_id"]
    assert checkin(workspace, version=1).status_code == 409
    with psycopg.connect(workspace.owner_url) as connection:
        assert connection.execute("SELECT count(*) FROM app.staff_events").fetchone() == (1,)


def test_staff_api_003_manager_correction_preserves_original_new_actor_time_and_reason(
    workspace: Workspace,
) -> None:
    """TC-FEAT-012-03 through the real manager API and append-only tables."""
    workspace.login("teacher")
    first = checkin(workspace).json()
    workspace.login("branch_manager")
    original = datetime.fromisoformat(first["occurred_at"])
    response = workspace.client.post(
        "/api/v1/staff-attendance/corrections",
        json={
            "employee_id": EMPLOYEE,
            "branch_id": BRANCH,
            "event_id": first["event_id"],
            "expected_version": 1,
            "corrected_at": (original - timedelta(minutes=5)).isoformat(),
            "reason": "Verified time entry correction",
        },
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 200
    correction = response.json()
    assert correction["original_at"] == first["occurred_at"]
    assert correction["reason"] == "Verified time entry correction"
    with psycopg.connect(workspace.owner_url) as connection:
        event = connection.execute("SELECT occurred_at FROM app.staff_events").fetchone()
        assert event == (original,)
        saved = connection.execute("SELECT actor_id,reason FROM app.staff_corrections").fetchone()
        assert saved == (
            identifier("branch_manager@garden.example.test"),
            "Verified time entry correction",
        )
        assert connection.execute(
            "SELECT count(*) FROM app.audit WHERE action='staff.correct'"
        ).fetchone() == (1,)


@pytest.mark.parametrize("role", ["parent", "finance"])
def test_staff_api_004_unapproved_roles_cannot_list_or_write(
    workspace: Workspace, role: str
) -> None:
    workspace.login(role)
    assert (
        workspace.client.get(
            "/api/v1/staff-attendance/employees", params={"branch_id": BRANCH}
        ).status_code
        == 403
    )
    assert checkin(workspace).status_code == 403


def test_staff_api_005_teacher_cannot_access_peer_or_foreign_tenant(workspace: Workspace) -> None:
    workspace.login("teacher")
    data = workspace.client.get(
        "/api/v1/staff-attendance/employees", params={"branch_id": BRANCH}
    ).json()
    assert [row["id"] for row in data["items"]] == [EMPLOYEE]
    peer = str(identifier("administrator@garden.example.test:employee"))
    response = workspace.client.get(
        "/api/v1/staff-attendance/history", params={"branch_id": BRANCH, "employee_id": peer}
    )
    assert response.status_code == 404
    response = workspace.client.get(
        "/api/v1/staff-attendance/employees", params={"branch_id": str(identifier("neighbormaadi"))}
    )
    assert response.status_code == 404


def test_staff_api_006_assignment_removal_prevents_replay(workspace: Workspace) -> None:
    workspace.login("teacher")
    operation = str(uuid4())
    assert checkin(workspace, operation=operation).status_code == 200
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            "DELETE FROM app.employee_assignments WHERE employee_id=%s",
            (identifier("teacher@garden.example.test:employee"),),
        )
    assert checkin(workspace, operation=operation).status_code == 404


def test_staff_api_007_database_history_cannot_be_updated_or_deleted_by_runtime(
    workspace: Workspace,
) -> None:
    workspace.login("teacher")
    assert checkin(workspace).status_code == 200
    with pytest.raises(InsufficientPrivilege):
        with workspace.database.transaction() as connection:
            set_context(
                connection,
                identifier("teacher@garden.example.test"),
                identifier("garden"),
                "teacher",
            )
            connection.execute("UPDATE app.staff_events SET occurred_at=now()")


def test_staff_api_008_employee_lock_serializes_racing_checkins(workspace: Workspace) -> None:
    workspace.login("teacher")
    # Separate HTTP requests share the employee key; a stale precondition must
    # not create another session when both start at version zero.
    with TestClient(workspace.client.app) as client:
        client.headers["origin"] = "http://localhost:3000"
        other = Workspace(client, workspace.database, workspace.owner_url, workspace.accounts)
        other.login("administrator")
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(checkin, workspace)
            second = pool.submit(checkin, other)
            responses = [first.result(), second.result()]
    assert sorted(response.status_code for response in responses) == [200, 409]
    with psycopg.connect(workspace.owner_url) as connection:
        assert connection.execute("SELECT count(*) FROM app.staff_events").fetchone() == (1,)


def test_staff_api_009_changed_operation_payload_is_rejected(workspace: Workspace) -> None:
    workspace.login("teacher")
    operation = str(uuid4())
    assert checkin(workspace, operation=operation).status_code == 200
    assert checkin(workspace, version=1, operation=operation).status_code == 409


def test_staff_api_010_daily_report_uses_branch_timezone(workspace: Workspace) -> None:
    workspace.login("teacher")
    assert checkin(workspace).status_code == 200
    day = datetime.now(UTC).astimezone(ZoneInfo("Africa/Cairo")).date()
    response = workspace.client.get(
        "/api/v1/staff-attendance/daily", params={"branch_id": BRANCH, "day": day.isoformat()}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["timezone"] == "Africa/Cairo"
    assert len(data["items"]) == 1 and data["items"][0]["present"]


def test_staff_api_011_inactive_employee_is_denied_without_persisting_event(
    workspace: Workspace,
) -> None:
    workspace.login("teacher")
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            "UPDATE app.employees SET active=false WHERE id=%s",
            (identifier("teacher@garden.example.test:employee"),),
        )
    assert checkin(workspace).status_code == 409
    with psycopg.connect(workspace.owner_url) as connection:
        assert connection.execute("SELECT count(*) FROM app.staff_events").fetchone() == (0,)


def test_staff_api_012_cross_tenant_insert_is_rejected_by_postgresql_rls(
    workspace: Workspace,
) -> None:
    with pytest.raises(InsufficientPrivilege):
        with workspace.database.transaction() as connection:
            set_context(
                connection,
                identifier("administrator@garden.example.test"),
                identifier("garden"),
                "administrator",
            )
            connection.execute(
                "INSERT INTO app.staff_presence(organization_id,employee_id) VALUES(%s,%s)",
                (identifier("neighbor"), identifier("teacher@neighbor.example.test:employee")),
            )


def test_staff_api_013_failed_audit_rolls_back_state_event_and_receipt(
    workspace: Workspace,
) -> None:
    workspace.login("teacher")
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute("""CREATE FUNCTION app.test_reject_audit() RETURNS trigger LANGUAGE plpgsql AS
            $$ BEGIN RAISE EXCEPTION 'simulated audit failure'; END $$;
            CREATE TRIGGER test_reject_audit BEFORE INSERT ON app.audit
            FOR EACH ROW EXECUTE FUNCTION app.test_reject_audit();""")
    try:
        with pytest.raises(psycopg.errors.RaiseException):
            checkin(workspace)
    finally:
        with psycopg.connect(workspace.owner_url) as connection:
            connection.execute(
                "DROP TRIGGER test_reject_audit ON app.audit; DROP FUNCTION app.test_reject_audit()"
            )
    with psycopg.connect(workspace.owner_url) as connection:
        for table in ("staff_presence", "staff_events", "staff_receipts", "audit"):
            assert connection.execute(f"SELECT count(*) FROM app.{table}").fetchone() == (0,)


def test_staff_api_015_truncated_branch_history_retains_newest_event(workspace: Workspace) -> None:
    workspace.login("teacher")
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            """INSERT INTO app.staff_events
            SELECT %s,gen_random_uuid(),%s,%s,%s,gen_random_uuid(),gen_random_uuid(),
                'check_in',now() - (1002-n)*interval '1 minute',now(),n
            FROM generate_series(1,1001)n""",
            (
                identifier("garden"),
                identifier("teacher@garden.example.test:employee"),
                identifier("gardenmaadi"),
                identifier("teacher@garden.example.test"),
            ),
        )
    response = workspace.client.get(
        f"/api/v1/staff-attendance/history?branch_id={BRANCH}&employee_id={EMPLOYEE}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["truncated"] and len(data["events"]) == 1000
    assert data["events"][0]["version"] == 2
    assert data["events"][-1]["version"] == 1001
