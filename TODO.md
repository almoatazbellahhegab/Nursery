# Development TODO

**Sprint 3 started. Only FEAT-030 Admissions Pipeline is active**, on `feat/FEAT-030-admissions-pipeline`. S01 and S02 remain incomplete and unaccepted. Prior work was pushed through `775b1ff`; new S03 work requires a new push instruction. The S02 checklist below is preserved as deferred carryover, not concurrent active work.

## Sprint 3 progress

- [x] Record user authorization and push existing planning/S02 commits and retained branches.
- [x] Create `sprint/03-review` and the dedicated FEAT-030 branch.
- [x] Preserve the previous TODO at `docs/delivery/S02-TODO.md`.
- [x] Review FEAT-030's six source tasks, five acceptance cases and unfinished FEAT-002/FEAT-005 dependencies.
- [x] Implement immutable, organization/branch-scoped stage snapshots and history facts.
- [x] Validate changes against explicit workflow policy without inventing approved transitions.
- [x] Reject stale versions, no-op moves, invalid times and unauthorized scope.
- [x] Preserve history actors/UTC timestamps and prevent direct enrollment without conversion.
- [x] Run admissions scenarios, attendance regressions, lint, formatting and strict typing.
- [ ] Record evidence/UAT mappings and commit the tested increment locally.

## FEAT-030 source tasks and operational delivery

- [ ] DEV-FEAT-030-01 Create and assign leads.
- [ ] DEV-FEAT-030-02 Move leads through valid pipeline states.
- [ ] DEV-FEAT-030-03 Schedule visits and trial days.
- [ ] DEV-FEAT-030-04 Convert accepted prospects into enrollment without duplicate re-entry.
- [ ] DEV-FEAT-030-05 Record loss reasons where approved.
- [ ] DEV-FEAT-030-06 Report pipeline volume and conversion.
- [ ] Complete FEAT-002/FEAT-005 branch and authoritative authorization prerequisites.
- [ ] Approve required inquiry fields, stage transitions, loss reasons and conversion/report definitions.
- [ ] Implement tenant-scoped PostgreSQL persistence, constraints/RLS and atomic history/audit.
- [ ] Build authorized web/mobile admissions journeys and run all five source integration cases.
- [ ] Deliver Windows 11 and physical iPhone UAT; obtain acceptance before pushing new S03 work.

The current increment uses opaque lead identifiers and no family/child identity data. Domain tests are partial coverage, not completed source tasks or feature acceptance.

## Sprint 3 feature queue

| Feature | Status | Dependencies / gates |
| --- | --- | --- |
| FEAT-030 Admissions Pipeline | Active domain increment | FEAT-002, FEAT-005; workflow/field definitions |
| FEAT-020 Standing Pickup | Queued / gated | FEAT-007, FEAT-008, FEAT-034; GATE-03 |
| FEAT-021 Temporary Pickup / Checkout | Queued / gated | FEAT-011, FEAT-020; GATE-03 |
| FEAT-022 Consent-aware Media | Queued / gated | FEAT-007, FEAT-008, FEAT-013, FEAT-035 |
| FEAT-023 Messaging | Queued | FEAT-005, FEAT-008, FEAT-009 |
| FEAT-024 Incidents | Queued / gated | FEAT-007, FEAT-017, FEAT-034; GATE-04 |
| FEAT-026 Fees / Discounts | Queued | FEAT-001, FEAT-002, FEAT-005 |
| FEAT-027 Invoices / Balances | Queued | FEAT-008, FEAT-026, FEAT-034 |
| FEAT-028 Payments | Queued / gated | FEAT-027, FEAT-034; GATE-06 |
| FEAT-029 Payment Reminders | Queued | FEAT-017, FEAT-027 |
| FEAT-031 Waiting List / Capacity | Queued | FEAT-009, FEAT-030 |
| FEAT-032 Analytics | Queued | FEAT-011, FEAT-016, FEAT-023, FEAT-027, FEAT-030, FEAT-031 |

- [ ] Complete all S03 tasks and 55 assigned source tests, plus applicable repeated cross-cutting checks.
- [ ] Deliver web/mobile review, test log, UAT checklist, release notes and open defects.

