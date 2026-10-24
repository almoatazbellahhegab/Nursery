# Connected runtime — local setup and verification

The user explicitly waived outstanding reviews for implementation/testing on
2026-10-24. See AGENTS.md's recorded override; reviews are waived, not signed off.
Original Product decisions, specification identifiers and acceptance/UAT scope
remain. No deployment or additional push is authorized by the waiver.

## Project-owned database

PostgreSQL 18.6 portable Windows binaries were downloaded from the official EDB
link listed by PostgreSQL's Windows download page:
`https://sbp.enterprisedb.com/getfile.jsp?fileid=1260609`.
Archive SHA-256: `E2246BA91D22345BC3D017586C09EDE52D9DF180B1EEB480F050445F1CAD84E2`.
The ignored archive and extracted toolchain are not part of Git.

Run using `services/api/.venv/Scripts/python.exe`:

1. `tools/setup-local-database.py`: extracts owned tools, initializes only
   `.tools/postgres-data`, starts loopback port 55432, creates dev/test databases
   and a NOSUPERUSER/NOBYPASSRLS application role, then applies Alembic revisions.
2. `tools/seed-local-workspace.py`: adds fictional organizations, branches and
   accounts. Generated passwords are written only to ignored local account files.
3. `node tools/run-runtime-checks.mjs`: real PostgreSQL identity/tenant integration,
   retained domain scenarios, Ruff, strict mypy and dependency consistency.
   Required integration skips fail this runner.

Runtime DSNs are in ignored `.tools/database-runtime.json`; do not print, commit,
share or reuse them in deployment. Migration/bootstrap use the local owner;
the API uses the restricted `dev_url`. Integration resets only `nursery_test`
after verifying `current_database()`. It must never reset production data.

Dependencies are pinned in pyproject.toml and requirements-dev.lock. Provision
PostgreSQL through approved environment tooling on other operating systems.
The Windows helper creates no Windows service or machine-wide policy change.

## Runtime identity and implementation choices

- Individual accounts use salted scrypt password hashes. Opaque random sessions
  are stored as digests, expire after 12 hours and after 30 minutes of inactivity.
- Organization, user and membership activity/role are checked on every request;
  JSON cannot supply role claims. Employee/assignment checks are added by the
  feature boundary before staff actions.
- Browser sessions use HttpOnly SameSite=Strict cookies and origin/CSRF checks;
  secure cookies are the default. `NURSERY_ENV=local` explicitly permits local
  HTTP. Native clients use revocable opaque bearer sessions.
- Failed login attempts are persisted and limited per account/IP fingerprint
  to ten per 15 minutes. Invalid credential responses do not reveal existence.
- App tenant context is transaction-local. FORCE RLS hides rows without a tenant
  and isolates organizations; branch lists are filtered by current assignments.
- API exceptions/validation omit database and submitted credential details.
- Production requires deployment TLS, secrets management, backed-up PostgreSQL,
  operational monitoring and actual deployment/UAT verification. Local setup does
  not establish those results or an MFA/provider integration.

## Migration and rollback

Revision `0001_identity` creates constrained identity/tenant tables and RLS with
no data backfill. Test on an empty database. No automatic destructive downgrade
is provided because it would remove access/history; use a reviewed forward fix.
New migrations must retain the original installed revision unchanged.

## First integration evidence

[218 scenarios and all coding/dependency checks pass](../testing/runs/2026-10-24T10-43-16-887Z-runtime.json):
14 real PostgreSQL identity scenarios plus 204 prior domain/regression scenarios.
This is the connected foundation, not completed module, deployment or UAT acceptance.
