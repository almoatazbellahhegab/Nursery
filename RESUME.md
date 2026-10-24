# Session checkpoint and resume instructions

## Latest request: commit pending changes (2026-10-24)

The user explicitly requested local Git commits. Git index writes were approved
through the host escalation flow. The earlier read-only Git blocker below is
historical for this handoff. Save verification, FEAT-041 demo and FEAT-030 retry
work in separate commits/retained branches and integrate locally into
`sprint/03-review`. Inspect `git log` for the resulting commit identifiers.
Do not push: this request grants no expanded sprint push approval. Preserve the
unrelated untracked attendance run `2026-10-23T20-50-36-104Z-attendance.json`.
Sprint 3 remains incomplete, policy gates remain open, and physical/native and
human UAT remain pending. The prior test evidence and next decisions below
remain the verification scope; committing does not accept them as complete.

## Current priority — continue Sprint 3 to actual completion

Latest user instruction: `continue on sprint 3 and let me know when its done`.
Keep S03/FEAT-030 active. Do not advance to S04 under the older resume ordering.
Sprint 3 is still incomplete; do not report it done or treat this instruction as
specialist policy approval, UAT acceptance or expanded push confirmation.

### New tested increment

- Admissions stage-change receipts support exact historical retry responses
  with `replayed=True`, preserving the original history/event rather than
  creating a duplicate or writing over a newer snapshot.
- Scope/current grant expiry precede receipt checks. Changed command/operation,
  other actor/resource, inconsistent stored parts and contradictory current
  state fail closed. History validates identifiers, versions, UTC and changes.
- All 73 backend scenarios pass: 44 admissions, 26 attendance and three
  health/fail-closed route guards. Ruff lint/format, strict mypy and dependency
  consistency pass. Evidence:
  `docs/testing/runs/2026-10-24T07-37-19-462Z-admissions.json`.
- Four review/source-integrity checks pass:
  `docs/testing/runs/2026-10-24T07-37-23-887Z-unit.json`.
- The first new retry run is retained: 71 tests passed, but strict typing found
  a test-fixture dynamic replacement issue. It was corrected and two additional
  contradictory-state scenarios added before the final passing run.
- No HTTP route, production database model, business policy defaults or actual
  authentication/authorization was added. Pure receipts do not prove durable
  idempotency, actual concurrent writes or atomic audit persistence.

### Completion blockers and next decisions

Read `docs/delivery/S03-DECISION-PACK.md`. It contains concrete **unapproved**
admissions field/workflow/loss/conversion/report proposals, all 12 S03 feature
dependencies, original GATE-01–07 owners/scope and completion evidence checklist.
A question was sent requesting the approved policy source vs a proposed packet;
no answer was received before preparing the packet. Do not install its draft
decisions as approved configuration. AGENTS.md requires affected policy gates
to close before implementation. Identity/branch/permission/PostgreSQL prerequisites
also remain unfinished, as do physical iPhone Safari/native/human Windows UAT.

The `.git` restriction remains: all current source/docs/demo/retry work is
uncommitted on `chore/S03-application-verification`, HEAD `3dde397`. No new branch,
commit, merge or push occurred, and no filesystem/security boundary was bypassed.
Separate prior S03 verification, later demo and this admissions increment into
appropriate retained feature/enabling branches once Git writes are authorized.
Do not push an expanded scope under the earlier narrowly recorded approval.

The existing compiled demos are unchanged by the backend retry increment and
remain the current web/mobile review result. Read the next section for their
direct parent/teacher URLs and current owned launcher. Do not claim the user's
unreproduced phone-network issue was resolved. Preserve all prior work and the
pre-existing untracked attendance run.

---

## Latest follow-up — direct Parent and Teacher links

The user reported the mobile link did not work and requested parent/teacher
views. Both localhost and `192.168.1.4` responded on ports 3000/3200 from the PC
before changes; the failure on the user's device has not been reproduced.
Questions about device/network and the visible error were sent; no answer yet.
Do not claim physical iPhone connectivity is fixed or proven.

Added direct Flutter entry links `/?view=parent` and `/?view=teacher`, renamed
the displayed Staff role to Teacher in English/Arabic, and made Reset retain the
link's initial role. Both links are printed by `Start-Applications.cmd`.
Mobile format/analyzer/five widget tests/build pass in
`docs/testing/runs/2026-10-24T07-24-22-477Z-clients.json`. All nine browser groups,
including direct role links and reset, pass in
`docs/testing/runs/2026-10-24T07-26-51-637Z-demo-browsers.json`. Inspected the two
direct-view screenshots under ignored test-results. Source changes remain
uncommitted under the recorded read-only `.git` restriction.

