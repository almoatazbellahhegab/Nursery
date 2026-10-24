# Sprint 3 application verification — 2026-10-24

This handoff covers compiled public foundation shells and the existing admissions
domain increment. No complete feature, sprint UAT or production release is accepted.

## Evidence

- Baseline tested commit: `3dde397e8162945f6d730a5993c8d1424b0fe8ec`.
- Backend: 51 pytest scenarios, Ruff lint/format, strict mypy and dependency
  consistency pass in `runs/2026-10-24T06-33-48-219Z-admissions.json`.
- Review unit checks RV-001–RV-004 pass in
  `runs/2026-10-24T06-37-15-806Z-unit.json`.
- RV-005–RV-007 prototype browser checks passed against the baseline. They do
  not verify the compiled applications.
- Existing full client quality/build evidence remains
  `runs/2026-10-24T05-42-34-047Z-clients.json`; unchanged Next.js checks were not
  repeated. The Arabic fallback change has a separate mobile check/build run.
- Initial compiled browser semantics/link checks passed in
  `runs/2026-10-24T06-34-46-394Z-compiled-browsers.json`, but visual inspection
  found Arabic missing-glyph boxes in Flutter. That run is insufficient for
  Arabic visual acceptance. The corrected build must pass a new browser run
  and screenshot inspection before integration.
- Corrected mobile format/analyzer/three widget tests/build pass in
  `runs/2026-10-24T06-36-58-935Z-clients.json`. Corrected compiled browser checks
  all pass in `runs/2026-10-24T06-38-54-697Z-compiled-browsers.json`, including
  local Arabic font delivery. Inspected `test-results/compiled-mobile-ar.png`
  and `compiled-mobile-en.png`: Arabic glyphs render, the language button is
  legible and RTL layout fits the viewport. Inspected the dashboard Arabic
  screenshot as well. These local screenshots are ignored build/test artifacts.
  DEF-S03-001 is closed for the tested emulated Chrome environment.
- A review-unit rerun initially failed because Node could not resolve an
  ancestor directory under this session's filesystem restrictions. The failed
  evidence is retained in `runs/2026-10-24T06-37-10-111Z-unit.json`. Process-local
  Node preserve-symlinks options allowed the same suite to run and pass; no
  global security or execution-policy setting changed.
- After recording the preserved S03 authorization, the content test exposed a
  stale assumption that push authorization must always be false. RV-001 now
  requires a matching scoped approval for an authorized active sprint instead.
  The failed run is retained in `runs/2026-10-24T06-40-42-059Z-unit.json`;
  all four checks pass in `runs/2026-10-24T06-40-58-486Z-unit.json`, preserving
  all original feature/task/test content and milestone exit criteria.

## Delivery status

The current font fix, verification changes and evidence remain uncommitted on
`chore/S03-application-verification`. `git add` and `git commit` failed because
the session permits only read access to `.git` (`index.lock`: Permission denied).
No merge, branch creation or push was attempted after that denial. The prior
S03 push authorization is recorded with scope/provenance in `approvals.json`,
but its final tested source commit must be filled in before any push. S04 has
readiness preparation only; S03 remains active. See
`../delivery/S04-FEAT-012-READINESS.md` for the next feature's gates and test map.

## Changes ready for review

Arabic glyphs now render in the offline Flutter web build through a bundled,
licensed fallback font. The browser harness checks local font delivery and
continues to save screenshots for inspection. The client runner can verify only
mobile changes without rebuilding the unchanged dashboard. No operational
business workflow was added or marked accepted.

## Review links

- Dashboard: <http://localhost:3000>
- Compiled Flutter web, same Wi-Fi: <http://192.168.1.4:3200>

The address was detected on this machine on 2026-10-24 and can change. Keep
`Start-Applications.cmd` running. These are local review links, not public hosting.
Successful LAN requests from this PC do not prove access from a physical phone.

## UAT checklist

- [ ] Windows 11 interactive browser: open dashboard, navigate Overview/Classrooms,
  switch English/Arabic, inspect glyphs/RTL and narrow layout. Automated headless
  Chrome coverage is separate from this human check.
- [ ] Physical iPhone Safari: on the same Wi-Fi, open the Flutter link, switch
  parent/staff, navigate Home/Timeline/Notices, switch languages and inspect
  Arabic glyphs, RTL, portrait/landscape and touch targets.
- [ ] Native iPhone: build/sign on macOS/Xcode, install and repeat the app review.
- [ ] Product source integration cases: execute when real APIs, identity,
  PostgreSQL and prerequisites exist. Current cases remain Not run.
- [ ] Record named user/specialist acceptance independently of automated results.

## Known limitations

No operational attendance/admissions HTTP routes, connected identity, persistent
PostgreSQL/RLS, durable receipt/audit/outbox adapters or hosted staging exist.
Native iPhone build/signing and physical iPhone Safari checks have not run.
Admissions field/workflow definitions and attendance DEC-06 are still open.
The upstream Starlette/AnyIO deprecation warning remains visible in backend
evidence. The temporary HTML portal is a prototype and no permission boundary.
