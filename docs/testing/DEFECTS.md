# Sprint 1 defect log

## Connected runtime fixes — 2026-10-24

| ID | Finding | Resolution and verification |
| --- | --- | --- |
| DEF-S04-001 | API correction responses inherited the database host's local timezone while first-write responses used UTC | Every app connection now sets UTC; real correction/source integration and browser round-trip pass. |
| DEF-S04-002 | Failed-test fixture representation printed a generated local database credential | Redact Database.url from representation, rotate the local application credential, and add representation regression coverage. The old credential is invalid; no credential value was written to tracked evidence. |
| DEF-S04-003 | Flutter browser automation filled accessibility mirror inputs without reliably updating framework controllers | Focus fields, await framework frames and type at an ordinary keyboard pace. Connected cross-client check-in/out passes; retain earlier failed runs. |
| DEF-S04-004 | Nested select labels were not found reliably by exact accessible names | Add explicit localized ARIA labels to Branch and Record; manager correction/report browser journey passes. |

These closures cover the tested environment, not human/physical Safari/native
acceptance. Credentials/DSNs and unsanitized browser request bodies are excluded
from tracked evidence; browser diagnostics redact generated account passwords.

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


## DEF-S01-005 ? Branch settings select accessible names

Connected Chrome checks found the nested member selector's computed name included
option text. Added explicit localized ARIA names for member and operating-status
selectors. Backend creation was correct; assignment UI automation exposed the
label defect. Rebuild/connected verification is pending the current run.

## DEF-S01-006 ? Flutter branch-card browser assertion

The branch create API returned 200 and persisted the exact fictional name.
Flutter exposes the card name/status through an accessibility group, rather than
a text node. The test now selects the named group and scrolls it into view.
This is a harness correction, not a failed database create. Failed run evidence
is retained; no product pass inferred before the corrected browser run.

## DEF-S01-007 - UTF-8 labels changed by a shell pipe

An additional Flutter Arabic branch check exposed question marks in newly inserted
Arabic strings. A PowerShell text pipe used a legacy encoding. Restored the labels
through the Unicode-safe patch tool, added the administrator Arabic entry widget
regression and explicit Arabic select-name browser assertions. The complete client
checks and both builds pass in `2026-10-24T15-04-29-041Z-clients.json` (12 Flutter
tests). Use Unicode-safe patches for localized source; do not rely on Python's
UTF-8 mode to change PowerShell's outgoing pipe encoding.

## DEF-S01-008 - Commit must precede an HTTP success

Request-scope dependency cleanup can run after response transmission. Added a
shared route boundary that commits prepared mutations before returning a response;
deferred commit failure now returns failure and rolls back presence/event/receipt/
audit. A real deferred PostgreSQL constraint-trigger regression passes in the
259-case run `2026-10-24T15-58-32-780Z-runtime.json`. MFA session revocation also
requires user/session lock ordering: activity updates occur after business locks,
and MFA rechecks session validity after acquiring the user lock. Recovery races,
immediate audit failures and other identity/staff regressions pass in that run.
