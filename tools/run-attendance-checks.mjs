/** Record executable FEAT-011 domain evidence without accepting integration UAT. */
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cwd = path.join(root, 'services/api');
const python = path.join(cwd, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const startedAt = new Date().toISOString();
const stamp = startedAt.replace(/[:.]/g, '-');
const outputDirectory = path.join(root, 'docs/testing/runs');
const junit = path.join(root, 'test-results', `attendance-${stamp}.xml`);
fs.mkdirSync(path.dirname(junit), { recursive: true });
fs.mkdirSync(outputDirectory, { recursive: true });
const checks = [
  ['pytest', ['-m', 'pytest', '-q', '-p', 'no:cacheprovider', `--junitxml=${junit}`]],
  ['ruff-lint', ['-m', 'ruff', 'check', 'src', 'tests']],
  ['ruff-format', ['-m', 'ruff', 'format', '--check', 'src', 'tests']],
  ['mypy-strict', ['-m', 'mypy', '--strict', 'src', 'tests']],
  ['dependency-consistency', ['-m', 'pip', 'check']],
];
const results = checks.map(([id, args]) => {
  let output;
  let result = 'Pass';
  try { output = execFileSync(python, args, { cwd, encoding: 'utf8' }); }
  catch (error) { output = String(error.stdout ?? '') + String(error.stderr ?? ''); result = 'Fail'; }
  console.log(`${id}: ${result}\n${output}`);
  return { id, args, result, output };
});
const mappings = [
  { cases: ['ATT-UNIT-001'], source: 'TC-FEAT-011-01', uat: 'UAT-S02-TC-FEAT-011-01', coverage: 'Partial: event decision only; no persistence/audit integration' },
  { cases: ['ATT-UNIT-002', 'ATT-UNIT-004', 'ATT-UNIT-012'], source: 'TC-FEAT-011-02', uat: 'UAT-S02-TC-FEAT-011-02', coverage: 'Partial: transition decisions only; no real PostgreSQL concurrency' },
  { cases: ['ATT-UNIT-003'], source: 'TC-FEAT-011-03', uat: 'UAT-S02-TC-FEAT-011-03', coverage: 'Partial: matching event/state instant; timeline integration not run' },
  { cases: ['ATT-UNIT-005', 'ATT-UNIT-006', 'ATT-UNIT-007', 'ATT-UNIT-013', 'ATT-UNIT-014', 'ATT-UNIT-017'], source: 'TC-FEAT-011-04', uat: 'UAT-S02-TC-FEAT-011-04', coverage: 'Partial: retry/conflict decisions; durable receipt and device offline integration not run' },
  { cases: ['ATT-UNIT-008', 'ATT-UNIT-009', 'ATT-UNIT-010', 'ATT-UNIT-011'], source: 'XCT-02', uat: 'UAT-S02-XCT-02', coverage: 'Supplemental grant-scope decisions only; no authoritative policy or QR verification' },
];
const record = {
  startedAt, completedAt: new Date().toISOString(), feature: 'FEAT-011', sprint: 'S02',
  codeCommit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
  workingTreeChanges: execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim() || null,
  python: execFileSync(python, ['--version'], { encoding: 'utf8' }).trim(), platform: process.platform,
  dependencyLockSha256: createHash('sha256').update(fs.readFileSync(path.join(cwd, 'requirements-dev.lock'))).digest('hex'),
  result: results.every(r => r.result === 'Pass') ? 'Pass' : 'Fail', checks: results, mappings,
  executedCases: fs.existsSync(junit) ? [...fs.readFileSync(junit, 'utf8').matchAll(/<testcase\b[^>]*name="([^"]+)"/g)].map(match => match[1]) : [],
  sourceAcceptanceCases: 'All five remain Not run at their required integration levels',
  TC_FEAT_011_05: 'Not run: QR and authoritative authorization not implemented',
  physicalIPhone: 'Not run', nativeIPhone: 'Blocked', userAcceptance: 'Pending',
};
const evidenceFile = path.join(outputDirectory, `${stamp}-attendance.json`);
fs.writeFileSync(evidenceFile, JSON.stringify(record, null, 2) + '\n');
console.log(`Evidence: ${evidenceFile}`);
if (record.result === 'Fail') process.exitCode = 1;
