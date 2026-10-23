/** Supplemental preview tests, deliberately separate from product acceptance. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createReviewServer, root, validateResult } from '../../tools/review-server.mjs';

test('RV-001 preserves every source feature, checklist item and acceptance case exactly once', async () => {
  const raw = JSON.parse((await fs.readFile(path.join(root, 'docs/source/catalogue.json'), 'utf8')).replace(/^\uFEFF/, ''));
  const plan = JSON.parse(await fs.readFile(path.join(root, 'docs/delivery/plan.json'), 'utf8'));
  const sources = [['Release Roadmap', 'features', /^FEAT-/], ['Feature Checklist', 'todos', /^DEV-/], ['Technical Work', 'technical', /^TW-/], ['Test Catalogue', 'cases', /^(TC-|XCT-|TECH-)/]];
  for (const [sheet, key, regex] of sources) {
    const ids = raw[sheet].slice(4).map(row => (row.value ?? row)[0]).filter(id => regex.test(id)).sort();
    assert.deepEqual(plan[key].map(item => item.id).sort(), ids);
    assert.equal(new Set(ids).size, ids.length);
    for (const item of plan[key]) assert.ok(plan.sprints.some(s => s.id === item.sprint));
  }
  for (const item of plan.cases) {
    assert.ok(item.uat.includes(item.id));
    assert.equal(item.status, 'Not run');
    assert.equal(item.evidence, null);
  }
  for (const feature of plan.features) {
    for (const dependency of feature.dependencies.match(/FEAT-\d+/g) ?? []) {
      const previous = plan.features.find(f => f.id === dependency);
      assert.ok(previous);
      assert.ok(previous.sprint <= feature.sprint, `${feature.id} precedes ${dependency}`);
    }
  }
});

test('RV-002 requires matching bilingual keys and rejects blank translation entries', async () => {
  const catalogue = JSON.parse(await fs.readFile(path.join(root, 'tools/review/messages.json'), 'utf8'));
  assert.deepEqual(Object.keys(catalogue.en).sort(), Object.keys(catalogue.ar).sort());
  for (const [locale, messages] of Object.entries(catalogue)) for (const [key, text] of Object.entries(messages)) assert.ok(text.trim(), `${locale}.${key}`);
});

test('RV-003 rejects unknown cases, oversized notes and misleading native passes', () => {
  const valid = { caseId: 'UAT-S01-01', device: 'Windows 11 browser', result: 'Pass', note: 'Synthetic preview checked.' };
  assert.ok(validateResult(valid));
  assert.equal(validateResult({ ...valid, caseId: 'TC-FEAT-001-01' }), false);
  assert.equal(validateResult({ ...valid, device: 'Native iPhone app' }), false);
  assert.ok(validateResult({ ...valid, device: 'Native iPhone app', result: 'Blocked' }));
  assert.equal(validateResult({ ...valid, note: 'a'.repeat(1001) }), false);
});

test('RV-004 serves only explicit public routes and prevents cross-origin or invalid evidence writes', async t => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'nursery-review-'));
  const server = createReviewServer({ evidenceDirectory: directory });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  t.after(async () => {
    await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    // The generated temporary path is checked before recursive cleanup.
    assert.ok(directory.startsWith(path.join(os.tmpdir(), 'nursery-review-')));
    await fs.rm(directory, { recursive: true, force: true });
  });
  for (const route of ['/', '/dashboard', '/mobile', '/review/plan', '/messages.json']) {
    const response = await fetch(origin + route);
    assert.equal(response.status, 200);
    assert.ok(response.headers.get('content-security-policy').includes("default-src 'self'"));
  }
  for (const route of ['/Document/Childcare_Platform_Technical_Design.docx', '/.git/config', '/docs/source/catalogue.json', '/%2e%2e/package.json', '/api/v1/children']) assert.equal((await fetch(origin + route)).status, 404);
  const value = { caseId: 'UAT-S01-05', device: 'Windows 11 browser', result: 'Pass', note: '<script>synthetic</script>' };
  const post = (body, requestOrigin = origin) => fetch(origin + '/review/uat', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: requestOrigin }, body });
  assert.equal((await post(JSON.stringify(value), 'https://unrelated.invalid')).status, 403);
  assert.equal((await post('invalid')).status, 400);
  assert.equal((await post(JSON.stringify({ ...value, caseId: 'unrelated' }))).status, 422);
  assert.equal((await post(JSON.stringify({ ...value, note: 'a'.repeat(9000) }))).status, 413);
  for (let n = 0; n < 2; n++) assert.equal((await post(JSON.stringify(value))).status, 201);
  const records = await (await fetch(origin + '/review/results')).json();
  assert.equal(records.length, 2);
  assert.equal(records[0].note, value.note);
  assert.notEqual(records[0].id, records[1].id);
  assert.ok(records.every(r => r.recordedAt.endsWith('Z')));
  assert.equal((await fs.readFile(path.join(directory, 'uat.jsonl'), 'utf8')).trim().split('\n').length, 2);
});
