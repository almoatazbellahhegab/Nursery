"""Real PostgreSQL identity and tenant isolation integration tests."""

import psycopg
import pytest
from conftest import Workspace
from nursery_api.runtime.bootstrap import identifier
from nursery_api.runtime.database import set_context


def test_identity_001_password_session_and_database_role(workspace: Workspace) -> None:
    if "postgresql" in repr(workspace.database):
        pytest.fail("Database representation must redact connection credentials")
    data = workspace.login()
    assert data["role"] == "administrator"
    assert len(data["branches"]) == 2
    assert workspace.client.get("/api/v1/auth/me").status_code == 200
    with workspace.database.transaction() as connection:
        assert connection.execute("SHOW timezone").fetchone() == {"TimeZone": "UTC"}
        role = connection.execute(
            "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        assert role == {"rolsuper": False, "rolbypassrls": False}
        assert connection.execute("SELECT count(*) AS n FROM app.employees").fetchone() == {"n": 0}


def test_identity_002_rls_isolates_tenants_and_missing_context(workspace: Workspace) -> None:
    with workspace.database.transaction() as connection:
        set_context(
            connection,
            identifier("administrator@garden.example.test"),
            identifier("garden"),
            "administrator",
        )
        rows = connection.execute("SELECT organization_id FROM app.employees").fetchall()
        assert len(rows) == 3
        assert {row["organization_id"] for row in rows} == {identifier("garden")}
        assert (
            connection.execute(
                "SELECT id FROM app.organizations WHERE id=%s", (identifier("neighbor"),)
            ).fetchone()
            is None
        )
    with workspace.database.transaction() as connection:
        assert connection.execute("SELECT id FROM app.branches").fetchall() == []


def test_identity_003_branch_manager_only_receives_assigned_branch(workspace: Workspace) -> None:
    data = workspace.login("branch_manager")
    assert [branch["id"] for branch in data["branches"]] == [str(identifier("gardenmaadi"))]


@pytest.mark.parametrize("case", ["unknown", "wrong_password", "inactive"])
def test_identity_004_credentials_fail_without_existence_details(
    workspace: Workspace, case: str
) -> None:
    if case == "inactive":
        with psycopg.connect(workspace.owner_url) as connection:
            connection.execute(
                "UPDATE app.users SET active=false WHERE email='administrator@garden.example.test'"
            )
    email = "missing@example.test" if case == "unknown" else "administrator@garden.example.test"
    response = workspace.client.post(
        "/api/v1/auth/login", json={"email": email, "password": "wrong-password-value"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_identity_005_browser_origin_and_csrf_are_enforced(workspace: Workspace) -> None:
    workspace.login()
    response = workspace.client.post(
        "/api/v1/auth/logout", headers={"origin": "https://untrusted.example.test"}
    )
    assert response.status_code == 403
    del workspace.client.headers["x-csrf-token"]
    assert workspace.client.post("/api/v1/auth/logout").status_code == 403
    assert workspace.client.get("/api/v1/auth/me").status_code == 200


def test_identity_006_logout_revokes_the_server_session(workspace: Workspace) -> None:
    workspace.login()
    assert workspace.client.post("/api/v1/auth/logout").status_code == 204
    assert workspace.client.get("/api/v1/auth/me").status_code == 401


def test_identity_007_membership_revocation_is_immediate(workspace: Workspace) -> None:
    workspace.login()
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            "UPDATE app.memberships SET active=false WHERE user_id=%s",
            (identifier("administrator@garden.example.test"),),
        )
    assert workspace.client.get("/api/v1/auth/me").status_code == 401


def test_identity_008_roles_are_reloaded_and_body_claims_are_rejected(workspace: Workspace) -> None:
    workspace.login()
    with psycopg.connect(workspace.owner_url) as connection:
        connection.execute(
            "UPDATE app.memberships SET role='teacher' WHERE user_id=%s",
            (identifier("administrator@garden.example.test"),),
        )
    assert workspace.client.get("/api/v1/auth/me").json()["role"] == "teacher"
    response = workspace.client.post(
        "/api/v1/auth/login",
        json={
            "email": "a@example.test",
            "password": "sensitive-not-to-echo",
            "role": "administrator",
        },
    )
    assert response.status_code == 422
    assert "sensitive-not-to-echo" not in response.text


def test_identity_009_unknown_tenant_selection_is_denied(workspace: Workspace) -> None:
    email = "administrator@garden.example.test"
    response = workspace.client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": workspace.accounts[email],
            "organization_id": str(identifier("neighbor")),
        },
    )
    assert response.status_code == 401


def test_identity_010_native_bearer_session_and_role_revalidation(workspace: Workspace) -> None:
    email = "teacher@garden.example.test"
    response = workspace.client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": workspace.accounts[email],
            "native": True,
        },
    )
    assert response.status_code == 200
    workspace.client.cookies.clear()
    workspace.client.headers["authorization"] = "Bearer " + response.json()["access_token"]
    assert workspace.client.get("/api/v1/auth/me").json()["role"] == "teacher"
    assert workspace.client.post("/api/v1/auth/logout").status_code == 204
    assert workspace.client.get("/api/v1/auth/me").status_code == 401


def test_identity_011_failed_login_attempts_are_persistently_limited(workspace: Workspace) -> None:
    for _ in range(10):
        response = workspace.client.post(
            "/api/v1/auth/login", json={"email": "bad@example.test", "password": "invalid"}
        )
        assert response.status_code == 401
    assert (
        workspace.client.post(
            "/api/v1/auth/login", json={"email": "bad@example.test", "password": "invalid"}
        ).status_code
        == 429
    )


def test_identity_012_database_passwords_and_sessions_are_not_plaintext(
    workspace: Workspace,
) -> None:
    workspace.login()
    with psycopg.connect(workspace.owner_url) as connection:
        row = connection.execute(
            "SELECT bool_and(password_hash LIKE 'scrypt1$%%') FROM app.users"
        ).fetchone()
        assert row == (True,)
        row = connection.execute(
            "SELECT bool_and(length(token_hash)=64) FROM app.sessions"
        ).fetchone()
        assert row == (True,)
