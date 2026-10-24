# Client demo implementation and verification

User request: populate the application with complete demo data and clear use
cases that demonstrate business value to potential clients.

Latest direct-view update: `/?view=parent` and `/?view=teacher` open the
corresponding mobile experience; Reset retains the linked role. The displayed
Staff label is now Teacher. Mobile checks/build and five widget tests pass in
`runs/2026-10-24T07-24-22-477Z-clients.json`; all nine browser groups pass in
`runs/2026-10-24T07-26-51-637Z-demo-browsers.json`. Both view screenshots were
inspected. The user's reported phone connection failure remains unconfirmed:
requests from this PC succeed, but no physical iPhone result is claimed.

The result is a client presentation increment on the actual Next.js and Flutter
web apps. Both start from `demo/seed.json`: two branches, four classrooms, eight
educators, 24 children/families, 24 invoices, six leads, 48 daily events and four
notices. There are no real child records, usable contact addresses or secrets.
The presentation script is in `docs/runbooks/client-demo.md`.

## What changed

- Web: branch overview, derived attendance/capacity/balance totals, educator and
  classroom rosters, searchable attendance, per-child timeline, local care
  updates, paid/unpaid invoices, reminder previews and sample visit scheduling.
- Four guided stories connect each interaction to a nursery business need.
- Mobile: branch/child exploration, parent summary, family invoice, timeline,
  notices, staff roster and local staff-to-parent care update simulation.
- Reset and reload restore a deterministic baseline. Both clients share a seed,
  but separate sessions/devices do not synchronize their local changes.
- English/Arabic text, RTL layout, isolated numeric ratios and bundled Arabic font.
- Fixture generator checks references, associations, invoice arithmetic and UTF-8
  Arabic labels, and verifies both generated client copies match the source.

## Verification scope

Final evidence (all selected checks pass):

| Check | Evidence |
| --- | --- |
| Web types, lint, format, production build | [Web run](runs/2026-10-24T07-09-58-940Z-clients.json) |
| Mobile format, analyzer, four widget scenarios, production web build | [Mobile run](runs/2026-10-24T07-10-09-671Z-clients.json) |
| Eight demo browser scenario groups; no page errors | [Browser run](runs/2026-10-24T07-12-22-845Z-demo-browsers.json) |
| Four review/source integrity checks | [Review run](runs/2026-10-24T07-12-14-020Z-unit.json) |

`node tools/generate-demo.mjs --check` also passes. Final English/Arabic desktop,
320px web and 390px Flutter screenshots were inspected under ignored
`test-results/demo-*.png`. Numeric ratios remain in the intended order, Arabic
glyphs render, and the old-language snackbar is cleared on language change.

Review links verified from this machine: <http://localhost:3000> and
<http://192.168.1.4:3200>. Both are local review addresses, not public hosting;
the mobile address requires the same Wi-Fi and may change with the network.

- Web TypeScript, ESLint, Prettier and optimized production build.
- Flutter format, analyzer, four meaningful widget scenarios and web build.
- Browser checks for baseline totals; attendance-to-timeline consistency; care
  updates; invoice filters and reminder amount; admissions visits; branch
  filtering; reset across mutations; Arabic layouts at 1440/390/320px; mobile
  staff-to-parent update/reset; LAN responses and static-file boundaries.
- Screenshot inspection for English/Arabic desktop and mobile presentation.
- Review-source integrity suite retains all original scope/identifiers.
- Dependency manifests did not change for this demo. The dependency audit was
  not repeated; the earlier audit evidence is retained.

Initial client/test runs are retained. The first fixture-generation path lost
Arabic through a Windows stdin encoding conversion; the canonical JSON was
corrected, a UTF-8 Arabic validation guard was added and both clients regenerated.
Widget checks also exposed lazy-list scrolling assumptions; the test now brings
its target into the visible viewport. Browser selectors were aligned with the
actual composed text and Flutter menu semantics, and now wait for its semantic
transition before checking an update. These failures are not reported as passes.
Visual inspection additionally identified RTL ratio order and stale-language
snackbar feedback, both corrected before final verification.

## Acceptance and known limitations

The human Windows 11, physical iPhone Safari, native iPhone and named Arabic/UAT
checks remain pending in the presentation runbook. Automated headless Chrome
and mobile emulation do not accept those environments.

The four TC-FEAT-041 source cases remain Not run at their required authenticated
API integration level. Branch/role selectors are presentation filters. No live
payments, notifications, enrollment, auth, PostgreSQL/RLS or cross-device sync
are implemented. No specialist or policy gate is waived.

The session still cannot write `.git`. No branch, commit, merge or push was made.
The requested branch when Git becomes writable is
`feat/FEAT-041-demo-scenarios`. Separate the demo from the older S03 verification
scope before recording any push approval. This request does not itself authorize
pushing the expanded sprint scope.
