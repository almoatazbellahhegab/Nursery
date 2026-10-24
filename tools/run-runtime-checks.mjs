/** Real local PostgreSQL integration plus all retained domain regressions. */
import fs from 'node:fs';
import { runApiChecks } from './api-checks.mjs';

if (!fs.existsSync('.tools/database-runtime.json')) {
  throw new Error('Run the owned PostgreSQL setup and seed wrappers before runtime integration tests.');
}
runApiChecks({
  feature: 'FEAT-003/FEAT-005 foundations', sprint: 'S04', slug: 'runtime',
  sourceAcceptanceCases: 'Identity/tenant integration evidence only; original feature acceptance remains mapped separately',
  requireNoSkips: true,
  mappings: [{ cases: ['IDENTITY-001','IDENTITY-002','IDENTITY-003','IDENTITY-004','IDENTITY-005','IDENTITY-006','IDENTITY-007','IDENTITY-008','IDENTITY-009','IDENTITY-010','IDENTITY-011','IDENTITY-012'], coverage: 'Real PostgreSQL identity sessions, current membership, tenant RLS, branch filtering, CSRF, revocation and login throttling; not complete identity/module acceptance' }],
});
