"""Health-only FastAPI application; never returns tenant or child information."""

import os

from fastapi import FastAPI

from .runtime.api import configure_runtime

app = FastAPI(title="Nursery API foundation", version="0.1.0")

if database_url := os.environ.get("NURSERY_DATABASE_URL"):
    configure_runtime(
        app,
        database_url,
        os.environ.get("NURSERY_ORIGINS", "http://localhost:3000,http://localhost:3200").split(","),
        os.environ.get("NURSERY_ENV") != "local",
    )


@app.get(
    "/api/v1/health",
    summary="Read process liveness without exposing tenant information",
    description="Public, side-effect-free and idempotent. Does not prove database readiness.",
)
def health() -> dict[str, str]:
    """Return process liveness only; dependencies are deliberately not claimed ready."""
    return {"status": "alive", "stage": "foundation"}
