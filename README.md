# Nursery

## Connected workspace

`Start-Applications.cmd` now opens the connected runtime: Next.js on port 3300,
Flutter web on 3400 and FastAPI on 8000, backed by project-owned PostgreSQL.
Staff attendance, history, manager corrections and daily reports share real
persistent state across the clients. Accounts and credentials are generated in
ignored local files; see [setup and verification](docs/runbooks/connected-runtime.md).

The original fictional presentation remains available at web `/demo` and mobile
`?demo=true` (including existing parent/teacher demo links). The final product is
still being implemented; this connected increment does not complete all 41
features or constitute deployment, specialist signoff or physical/native UAT.

## Client demonstration

Ready-to-present dashboard: **http://localhost:3300/demo**.
Mobile parent: **http://192.168.8.154:3400/?view=parent**.
Mobile educator: **http://192.168.8.154:3400/?view=teacher**.
Presentation links need no login; the phone must share the PC's Wi-Fi.
The current IP can change; the launcher prints its current value.

The actual web and mobile apps now include a fictional Little Garden nursery
with two branches, 24 children/families, educator rosters, daily care, attendance,
invoices and admissions inquiries. Open `Start-Applications.cmd`, then open the
dashboard `/demo` route for four guided stories. Reset demo restores starting data.

See the [eight-minute client presentation script](docs/runbooks/client-demo.md)
for the value stories, exact steps and expected outcomes. Demo actions are local
simulations; they do not send messages, process payments or synchronize devices.
The [fixture guide](demo/README.md) documents the shared synthetic dataset.

The four original specifications are preserved in `Document`. The cumulative
Sprint 4 assembly includes connected staff attendance, branch administration and
application MFA. Earlier-sprint account/provider and onboarding prerequisites are
being completed. The complete product, native iPhone delivery and sprint UAT are
not accepted or claimed complete.

## One click review on Windows 11

For the compiled connected Next.js and Flutter web apps, double-click
**Start-Applications.cmd**. It prints dashboard port 3300 and same-Wi-Fi mobile
port 3400. The root routes require sign-in; `/demo` and `?view=parent` or
`?view=teacher` open the separate fictional presentation. **Test-Applications.cmd**
records client checks; stop owned app servers before rebuilding. Flutter web
review does not accept a native iPhone app.

Double-click **Start-Sprint-Review.cmd**. Node.js 20.9 or newer must be installed. The launcher starts the server, then opens http://localhost:3100 and prints your computer's local Wi-Fi URL. Keep the terminal open; Ctrl+C stops the server.

On your iPhone, join the same Wi-Fi and open the printed `http://<computer-ip>:3100` URL in Safari. Tap Mobile preview. If Windows Firewall blocks local network access, allow Node on your private network only. No firewall rule is changed automatically. A hosted HTTPS link is a later delivery step once staging exists; no cloud deployment is configured yet.

The iPhone view is a browser prototype, not a compiled Flutter application. Native iPhone review requires a macOS/Xcode build and signing or TestFlight. Neither the native build nor physical iPhone acceptance has run here.

## Review and tests

- Active work: FEAT-003 identity prerequisites, one feature at a time, with prior
  connected increments retained in the local cumulative assembly. See [TODO.md](TODO.md).
  The user waived reviews for implementation/testing. Earlier admissions/child
  attendance domain groundwork and fictional presentation do not establish
  connected completion of those modules.

- The portal shows four sprints retaining all 14 original milestone work packages, 41 features, 204 itemized feature tasks, 69 technical tasks and 216 source tests with stable UAT IDs and current-sprint aliases. Duration is to be estimated; no scope is removed.
- Review both interfaces, switch English/Arabic and record results under the actual device used. Download the UAT log from the portal; local observations are appended to `review-results/uat.jsonl` and excluded from Git.
- Double-click **Test-Sprint.cmd** or run `npm test` for automated plan, server and safety checks. These are supplemental prototype tests; source product tests remain Not run.
- See [sprint tasks](docs/delivery/SPRINTS.md), [workflow](docs/delivery/WORKFLOW.md), [S01 status](docs/delivery/S01-REVIEW.md) and [test case mapping](docs/testing/CASES.md).

## Production architecture

`apps/admin-web` (Next.js/TypeScript), `apps/mobile` (Flutter), `services/api` (FastAPI), `services/worker`, `contracts/openapi`, `infra/terraform`, `tests/system` and `docs` follow the engineering standards. The dependency-free portal under `tools/review` is temporary; [ENV-001](docs/adr/ADR-0001-offline-review.md) records the exception and removal condition. It is not suitable for production or private data.

## Git delivery

Each feature gets its own branch on implementation. Enabling work uses chore/test branches. Local review integration uses `sprint/01-review`. Coherent changes are committed throughout development; **nothing is pushed until you explicitly confirm the sprint**. User UAT and specialist approvals remain separate from automated tests and from production release permission.
