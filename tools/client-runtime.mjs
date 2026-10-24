/** Resolve local client tooling without changing global Node/npm/Flutter installs. */
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export function nodeRuntime() {
  const candidates = [process.env.NURSERY_APP_NODE, process.execPath, path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')].filter(Boolean);
  const runtime = candidates.find(candidate => {
    const result = spawnSync(candidate, ['--version'], { encoding: 'utf8', windowsHide: true });
    const [major, minor] = result.stdout.trim().replace(/^v/, '').split('.').map(Number);
    return result.status === 0 && (major > 24 || (major === 24 && minor >= 19));
  });
  if (!runtime) throw new Error('Node 24.19+ is required. Set NURSERY_APP_NODE to its executable.');
  return runtime;
}
export const flutter = process.env.NURSERY_FLUTTER ?? path.join(root, '.tools/flutter/bin/flutter.bat');
export function npmCli(runtime) {
  const candidates = [process.env.NURSERY_NPM_CLI, path.join(root, '.tools/npm-cli/node_modules/npm/bin/npm-cli.js'), path.join(path.dirname(runtime), 'node_modules/npm/bin/npm-cli.js')].filter(Boolean);
  const file = candidates.find(candidate => fs.existsSync(candidate));
  if (!file) throw new Error('npm 12.2.1 is required. Set NURSERY_NPM_CLI to npm-cli.js.');
  return file;
}
