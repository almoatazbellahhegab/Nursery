# Sprint 1 review handoff

Status: **In progress, environment blocked. Not accepted. No push authorized.**

This handoff records the original foundation increment. The current four-sprint plan expands S01 to include original milestones S01–S04; see SPRINTS.md for its full unchanged scope. Previous pushed work was authorized separately; this plan revision is local pending a new push instruction.

## Result available now

- One click Windows review: double-click `Start-Sprint-Review.cmd` or open http://localhost:3100 while the server is running.
- iPhone browser review on the same Wi-Fi: open the computer URL printed by the launcher and tap Mobile preview. The initial computer Wi-Fi address is http://192.168.1.2:3100 and may change.
- Administration preview: four navigation views, illustrative classroom figures and English/Arabic direction switching.
- Parent/staff mobile browser prototype: experience switcher, three navigation views, English/Arabic and explicit offline preview status. It does not queue writes.
- Complete itemized sprint backlog and source-to-test-to-UAT mapping. Human observations can be saved locally and downloaded.
- Production Next.js, Flutter and health-only FastAPI source skeletons; no working identity, database, native storage or operational APIs.

## Verification

RV-001 through RV-004 passed against the plan, translation keys, evidence validation and HTTP/persistence boundary. RV-005 through RV-007 passed in headless Chrome on Windows with desktop and emulated mobile sizes, including Arabic layout, parent/staff navigation, safe observation rendering and reload persistence. Screenshots were visually inspected. Evidence records are in `docs/testing/runs`; initial failed browser harness run is retained alongside the final run. Defects are tracked in `docs/testing/DEFECTS.md`.

Headless desktop Chrome is not a physical iPhone or Safari test. Physical Windows interaction, browser zoom, keyboard/screen-reader acceptance, Arabic owner approval, physical iPhone and native application checks remain pending. All 216 source product test cases remain Not run. Security scans and production CI/build jobs have not run; the included CI job covers review tools only and has not executed remotely.

## Open blockers and next work

- ENV-001 update during S02: registry access is working again, and API/test dependencies have been installed into a project-local virtual environment with a resolved version lock. The original DNS failure is historical; actual web/Flutter builds remain unverified.
- Flutter SDK and generated platform runners are unavailable. Generate localizations, run format/analyze/widget tests and build the actual app before claiming mobile delivery.
- FastAPI dependency/setup blocker is resolved during S02. Health and attendance domain tests now run in the project environment; this does not close identity, PostgreSQL or operational API prerequisites.
- Native iOS needs macOS/Xcode and signing/TestFlight provisioning.
- TW-006/GATE-05: Windows 11 and iPhone are requested targets. Exact browser/iOS support versions, accessibility target and performance objectives still need a named decision.
- TW-010 and policy gates remain open. Source files identify required operations, safeguarding, finance, privacy and Arabic-language owners.

Complete the actual web/Flutter build and agreed device checks before closing Sprint 1. Then request explicit user sprint confirmation. Record approval against the reviewed commit before pushing that sprint and its feature branches. No production deployment is authorized.

## Branches

- `chore/S01-review-portal`: dependency-free prototype and traceability checks.
- `chore/S01-stack-skeletons`: production directory and source foundations.
- `feat/FEAT-036-localization-foundation`: isolated public-shell localization groundwork; full feature now belongs to consolidated S01 (original S04).
- `test/S01-browser-evidence`: regression checks, test evidence, launchers and handoff.
- `sprint/01-review`: local integration result. Feature and work branches are retained. `main` remains the original baseline.
