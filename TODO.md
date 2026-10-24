# Development TODO — Sprint 4

## Latest execution override

### Pause and backup checkpoint - 2026-10-24

- [x] User authorized committing/pushing all current local work and branches.
- [x] Hosted owner-private fictional mobile demo; links and Site identity in RESUME.md.
- [x] Final focused provider/privacy tests: 24 pass; Python lint/format pass.
- [ ] Resume unfinished provider flow, linking, callback/native exchange and session hardening.
- [ ] Verify draft migration0006 before applying; preserve installed0001-0005.
- [ ] Run full current-source regression and rebuild both clients before replacing the compiled demo.
- [ ] Verify hosted demo interactively and on physical iPhone Safari; native iPhone remains separate.

This is an authorized WIP backup, not Sprint4 completion or UAT acceptance.

### Connected delivery progress

- [x] Connected application MFA, encrypted enrollment, one-use recovery, throttle and commit-before-response.
- [x] 259 full backend cases; 12 targeted security checks; 14 Flutter tests; both builds; four MFA browser groups.
- [ ] Continue FEAT-003 provider-backed login/recovery and final security hardening.

- [x] Connected FEAT-002 branch API/RLS and paginated Next.js/Flutter administration.
- [x] 248 backend scenarios; 11 Flutter tests; web/mobile builds; connected branch and staff browser checks.
- [ ] Commit/integrate the tested branch prerequisite, then continue account security and onboarding.

- [x] Real PostgreSQL 18.6 dev/test, Alembic migrations and restricted RLS role.
- [x] Real password/session identity, current tenant/role/branch and revocation checks.
- [x] Transactional staff attendance/corrections/receipt/audit API and daily report.
- [x] Connected Next.js and Flutter staff journeys with shared persisted state.
- [x] 232 backend scenarios, eight Flutter tests, build/quality checks and connected browser groups.
- [x] Actual API integration coverage of TC-FEAT-012-01, 02 and 03 (UAT not accepted).
- [ ] Finish profile/account/child/classroom onboarding and privileged MFA.
- [x] Harden session-restore races and truncated branch-history boundary.
- [ ] Generate contract clients and complete large-data pagination.
- [ ] Implement/test the remaining original product features and all S04 modules sequentially.

Earlier review-blocked and domain-only descriptions below are historical under
the explicit override. The connected staff increment is not the final product.

User explicitly waived the pending reviews for implementation/testing:
`please skip this review and complete implementation and testing of the final product`.
Do not re-request specialist-review evidence as a development prerequisite.
Original review records remain waived, not approved; physical/native UAT and
deployment/push permissions remain separate.

- [ ] Build and test real PostgreSQL/migration and identity/tenant foundations.
- [ ] Deliver connected transactional staff API and authorized Next.js/Flutter flows.
- [ ] Implement remaining original product scope using documented defaults.
- [ ] Execute original API/client/source tests and production-like regressions.

## Latest completion request

User: `complete sprint 4 development`. Product intent covers the unchanged S04
scope; original specialist gates still apply. See the concrete
[completion checklist](docs/delivery/S04-COMPLETION.md) for all six features and
the exact required policy/design evidence. The owner/document question is pending.

- [x] Audit all 29 feature tasks, five technical gates and 25 source cases.
- [x] Add exact staff retry receipts, original session/event replay and corruption rejection.
- [x] Pass 204 backend scenarios (67 staff), lint/format, strict types and dependencies.
- [x] Check local database tooling; PostgreSQL/Docker are unavailable here.
- [ ] Receive the original required named specialist policy/design evidence.
- [ ] Complete prerequisites, real persistence/API/client journeys and source tests.

The 168-scenario result below is prior evidence. Full S04 remains incomplete;
no governed module, source acceptance or physical/native UAT is marked complete.

User instruction: `push and start development of sprint 4`.
Only FEAT-012 Staff Attendance is active. S01–S03 remain incomplete/unaccepted;
the Sprint 3 checkpoint is preserved at [S03 carryover](docs/delivery/S03-TODO.md).
S03 through `1d8c766` and its four new retained work branches were pushed.
S04 stays local until separately confirmed for push. Read [RESUME.md](RESUME.md).

## First feature — FEAT-012 Staff Attendance

- [x] Create `sprint/04-review` and retained `feat/FEAT-012-staff-attendance`.
- [x] Archive S03 TODO unchanged and preserve its policy decisions/test scope.
- [x] Keep staff attendance types and grants distinct from child attendance.
- [x] Add opaque check-in/out and one organization-wide open employee session.
- [x] Deny duplicate cross-branch check-in, wrong-branch checkout, stale versions,
  inactive employees, expired/mismatched grants and invalid chronology.
- [x] Pass 168 backend scenarios, Ruff lint/format, strict typing and dependencies.
- [x] Record evidence, source mappings, UAT checklist and known limitations.
- [ ] Complete FEAT-010 and authoritative identity/status/branch/action permissions.
- [ ] Resolve staff-specific correction roles/reasons/windows and field/report rules.
- [ ] Persist staff state/event/receipt/audit atomically with real PostgreSQL/RLS.
- [ ] Verify employee-wide locking, operation replay, concurrency and rollback.
- [ ] Deliver authorized Next.js and Flutter staff journeys after prerequisites.
- [ ] Execute all three source API cases and applicable cross-cutting cases.
- [ ] Record Windows 11 human, physical iPhone Safari and native iPhone UAT separately.

## Original FEAT-012 tasks

- [ ] DEV-FEAT-012-01 Record staff attendance with timestamp and branch.
- [ ] DEV-FEAT-012-02 Permit authorized corrections with reason and audit history.
- [ ] DEV-FEAT-012-03 Restrict employee attendance details to approved roles.
- [ ] DEV-FEAT-012-04 Provide basic daily staff-presence reporting.

The pure domain increment is partial DEV-FEAT-012-01 groundwork. It is not an
operational staff module, a completed source case or staff policy approval.
Child DEC-06 does not approve employee corrections, overtime, leave or payroll.

## Remaining Sprint 4 queue

| Feature | Status | Required gates / dependencies |
| --- | --- | --- |
| FEAT-025 Medication | Queued/gated | FEAT-007/013/034; TW-065 medical/safeguarding |
| FEAT-033 Transport | Queued/gated | FEAT-005/007/017; TW-066 operating model |
| FEAT-038 Commercial KPIs | Queued/gated | FEAT-006/027/032/037; TW-067 metric/privacy |
| FEAT-039 Parent community | Queued/gated | FEAT-008/035/037; TW-068 moderation/safeguarding; DEC-13 |
| FEAT-040 Commerce readiness | Queued/gated | FEAT-027/028/037; TW-069 business case/boundaries |

## Sprint review and completion

- [ ] Complete unchanged S04 scope: six features, 29 feature tasks, five technical
  tasks and 25 assigned source tests, plus affected cross-cutting checks.
- [ ] Deliver reviewable connected web/mobile journeys, test report, release
  changes, defects, UAT checklist and limitations.
- [ ] Obtain named specialist/operational/Arabic and user acceptance.
- [ ] Record explicit S04 push confirmation and exact scope before pushing.

Specifications in `Document` and all original identifiers/exit criteria remain
unchanged in [SPRINTS.md](docs/delivery/SPRINTS.md). Prior demo clients remain
reviewable but are not evidence of an operational staff-attendance UI.
