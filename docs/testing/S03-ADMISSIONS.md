# Admissions domain tests and UAT links

## Latest verification: retry chronology (2026-10-24)

Retry receipts now reject a saved event later than the supplied server instant
with `admissions_operation_conflict`. A retry at the exact event instant remains
valid. ADM-UNIT-029 and ADM-UNIT-030 each cover UTC, UTC+3 and UTC-5, checking
instant comparison and preservation of the original snapshot/history objects.
These are partial TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 domain checks.

[All 79 backend scenarios, lint, format, strict types and dependency checks pass](runs/2026-10-24T08-08-47-850Z-admissions.json).
The suite contains 50 admissions, 26 attendance and three route/health scenarios.
The upstream Starlette/AnyIO deprecation warning remains. Existing compiled web
and mobile demos are unchanged; their prior evidence and separate Windows human,
physical iPhone Safari and native iPhone UAT checklist remain applicable. No
operational source acceptance case or policy gate is completed by this change.

| Cases | Behavior | Source / current UAT | Coverage limit |
| --- | --- | --- | --- |
| ADM-UNIT-001 | Prior/new stage, actor, UTC time, version and policy recorded | TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 | Domain only; no database/history API integration |
| ADM-UNIT-002–004, 016 | Explicit configured moves; deny implicit skipping/self edges; configured reopening | TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 | Synthetic policy fixtures; no business-policy approval claimed |
| ADM-UNIT-005–008 | Other organization/branch/lead/policy and expiry denied | TC-FEAT-030-04 / UAT-S03-TC-FEAT-030-04 | Trusted input decisions only; actual visibility UI/E2E pending |
| ADM-UNIT-009–010, 012–015, 017 | Stale/no-op, time/version and immutability invariants | TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 | Real concurrency and durable history pending |
| ADM-UNIT-011 | Stage-edit path cannot create or undo enrollment | TC-FEAT-030-03 / UAT-S03-TC-FEAT-030-03 | Conversion guard only; onboarding/deduplication not implemented |
| ADM-UNIT-018–028 | Trusted exact-retry replay, payload/receipt consistency, actor/scope/expiry checks, immutable original fact and no state rollback | Partial TC-FEAT-030-02 and TC-FEAT-030-04 | Pure domain only; real database receipts/transactions and current authorization remain unimplemented |
| Admissions route guard | No public mutation endpoint exists before branch authorization | Supplemental release guard | Does not prove working admissions API |
| TC-FEAT-030-01, 03, 05 | Inquiry creation, real conversion and reporting | Corresponding UAT-S03 aliases | Not run at required API integration level |

All five source cases remain Not run at their required integration/component/E2E levels; old UAT-S12 identifiers remain stable in plan.json alongside current aliases. Parameterization expands 17 named admissions cases into 22 scenarios. The full current suite also includes 26 attendance scenarios and three health/fail-closed transport guards.

Initial validation: 51 pytest scenarios passed; strict mypy found a test-fixture typing problem in parametrized `dataclasses.replace` on a mixed-type grant. Replacing the dynamically expanded field dictionary with explicit typed branch/organization replacements fixed it. No product assertions failed. Final checks and code-tied evidence are recorded separately; the existing upstream Starlette/AnyIO deprecation warning is retained.

## Recorded increment result

Code under test: `eb29e670807338f2abbd01a702e771bf0a42e6f8`.

| Check | Result | Evidence |
| --- | --- | --- |
| 22 admissions scenarios, 26 attendance regressions, three health/fail-closed guards | 51 passed | [Domain/API checks](runs/2026-10-23T21-54-31-497Z-admissions.json) |
| Ruff lint / format | Passed; 10 files formatted | Same domain/API run |
| Strict mypy | Passed; 10 files | Same domain/API run |
| Dependency consistency | Passed | Same domain/API run |
| Plan and server regression | Four passed | [Review unit run](runs/2026-10-23T21-54-31-505Z-unit.json) |
| Desktop/emulated-mobile preview and S03/FEAT-030 indicator | Three passed | [Portal browser run](runs/2026-10-23-S03-admissions-portal.json) |
| Original admissions integration cases and physical/native device checks | Not run / Pending / Blocked | No operational feature acceptance claimed |

The only untracked files at final verification were evidence artifacts, including a pre-existing attendance run left untouched. New S03 commits are not pushed. Workflow/field approval, actual branch authorization, PostgreSQL and client integration remain open.

## 2026-10-24 continuation: admissions retries

The user requested continuing S03 through completion. A trusted `StageReceipt`
now allows an exact retry to return the original state/history with `replayed`
true. It never creates a new event or overwrites a newer state. Current grant
scope/expiry is checked before receipt conflicts. Changed payload/operation,
another actor or resource, inconsistent receipt parts and contradictory current
state are denied with safe codes. Historical success retains its original policy
reference even if the current configured edges have changed; the retry still
requires a current trusted grant. Stage history validates UUIDs, non-boolean
positive versions, actual stage changes and aware UTC timestamps.

The adapter must obtain authoritative grants on each request, load the receipt
under organization/branch/actor/operation scope, and persist state, history,
receipt and audit in one transaction. A replay is a historical response and
must not be saved as the current snapshot. These tests do not prove durable
idempotency, concurrent-write safety, authentication or production authorization.

Final evidence: [73 backend scenarios and all coding/dependency checks pass](runs/2026-10-24T07-37-19-462Z-admissions.json):
44 admissions, 26 attendance regressions and three health/fail-closed guards.
[Four review/source integrity checks pass](runs/2026-10-24T07-37-23-887Z-unit.json).
The earlier retry run is retained: tests passed but strict typing found an
invalid dynamic test-fixture replacement; explicit typed replacements corrected
it. The existing upstream Starlette/AnyIO warning remains visible.

No source product task or acceptance case is marked complete. No API route,
production data model or policy defaults were added. Web/mobile source is
unchanged by this retry increment; their latest verified demo builds remain
reviewable. All current work remains uncommitted under the recorded `.git`
restriction. See [the decision pack](../delivery/S03-DECISION-PACK.md) for the
operational dependencies, owners and approval inputs needed to finish S03.
