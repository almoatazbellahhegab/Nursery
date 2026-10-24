# Session checkpoint and resume instructions

## Start here

The user's latest instruction was to commit the current work so it can continue after reopening the session. Stop after saving this checkpoint. Current branch: `chore/S03-application-verification`. The checkpoint commit is the latest local commit on this branch; inspect `git log -1` for its hash.

The outstanding task is: **push Sprint 3 after application testing, start Sprint 4, and provide one dashboard link and one mobile test link**. This task is not finished. Sprint 3 has not been pushed, Sprint 4 has not been started, and the final live client browser/link checks are pending.

## User preferences and authorization

- Show work as itemized updates and print Markdown TODO progress in the terminal while working (`Get-Content TODO.md -Encoding UTF8`).
- Work on one feature at a time and keep separate feature branches. Preserve the four-sprint plan and every original feature/task/test identifier.
- User authorized pushing Sprint 3 after testing and starting Sprint 4. Record the exact approval and tested commit in `docs/delivery/approvals.json` before that push.
- User also said to proceed with routine implementation/testing and answer yes to subsequent routine permission questions. Host sandbox/approval requirements still apply. No global security or execution-policy settings were changed.
- A pasted `codex --sandbox workspace-write --ask-for-approval never` command did not change this active session's permissions. Do not launch another coding agent in this checkout merely to apply those options.
- S01, S02 and S03 are not accepted as complete operational releases. Advancing sprints defers open work; it does not pass UAT or resolve specialist policy gates.

## Committed history before this checkpoint

- `sprint/01-review`: `bf37d4e`, already pushed.
- `sprint/02-review`: `775b1ff`, already pushed with planning and attendance feature branches.
- `sprint/03-review`: `fb97301`, **local only**. Contains FEAT-030 admissions domain increment and its evidence.
- `feat/FEAT-030-admissions-pipeline`: `8f0fd3b`, **local only**; retain/push alongside S03 when verification completes.
- Current verification branch was created from `fb97301`. Its application setup, tooling, locks, generated runners and checkpoint are saved in the current commit.

## What now works

### Backend/domain

`services/api/.venv` is installed locally; `requirements-dev.lock` pins its resolved dependencies. The managed bundled Python was not modified. Latest pre-handoff run: **51 passing pytest scenarios** (22 admissions, 26 attendance, three health/fail-closed route checks), Ruff lint/format, strict mypy and dependency consistency.

Evidence: `docs/testing/runs/2026-10-23T22-08-45-662Z-admissions.json`. A Starlette/AnyIO upstream deprecation warning is retained. There are still no operational attendance/admissions HTTP routes, identity integration, PostgreSQL, RLS or persistent audit/receipt/outbox adapters.

### Actual Next.js administration shell

- Node **24.19.0** is available at `C:/Users/localadmin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`.
- Global Node is **20.11.1**; do not use it for the web toolchain. Root review scripts still work on the older runtime.
- npm **12.2.1** is installed locally in `.tools/npm-cli/node_modules/npm/bin/npm-cli.js`; no global npm upgrade was performed.
- `apps/admin-web/package-lock.json` was regenerated with npm 12 in an empty tooling directory and **successfully reproduced with npm ci**.
- The initial interrupted install had an invalid Windows native SWC binary and incomplete optional-package lock. The verified build uses Next **16.4.2**, Webpack (`next build --webpack`) and the matching explicit `@next/swc-wasm-nodejs` dependency.
- TypeScript, ESLint, Prettier, npm audit (**zero reported vulnerabilities**) and the production build all pass. The framework-generated `next-env.d.ts` and tsconfig updates are retained.

### Actual Flutter mobile shell

- SDK: **Flutter 3.47.8 / Dart 3.13.7**, checked out in ignored `.tools/flutter`; immutable tag `3.47.8` was verified at HEAD.
- Project pub cache: `.tools/pub-cache`; `apps/mobile/pubspec.lock` records resolved dependencies.
- Web/iOS platform runner files and localization Dart output were generated around the existing source. Generated native signing configuration is not provisioned; no secrets were added.
- Dart format, Flutter analyzer, **three widget tests** (parent/staff experience, Arabic direction, timeline navigation) and the **Flutter web production build** all pass.
- Build command: `flutter build web --no-pub --no-web-resources-cdn`. Web engine resources are hosted locally. Adding pinned `cupertino_icons: 1.0.8` resolved the missing iOS icon-font build warning.
- Native iPhone compilation and physical iPhone/Safari UAT have **not** run. macOS/Xcode/signing remain required for native installation.

### Consolidated client evidence