Current owned launcher session: `25646`; older launcher `96351` was stopped
before rebuilding. Parent on this PC: `http://localhost:3200/?view=parent`;
Teacher: `http://localhost:3200/?view=teacher`. On same Wi-Fi use
`http://192.168.1.4:3200/?view=parent` and `...?view=teacher`. These are private
network links, not public hosting. Do not use localhost on a physical phone.
Computer-use browser inventory was empty, so user-visible tabs could not be
opened; automated Chrome app tests and screenshots verified the actual pages.

---

## Latest request — populated client demo (supersedes older client status below)

The user asked: `please add complete demo data to the application with a clear
use cases for the demo of actual business value to the potential clients`.
The actual Next.js and Flutter web apps now contain the fictional Little Garden
client presentation demo, replacing their empty foundation screens.

### Delivered in the working tree

- Shared canonical fixture `demo/seed.json`: two branches, four classrooms,
  eight educators, 24 children/families, 24 invoices, six leads, 48 daily-care
  events and four notices; English/Arabic labels and a fixed 24 October snapshot.
- `tools/generate-demo.mjs` validates references, branch/classroom relationships,
  money and UTF-8 labels and generates both clients' identical starting data.
- Web: overview, classrooms, searchable attendance, timeline, care update,
  invoice filters, reminder preview, sample visit scheduling and reset. Four
  guided business stories select Maadi so named examples are repeatable.
- Flutter: parent/staff, branch/child exploration, attendance roster, care update,
  parent timeline, invoice summary, notices and reset. Staff/parent views share
  local state within one app session. Separate web/mobile sessions do not sync.
- Read `docs/runbooks/client-demo.md` for the eight-minute presentation script,
  business questions, expected results and separate device UAT checklist.
- Read `docs/testing/CLIENT-DEMO.md` for evidence, defects corrected and limits.

### Final verification

- Web types/lint/format/build: `2026-10-24T07-09-58-940Z-clients.json`.
- Mobile format/analyzer/four widget tests/build:
  `2026-10-24T07-10-09-671Z-clients.json`.
- All eight demo browser groups pass:
  `2026-10-24T07-12-22-845Z-demo-browsers.json`.
- All four source/review integrity checks pass:
  `2026-10-24T07-12-14-020Z-unit.json`.
- Fixture parity/reference/UTF-8 check passes. Inspected final desktop and mobile
  English/Arabic screenshots, including corrected RTL ratios and snackbar
  locale. Failed intermediate runs are retained with explanations in the report.
- Dependencies were unchanged for this demo; prior audit retained without rerun.
- Human Windows, physical iPhone Safari, native iPhone and Arabic UAT remain
  pending. All four FEAT-041 authenticated API acceptance cases remain Not run.

### Current runtime and Git state

Dashboard: `http://localhost:3000`; same-Wi-Fi Flutter web:
`http://192.168.1.4:3200`. Owned launcher session `96351` is running, but check
listeners after reopening because process survival is not guaranteed. The prior
owned launcher was stopped before rebuilding. The current CLI labels this as a
fictional client demo. No operational API, auth, database or messaging was added.

All changes are **uncommitted** on `chore/S03-application-verification` at
`3dde397e8162945f6d730a5993c8d1424b0fe8ec`. The session's `.git` remains read-only;
do not retry/bypass this boundary or claim a commit/push. No branches were made.
The intended demo branch is `feat/FEAT-041-demo-scenarios`. Preserve all earlier
uncommitted S03 work and the pre-existing untracked attendance evidence.

The saved earlier S03 push approval excludes this later demo scope (recorded in
`approvals.json`). Once Git is writable, separate and review the older S03
verification increment and this demo increment on appropriate retained branches
before committing/integrating. Do not push the expanded demo scope without its
own sprint confirmation. S03 remains the formal active sprint; S04 has not
started. Presentation work does not waive FEAT-041 operational prerequisites or
the specialist/policy gates.

The earlier checkpoint below preserves the prior S03 handoff and policy scope.
Its statement that the client apps are empty shells is now historical; its
instructions to push must be applied only to their explicitly approved scope.

---

## Latest continuation — 2026-10-24 (read before the historical checkpoint below)

The user requested `continue from resume.md`. Browser/application verification
is now complete. The current branch remains `chore/S03-application-verification`
at `3dde397e8162945f6d730a5993c8d1424b0fe8ec`, with **uncommitted changes**.

