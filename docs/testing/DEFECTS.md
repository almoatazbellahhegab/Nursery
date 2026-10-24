# Sprint 1 defect log

| ID | Finding | Resolution | Regression and status |
| --- | --- | --- | --- |
| DEF-S01-001 | Browser harness attempted an inline stylesheet blocked by the portal CSP | Keep CSP; use half-width responsive reflow check. Manual browser 200% zoom remains pending. | RV-005 rerun passes; initial failed run retained. Closed harness issue. |
| DEF-S01-002 | Windows launchers used a wildcard test path and opened a browser before server readiness | Use explicit Node test path; open browser from the server listening callback only when --open is supplied. | Unit/server suite rerun and launcher content inspected. Interactive double-click UAT pending. |

ENV-001 remains open: registry DNS resolution failed after escalation; Flutter SDK and application dependency builds unavailable. It blocks production stack verification, not local preview operation.

## 2026-10-24 application verification update

The earlier ENV-001 dependency/tooling blocker is resolved for local builds:
Next.js and Flutter web compile and quality checks pass. Production deployment,
operational integrations and native iPhone signing remain unavailable.

DEF-S03-001: Visual inspection found Arabic missing-glyph boxes in the compiled
Flutter web shell despite passing semantic text checks. Bundle the unchanged
OFL-licensed Noto Naskh Arabic font from the pinned Flutter SDK as a local
fallback. Closure requires mobile build/quality checks, browser font delivery
and screenshot inspection; physical Arabic UAT remains pending.

Closed for emulated Chrome: mobile quality/build run
`2026-10-24T06-36-58-935Z-clients.json` and browser run
`2026-10-24T06-38-54-697Z-compiled-browsers.json` pass; Arabic/English screenshots
were inspected with readable glyphs. Physical iPhone Arabic UAT remains pending.
