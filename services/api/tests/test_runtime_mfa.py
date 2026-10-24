"""Real PostgreSQL MFA boundary, replay, recovery, throttling and concurrency."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import Any
from uuid import uuid4

import psycopg
import pyotp
import pytest
from cryptography.fernet import Fernet
from fastapi import FastAPI
from fastapi.testclient import TestClient

from conftest import Workspace
from nursery_api.runtime.api import now_utc
from nursery_api.runtime.bootstrap import identifier
from nursery_api.runtime.database import set_context
from nursery_api.runtime.security import digest


@pytest.fixture
def secured(workspace: Workspace) -> Workspace:
    app = workspace.client.app
    assert isinstance(app, FastAPI)
    app.state.mfa_cipher = Fernet(Fernet.generate_key())
    app.state.require_mfa = True
    return workspace


def send(client: TestClient, path: str, body: dict[str, Any], operation: str | None = None) -> Any:
    response = client.post(
        "/api/v1/auth/mfa/" + path,
        json=body,
        headers={"Idempotency-Key": operation or str(uuid4())},
    )
    if response.status_code == 200 and "profile" in response.json():
        client.headers["x-csrf-token"] = response.json()["profile"]["csrf_token"]
    return response


def enroll(workspace: Workspace, operation: str | None = None) -> tuple[pyotp.TOTP, Any]:
    begin = send(workspace.client, "begin", {})
    assert begin.status_code == 200
    otp = pyotp.TOTP(begin.json()["secret"])
    result = send(workspace.client, "confirm", {"code": otp.now()}, operation)
    assert result.status_code == 200
    return otp, result


def other_session(workspace: Workspace) -> TestClient:
    client = TestClient(workspace.client.app, headers={"origin": "http://localhost:3000"})
    email = "administrator@garden.example.test"
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": workspace.accounts[email]}
    )
    assert response.status_code == 200
    client.headers["x-csrf-token"] = response.json()["csrf_token"]
    return client


def test_mfa_001_primary_privileged_session_cannot_read_or_write_product_data(
    secured: Workspace,
) -> None:
    data = secured.login()
    assert data["mfa_required"] and not data["mfa_enrolled"] and data["branches"] == []
    assert secured.client.get("/api/v1/branches").json()["code"] == "mfa_required"
    assert (
        secured.client.post(
            "/api/v1/branches", json={"name": "Denied"}, headers={"Idempotency-Key": str(uuid4())}
        ).status_code
        == 403
    )
    assert secured.client.get("/api/v1/auth/me").status_code == 200
    assert secured.client.post("/api/v1/auth/logout").status_code == 204
    assert secured.client.get("/api/v1/auth/me").status_code == 401


def test_mfa_002_enrollment_encrypts_secrets_and_issues_hashed_recovery(secured: Workspace) -> None:
    secured.login()
    _, result = enroll(secured)
    data = result.json()
    assert not data["profile"]["mfa_required"] and data["profile"]["mfa_enrolled"]
    assert len(data["recovery_codes"]) == 10
    assert secured.client.get("/api/v1/branches").status_code == 200
    with psycopg.connect(secured.owner_url) as connection:
        row = connection.execute(
            "SELECT secret_cipher,activated_at,pending_cipher FROM app.mfa_enrollments"
        ).fetchone()
        assert row is not None and row[1] is not None and row[2] is None
        assert row[0].startswith("gAAAA")
        values = connection.execute("SELECT code_hash FROM app.mfa_recovery_codes").fetchall()
        assert len(values) == 10 and all(len(row[0]) == 64 for row in values)
        audit = str(
            connection.execute("SELECT details FROM app.audit WHERE action LIKE 'mfa.%'").fetchall()
        )
        for code in data["recovery_codes"]:
            if code in audit or any(code == row[0] for row in values):
                raise AssertionError(
                    "Recovery material must not appear in audit or unhashed storage"
                )


def test_mfa_003_exact_confirm_retry_is_bound_to_session_and_current_scope(
    secured: Workspace,
) -> None:
    secured.login()
    started = send(secured.client, "begin", {}).json()
    otp = pyotp.TOTP(started["secret"])
    body = {"code": otp.now()}
    operation = str(uuid4())
    first = send(secured.client, "confirm", body, operation)
    assert first.status_code == 200
    with psycopg.connect(secured.owner_url) as connection:
        connection.execute(
            "UPDATE app.memberships SET role='branch_manager' WHERE user_id=%s",
            (identifier("administrator@garden.example.test"),),
        )
        connection.execute(
            "DELETE FROM app.branch_memberships WHERE user_id=%s AND branch_id=%s",
            (identifier("administrator@garden.example.test"), identifier("gardencairo")),
        )
    retry = send(secured.client, "confirm", body, operation)
    assert retry.status_code == 200 and retry.json()["replayed"]
    assert retry.json()["profile"]["role"] == "branch_manager"
    assert len(retry.json()["profile"]["branches"]) == 1
    assert len(retry.json()["recovery_codes"]) == 10
    assert send(secured.client, "confirm", {"code": "changed"}, operation).status_code == 409
    with psycopg.connect(secured.owner_url) as connection:
        assert connection.execute("SELECT count(*) FROM app.auth_receipts").fetchone() == (2,)
        assert connection.execute(
            "SELECT count(*) FROM app.audit WHERE action='mfa.enrollment_confirmed'"
        ).fetchone() == (1,)


def test_mfa_004_pending_enrollment_cannot_be_confirmed_from_another_session(
    secured: Workspace,
) -> None:
    secured.login()
    otp = pyotp.TOTP(send(secured.client, "begin", {}).json()["secret"])
    other = other_session(secured)
    try:
        assert send(other, "confirm", {"code": otp.now()}).status_code == 403
        assert send(secured.client, "confirm", {"code": otp.now()}).status_code == 200
        assert other.get("/api/v1/auth/me").status_code == 401
    finally:
        other.close()


def test_mfa_005_totp_replay_denied_and_recovery_consumed_once(secured: Workspace) -> None:
    secured.login()
    otp, result = enroll(secured)
    code = result.json()["recovery_codes"][0]
    client = other_session(secured)
    try:
        assert client.get("/api/v1/branches").status_code == 403
        # Enrollment consumed this time step; it cannot authorize a new session.
        with psycopg.connect(secured.owner_url) as connection:
            saved = connection.execute("SELECT last_counter FROM app.mfa_enrollments").fetchone()
            assert saved is not None
            counter = saved[0]
        assert send(client, "verify", {"code": otp.generate_otp(counter)}).status_code == 403
        operation = str(uuid4())
        assert (
            send(client, "verify", {"kind": "recovery", "code": code}, operation).status_code == 200
        )
        assert send(client, "verify", {"kind": "recovery", "code": code}, operation).json()[
            "replayed"
        ]
        assert send(client, "verify", {"kind": "recovery", "code": code}).status_code == 403
        assert client.get("/api/v1/branches").status_code == 200
    finally:
        client.close()


def test_mfa_006_failures_persist_across_transactions_and_new_logins(secured: Workspace) -> None:
    secured.login()
    otp = pyotp.TOTP(send(secured.client, "begin", {}).json()["secret"])
    for _ in range(5):
        assert send(secured.client, "confirm", {"code": "invalid"}).status_code == 403
    assert send(secured.client, "confirm", {"code": otp.now()}).status_code == 429
    secured.login()
    assert send(secured.client, "confirm", {"code": "invalid"}).status_code == 429
    with psycopg.connect(secured.owner_url) as connection:
        assert connection.execute("SELECT failures FROM app.mfa_enrollments").fetchone() == (5,)
        connection.execute(
            "UPDATE app.mfa_enrollments SET window_started_at=%s",
            (now_utc() - timedelta(minutes=6),),
        )
    # The prior enrollment was bound to the prior session; a new start is required.
    _, result = enroll(secured)
    assert result.status_code == 200


def test_mfa_007_role_promotion_does_not_upgrade_an_existing_weak_session(
    secured: Workspace,
) -> None:
    secured.login("teacher")
    assert secured.client.get("/api/v1/branches").status_code == 200
    with psycopg.connect(secured.owner_url) as connection:
        connection.execute(
            "UPDATE app.memberships SET role='administrator' WHERE user_id=%s",
            (identifier("teacher@garden.example.test"),),
        )
    assert secured.client.get("/api/v1/branches").json()["code"] == "mfa_required"
    assert secured.client.get("/api/v1/auth/me").json()["branches"] == []


def test_mfa_008_stale_second_factor_cannot_manage_branch_access(secured: Workspace) -> None:
    secured.login()
    enroll(secured)
    with psycopg.connect(secured.owner_url) as connection:
        connection.execute(
            "UPDATE app.sessions SET authenticated_at=%s,mfa_at=%s",
            (now_utc() - timedelta(minutes=20), now_utc() - timedelta(minutes=16)),
        )
    assert secured.client.get("/api/v1/branches").status_code == 200
    assert (
        secured.client.get("/api/v1/branches/members").json()["code"] == "reauthentication_required"
    )
    assert send(secured.client, "begin", {}).status_code == 403


def test_mfa_009_enrollment_audit_failure_rolls_back_proof_and_recovery(secured: Workspace) -> None:
    secured.login()
    otp = pyotp.TOTP(send(secured.client, "begin", {}).json()["secret"])
    with psycopg.connect(secured.owner_url) as connection:
        connection.execute("""CREATE FUNCTION app.test_reject_mfa() RETURNS trigger LANGUAGE plpgsql AS
            $$ BEGIN IF NEW.action='mfa.enrollment_confirmed' THEN RAISE EXCEPTION 'simulated audit failure'; END IF; RETURN NEW; END $$;
            CREATE TRIGGER test_reject_mfa BEFORE INSERT ON app.audit FOR EACH ROW EXECUTE FUNCTION app.test_reject_mfa();""")
    try:
        with pytest.raises(psycopg.errors.RaiseException):
            send(secured.client, "confirm", {"code": otp.now()})
    finally:
        with psycopg.connect(secured.owner_url) as connection:
            connection.execute(
                "DROP TRIGGER test_reject_mfa ON app.audit; DROP FUNCTION app.test_reject_mfa()"
            )
    with psycopg.connect(secured.owner_url) as connection:
        assert connection.execute("SELECT activated_at FROM app.mfa_enrollments").fetchone() == (
            None,
        )
        assert connection.execute("SELECT count(*) FROM app.mfa_recovery_codes").fetchone() == (0,)
        assert connection.execute("SELECT count(*) FROM app.auth_receipts").fetchone() == (0,)
        assert connection.execute("SELECT mfa_at FROM app.sessions").fetchone() == (None,)


def test_mfa_010_two_sessions_racing_one_recovery_code_have_one_winner(secured: Workspace) -> None:
    secured.login()
    _, result = enroll(secured)
    code = result.json()["recovery_codes"][0]
    clients = [other_session(secured), other_session(secured)]
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(
                pool.map(
                    lambda client: send(client, "verify", {"kind": "recovery", "code": code}),
                    clients,
                )
            )
        assert sorted(response.status_code for response in responses) == [200, 403]
    finally:
        for client in clients:
            client.close()
    with psycopg.connect(secured.owner_url) as connection:
        assert connection.execute(
            "SELECT count(*) FROM app.mfa_recovery_codes WHERE used_at IS NOT NULL"
        ).fetchone() == (1,)
        assert connection.execute(
            "SELECT count(*) FROM app.audit WHERE action='mfa.recovery_used'"
        ).fetchone() == (1,)


def test_mfa_011_rls_prevents_other_users_reading_or_changing_factor_material(
    secured: Workspace,
) -> None:
    secured.login()
    enroll(secured)
    teacher = identifier("teacher@garden.example.test")
    with secured.database.transaction() as connection:
        set_context(connection, teacher, identifier("garden"), "teacher")
        for table in ("mfa_enrollments", "mfa_recovery_codes", "auth_receipts"):
            assert connection.execute(f"SELECT count(*) AS total FROM app.{table}").fetchone() == {
                "total": 0
            }
        assert connection.execute("UPDATE app.mfa_enrollments SET failures=0").rowcount == 0
    with (
        pytest.raises(psycopg.errors.InsufficientPrivilege),
        secured.database.transaction() as connection,
    ):
        set_context(connection, teacher, identifier("garden"), "teacher")
        connection.execute(
            "INSERT INTO app.mfa_enrollments(user_id) VALUES(%s)",
            (identifier("parent@garden.example.test"),),
        )


def test_mfa_012_rotation_bridge_only_recovers_exact_response_and_cannot_survive_logout(
    secured: Workspace,
) -> None:
    secured.login()
    previous = secured.client.cookies.get("nursery_session")
    previous_csrf = secured.client.headers["x-csrf-token"]
    assert previous is not None
    otp = pyotp.TOTP(send(secured.client, "begin", {}).json()["secret"])
    body = {"code": otp.now()}
    operation = str(uuid4())
    assert send(secured.client, "confirm", body, operation).status_code == 200
    current = secured.client.cookies.get("nursery_session")
    assert current is not None and digest(current) != digest(previous)
    old = TestClient(
        secured.client.app,
        headers={"origin": "http://localhost:3000", "x-csrf-token": previous_csrf},
    )
    old.cookies.set("nursery_session", previous, domain="testserver.local", path="/api/v1")
    try:
        assert old.get("/api/v1/branches").status_code == 401
        assert send(old, "verify", body).status_code == 401
        assert send(old, "confirm", body, operation).json()["replayed"]
        assert old.get("/api/v1/branches").status_code == 200
        assert secured.client.post("/api/v1/auth/logout").status_code == 204
        assert old.get("/api/v1/branches").status_code == 401
        old.cookies.clear()
        old.cookies.set("nursery_session", previous, domain="testserver.local", path="/api/v1")
        old.headers["x-csrf-token"] = previous_csrf
        assert send(old, "confirm", body, operation).status_code == 401
    finally:
        old.close()


def test_mfa_013_second_factor_does_not_extend_primary_absolute_expiry(secured: Workspace) -> None:
    secured.login()
    cap = now_utc() + timedelta(minutes=2)
    with psycopg.connect(secured.owner_url) as connection:
        connection.execute(
            "UPDATE app.sessions SET absolute_expires_at=%s,expires_at=%s", (cap, cap)
        )
    enroll(secured)
    with psycopg.connect(secured.owner_url) as connection:
        rows = connection.execute(
            "SELECT expires_at,absolute_expires_at FROM app.sessions"
        ).fetchall()
        assert len(rows) == 2 and all(row[0] <= cap and row[1] == cap for row in rows)


def test_mfa_014_native_rotation_returns_new_bearer_and_retires_old_authority(
    secured: Workspace,
) -> None:
    client = TestClient(secured.client.app)
    email = "administrator@garden.example.test"
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": secured.accounts[email], "native": True},
    )
    assert login.status_code == 200
    previous = login.json()["access_token"]
    client.headers["authorization"] = "Bearer " + previous
    otp = pyotp.TOTP(send(client, "begin", {}).json()["secret"])
    body = {"code": otp.now()}
    operation = str(uuid4())
    try:
        confirmed = send(client, "confirm", body, operation)
        assert confirmed.status_code == 200
        current = confirmed.json()["profile"]["access_token"]
        assert digest(current) != digest(previous)
        assert client.get("/api/v1/branches").status_code == 401
        replay = send(client, "confirm", body, operation)
        assert replay.status_code == 200 and replay.json()["replayed"]
        if digest(replay.json()["profile"]["access_token"]) != digest(current):
            raise AssertionError("Exact retry must recover the same rotated session")
        client.headers["authorization"] = "Bearer " + current
        assert client.get("/api/v1/branches").status_code == 200
    finally:
        client.close()


def test_mfa_015_logout_racing_enrollment_cannot_leave_an_elevated_session_live(
    secured: Workspace,
) -> None:
    secured.login()
    otp = pyotp.TOTP(send(secured.client, "begin", {}).json()["secret"])
    logout_client = TestClient(
        secured.client.app,
        headers={
            "origin": "http://localhost:3000",
            "x-csrf-token": secured.client.headers["x-csrf-token"],
        },
    )
    logout_client.cookies.update(secured.client.cookies)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            elevation = pool.submit(send, secured.client, "confirm", {"code": otp.now()})
            logout = pool.submit(logout_client.post, "/api/v1/auth/logout")
            assert elevation.result().status_code in {200, 401}
            assert logout.result().status_code == 204
    finally:
        logout_client.close()
    with psycopg.connect(secured.owner_url) as connection:
        assert connection.execute(
            "SELECT count(*) FROM app.sessions WHERE NOT revoked AND replaced_by_hash IS NULL"
        ).fetchone() == (0,)
