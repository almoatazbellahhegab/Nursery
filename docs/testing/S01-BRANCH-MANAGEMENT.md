# FEAT-002 connected branch management

Original identifiers and source sprint S01 are retained. This is prerequisite
work resumed under the user's instruction to finish the final product; it builds
on the current locally integrated connected runtime and S04 staff workflow.
The original review prerequisites are waived for implementation, not accepted.

## Implemented scope

Next.js and Flutter administrators can create, edit, activate and deactivate
branches; maintain contact details, IANA timezone, capacity context and operating
status; assign/remove existing organization members; and browse bounded pages.
The API checks current administrator authority on every mutation. Reads use
current tenant and branch RLS. Branch assignment changes affect existing sessions
immediately. Classroom, employee and child assignments remain distinct controls.
Creates/edits/assignments use durable operation receipts, immutable minimal audit
and optimistic branch versions. Inactive branches retain authorized history and
reject new staff transitions. Staff report boundaries use the configured branch
timezone, including daylight-saving transitions.

Implementation defaults: branch capacity is planning context, not an enrollment
limit; active status controls new operational records. Operating status describes
planned/open/temporarily closed operations independently. No branch or historical
staff event is deleted by deactivation. Contact fields are optional; name and
valid IANA timezone are required. Membership assignment does not create accounts.
No commercial tier quantities or branch prices are invented.

## Verification and UAT

Full backend: 248 scenarios and coding checks pass in
`runs/2026-10-24T14-49-27-829Z-runtime.json`, including 15 branch scenarios.
Next.js types/lint/format/build and Flutter build pass in the otherwise failed
`runs/2026-10-24T14-49-38-820Z-clients.json` (test-only lint issue corrected).
Flutter format/analyzer/11 tests pass in `runs/2026-10-24T14-53-28-922Z-clients.json`.
Four source/review integrity checks pass in `runs/2026-10-24T14-54-32-964Z-unit.json`.
The source cases TC-FEAT-002-01/02/03 have matching real API integration passes
recorded in the execution overlay. No automated result accepts UAT.
Final Next.js/Flutter format, lint/analysis, types, 12 widget tests and both builds
pass in `runs/2026-10-24T15-04-29-041Z-clients.json`. All five connected branch
browser groups, including Arabic controls in both clients, pass in
`runs/2026-10-24T15-09-58-298Z-branch-browsers.json`. Affected staff browser
regressions pass all five groups in `runs/2026-10-24T15-00-54-786Z-connected-browsers.json`.
English/Arabic desktop/mobile screenshots inspected; earlier failed runs retained.

- [ ] Windows 11 human Chrome/Edge: create/edit/deactivate, branch/member pagination,
      version conflict, assignment removal, retained history and timezone report.
- [ ] Physical iPhone Safari: keyboard, dialogs, scrolling, RTL, branch settings.
- [ ] Native iPhone: compile/sign/install and repeat connected flows.
- [ ] Arabic content, screen-reader and keyboard review by a human.
- [ ] User acceptance explicitly recorded.

Known limits: generated contract clients, provider identity/MFA/account lifecycle,
other original product features and production operations remain unfinished.
Profile branch picker is bounded to 100 entries while branch administration has
explicit pagination. Deactivating a branch with an open staff session blocks its
next transition; temporarily reactivate it to close that session. Physical/native
checks are not inferred from emulated Chrome.
