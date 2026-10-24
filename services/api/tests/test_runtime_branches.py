"""Original branch source cases against real PostgreSQL and restricted runtime role."""

from typing import Any
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.errors import InsufficientPrivilege

from conftest import Workspace
from nursery_api.runtime.bootstrap import identifier
from nursery_api.runtime.database import set_context

BRANCH = str(identifier("gardenmaadi"))
OTHER_BRANCH = str(identifier("gardencairo"))


def create(workspace: Workspace, operation: str | None = None, **fields: Any) -> Any:
    return workspace.client.post(
        "/api/v1/branches",
        json={"name": "Fictional Riverside", **fields},
        headers={"Idempotency-Key": operation or str(uuid4())},
    )


def test_branch_api_001_create_metadata_assignment_and_audit(workspace: Workspace) -> None:
    """TC-FEAT-002-01 at its actual API integration level."""
    workspace.login()
    response = create(
        workspace,
        capacity=80,
        contact_email="office@example.test",
        contact_phone="fictional contact",
        address="Fictional site",
        timezone="Africa/Cairo",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 1 and data["capacity"] == 80 and data["active"]
    assigned = workspace.client.post(
        f"/api/v1/branches/{data['id']}/members",
        json={
            "user_id": str(identifier("branch_manager@garden.example.test")),
            "assigned": True,
            "expected_version": 1,
        },
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert assigned.status_code == 200 and assigned.json()["version"] == 2
    workspace.login("branch_manager")
    assert workspace.client.get(f"/api/v1/branches/{data['id']}").status_code == 200
    with psycopg.connect(workspace.owner_url) as connection:
        assert connection.execute(
            "SELECT count(*) FROM app.audit WHERE resource_id=%s", (data["id"],)
        ).fetchone() == (2,)


def test_branch_api_002_manager_scope_and_combined_results(workspace: Workspace) -> None:
    """TC-FEAT-002-02: neither direct nor combined reads reveal another branch."""
    workspace.login("branch_manager")
    items = workspace.client.get("/api/v1/branches").json()["items"]
    assert [str(row["id"]) for row in items] == [BRANCH]
    assert workspace.client.get(f"/api/v1/branches/{OTHER_BRANCH}").status_code == 404
    assert (
        workspace.client.get(f"/api/v1/branches/{identifier('neighbormaadi')}").status_code == 404
    )
    assert workspace.client.get("/api/v1/branches/members").status_code == 403
    assert workspace.client.get(f"/api/v1/branches/{BRANCH}/members").status_code == 403
    assert create(workspace).status_code == 403


def test_branch_api_003_inactive_blocks_writes_but_retains_authorized_history(
    workspace: Workspace,
) -> None:
    """TC-FEAT-002-03: deactivation is not deletion of operational history."""
    workspace.login("teacher")
    employee = str(identifier("teacher@garden.example.test:employee"))
    body = {
        "employee_id": employee,
        "branch_id": BRANCH,
        "action": "check_in",
        "expected_version": 0,
    }
    first = workspace.client.post(
        "/api/v1/staff-attendance/transitions", json=body, headers={"Idempotency-Key": str(uuid4())}
    )
    assert first.status_code == 200
    workspace.login()
    response = workspace.client.post(
        f"/api/v1/branches/{BRANCH}",
        json={"name": "Maadi", "active": False, "expected_version": 1},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 200
    workspace.login("teacher")
    assert any(
        row["id"] == BRANCH and not row["active"]
        for row in workspace.client.get("/api/v1/auth/me").json()["branches"]
    )
    assert (
        workspace.client.get(
            f"/api/v1/staff-attendance/history?branch_id={BRANCH}&employee_id={employee}"
        ).json()["events"][0]["id"]
        == first.json()["event_id"]
    )
    body.update(action="check_out", expected_version=1)
    assert (
        workspace.client.post(
            "/api/v1/staff-attendance/transitions",
            json=body,
            headers={"Idempotency-Key": str(uuid4())},
        ).status_code
        == 404
    )


def test_branch_api_004_create_and_edit_retries_conflicts_and_revoked_authority(
    workspace: Workspace,
) -> None:
    workspace.login()
    operation = str(uuid4())
    first = create(workspace, operation).json()
    retry = create(workspace, operation)
    assert (
        retry.status_code == 200 and retry.json()["replayed"] and retry.json()["id"] == first["id"]
    )
    assert create(workspace, operation, name="Changed payload").status_code == 409
    edit_operation = str(uuid4())
    body = {"name": "Updated branch", "expected_version": 1}
    edit = workspace.client.post(
        f"/api/v1/branches/{first['id']}", json=body, headers={"Idempotency-Key": edit_operation}
    )
    assert edit.status_code == 200 and edit.json()["version"] == 2
    assert workspace.client.post(
        f"/api/v1/branches/{first['id']}", json=body, headers={"Idempotency-Key": edit_operation}
    ).json()["replayed"]
    assert (
        workspace.client.post(
            f"/api/v1/branches/{first['id']}", json=body, headers={"Idempotency-Key": str(uuid4())}
        ).status_code
        == 409
    )
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            "UPDATE app.memberships SET role='teacher' WHERE user_id=%s",
            (identifier("administrator@garden.example.test"),),
        )
    assert create(workspace, operation).status_code == 403


def test_branch_api_005_assignment_removal_applies_to_existing_session(
    workspace: Workspace,
) -> None:
    manager = TestClient(workspace.client.app, headers={"origin": "http://localhost:3000"})
    email = "branch_manager@garden.example.test"
    assert (
        manager.post(
            "/api/v1/auth/login", json={"email": email, "password": workspace.accounts[email]}
        ).status_code
        == 200
    )
    workspace.login()
    user = str(identifier(email))
    operation = str(uuid4())
    body = {"user_id": user, "assigned": False, "expected_version": 1}
    response = workspace.client.post(
        f"/api/v1/branches/{BRANCH}/members", json=body, headers={"Idempotency-Key": operation}
    )
    assert response.status_code == 200
    assert workspace.client.post(
        f"/api/v1/branches/{BRANCH}/members", json=body, headers={"Idempotency-Key": operation}
    ).json()["replayed"]
    assert manager.get(f"/api/v1/branches/{BRANCH}").status_code == 404
    assert manager.get("/api/v1/auth/me").json()["branches"] == []
    manager.close()


@pytest.mark.parametrize(
    "fields",
    [
        {"name": " "},
        {"timezone": "fictional/unknown"},
        {"capacity": 0},
        {"capacity": True},
        {"contact_email": "broken"},
        {"organization_id": str(uuid4())},
    ],
)
def test_branch_api_006_invalid_and_injected_fields_are_rejected(
    workspace: Workspace, fields: dict[str, Any]
) -> None:
    workspace.login()
    assert create(workspace, **fields).status_code == 422


def test_branch_api_007_foreign_member_and_tenant_are_not_writable(workspace: Workspace) -> None:
    workspace.login()
    response = workspace.client.post(
        f"/api/v1/branches/{BRANCH}/members",
        json={
            "user_id": str(identifier("teacher@neighbor.example.test")),
            "assigned": True,
            "expected_version": 1,
        },
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 404
    assert (
        workspace.client.post(
            f"/api/v1/branches/{identifier('neighbormaadi')}",
            json={"name": "Intrusion", "expected_version": 1},
            headers={"Idempotency-Key": str(uuid4())},
        ).status_code
        == 404
    )
    with pytest.raises(InsufficientPrivilege), workspace.database.transaction() as connection:
        set_context(
            connection, identifier("teacher@garden.example.test"), identifier("garden"), "teacher"
        )
        connection.execute(
            "INSERT INTO app.branches(organization_id,id,name) VALUES(%s,%s,'Denied')",
            (identifier("garden"), uuid4()),
        )


def test_branch_api_008_cursor_boundaries_are_deterministic(workspace: Workspace) -> None:
    workspace.login()
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            "INSERT INTO app.branches(organization_id,id,name) SELECT %s,gen_random_uuid(),'Fictional site '||n FROM generate_series(1,105)n",
            (identifier("garden"),),
        )
    first = workspace.client.get("/api/v1/branches").json()
    assert len(first["items"]) == 100 and first["next_cursor"]
    second = workspace.client.get("/api/v1/branches?cursor=" + first["next_cursor"]).json()
    assert len(second["items"]) == 7 and second["next_cursor"] is None
    assert not ({row["id"] for row in first["items"]} & {row["id"] for row in second["items"]})


def test_branch_api_009_daily_report_uses_branch_timezone_and_dst_boundary(
    workspace: Workspace,
) -> None:
    workspace.login()
    response = workspace.client.post(
        f"/api/v1/branches/{BRANCH}",
        json={"name": "Maadi", "timezone": "America/New_York", "expected_version": 1},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 200
    report = workspace.client.get(
        f"/api/v1/staff-attendance/daily?branch_id={BRANCH}&day=2026-11-01"
    )
    assert report.status_code == 200
    from datetime import datetime

    data = report.json()
    assert data["timezone"] == "America/New_York"
    assert (
        datetime.fromisoformat(data["end"]) - datetime.fromisoformat(data["start"])
    ).total_seconds() == 25 * 3600


def test_branch_api_010_runtime_teacher_cannot_change_branch_or_own_grants(
    workspace: Workspace,
) -> None:
    with workspace.database.transaction() as connection:
        set_context(
            connection, identifier("teacher@garden.example.test"), identifier("garden"), "teacher"
        )
        assert (
            connection.execute(
                "UPDATE app.branches SET name='Denied' WHERE id=%s", (BRANCH,)
            ).rowcount
            == 0
        )
        assert (
            connection.execute(
                "DELETE FROM app.branch_memberships WHERE user_id=%s",
                (identifier("teacher@garden.example.test"),),
            ).rowcount
            == 0
        )
