# Sprint 1 test execution log

Code under test: `e424992b0c4be74cb2ca01cd6170134ca9a8c991`. Automated checks ran on Windows with Node 20.11.1 and headless desktop Chrome. No physical iPhone, Safari or native app checks were performed.

| Case | Result | Acceptance link | Evidence |
| --- | --- | --- | --- |
| RV-001 baseline integrity and traceability | Pass | UAT-S01-04 | [Unit run](runs/2026-10-23T19-09-50-483Z-unit.json) |
| RV-002 translation key completeness | Pass | UAT-S01-03 | [Unit run](runs/2026-10-23T19-09-50-483Z-unit.json) |
| RV-003 review-result validation | Pass | UAT-S01-05, UAT-S01-06 | [Unit run](runs/2026-10-23T19-09-50-483Z-unit.json) |
| RV-004 HTTP boundary and persistence | Pass | UAT-S01-05 | [Unit run](runs/2026-10-23T19-09-50-483Z-unit.json) |
| RV-005 desktop navigation and Arabic layout | Pass | UAT-S01-01, UAT-S01-03 | [Browser run](runs/2026-10-23-browser-final.json) |
| RV-006 emulated mobile navigation and layout | Pass | UAT-S01-02, UAT-S01-03 | [Browser run](runs/2026-10-23-browser-final.json) |
| RV-007 UAT mapping, safe rendering and reload | Pass | UAT-S01-04, UAT-S01-05 | [Browser run](runs/2026-10-23-browser-final.json) |
| All 216 source product cases | Not run | Each case's linked UAT ID in plan.json | Production runtime unavailable |
| Next.js type/lint/build | Blocked | Actual web shell acceptance pending | ENV-001 |
| Flutter format/analyze/widget/build | Blocked | Actual mobile shell acceptance pending | ENV-001; two widget scenarios authored but not executed |
| FastAPI quality and health test | Blocked | Actual API foundation pending | Application dependencies absent |
| Windows interactive and physical iPhone Safari UAT | Pending | UAT-S01-01 through UAT-S01-05 | User review required |
| Native iPhone application | Blocked | UAT-S01-06 | macOS/Xcode/signing and Flutter build unavailable |

The [initial failed browser run](runs/2026-10-23-browser-initial.json) is retained. DEF-S01-001 documents the corrected test harness issue. Automated observations use an isolated test evidence directory and do not populate the user's review log. Human acceptance and sprint push approval remain pending.

## Four sprint plan revision verification

Code under test: `a575a4bdb12ed52d8698ab504a1033a6147f325c`. All seven supplemental checks pass after consolidation. RV-001 additionally verifies exact content preservation against the archived 14-sprint plan, four sprint assignments, all 14 retained milestone exit criteria, unchanged decisions/controls and stable UAT identifiers. RV-007 verifies the four-group portal and both original and current-sprint UAT links.

- [Unit/content preservation run](runs/2026-10-23T20-22-55-797Z-unit.json): RV-001 through RV-004 pass.
- [Browser run](runs/2026-10-23-four-sprint-browser.json): RV-005 through RV-007 pass. Its only working-tree change was the generated unit evidence record, not application code.

Product test execution, physical-device acceptance and native builds retain their previous Not run, Pending or Blocked states. This planning revision changes no feature acceptance or historical test outcome.

## Sprint 2 FEAT-011 domain increment

Sprint 2 is active at the user's request, without accepting unfinished Sprint 1. FEAT-011 is the only active feature. [Attendance test log](S02-ATTENDANCE.md) records 28 passing pytest scenarios, Ruff lint/format, strict mypy and dependency-consistency checks against `a271e83`. The four review unit checks and three desktop/emulated-mobile browser checks also pass. All five source attendance API/mobile acceptance cases remain Not run; physical-device/native UAT and durable authorization/database/QR/offline integrations are not claimed complete.

## Sprint 3 FEAT-030 domain increment

At the user's instruction, existing commits were pushed through `775b1ff`, S02/FEAT-011 was deferred without acceptance, and S03/FEAT-030 became the sole active feature. [Admissions test log](S03-ADMISSIONS.md) records 51 passing pytest scenarios, coding/dependency checks, four review unit checks and three preview browser checks against `eb29e67`. Source admissions cases remain Not run at their required API/component/E2E levels. New S03 commits stay local pending another push instruction.
