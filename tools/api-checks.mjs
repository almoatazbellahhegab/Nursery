/** Shared project-local API/domain quality runner; appends evidence, never UAT approval. */
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export function runApiChecks({ feature, sprint, slug, mappings, sourceAcceptanceCases = 'All five source cases remain Not run at their required integration levels' }) {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const cwd = path.join(root, 'services/api');
  const python = path.join(cwd, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  const startedAt = new Date().toISOString();
  const stamp = startedAt.replace(/[:.]/g, '-');
  const junit = path.join(root, 'test-results', `${slug}-${stamp}.xml`);
  const outputDirectory = path.join(root, 'docs/testing/runs');
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
  const record = {
    startedAt, completedAt: new Date().toISOString(), feature, sprint,
    codeCommit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    workingTreeChanges: execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim() || null,
    python: execFileSync(python, ['--version'], { encoding: 'utf8' }).trim(), platform: process.platform,
    dependencyLockSha256: createHash('sha256').update(fs.readFileSync(path.join(cwd, 'requirements-dev.lock'))).digest('hex'),
    result: results.every(r => r.result === 'Pass') ? 'Pass' : 'Fail', checks: results, mappings,
    executedCases: fs.existsSync(junit) ? [...fs.readFileSync(junit, 'utf8').matchAll(/<testcase\b[^>]*name="([^"]+)"/g)].map(match => match[1]) : [],
    sourceAcceptanceCases,
    physicalIPhone: 'Not run', nativeIPhone: 'Blocked', userAcceptance: 'Pending',
  };
  const evidenceFile = path.join(outputDirectory, `${stamp}-${slug}.json`);
  fs.writeFileSync(evidenceFile, JSON.stringify(record, null, 2) + '\n');
  console.log(`Evidence: ${evidenceFile}`);
  if (record.result === 'Fail') process.exitCode = 1;
  return record;
}
