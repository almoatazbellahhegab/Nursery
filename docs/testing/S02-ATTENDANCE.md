# Attendance domain test log and UAT links

Automated domain cases are supplemental to the original acceptance catalogue. They do not pass the source API/mobile cases. Current UAT aliases below retain their original `UAT-S05-...` identifiers in plan.json.

| Unit case | Observable behavior | Source / current UAT | Coverage limit |
| --- | --- | --- | --- |
| ATT-UNIT-001 | Check-in returns exact scope, actor, version and UTC timestamps | TC-FEAT-011-01 / UAT-S02-TC-FEAT-011-01 | Database, audit and API integration pending |
| ATT-UNIT-002, 004, 012 | Duplicate/invalid transitions and stale versions are rejected | TC-FEAT-011-02 / UAT-S02-TC-FEAT-011-02 | Real concurrent transactions pending |
| ATT-UNIT-003 | Check-out event/state share the same timestamp | TC-FEAT-011-03 / UAT-S02-TC-FEAT-011-03 | Timeline integration pending |
| ATT-UNIT-005–007, 013–014, 017 | Stable retries, changed-payload rejection, chronology and receipt consistency | TC-FEAT-011-04 / UAT-S02-TC-FEAT-011-04 | Durable receipt, offline device and reconnect integration pending |
| ATT-UNIT-008–011 | Wrong organization/branch/classroom/child, expired grant and another actor are denied | XCT-02 / UAT-S02-XCT-02 | Grant decisions only; no authoritative policy or QR verification |
| ATT-UNIT-015–016, 018 | Naive time/invalid version rejection and immutable facts | Supplemental FEAT-011 invariants | Domain only |
| API boundary regression | No public attendance mutation endpoint exists before authorization | Supplemental release guard | Does not claim a working attendance API |
| TC-FEAT-011-05 | Unauthorized QR cannot change attendance | UAT-S02-TC-FEAT-011-05 | Not run; QR not implemented |

The run script appends UTC timestamps, code commit, working-tree state, dependency-lock hash, individual check outputs, executed test names and UAT mappings. Pytest parameterization expands several unit cases into separate scenarios. Physical Windows interaction, physical iPhone Safari, native app and user acceptance remain separate pending checks.

## Recorded increment result

Code under test: `a271e83cd691d95cf513c0b01e091858f66c5667`.

| Check | Result | Evidence |
| --- | --- | --- |
| 26 attendance domain scenarios plus health and fail-closed route guard | 28 passed | [Attendance run](runs/2026-10-23T20-45-31-381Z-attendance.json) |
| Ruff lint and format | Passed | Same attendance run |
| Strict mypy over source and tests | Passed; 7 files | Same attendance run |
| Locked dependency consistency | Passed | Same attendance run |
| Four plan/server regression checks | Passed | [Review unit run](runs/2026-10-23T20-45-31-382Z-unit.json) |
| Three desktop/emulated-mobile portal checks | Passed; active S02/FEAT-011 displayed | [Portal browser run](runs/2026-10-23-S02-attendance-portal.json) |
| All five source attendance acceptance cases | Not run at required integration levels | Dependencies and DEC-06 remain open |

The Starlette TestClient/AnyIO dependency combination emits one upstream deprecation warning; it is retained in the output. No warnings indicate failed attendance assertions. The initial run also recorded a pytest cache-permission warning; the repeatable runner now disables the optional cache and the final run has no cache warning. The CI job is authored but has not run remotely because this increment has not been pushed.
