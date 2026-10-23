# API foundation

Health-only FastAPI scaffold. No production data model, authentication, database, authorization or audit implementation is present. Domain work is gated by the source decisions.

Use Python 3.12 in a project virtual environment. Dependency candidates are pinned but unresolved; install a lock tool, resolve and commit a reproducible lockfile before CI adoption. Once dependencies are available, install `.[dev]`, then run Ruff, mypy and pytest; start with `uvicorn nursery_api.main:app --app-dir src`.

The current machine has only the bundled artifact Python runtime and no FastAPI/pytest dependencies. Do not install application packages into the managed bundled runtime. Application build and tests remain Blocked under ENV-001.