**Blocking condition:** this session explicitly grants only read access to
`.git`. Both `git add` and `git commit` failed with `index.lock: Permission
denied`. Do not work around that boundary or claim the work is committed.
No merge, S04 branch creation or S03 push occurred. Git write access in a
properly configured session is required to finish the saved handoff.

### Completed in this continuation

- All 51 backend scenarios, Ruff lint/format, strict mypy and dependency checks
  pass: `docs/testing/runs/2026-10-24T06-33-48-219Z-admissions.json`.
- Review checks RV-001–RV-004 pass after updating a stale hard-coded
  `pushAuthorized=false` assumption to require a scoped active-sprint approval:
  `docs/testing/runs/2026-10-24T06-40-58-486Z-unit.json`.
- Prototype browser checks RV-005–RV-007 pass:
  `docs/testing/runs/2026-10-24-S03-review-portal.json`.
- Real compiled-client checks all pass:
  `docs/testing/runs/2026-10-24T06-38-54-697Z-compiled-browsers.json`.
- Screenshot inspection found missing Arabic glyphs despite semantic test
  success. Fixed by bundling unchanged OFL-licensed Noto Naskh Arabic from the
  pinned local Flutter SDK. Font license/source/hash are under
  `apps/mobile/assets/fonts`. Corrected Arabic/English screenshots were inspected
  and show readable glyphs and RTL reflow. DEF-S03-001 closed for emulated Chrome.
- Mobile format/analyzer/three widget tests/rebuilt Flutter web all pass:
  `docs/testing/runs/2026-10-24T06-36-58-935Z-clients.json`. Next.js was unchanged;
  preserve its prior successful quality/build evidence without redundant builds.
- `tools/check-clients.mjs --mobile-only` supports focused verification.
- Prior S03 push authorization/scope/provenance is recorded in
  `docs/delivery/approvals.json`; `finalTestedCommit` remains null until this
  tested work can be committed. No production or UAT acceptance was granted.
- S04 preparation only: `docs/delivery/S04-FEAT-012-READINESS.md` retains four
  original staff-attendance tasks, three source cases/UAT IDs, predecessor and
  policy gates. S03/FEAT-030 remains active in `execution.json` and generated
  `plan.json`. All original scope/identifiers/exit criteria remain intact.

### Review links and runtime

- Dashboard: `http://localhost:3000`
- Compiled Flutter web on the same Wi-Fi: `http://192.168.1.4:3200`

Both returned successfully from this computer and browser checks pass. The
owned launcher is running in tool session `54429` at this checkpoint; process
survival after reopening is unknown. Check listeners before starting another
launcher. The current Wi-Fi address can change. Neither physical inbound phone
access nor physical Safari/native iPhone UAT is proven. Both apps are public
foundation shells without connected operational APIs or records.

Node ancestor realpath resolution in this managed session required process-local
`NODE_OPTIONS=--preserve-symlinks --preserve-symlinks-main`. No machine policy
was modified. This is separate from the `.git` write restriction and does not
resolve it. Failed unit runs are retained with explanations in the handoff.

### Remaining actions, in order

1. Read this update and TODO; inspect status and keep the pre-existing untracked
   `docs/testing/runs/2026-10-23T20-50-36-104Z-attendance.json` untouched/excluded.
2. In a session authorized to write `.git`, review the current diff and commit
   the tested font/tooling/evidence/docs increment on the existing chore branch.
   Do not add ignored toolchains/build outputs/screenshots. Avoid blanket adds.
3. Record that tested source commit in the approval record, commit the record
   and integrate locally into `sprint/03-review`, retaining all feature branches.
   Push the three explicitly authorized S03 branches without force. Record actual
   outcomes; the present authorization is preserved and need not be requested again.
4. Then create `sprint/04-review` and `feat/FEAT-012-staff-attendance`; archive the
   current TODO as S03 carryover at actual transition. Activate only FEAT-012,
   regenerate the plan, verify preservation and commit S04 readiness locally.
   No S04 push is authorized and no policy-dependent implementation may start
   before its prerequisites and separate module approval close.
5. Keep source product acceptance Not run and physical/native UAT pending until
   executed. Use `docs/testing/S03-APPLICATIONS.md` for evidence, review links,
   UAT checklist, release changes and known limitations.

The earlier checkpoint below is retained as history. Its pending browser checks,
old Wi-Fi address, stop instruction and committed-clean-tree description are
superseded by this continuation; its original scope and policy gates remain valid.

---

## Historical checkpoint before this continuation

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
