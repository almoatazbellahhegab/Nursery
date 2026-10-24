/** Canonical synthetic fixtures for both real clients; no operational seeding. */
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import { root } from './client-runtime.mjs';
import path from 'node:path';

const seed = JSON.parse(await fs.readFile(path.join(root, 'demo/seed.json'), 'utf8'));
assert.equal(seed.demoOnly, true);
function validateLabels(value) {
  if (!value || typeof value !== 'object') return;
  if ('en' in value && 'ar' in value) {
    assert.ok(value.en.trim() && /[\u0600-\u06ff]/u.test(value.ar), 'Every label needs English and Arabic text');
    assert.ok(!value.ar.includes('?'), 'Arabic text must survive UTF-8 generation');
  }
  for (const child of Object.values(value)) validateLabels(child);
}
validateLabels(seed);
for (const key of ['branches', 'classrooms', 'staff', 'children', 'guardians', 'invoices', 'leads', 'events', 'notices', 'scenarios']) {
  assert.equal(new Set(seed[key].map(row => row.id)).size, seed[key].length, `${key}: duplicate identifier`);
}
const find = (key, id) => { const row = seed[key].find(row => row.id === id); assert.ok(row, `${key}: missing ${id}`); return row; };
for (const child of seed.children) {
  assert.equal(find('classrooms', child.classroomId).branchId, child.branchId);
  find('guardians', child.guardianId);
}
for (const invoice of seed.invoices) {
  assert.equal(find('children', invoice.childId).branchId, invoice.branchId);
  assert.ok(Number.isInteger(invoice.amountMinor) && invoice.paidMinor >= 0 && invoice.paidMinor <= invoice.amountMinor);
}
for (const event of seed.events) {
  const child = find('children', event.childId);
  const staff = find('staff', event.staffId);
  assert.equal(child.branchId, event.branchId);
  assert.equal(staff.classroomId, child.classroomId);
}
for (const lead of seed.leads) assert.equal(find('staff', lead.ownerId).branchId, lead.branchId);
for (const group of ['classrooms', 'staff', 'children', 'invoices', 'leads', 'notices']) for (const row of seed[group]) find('branches', row.branchId);
assert.ok(seed.guardians.every(row => row.email.endsWith('@example.invalid')));

const web = path.join(root, 'apps/admin-web/app/demo-data.json');
const mobile = path.join(root, 'apps/mobile/lib/demo_data.dart');
const dart = `// Generated from demo/seed.json by tools/generate-demo.mjs.\n// Fictional presentation data only. No identity or production storage.\nconst demoSeedJson =\n    r'''${JSON.stringify(seed)}''';\n`;
if (process.argv.includes('--check')) {
  assert.deepEqual(JSON.parse(await fs.readFile(web, 'utf8')), seed);
  assert.equal(await fs.readFile(mobile, 'utf8'), dart);
} else {
  await fs.writeFile(web, JSON.stringify(seed, null, 2) + '\n');
  await fs.writeFile(mobile, dart);
}
console.log(`Demo fixtures verified: ${seed.branches.length} branches, ${seed.children.length} children, ${seed.invoices.length} invoices, ${seed.events.length} daily events; both clients match.`);
