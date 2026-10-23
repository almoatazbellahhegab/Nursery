"""Transport smoke check; not a substitute for real API authorization tests."""

from fastapi.testclient import TestClient

from nursery_api.main import app


def test_health_exposes_no_operational_records() -> None:
    """A public liveness call exposes only the process foundation status."""
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "stage": "foundation"}
