/** FEAT-030 domain evidence only; policy fixtures do not approve a business workflow. */
import { runApiChecks } from './api-checks.mjs';

runApiChecks({
  feature: 'FEAT-030', sprint: 'S03', slug: 'admissions',
  mappings: [
    { cases: ['ADM-APPT-001', 'ADM-APPT-002', 'ADM-APPT-003', 'ADM-APPT-004', 'ADM-APPT-006', 'ADM-APPT-007', 'ADM-APPT-008', 'ADM-APPT-009', 'ADM-APPT-010', 'ADM-APPT-011', 'ADM-APPT-012', 'ADM-APPT-013', 'ADM-APPT-014', 'ADM-APPT-015', 'ADM-APPT-016', 'ADM-APPT-017', 'ADM-APPT-018', 'ADM-APPT-019', 'ADM-APPT-020', 'ADM-APPT-021', 'ADM-APPT-022'], task: 'DEV-FEAT-030-03', coverage: 'Partial task-level calendar planning: explicit UTC availability, host overlap, versioned reschedule/cancel history and supplied reasons; no direct source acceptance case for scheduling and no production transaction/API' },
    { cases: ['ADM-APPT-005'], source: 'TC-FEAT-030-04', uat: 'UAT-S03-TC-FEAT-030-04', coverage: 'Partial: trusted appointment scope/current expiry denial before conflicts; no real role/branch authorization or visibility UI' },
    { cases: ['ADM-UNIT-029', 'ADM-UNIT-030'], source: 'TC-FEAT-030-02', uat: 'UAT-S03-TC-FEAT-030-02', coverage: 'Partial: future receipt rejection and equivalent-offset boundary replay; no durable database idempotency' },
    { cases: ['ADM-UNIT-018', 'ADM-UNIT-019', 'ADM-UNIT-020', 'ADM-UNIT-024', 'ADM-UNIT-025', 'ADM-UNIT-026', 'ADM-UNIT-027', 'ADM-UNIT-028'], source: 'TC-FEAT-030-02', uat: 'UAT-S03-TC-FEAT-030-02', coverage: 'Partial: trusted receipt exact replay, payload/history integrity and no rollback; no durable database idempotency' },
    { cases: ['ADM-UNIT-021', 'ADM-UNIT-022', 'ADM-UNIT-023'], source: 'TC-FEAT-030-04', uat: 'UAT-S03-TC-FEAT-030-04', coverage: 'Partial: retry actor/scope/expiry denial; real authentication and branch visibility not implemented' },
    { cases: ['ADM-UNIT-001', 'ADM-UNIT-002', 'ADM-UNIT-003', 'ADM-UNIT-004', 'ADM-UNIT-009', 'ADM-UNIT-010', 'ADM-UNIT-012', 'ADM-UNIT-013', 'ADM-UNIT-014', 'ADM-UNIT-015', 'ADM-UNIT-016', 'ADM-UNIT-017'], source: 'TC-FEAT-030-02', uat: 'UAT-S03-TC-FEAT-030-02', coverage: 'Partial: stage/history decisions with synthetic explicit policy; no API/persistence' },
    { cases: ['ADM-UNIT-005', 'ADM-UNIT-006', 'ADM-UNIT-007', 'ADM-UNIT-008'], source: 'TC-FEAT-030-04', uat: 'UAT-S03-TC-FEAT-030-04', coverage: 'Partial: scope/expiry rejection only; actual branch visibility UI/E2E not run' },
    { cases: ['ADM-UNIT-011'], source: 'TC-FEAT-030-03', uat: 'UAT-S03-TC-FEAT-030-03', coverage: 'Guard only: stage edits cannot create/undo enrollment; real conversion/deduplication not implemented' },
  ],
});
