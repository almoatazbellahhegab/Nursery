/** Browser evidence for prototypes only. Mobile viewport is not physical iPhone UAT. */
import { createRequire } from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createReviewServer, root } from './review-server.mjs';

const require = createRequire(import.meta.url);
const dependency = process.env.NURSERY_PLAYWRIGHT ?? path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { chromium } = require(dependency);
const output = path.join(root, 'test-results');
await fs.mkdir(output, { recursive: true });
const server = createReviewServer({ evidenceDirectory: path.join(output, 'browser-uat') });
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ headless: true, executablePath: process.env.NURSERY_CHROME ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const runs = [];
const errors = [];
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
page.on('pageerror', error => errors.push(error.message));
const check = async (id, uat, name, task) => {
  try { await task(); runs.push({ id, uat, name, result: 'Pass' }); }
  catch (error) { runs.push({ id, uat, name, result: 'Fail', detail: error.message }); }
};
try {
  await check('RV-005', ['UAT-S01-01', 'UAT-S01-03'], 'Desktop navigation and bilingual layout in headless Chrome on Windows', async () => {
    await page.goto(base + '/dashboard');
    await page.getByRole('heading', { name: 'A little care. A big difference.' }).waitFor();
    await page.getByRole('button', { name: 'Classrooms', exact: true }).click();
    await page.getByRole('heading', { name: 'Small rooms, big discoveries' }).waitFor();
    await page.getByRole('button', { name: 'Settings', exact: true }).click();
    await page.getByRole('heading', { name: 'Made for your nursery' }).waitFor();
    await page.getByRole('button', { name: 'العربية', exact: true }).click();
    assert.equal(await page.locator('html').getAttribute('dir'), 'rtl');
    await page.getByRole('heading', { name: 'مصممة لحضانتك' }).waitFor();
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.getByRole('button', { name: 'نظرة عامة', exact: true }).click();
    await page.screenshot({ path: path.join(output, 'dashboard-ar.png'), fullPage: true });
    await page.getByRole('button', { name: 'English', exact: true }).click();
    assert.equal(await page.locator('html').getAttribute('dir'), 'ltr');
    await page.screenshot({ path: path.join(output, 'dashboard-en.png'), fullPage: true });
    // Half-width reflow is supplemental coverage. Human browser zoom remains pending.
    await page.setViewportSize({ width: 720, height: 1100 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  });
  await check('RV-006', ['UAT-S01-02', 'UAT-S01-03'], 'Mobile 390px and 320px viewports, staff/parent navigation and RTL', async () => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(base + '/mobile');
    await page.getByRole('heading', { name: 'A little closer, all day.' }).waitFor();
    await page.locator('#role').selectOption('staff');
    await page.getByRole('heading', { name: 'More time for little moments.' }).waitFor();
    await page.getByRole('button', { name: 'Timeline', exact: true }).click();
    await page.getByRole('heading', { name: 'No operational records in this preview' }).waitFor();
    await page.getByRole('button', { name: 'Notices', exact: true }).click();
    await page.getByRole('heading', { name: 'Good things ahead' }).waitFor();
    await page.getByRole('button', { name: 'Home', exact: true }).click();
    await page.locator('#role').selectOption('parent');
    await page.screenshot({ path: path.join(output, 'mobile-en.png'), fullPage: true });
    await page.getByRole('button', { name: 'العربية', exact: true }).click();
    assert.equal(await page.locator('html').getAttribute('dir'), 'rtl');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: path.join(output, 'mobile-ar.png'), fullPage: true });
    for (const size of [{ width: 320, height: 568 }, { width: 844, height: 390 }]) {
      await page.setViewportSize(size);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.context().setOffline(true);
    await page.getByRole('status').filter({ hasText: 'غير متصل' }).waitFor();
    await page.context().setOffline(false);
  });
  await check('RV-007', ['UAT-S01-04', 'UAT-S01-05'], 'Plan-to-UAT mapping, safe saved observations and reload persistence', async () => {
    await page.setViewportSize({ width: 1440, height: 1100 });
    await page.goto(base);
    await page.getByText('41 features · 204 checklist items · 216 source tests').waitFor();
    assert.equal(await page.locator('details.sprint').count(), 4);
    await page.locator('#S01 > summary').click();
    await page.locator('#TC-FEAT-001-01 > summary').click();
    await page.getByText('UAT-S02-TC-FEAT-001-01', { exact: true }).waitFor();
    await page.getByText('UAT-S01-TC-FEAT-001-01', { exact: true }).waitFor();
    await page.locator('select[name=caseId]').selectOption('UAT-S01-05');
    await page.locator('select[name=device]').selectOption('Emulated mobile browser');
    const note = `<img src=x onerror="window.__injected=true"> synthetic browser check ${Date.now()}`;
    await page.locator('textarea[name=note]').fill(note);
    await page.getByRole('button', { name: 'Save review result' }).click();
    await page.getByText('Observation saved. Sprint approval remains pending.').waitFor();
    assert.equal(await page.evaluate(() => window.__injected), undefined);
    await page.reload();
    await page.getByText(note, { exact: true }).waitFor();
    assert.equal(await page.evaluate(() => window.__injected), undefined);
    await page.locator('#S01 > summary').click();
    await page.screenshot({ path: path.join(output, 'review.png'), fullPage: true });
    assert.deepEqual(errors, []);
  });
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
  const record = {
    recordedAt: new Date().toISOString(), codeCommit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    workingTreeChanges: execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim() || null,
    environment: { platform: process.platform, node: process.version, browser: 'Headless desktop Chrome; mobile viewport emulation only' },
    command: 'node tools/browser-checks.mjs', cases: runs, consoleErrors: errors, physicalIPhone: 'Not run', nativeIPhone: 'Blocked', userAcceptance: 'Pending',
  };
  await fs.writeFile(path.join(output, 'browser-run.json'), JSON.stringify(record, null, 2));
  console.log(JSON.stringify(record, null, 2));
  if (runs.some(r => r.result === 'Fail')) process.exitCode = 1;
}
