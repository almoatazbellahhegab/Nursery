# API foundation

## Latest connected runtime

The configured API now provides PostgreSQL-backed identity/session/tenant access
and transactional staff attendance, immutable corrections, receipts, audit and
daily reports. Set NURSERY_DATABASE_URL to the restricted app role and explicit
origins; without a configured database the app retains its health-only fallback.
Use the root connected-runtime runbook and run-runtime-checks.mjs for real DB tests.
The user's explicit review waiver permits continued implementation/testing;
historical policy-blocked/unavailable descriptions below are superseded. MFA,
onboarding and remaining product modules are still being developed.

Health-only FastAPI scaffold. No production data model, authentication, database, authorization or audit implementation is present. Domain work is gated by the source decisions.

Use Python 3.12 in a project virtual environment. Install the resolved development lock and local package as described below, then run Ruff, mypy and pytest; start the health-only API with `uvicorn nursery_api.main:app --app-dir src`.

The project now has an isolated `.venv` with FastAPI/pytest and coding tools; the bundled artifact runtime was not modified. The health test and FEAT-011 domain checks can run. Flutter, PostgreSQL and authoritative identity integration remain unavailable. Do not install application packages into the managed bundled runtime.

`requirements-dev.lock` pins the resolved runtime/test environment (Python 3.12 on Windows); it excludes the editable local project path. To recreate, make a project virtual environment, run `python -m pip install -r requirements-dev.lock -e .`, then `python -m pip check`. The lock pins versions, not artifact hashes. Build-backend pin remains in pyproject.toml.

Run the implemented attendance increment with `Test-Attendance.cmd` from the repository root. See `docs/delivery/S02-FEAT-011.md` for the transaction/authorization integration requirements. No attendance HTTP route is present. Resolved dependencies currently emit an upstream Starlette/AnyIO deprecation warning in TestClient; it is preserved in test output rather than suppressed.

S03 adds a PII-free admissions stage/history decision module. Run `Test-Admissions.cmd` for its checks and attendance regressions; see `docs/delivery/S03-FEAT-030.md`. No admissions HTTP route, default workflow policy, enrollment conversion or persisted family inquiry model is implemented.
