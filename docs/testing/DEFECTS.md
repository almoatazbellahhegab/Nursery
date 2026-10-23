# Sprint 1 defect log

| ID | Finding | Resolution | Regression and status |
| --- | --- | --- | --- |
| DEF-S01-001 | Browser harness attempted an inline stylesheet blocked by the portal CSP | Keep CSP; use half-width responsive reflow check. Manual browser 200% zoom remains pending. | RV-005 rerun passes; initial failed run retained. Closed harness issue. |
| DEF-S01-002 | Windows launchers used a wildcard test path and opened a browser before server readiness | Use explicit Node test path; open browser from the server listening callback only when --open is supplied. | Unit/server suite rerun and launcher content inspected. Interactive double-click UAT pending. |

ENV-001 remains open: registry DNS resolution failed after escalation; Flutter SDK and application dependency builds unavailable. It blocks production stack verification, not local preview operation.