`docs/testing/runs/2026-10-24T05-42-34-047Z-clients.json`: all **nine** client check/build steps pass. The record correctly points at parent commit `fb97301` and lists the then-uncommitted working tree; this checkpoint now preserves those files. This evidence is for real compiled public foundation shells, not complete business workflows.

## Tools and commands ready for continuation

- `Test-Applications.cmd` / `node tools/check-clients.mjs`: web types/lint/format/audit/build and Flutter format/analyze/widget/web build; appends timestamped evidence. Stop running app servers before rebuilding.
- `Start-Applications.cmd` / `node tools/start-applications.mjs`: runs compiled Next.js on **3000** and serves compiled Flutter web on **3200**, both bound for same-network review. Chooses a supported Node runtime through `tools/client-runtime.mjs`.
- `node tools/check-client-browsers.mjs`: **authored but not yet executed**. Tests the actual built clients, desktop/mobile layouts, language switching, LAN link availability and static-file boundaries. It tries enabling Flutter's accessibility placeholder to inspect semantic controls. Debug this test if the current Flutter DOM/semantics differs; do not claim a pass without running it.
- `Start-Sprint-Review.cmd` / port **3100**: older HTML prototype/delivery portal, separate from the compiled applications. Existing `tools/browser-checks.mjs` covers those prototypes and must not be presented as real-client testing.
- `Test-Admissions.cmd` / `node tools/run-admissions-checks.mjs`: domain/API-boundary regression evidence.
- `Test-Attendance.cmd`: preserved domain regression entry point.
- `docs/runbooks/application-review.md` explains compiled-app review; ADR-0003 records the toolchain resolution.

The command to start the real app servers was interrupted during a tool call. **Process state is unknown**: they might be running or might not have started. Check existing listeners/HTTP responses before starting duplicate servers. Background sessions might not survive reopening.

The last observed physical Wi-Fi IP was **192.168.1.3**, different from the earlier 192.168.1.2. Re-read it using Node's `os.networkInterfaces()`. Intended URLs, not yet finally browser-verified, are `http://localhost:3000` for the dashboard and `http://<current-Wi-Fi-IP>:3200` for mobile Safari. They are local-network URLs, not public hosting. Both devices must share Wi-Fi; physical inbound firewall/device access is not proven by a localhost test.

## Next actions in order

1. Read `AGENTS.md`, this checkpoint, `TODO.md`, and current git status. Do not repeat downloads or successful builds without a change/failure that justifies it; ignored tooling/build artifacts remain locally available.
2. Check whether the interrupted server start and review-regression commands executed. Ensure ports 3000/3200 are serving the existing builds; start through `tools/start-applications.mjs` if needed.
3. Run `tools/check-client-browsers.mjs`, inspect its screenshots/ARIA diagnostics under `test-results`, and fix any real issue or test harness incompatibility. Record browser testing accurately as Windows Chrome plus mobile emulation, not a physical iPhone/native pass.
4. Complete/re-record the four review unit checks and any needed HTML portal regression checks. Add a concise application test summary and actual verified review URLs. Keep all source product acceptance cases at their true status.
5. Merge `chore/S03-application-verification` locally into `sprint/03-review` after verification, retaining branches. Record the user's explicit S03 push instruction and scope, then push `sprint/03-review`, `feat/FEAT-030-admissions-pipeline`, and the verification branch as appropriate, without force.
6. Start `sprint/04-review` from that integrated state. S04 contains FEAT-012 staff attendance, FEAT-025 medication, FEAT-033 transport, FEAT-038 KPIs, FEAT-039 community and FEAT-040 commerce. Begin with **FEAT-012 readiness** on its own branch if dependencies are still incomplete. FEAT-010 and approved correction/access rules remain prerequisites. Medical, transport, community, finance/privacy and other specialist gates are not waived.
7. Archive the current TODO as S03 carryover, update `execution.json` to one active S04 feature, regenerate the plan without altering scope, print Markdown progress, and commit new S04 work locally. Do not report it as a completed sprint.
8. Return one dashboard link and one compiled Flutter web link, state what was tested, and distinguish unimplemented operational workflows and unperformed native/physical-device acceptance.

## Preserve and exclude

- Original specification files in `Document` and the archived 14-sprint baseline are unchanged.
- A **pre-existing untracked** file `docs/testing/runs/2026-10-23T20-50-36-104Z-attendance.json` was present before the verification work. It is intentionally left untouched and excluded from this checkpoint commit.
- `.tools`, `.venv`, `node_modules`, `.next`, Flutter build outputs, caches and screenshots are ignored and must not be accidentally committed. Locally cached dependencies/builds do not accompany a fresh clone; READMEs document reproduction.
- Do not modify global Codex/security/execution policies or stop unrelated processes to resume this task.
