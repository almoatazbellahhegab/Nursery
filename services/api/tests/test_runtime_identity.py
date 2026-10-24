"""Real PostgreSQL identity/RLS integration; refuses to reset anything but nursery_test."""

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from nursery_api.runtime.api import configure_runtime
from nursery_api.runtime.bootstrap import identifier, seed_workspace
from nursery_api.runtime.database import Database, set_context

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class Workspace:
    client: TestClient
    database: Database
    owner_url: str = field(repr=False)
    accounts: dict[str, str] = field(repr=False)

    def login(self, role: str = "administrator", tenant: str = "garden") -> dict[str, Any]:
        email = f"{role}@{tenant}.example.test"
        response = self.client.post(
            "/api/v1/auth/login", json={"email": email, "password": self.accounts[email]}
        )
        assert response.status_code == 200
        data: dict[str, Any] = response.json()
        self.client.headers["x-csrf-token"] = data["csrf_token"]
        return data


@pytest.fixture
def workspace() -> Iterator[Workspace]:
    runtime_file = ROOT / ".tools/database-runtime.json"
    if not runtime_file.exists():
        pytest.skip("Owned PostgreSQL setup required: tools/setup-local-database.py")
    runtime = json.loads(runtime_file.read_text())
    with psycopg.connect(runtime["test_owner_url"]) as connection:
        database = connection.execute("SELECT current_database()").fetchone()
        if database != ("nursery_test",):
            raise RuntimeError("Refusing to reset a database other than the owned nursery_test")
        connection.execute("""TRUNCATE app.audit,app.sessions,app.login_limits,app.employee_assignments,
            app.employees,app.branch_memberships,app.memberships,app.branches,app.users,
            app.organizations CASCADE""")
        seed_workspace(connection, ROOT / ".tools/test-accounts.json")
    accounts = json.loads((ROOT / ".tools/test-accounts.json").read_text())
    app = FastAPI()
    configure_runtime(app, runtime["test_url"], ["http://localhost:3000"], False)
    with TestClient(app) as client:
        client.headers["origin"] = "http://localhost:3000"
        yield Workspace(client, Database(runtime["test_url"]), runtime["test_owner_url"], accounts)


def test_identity_001_password_session_and_database_role(workspace: Workspace) -> None:
    data = workspace.login()
    assert data["role"] == "administrator"
    assert len(data["branches"]) == 2
    assert workspace.client.get("/api/v1/auth/me").status_code == 200
    with workspace.database.transaction() as connection:
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
