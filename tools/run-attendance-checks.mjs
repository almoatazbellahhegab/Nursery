/** Record executable FEAT-011 domain evidence without accepting integration UAT. */
import { runApiChecks } from './api-checks.mjs';
const mappings = [
  { cases: ['ATT-UNIT-001'], source: 'TC-FEAT-011-01', uat: 'UAT-S02-TC-FEAT-011-01', coverage: 'Partial: event decision only; no persistence/audit integration' },
  { cases: ['ATT-UNIT-002', 'ATT-UNIT-004', 'ATT-UNIT-012'], source: 'TC-FEAT-011-02', uat: 'UAT-S02-TC-FEAT-011-02', coverage: 'Partial: transition decisions only; no real PostgreSQL concurrency' },
  { cases: ['ATT-UNIT-003'], source: 'TC-FEAT-011-03', uat: 'UAT-S02-TC-FEAT-011-03', coverage: 'Partial: matching event/state instant; timeline integration not run' },
  { cases: ['ATT-UNIT-005', 'ATT-UNIT-006', 'ATT-UNIT-007', 'ATT-UNIT-013', 'ATT-UNIT-014', 'ATT-UNIT-017'], source: 'TC-FEAT-011-04', uat: 'UAT-S02-TC-FEAT-011-04', coverage: 'Partial: retry/conflict decisions; durable receipt and device offline integration not run' },
  { cases: ['ATT-UNIT-008', 'ATT-UNIT-009', 'ATT-UNIT-010', 'ATT-UNIT-011'], source: 'XCT-02', uat: 'UAT-S02-XCT-02', coverage: 'Supplemental grant-scope decisions only; no authoritative policy or QR verification' },
];
runApiChecks({ feature: 'FEAT-011', sprint: 'S02', slug: 'attendance', mappings });
