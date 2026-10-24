/** Build/check actual client shells and append evidence; no product UAT acceptance. */
import { spawnSync, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { root, nodeRuntime, npmCli, flutter } from './client-runtime.mjs';

const node = nodeRuntime();
const web = path.join(root, 'apps/admin-web');
const mobile = path.join(root, 'apps/mobile');
const startedAt = new Date().toISOString();
const environment = { ...process.env, NEXT_TELEMETRY_DISABLED: '1', FLUTTER_SUPPRESS_ANALYTICS: 'true', PUB_CACHE: path.join(root, '.tools/pub-cache') };
const checks = [
  ['APP-WEB-TYPES', node, ['node_modules/typescript/bin/tsc', '--noEmit'], web],
  ['APP-WEB-LINT', node, ['node_modules/eslint/bin/eslint.js', '.'], web],
  ['APP-WEB-FORMAT', node, ['node_modules/prettier/bin/prettier.cjs', '--check', '.'], web],
  ['APP-WEB-AUDIT', node, [npmCli(node), 'audit', '--json'], web],
  ['APP-WEB-BUILD', node, ['node_modules/next/dist/bin/next', 'build', '--webpack'], web],
  ['APP-MOBILE-FORMAT', path.join(root, '.tools/flutter/bin/cache/dart-sdk/bin/dart.exe'), ['format', '--output=none', '--set-exit-if-changed', 'lib', 'test'], mobile],
  ['APP-MOBILE-ANALYZE', flutter, ['analyze', '--no-pub'], mobile],
  ['APP-MOBILE-WIDGET', flutter, ['test', '--no-pub'], mobile],
  ['APP-MOBILE-BUILD', flutter, ['build', 'web', '--no-pub', '--no-web-resources-cdn'], mobile],
];
const results = [];
for (const [id, command, args, cwd] of checks) {
  if (process.argv.includes('--mobile-only') && !id.startsWith('APP-MOBILE-')) continue;
  if (process.argv.includes('--web-only') && !id.startsWith('APP-WEB-')) continue;
  if (process.argv.includes('--skip-audit') && id === 'APP-WEB-AUDIT') continue;
  if (process.argv.includes('--skip-build') && id.endsWith('-BUILD')) continue;
  console.log(`Starting ${id}`);
  // All shell arguments are fixed internal Flutter options, never request data.
  const result = spawnSync(command, args, { cwd, env: environment, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024, windowsHide: true, shell: command.endsWith('.bat') });
  const output = String(result.stdout ?? '') + String(result.stderr ?? '') + String(result.error?.message ?? '');
  const status = result.status === 0 ? 'Pass' : 'Fail';
  console.log(`${id}: ${status}\n${output}`);
  results.push({ id, result: status, exitCode: result.status, output });
}
const record = {
  startedAt, completedAt: new Date().toISOString(),
  codeCommit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
  workingTreeChanges: execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim() || null,
  node: execFileSync(node, ['--version'], { encoding: 'utf8' }).trim(),
  flutterSdk: '3.47.8 / Dart 3.13.7', results,
  selection: process.argv.includes('--mobile-only') ? 'Mobile checks only' : process.argv.includes('--web-only') ? 'Web checks only' : 'All client checks',
  dependencyAudit: process.argv.includes('--skip-audit') ? 'npm audit not rerun in this selection; dependency changes and prior evidence are documented separately' : 'See selected results',
  buildSelection: process.argv.includes('--skip-build') ? 'Build not rerun; retain prior same-source compiled artifact evidence' : 'See selected results',
  result: results.every(r => r.result === 'Pass') ? 'Pass' : 'Fail',
  scope: 'Actual compiled clients; connected staff journeys tested separately by check-connected-browsers.mjs; no UAT acceptance implied',
  physicalIPhone: 'Not run', nativeIOSBuild: 'Blocked on macOS/Xcode/signing', userAcceptance: 'Pending',
};
const file = path.join(root, 'docs/testing/runs', `${startedAt.replace(/[:.]/g, '-')}-clients.json`);
fs.writeFileSync(file, JSON.stringify(record, null, 2) + '\n');
console.log(`Evidence: ${file}`);
if (record.result === 'Fail') process.exitCode = 1;
