/** Append review-tool test evidence tied to the checked-out code commit. */
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
const startedAt = new Date().toISOString();
const commit = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
const dirty = execFileSync('git', ['status', '--porcelain'], { encoding: 'utf8' }).trim();
let output;
let result = 'Pass';
try {
  output = execFileSync(process.execPath, ['--test', 'tests/system/review.test.mjs'], { encoding: 'utf8' });
} catch (error) {
  output = String(error.stdout ?? '') + String(error.stderr ?? ''); result = 'Fail';
}
const ids = ['RV-001', 'RV-002', 'RV-003', 'RV-004'];
const uat = [['UAT-S01-04'], ['UAT-S01-03'], ['UAT-S01-05', 'UAT-S01-06'], ['UAT-S01-05']];
const cases = ids.map((id, index) => ({ id, uat: uat[index], result: new RegExp(`^ok \\d+ - ${id}`, 'm').test(output) ? 'Pass' : 'Fail' }));
const record = { startedAt, completedAt: new Date().toISOString(), codeCommit: commit, workingTreeChanges: dirty || null, environment: { node: process.version, platform: process.platform }, command: 'node --test tests/system/review.test.mjs', result, cases, output, sourceProductTests: 'Not run', userAcceptance: 'Pending' };
const file = `docs/testing/runs/${startedAt.replace(/[:.]/g, '-')}-unit.json`;
fs.mkdirSync('docs/testing/runs', { recursive: true });
fs.writeFileSync(file, JSON.stringify(record, null, 2) + '\n');
console.log(output);
console.log(`Evidence: ${file}`);
if (result === 'Fail') process.exitCode = 1;
