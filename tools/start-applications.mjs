/** Launch compiled public app shells; never enables operational APIs or access. */
import { spawn, execFile } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { root, nodeRuntime } from './client-runtime.mjs';

const runtime = nodeRuntime();
for (const file of ['apps/admin-web/.next/BUILD_ID', 'apps/mobile/build/web/index.html']) {
  if (!fs.existsSync(path.join(root, file))) throw new Error(`Missing build: ${file}. See docs/runbooks/application-review.md.`);
}
const children = [
  spawn(runtime, [path.join(root, 'apps/admin-web/node_modules/next/dist/bin/next'), 'start', '--hostname', '0.0.0.0', '--port', '3000'], { cwd: path.join(root, 'apps/admin-web'), stdio: 'inherit', windowsHide: true }),
  spawn(runtime, [path.join(root, 'tools/serve-mobile.mjs')], { cwd: root, stdio: 'inherit', windowsHide: true }),
];
const stop = () => { for (const child of children) child.kill(); };
process.on('SIGINT', stop);
process.on('SIGTERM', stop);
for (const child of children) {
  child.on('error', error => { console.error(error.message); stop(); process.exitCode = 1; });
  child.on('exit', code => { if (code) { stop(); process.exitCode = code; } });
}
const addresses = Object.entries(os.networkInterfaces()).flatMap(([name, values]) => (values ?? []).filter(a => a.family === 'IPv4' && !a.internal && !/virtual|vethernet/i.test(name)).map(a => a.address));
const address = addresses[0] ?? 'localhost';
console.log(`Dashboard: http://localhost:3000`);
console.log(`Mobile on the same Wi-Fi: http://${address}:3200`);
console.log('Compiled foundation shells only; no operational records. Keep this terminal open.');
if (process.argv.includes('--open')) {
  let ready = false;
  for (let attempt = 0; attempt < 30 && !ready; attempt++) {
    try { ready = (await fetch('http://localhost:3000')).ok && (await fetch('http://localhost:3200')).ok; }
    catch { /* Wait for the child listeners before opening the review browser. */ }
    if (!ready) await new Promise(resolve => setTimeout(resolve, 500));
  }
  if (ready && process.platform === 'win32') execFile('explorer.exe', ['http://localhost:3000'], () => {});
}
