# Sprint 4 staff attendance — initial domain evidence

FEAT-012 is the sole active feature. [Run evidence](runs/2026-10-24T09-12-37-183Z-staff-attendance.json)
records 168 passing backend scenarios, Ruff lint/format, strict mypy and
dependency consistency. There are 31 staff, 58 admissions appointment,
50 admissions stage/retry, 26 child attendance and three health/route scenarios.
The existing upstream Starlette/AnyIO deprecation warning remains. No dependency
or database migration changed.

[Four review/source-preservation checks pass](runs/2026-10-24T09-11-52-566Z-unit.json).
Regeneration retains all 41 features, 204 feature tasks, 69 technical tasks and
216 source cases. The S03 TODO archive's Git content hash matches the prior
committed TODO exactly. `git diff --check` passes. The first passing staff run
is retained; the final run also uses a distinct operation ID for the next-session
fixture, avoiding any implication that operation reuse is an approved retry.

## Result and boundary

`staff_attendance` uses distinct employee types and grants. Presence state is
keyed by organization/employee, so another branch cannot bypass an open session.
Check-in proposes a session/event; checkout links to that session at its branch.
Active status, exact action/branch, expiry and current identity are checked
before state/version conflict details. Future/naive/backwards instants and
inconsistent states fail with stable non-identifying codes.

No role policy, employee corrections, reports, shifts, leave, overtime, payroll,
personal staff profile, API endpoint or database adapter was introduced. The
future server must enforce real identity/profile/assignment/revocation/module
access and use an organization-wide employee lock plus operation uniqueness and
atomic state/event/receipt/audit persistence. Pure unit decisions do not prove
durable retries or actual concurrent-write safety. Inactive-worker checkout
exceptions and cross-branch corrections require their separately approved policy.

## Source mapping

| Scenarios | Source / UAT alias | Coverage |
| --- | --- | --- |
| STAFF-UNIT-001, 003 | TC-FEAT-012-01 / UAT-S04-TC-FEAT-012-01 | Partial scoped state/event and session check-in/out proposal |
| STAFF-UNIT-002, 004, 005, 008, 009 | TC-FEAT-012-02 / UAT-S04-TC-FEAT-012-02 | Partial duplicate/impossible/stale decisions, including other branches |
| STAFF-UNIT-006, 007, 014 | Supplemental XCT-02 | Trusted scope/action/activity/expiry and child-grant separation only |
| STAFF-UNIT-010–013 | DEV-FEAT-012-01 | UTC normalization, safe validation and state consistency |
| Not implemented | TC-FEAT-012-03 / UAT-S04-TC-FEAT-012-03 | Staff corrections and original/new/reason audit integration |

All three source cases remain **Not run at their required API integration
levels**. Stable legacy UAT-S14 identifiers remain in the unchanged plan.
The runner accepts explicit source-acceptance wording to avoid mislabelling
FEAT-012 as having the five source cases of earlier modules.

## Review result and UAT checklist

The existing compiled web/mobile presentation demos are unchanged. They remain
fictional local simulations, with prior browser/build evidence; no new connected
staff attendance UI exists. Staff domain results are reviewed through the tests
and `node tools/run-staff-attendance-checks.mjs`.

- [x] Automated Python scenarios run on Windows; these are not browser UAT.
- [ ] Real PostgreSQL tenant/RLS, employee-lock races, receipt/retry and rollback.
- [ ] Authoritative active/inactive employee, branch/action and revocation tests.
- [ ] Connected authorized Next.js and Flutter allowed/denied journeys.
- [ ] Windows 11 human browser UAT.
- [ ] Emulated browser staff workflow after the UI exists (prior demo runs do not apply).
- [ ] Physical iPhone Safari UAT.
- [ ] Native iPhone build/signing and physical UAT on macOS/Xcode.
- [ ] Staff correction/privacy/report policy and named specialist/user acceptance.

Rollback is reverting the isolated staff module/tests, runner and execution
checkpoint; no production data migration or route needs rollback. All six S04
features, 29 feature tasks, five technical tasks and 25 source cases remain in
the plan. No S04 branch is pushed under the S03 approval.
