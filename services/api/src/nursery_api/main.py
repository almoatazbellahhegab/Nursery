"""Health-only FastAPI application; never returns tenant or child information."""

from fastapi import FastAPI

app = FastAPI(title="Nursery API foundation", version="0.1.0")


@app.get(
    "/api/v1/health",
    summary="Read process liveness without exposing tenant information",
    description="Public, side-effect-free and idempotent. Does not prove database readiness.",
)
def health() -> dict[str, str]:
    """Return process liveness only; dependencies are deliberately not claimed ready."""
    return {"status": "alive", "stage": "foundation"}
