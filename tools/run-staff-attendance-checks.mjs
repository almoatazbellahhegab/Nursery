/** FEAT-012 groundwork evidence; no staff policy, API integration or UAT acceptance. */
import { runApiChecks } from './api-checks.mjs';

runApiChecks({
  feature: 'FEAT-012', sprint: 'S04', slug: 'staff-attendance',
  sourceAcceptanceCases: 'All three FEAT-012 source cases remain Not run at their required API integration levels',
  mappings: [
    { cases: ['STAFF-UNIT-015', 'STAFF-UNIT-016', 'STAFF-UNIT-017', 'STAFF-UNIT-020', 'STAFF-UNIT-021', 'STAFF-UNIT-022', 'STAFF-UNIT-023', 'STAFF-UNIT-024', 'STAFF-UNIT-025'], source: 'TC-FEAT-012-02', uat: 'UAT-S04-TC-FEAT-012-02', coverage: 'Partial: exact historical replay, immutable session/event, payload/receipt/current-state integrity and chronology; no durable receipt, real transaction or concurrent API integration' },
    { cases: ['STAFF-UNIT-018', 'STAFF-UNIT-019'], source: 'XCT-02', uat: 'UAT-S04-XCT-02', coverage: 'Supplemental receipt actor/target and current employee activity/action/expiry checks before payload conflicts; no authoritative identity policy' },
    { cases: ['STAFF-UNIT-001', 'STAFF-UNIT-003'], source: 'TC-FEAT-012-01', uat: 'UAT-S04-TC-FEAT-012-01', coverage: 'Partial: pure scoped staff session/event proposal; no active-profile provider, database, API or audit integration' },
    { cases: ['STAFF-UNIT-002', 'STAFF-UNIT-004', 'STAFF-UNIT-005', 'STAFF-UNIT-008', 'STAFF-UNIT-009'], source: 'TC-FEAT-012-02', uat: 'UAT-S04-TC-FEAT-012-02', coverage: 'Partial: duplicate/impossible/stale decisions, including another branch; no real concurrent transactions or durable receipts' },
    { cases: ['STAFF-UNIT-006', 'STAFF-UNIT-007', 'STAFF-UNIT-014'], source: 'XCT-02', uat: 'UAT-S04-XCT-02', coverage: 'Supplemental trusted employee/branch/action/activity/expiry and child-grant separation; no actual identity or role matrix' },
    { cases: ['STAFF-UNIT-010', 'STAFF-UNIT-011', 'STAFF-UNIT-012', 'STAFF-UNIT-013'], task: 'DEV-FEAT-012-01', coverage: 'UTC normalization, immutable well-formed staff state and safe value rejection only' },
  ],
});
