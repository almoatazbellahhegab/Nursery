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
