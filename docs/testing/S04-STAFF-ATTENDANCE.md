# Sprint 4 staff attendance — connected implementation and evidence

## Connected implementation — review waiver applied

The user's explicit instruction to skip outstanding reviews supersedes the
historical gate-blocked descriptions below for development/testing. Staff now
has real PostgreSQL state, immutable events/corrections, actor-scoped durable
receipts and atomic audit. Employees and assignments are loaded from authoritative
tables; roles, organization, session and scope are resolved per request. Parent/
finance accounts are denied; teachers see only themselves; managers see assigned
branches; organization administrators see their organization. No client role
selector is a permission boundary.

Implementation defaults: managers/admins can correct another employee's record
within seven days of recording, with a mandatory reason and timeline-order checks.
Original facts remain immutable, and reports apply the newest correction. There
is no self-correction, payroll, overtime or leave calculation. Branch day boundaries
use Africa/Cairo, stored/returned instants are UTC. Histories and reports are
bounded and expose truncation flags; large-history/pagination refinement remains.

The compiled Next.js root and Flutter root now sign into the same API/database.
Both support branch selection, check-in/out, history, manager corrections, daily
report and English/Arabic. Fictional presentation is separate at web `/demo` and
Flutter `?demo=true`; existing `?view=parent/teacher` remain fictional demo links.

| Verification | Result / evidence |
| --- | --- |
| 232 scenarios: 204 prior, 14 identity/RLS, 14 staff API/PostgreSQL | [Pass](runs/2026-10-24T11-27-57-018Z-runtime.json) |
| Ruff lint/format, strict mypy, dependency consistency | Same passing runtime run |
| Next.js types/lint/format/build and npm audit (zero reported vulnerabilities) | [Pass](runs/2026-10-24T11-43-50-863Z-clients.json) |
| Flutter format/analyzer and eight tests | [Pass](runs/2026-10-24T11-43-21-695Z-clients.json) |
| Flutter web build | Pass in [retained run](runs/2026-10-24T11-28-07-768Z-clients.json); that run's test-style lint findings were fixed before final passing checks |
| Connected web reload persistence, Flutter shared state, manager correction/report, Arabic and parent denial | [Four groups pass](runs/2026-10-24T11-52-41-195Z-connected-browsers.json) |
| Screenshot inspection | Desktop English, desktop Arabic and mobile staff screens inspected; readable/no visible clipping |

TC-FEAT-012-01/02/03 now have **passing actual API integration coverage** through
STAFF-API-001/002/003, with extra race/rollback/RLS/revocation scenarios. This does
not accept UAT. Stable original source definitions/IDs remain unchanged; historical
Not run labels below refer to the earlier domain-only increments.

Profile/organization account onboarding, MFA, broader policy configuration,
generated contract clients, large-history pagination and the remaining product
features are unfinished. Existing fictional employee profiles make this connected
journey testable, but do not complete all predecessor features. Physical iPhone
Safari, signed native iPhone and human Windows/Arabic acceptance remain pending.
Earlier failed client/browser runs are retained with defects described in DEFECTS.md.

[All nine fictional-demo regression groups pass](runs/2026-10-24T12-06-08-668Z-demo-browsers.json),
including the corrected new-port LAN/static checks. [Four source/review checks
pass](runs/2026-10-24T12-06-07-688Z-unit.json); the source-case execution overlay
now verifies actual passing artifact/test names without marking UAT accepted.

## Latest increment — trusted retry integrity

[204 backend scenarios and all coding/dependency checks pass](runs/2026-10-24T09-29-04-273Z-staff-attendance.json).
There are 67 staff scenarios and 137 earlier regressions. STAFF-UNIT-015–025
add exact check-in/checkout replay, equivalent timezone offsets, unchanged
original session/event, changed-command rejection, actor/target isolation,
current activity/action/expiry denial, contradictory current/historical facts,
positive event versions and receipt chronology. These are partial
TC-FEAT-012-02 / UAT-S04-TC-FEAT-012-02 and supplemental XCT-02 checks, not
durable idempotency or completed source integration cases.

Trusted `StaffReceipt` must be loaded and committed atomically with state/event/
audit under actor/employee/branch/organization/operation scope. A replay returns
the historical snapshot with `replayed=True`; never persist it over current
state or publish another event. Current scope, action, employee activity and
grant expiry are checked on retries. Corrupt saved parts or inconsistent
current state fail closed. StaffEvent now validates identifiers, aware UTC
times and positive non-boolean version. No staff correction policy is inferred.

No dependencies, migration, runtime policy or UI changed. Earlier client build/
emulation evidence remains unchanged and does not pass the new staff workflow.
All original API cases and the independent UAT checklist below remain pending.
Full S04 blockers and original gate ownership are in
[the completion checklist](../delivery/S04-COMPLETION.md).

[Four source/review checks pass](runs/2026-10-24T09-31-13-312Z-unit.json);
the regenerated plan preserves 41 features, 204 feature tasks, 69 technical
tasks and 216 source cases. `git diff --check` passes.

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
