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
from nursery_api.runtime.bootstrap import seed_workspace
from nursery_api.runtime.database import Database

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
