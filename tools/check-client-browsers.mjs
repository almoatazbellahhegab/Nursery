/** Browser checks against the actual built clients, distinct from HTML prototypes. */
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { root } from './client-runtime.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.NURSERY_PLAYWRIGHT ?? path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const startedAt = new Date().toISOString();
const output = path.join(root, 'test-results');
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--enable-unsafe-swiftshader'] });
const errors = [];
const results = [];
const web = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
for (const page of [web, mobile]) page.on('pageerror', error => errors.push(error.message));
const check = async (id, action) => {
  try { await action(); results.push({ id, result: 'Pass' }); }
  catch (error) { results.push({ id, result: 'Fail', detail: error.message }); }
};
try {
  await check('APP-BROWSER-WEB', async () => {
    assert.equal((await web.goto('http://localhost:3000')).status(), 200);
    await web.getByRole('heading', { name: 'A little care. A big difference.' }).waitFor();
    await web.getByRole('button', { name: 'Classrooms', exact: true }).click();
    await web.getByRole('heading', { name: 'Classrooms', exact: true }).waitFor();
    await web.getByRole('button', { name: 'العربية', exact: true }).click();
    assert.equal(await web.locator('html').getAttribute('dir'), 'rtl');
    await web.getByRole('heading', { name: 'رعاية صغيرة. أثر كبير.' }).waitFor();
    await web.screenshot({ path: path.join(output, 'compiled-dashboard-ar.png'), fullPage: true });
    await web.getByRole('button', { name: 'English', exact: true }).click();
    await web.screenshot({ path: path.join(output, 'compiled-dashboard-en.png'), fullPage: true });
    await web.setViewportSize({ width: 390, height: 844 });
    assert.ok(await web.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  });
  await check('APP-BROWSER-MOBILE', async () => {
    assert.equal((await mobile.goto('http://localhost:3200')).status(), 200);
    await mobile.locator('flutter-view').waitFor({ state: 'attached', timeout: 60000 });
    const semantics = mobile.locator('flt-semantics-placeholder');
    if (await semantics.count()) await semantics.evaluate(element => element.click());
    await mobile.getByRole('button', { name: 'العربية', exact: true }).waitFor({ timeout: 30000 });
    assert.match(await mobile.locator('body').ariaSnapshot(), /A little closer, all day/);
    await mobile.screenshot({ path: path.join(output, 'compiled-mobile-en.png'), fullPage: true });
    await mobile.getByRole('button', { name: 'العربية', exact: true }).click();
    await mobile.getByRole('button', { name: 'English', exact: true }).waitFor();
    assert.match(await mobile.locator('body').ariaSnapshot(), /أقرب إلى طفلك/);
    await mobile.screenshot({ path: path.join(output, 'compiled-mobile-ar.png'), fullPage: true });
    assert.ok(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  });
  await check('APP-BROWSER-LINKS', async () => {
    const address = Object.entries(os.networkInterfaces()).flatMap(([name, values]) => (values ?? []).filter(a => a.family === 'IPv4' && !a.internal && !/virtual|vethernet/i.test(name)).map(a => a.address))[0];
    assert.ok(address, 'A physical LAN/Wi-Fi address is needed for the iPhone link');
    for (const port of [3000, 3200]) assert.ok((await fetch(`http://${address}:${port}`, { signal: AbortSignal.timeout(10000) })).ok);
    const js = await mobile.request.get('http://localhost:3200/flutter_bootstrap.js');
    assert.equal(js.status(), 200);
    assert.match(js.headers()['content-type'], /javascript/);
    for (const route of ['/.git/config', '/..%2F..%2Fpackage.json']) assert.equal((await mobile.request.get('http://localhost:3200' + route)).status(), 404);
    assert.deepEqual(errors, []);
  });
} finally {
  for (const [name, page] of [['web', web], ['mobile', mobile]]) {
    await fs.writeFile(path.join(output, `compiled-${name}-aria.txt`), await page.locator('body').ariaSnapshot());
  }
  await browser.close();
  const record = {
    startedAt, completedAt: new Date().toISOString(),
    codeCommit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    workingTreeChanges: execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim() || null,
    environment: 'Windows Chrome headless; 1440px desktop and 390px mobile emulation; software WebGL',
    scope: 'Actual Next.js and Flutter web foundation shells; no operational workflow acceptance',
    results, pageErrors: errors, physicalIPhone: 'Not run', nativeIOS: 'Not run', userAcceptance: 'Pending',
  };
  const file = path.join(root, 'docs/testing/runs', `${startedAt.replace(/[:.]/g, '-')}-compiled-browsers.json`);
  await fs.writeFile(file, JSON.stringify(record, null, 2) + '\n');
  console.log(JSON.stringify(record, null, 2));
  console.log(`Evidence: ${file}`);
  if (results.some(r => r.result === 'Fail')) process.exitCode = 1;
}
