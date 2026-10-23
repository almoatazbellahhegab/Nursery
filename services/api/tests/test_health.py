"""Transport smoke check; not a substitute for real API authorization tests."""

from fastapi.testclient import TestClient

from nursery_api.main import app


def test_health_exposes_no_operational_records() -> None:
    """A public liveness call exposes only the process foundation status."""
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "stage": "foundation"}


def test_attendance_has_no_public_mutation_route_before_authorization_exists() -> None:
    """The domain increment must not accidentally expose unauthenticated writes."""
    response = TestClient(app).post("/api/v1/attendance", json={"action": "check_in"})
    assert response.status_code == 404


def test_admissions_has_no_public_mutation_route_before_branch_authorization_exists() -> None:
    """An isolated stage engine must not expose unauthenticated lead writes."""
    response = TestClient(app).post("/api/v1/admissions", json={"stage": "accepted"})
    assert response.status_code == 404
