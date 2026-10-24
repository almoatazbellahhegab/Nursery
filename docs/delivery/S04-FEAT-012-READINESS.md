# Sprint 4 preparation — FEAT-012 Staff Attendance

Prepared on 2026-10-24. Sprint 4 has not started: the session cannot write `.git`,
so Sprint 3 cannot be committed/integrated/pushed and no new branch can be
created. This document is readiness preparation on the existing enabling branch,
not policy-dependent implementation or feature acceptance.

## Entry checklist

- [x] Review unchanged FEAT-012 scope and three source acceptance cases.
- [x] Identify FEAT-010 Staff Profiles and Assignments as the required predecessor.
- [x] Preserve separate optional-module approval and correction/access gates.
- [ ] Commit/integrate/push the authorized tested S03 scope, retaining branches.
- [ ] Create `sprint/04-review`, then `feat/FEAT-012-staff-attendance`.
- [ ] Archive the S03 TODO at actual transition and activate only FEAT-012.
- [ ] Close FEAT-010 and authoritative identity/branch/access/storage prerequisites.
- [ ] Obtain separate staff-attendance scope approval before product implementation.
- [ ] Obtain explicit staff correction/access/report rules; do not assume child
  attendance DEC-06 decisions also approve staff policy.

## Original source tasks and readiness

| Task | Scope | Required before implementation |
| --- | --- | --- |
| DEV-FEAT-012-01 | Record staff attendance with timestamp and branch. | Active staff identity, authorized branch assignments, approved time rules and tenant-scoped transactions. |
| DEV-FEAT-012-02 | Permit authorized corrections with reason and audit history. | Approved correction roles/reasons/windows and immutable original/new values in an atomic audit transaction. |
| DEV-FEAT-012-03 | Restrict employee attendance details to approved roles. | Approved staff field/relationship permission matrix, authoritative evaluation and PostgreSQL RLS. |
| DEV-FEAT-012-04 | Provide basic daily staff-presence reporting. | Approved branch timezone/day boundaries, report recipients, filters and metric definitions. |

All four source tasks remain open. The child-attendance domain package must not
be treated as staff authorization, staff policy approval or persistent storage.
No real employee/child records are introduced in this preparation.

## Acceptance mapping

| Source case | Original stable UAT ID | S04 alias | Required result and level | Status |
| --- | --- | --- | --- | --- |
| TC-FEAT-012-01 | UAT-S14-TC-FEAT-012-01 | UAT-S04-TC-FEAT-012-01 | Active authorized employee check-in creates one open record; API integration. | Not run |
| TC-FEAT-012-02 | UAT-S14-TC-FEAT-012-02 | UAT-S04-TC-FEAT-012-02 | Duplicate check-in is prevented; API integration. | Not run |
| TC-FEAT-012-03 | UAT-S14-TC-FEAT-012-03 | UAT-S04-TC-FEAT-012-03 | Manager correction retains original/new value, actor, time and reason; API integration. | Not run |

Repeat applicable tenant/access denial, field filtering, concurrency, retry,
audit and localization checks from the unchanged cross-cutting catalogue.

## Sprint review requirements

- [ ] Authorized web journey with allowed/denied staff record and correction flows.
- [ ] Equivalent Flutter journey using the authoritative API.
- [ ] Real PostgreSQL race/retry/rollback and RLS evidence.
- [ ] Windows 11 human browser UAT recorded independently of headless checks.
- [ ] Physical iPhone Safari UAT recorded independently of browser emulation.
- [ ] Signed native iPhone build and device UAT, using macOS/Xcode.
- [ ] Test evidence, open defects, limitations and named acceptance before release.

## Remaining S04 queue

FEAT-025 retains TW-065 medical/safeguarding approval; FEAT-033 retains TW-066
transport operating-model approval; FEAT-038 retains TW-067 metric/privacy
approval; FEAT-039 retains TW-068 moderation/safeguarding approval; FEAT-040
retains TW-069 commerce business-case/boundary approval. All predecessor features
and the six-feature, 29-feature-task, five-technical-task, 25-source-test S04
scope remain unchanged. Only one feature may become active at transition.
