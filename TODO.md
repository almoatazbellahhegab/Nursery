# Development TODO

Sprint 2 is started at the user's request. Sprint 1 remains incomplete and unaccepted. Work proceeds on one feature at a time; the current feature is **FEAT-011 Child Attendance** on `feat/FEAT-011-child-attendance`. No push is authorized for this increment.

## Current feature

- [x] Review FEAT-011's five source development tasks and five acceptance cases.
- [x] Identify unfinished FEAT-007/FEAT-009 and identity/authorization/storage prerequisites.
- [x] Request DEC-06 attendance correction/override/absence policy without inventing defaults.
- [ ] Implement immutable check-in/check-out transition decisions with UTC instants and version preconditions.
- [ ] Reject duplicate/impossible transitions and reused operation IDs with changed payloads.
- [ ] Verify exact retry behavior and rejection of expired or differently scoped trusted grants.
- [ ] Run pytest, Ruff and strict mypy; preserve test evidence and UAT links.
- [ ] Connect real PostgreSQL transactions/RLS, durable receipts, audit/outbox and server-owned authorization after prerequisites close.
- [ ] Build authorized web/mobile attendance entry, timeline consistency and reports.
- [ ] Implement QR and approved offline synchronization after their identity/security prerequisites close.
- [ ] Implement correction, lateness, early departure and absence behavior after DEC-06 approval.
- [ ] Run all five source acceptance cases through real API/mobile integration.
- [ ] Deliver Windows 11 and physical iPhone acceptance results; obtain user review.

Domain-only tests prove decisions, not durable storage, actual authorization, QR security, concurrency safety or completed feature acceptance. Source acceptance cases remain Not run until their specified integration levels execute.

## Sprint 2 feature queue

Only FEAT-011 may be active. Start the next feature after the current feature is accepted or explicitly deferred by the user, and only after its recorded dependencies close.

| Order | Feature | Status | Required predecessor features |
| --- | --- | --- | --- |
| 1 | FEAT-011 Child Attendance | Active: domain increment; operational integration blocked | FEAT-007, FEAT-009 |
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
| S02 | Daily operations and Phase 1 release; started | 9 | 44 | 18 | 75 |
| S03 | Safety, communication, finance and growth; queued | 12 | 63 | 9 | 55 |
| S04 | Advanced and optional modules; separate approvals retained | 6 | 29 | 5 | 25 |
| Total | Original scope unchanged | 41 | 204 | 69 | 216 |

The unchanged itemized source task text, all features and all technical tasks remain in [SPRINTS.md](docs/delivery/SPRINTS.md). Execution state is separate from that baseline in [execution.json](docs/delivery/execution.json). Historical UAT links and test outcomes are retained.