## Deferred Sprint 2 work

## Deferred attendance increment

- [x] Review FEAT-011's five source development tasks and five acceptance cases.
- [x] Identify unfinished FEAT-007/FEAT-009 and identity/authorization/storage prerequisites.
- [x] Request DEC-06 attendance correction/override/absence policy without inventing defaults.
- [x] Implement immutable check-in/check-out transition decisions with UTC instants and version preconditions.
- [x] Reject duplicate/impossible transitions and reused operation IDs with changed payloads.
- [x] Verify exact retry behavior and rejection of expired or differently scoped trusted grants.
- [x] Run pytest, Ruff and strict mypy; preserve test evidence and UAT links.
- [ ] Connect real PostgreSQL transactions/RLS, durable receipts, audit/outbox and server-owned authorization after prerequisites close.
- [ ] Build authorized web/mobile attendance entry, timeline consistency and reports.
- [ ] Implement QR and approved offline synchronization after their identity/security prerequisites close.
- [ ] Implement correction, lateness, early departure and absence behavior after DEC-06 approval.
- [ ] Run all five source acceptance cases through real API/mobile integration.
- [ ] Deliver Windows 11 and physical iPhone acceptance results; obtain user review.

Domain-only tests prove decisions, not durable storage, actual authorization, QR security, concurrency safety or completed feature acceptance. Source acceptance cases remain Not run until their specified integration levels execute.

## Sprint 2 feature queue

This is the retained S02 queue. FEAT-011 was deferred by the user's explicit next-sprint instruction; it is no longer active. Start another feature only after the current active feature is accepted or explicitly deferred and its dependencies close.

| Order | Feature | Status | Required predecessor features |
| --- | --- | --- | --- |
| 1 | FEAT-011 Child Attendance | Deferred: domain increment; operational integration blocked | FEAT-007, FEAT-009 |
| 2 | FEAT-013 Daily Child Timeline | Queued | FEAT-007, FEAT-011 |
| 3 | FEAT-014 Quick and Batch Care Entry | Queued | FEAT-009, FEAT-013 |
| 4 | FEAT-016 Announcements | Queued | FEAT-002, FEAT-005, FEAT-009 |
| 5 | FEAT-017 Notifications and Preference Management | Queued | FEAT-013, FEAT-016 |
| 6 | FEAT-018 Calendar and Relevant Events | Queued | FEAT-002, FEAT-009 |
| 7 | FEAT-019 Administrative Search | Queued | FEAT-005, FEAT-007, FEAT-009, FEAT-010 |
| 8 | FEAT-015 Parent Home and Daily Summary | Queued | FEAT-008, FEAT-013, FEAT-017, FEAT-019 |
| 9 | FEAT-041 Demo Organization and Scenario Data | Queued | FEAT-001 through FEAT-019 as applicable |

## Sprint 2 completion

- [ ] Complete TW-038 through TW-045 daily-care, offline and engagement work.
- [ ] Complete TW-046 through TW-055 release-hardening, recovery and operational UAT work.
- [ ] Run 75 assigned source cases and repeat applicable cross-cutting checks per changed feature.
- [ ] Deliver the web/mobile review, test log, UAT checklist, release notes and open defects.
- [ ] Obtain explicit sprint confirmation before pushing.

## Complete four sprint scope

| Sprint | Scope | Features | Feature tasks | Technical tasks | Source tests |
| --- | --- | ---: | ---: | ---: | ---: |
| S01 | Foundations and nursery setup; incomplete | 14 | 68 | 37 | 61 |
| S02 | Daily operations and Phase 1 release; deferred / incomplete | 9 | 44 | 18 | 75 |
| S03 | Safety, communication, finance and growth; started / FEAT-030 only | 12 | 63 | 9 | 55 |
| S04 | Advanced and optional modules; separate approvals retained | 6 | 29 | 5 | 25 |
| Total | Original scope unchanged | 41 | 204 | 69 | 216 |

The unchanged itemized source task text, all features and all technical tasks remain in [SPRINTS.md](docs/delivery/SPRINTS.md). Execution state is separate from that baseline in [execution.json](docs/delivery/execution.json). Historical UAT links and test outcomes are retained.
