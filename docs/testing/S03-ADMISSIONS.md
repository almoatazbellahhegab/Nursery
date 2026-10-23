# Admissions domain tests and UAT links

| Cases | Behavior | Source / current UAT | Coverage limit |
| --- | --- | --- | --- |
| ADM-UNIT-001 | Prior/new stage, actor, UTC time, version and policy recorded | TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 | Domain only; no database/history API integration |
| ADM-UNIT-002–004, 016 | Explicit configured moves; deny implicit skipping/self edges; configured reopening | TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 | Synthetic policy fixtures; no business-policy approval claimed |
| ADM-UNIT-005–008 | Other organization/branch/lead/policy and expiry denied | TC-FEAT-030-04 / UAT-S03-TC-FEAT-030-04 | Trusted input decisions only; actual visibility UI/E2E pending |
| ADM-UNIT-009–010, 012–015, 017 | Stale/no-op, time/version and immutability invariants | TC-FEAT-030-02 / UAT-S03-TC-FEAT-030-02 | Real concurrency and durable history pending |
| ADM-UNIT-011 | Stage-edit path cannot create or undo enrollment | TC-FEAT-030-03 / UAT-S03-TC-FEAT-030-03 | Conversion guard only; onboarding/deduplication not implemented |
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
