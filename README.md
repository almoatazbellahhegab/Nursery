# Nursery

The four original specifications are preserved in `Document`. Development has started with a traceable delivery plan and an offline review prototype. Sprint 1 is in progress and blocked on production dependencies. No product feature, native app or sprint acceptance is claimed.

## One click review on Windows 11

Double-click **Start-Sprint-Review.cmd**. Node.js 20.9 or newer must be installed. The launcher starts the server, then opens http://localhost:3100 and prints your computer's local Wi-Fi URL. Keep the terminal open; Ctrl+C stops the server.

On your iPhone, join the same Wi-Fi and open the printed `http://<computer-ip>:3100` URL in Safari. Tap Mobile preview. If Windows Firewall blocks local network access, allow Node on your private network only. No firewall rule is changed automatically. A hosted HTTPS link is a later delivery step once staging exists; no cloud deployment is configured yet.

The iPhone view is a browser prototype, not a compiled Flutter application. Native iPhone review requires a macOS/Xcode build and signing or TestFlight. Neither the native build nor physical iPhone acceptance has run here.

## Review and tests

- Active work: Sprint 3, one feature at a time. See [TODO.md](TODO.md). FEAT-030 admissions is a domain increment only; double-click **Test-Admissions.cmd** for its checks. Deferred attendance checks remain available through **Test-Attendance.cmd**. Operational web/mobile integration remains gated by unfinished prerequisites and approvals.

- The portal shows four sprints retaining all 14 original milestone work packages, 41 features, 204 itemized feature tasks, 69 technical tasks and 216 source tests with stable UAT IDs and current-sprint aliases. Duration is to be estimated; no scope is removed.
- Review both interfaces, switch English/Arabic and record results under the actual device used. Download the UAT log from the portal; local observations are appended to `review-results/uat.jsonl` and excluded from Git.
- Double-click **Test-Sprint.cmd** or run `npm test` for automated plan, server and safety checks. These are supplemental prototype tests; source product tests remain Not run.
- See [sprint tasks](docs/delivery/SPRINTS.md), [workflow](docs/delivery/WORKFLOW.md), [S01 status](docs/delivery/S01-REVIEW.md) and [test case mapping](docs/testing/CASES.md).

## Production architecture

`apps/admin-web` (Next.js/TypeScript), `apps/mobile` (Flutter), `services/api` (FastAPI), `services/worker`, `contracts/openapi`, `infra/terraform`, `tests/system` and `docs` follow the engineering standards. The dependency-free portal under `tools/review` is temporary; [ENV-001](docs/adr/ADR-0001-offline-review.md) records the exception and removal condition. It is not suitable for production or private data.

## Git delivery

Each feature gets its own branch on implementation. Enabling work uses chore/test branches. Local review integration uses `sprint/01-review`. Coherent changes are committed throughout development; **nothing is pushed until you explicitly confirm the sprint**. User UAT and specialist approvals remain separate from automated tests and from production release permission.
