/** Preserve source identifiers while allocating delivery and acceptance work. */
import fs from 'node:fs';
const raw = JSON.parse(fs.readFileSync('docs/source/catalogue.json', 'utf8').replace(/^\uFEFF/, ''));
const rows = name => raw[name].slice(4).map(row => row.value ?? row);
const definitions = [
  ['S01', 'Review foundations', [], 'Review portal, bilingual interface prototypes, stack skeletons and traceability. Production builds are blocked by dependency access.', 'Windows and iPhone review flows visible; prototype checks pass; physical device UAT remains pending.'],
  ['S02', 'Tenant and access foundations', [1, 2, 3, 5, 34], 'Organization, branches, identity, server authorization and append-only audit.', 'Allowed and denied API journeys, real PostgreSQL RLS and suspension tests pass.'],
  ['S03', 'People and classroom setup', [4, 7, 8, 10, 9], 'Invitations, children, guardian relationships, staff and classrooms.', 'Administrator sets up a synthetic center; staff and parents see only permitted records.'],
  ['S04', 'Privacy and platform controls', [35, 6, 36, 37], 'Consent and lifecycle, audited support, full localization and plan/module controls.', 'Privacy review, support expiry, disabled-module denial and bilingual journeys pass.'],
  ['S05', 'Attendance and daily care', [11, 13, 14], 'Attendance, timeline, batch entry and encrypted offline command recovery.', 'Staff completes a classroom day; retry and conflict tests show no silent loss or duplication.'],
  ['S06', 'Parent engagement and Phase 1 acceptance', [16, 17, 18, 19, 15, 41], 'Announcements, notification ledger, calendar, search, parent home and complete demo.', 'A representative center completes a full day in English and Arabic.'],
  ['S07', 'Phase 1 release hardening', [], 'Security, accessibility, performance, resilience, backup restore and operational UAT.', 'Blocking release controls pass with named specialist signoffs and rollback evidence.'],
  ['S08', 'Pickup and incidents', [20, 21, 24], 'Standing/temporary pickup, atomic checkout and incident acknowledgement.', 'Safeguarding owner accepts identity, replay, escalation and acknowledgement scenarios.'],
  ['S09', 'Private media and messaging', [22, 23], 'Consent-aware media and scoped conversations with private attachments.', 'Revoked-consent, unrelated-child and unauthorized-participant denial tests pass.'],
  ['S10', 'Billing and payment reminders', [26, 27, 29], 'Fee rules, invoices, immutable balances and reminder delivery.', 'Finance accepts minor-unit calculations, corrections, access filtering and balances.'],
  ['S11', 'Payments and reconciliation', [28], 'Provider adapter, signature/replay checks and settlement reconciliation.', 'Finance/security accept duplicate and out-of-order webhooks and reconciled settlement.'],
  ['S12', 'Admissions and operational analytics', [30, 31, 32], 'Admissions pipeline, waiting list and approved metric projections.', 'Operations accepts capacity and metric definitions; Phase 2 release tests pass.'],
  ['S13', 'Later approved modules', [25, 33, 38], 'Medication, transportation and platform KPIs; scope requires separate approval.', 'Medical, transport, privacy and metric owners approve before implementation.'],
  ['S14', 'Optional future modules', [12, 39, 40], 'Staff attendance, community and commerce; scope requires separate approval.', 'Separate product case, safeguards and feature acceptance are approved.'],
];
const featureId = n => `FEAT-${String(n).padStart(3, '0')}`;
const legacySprints = definitions.map(([id, title, numbers, milestone, exit]) => ({ id, title, features: numbers.map(featureId), milestone, exit }));
const sprintFor = id => legacySprints.find(s => s.features.includes(id))?.id ?? 'S07';
const features = rows('Release Roadmap').filter(r => /^FEAT-/.test(r[0])).map(r => ({ id: r[0], title: r[1], release: r[2], dependencies: r[4], sprint: sprintFor(r[0]), branch: `feat/${r[0]}-${r[1].toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-$/, '')}`, status: 'Not started' }));
features.find(f => f.id === 'FEAT-036').branch = 'feat/FEAT-036-localization-foundation';
features.find(f => f.id === 'FEAT-036').status = 'Groundwork only; full feature acceptance pending S01';
const todos = rows('Feature Checklist').filter(r => /^DEV-/.test(r[0])).map(r => ({ id: r[0], feature: r[1], title: r[5], dependencies: r[6], sprint: sprintFor(r[1]), status: 'Not started' }));
function technicalSprint(id) {
  const n = Number(id.slice(3));
  if ([6, 10, 11, 12, 13, 14, 20, 30, 34, 35].includes(n)) return 'S01';
  if (n <= 10) return 'S02';
  if ([15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 28, 31, 32, 36].includes(n)) return 'S02';
  if ([26, 37].includes(n)) return 'S03';
  if ([27, 29, 33].includes(n)) return 'S04';
  if (n >= 38 && n <= 42) return 'S05';
  if (n <= 45) return 'S06';
  if (n <= 55) return 'S07';
  if ([56, 59].includes(n)) return 'S08';
  if ([57, 58].includes(n)) return 'S09';
  if (n === 60) return 'S10';
  if (n === 61) return 'S11';
  if (n <= 64) return 'S12';
  return n <= 67 ? 'S13' : 'S14';
}
const technical = rows('Technical Work').filter(r => /^TW-/.test(r[0])).map(r => ({ id: r[0], title: r[3], evidence: r[4], dependencies: r[5], owner: r[6], sprint: technicalSprint(r[0]), status: 'Not started' }));
for (const item of technical) {
  if (['TW-011', 'TW-013', 'TW-030', 'TW-034', 'TW-035'].includes(item.id)) item.status = 'Partial groundwork; production builds or prerequisites blocked';
  if (item.id === 'TW-020') item.status = 'Partial synthetic preview fixtures; operational scenario seeding not started';
}
const cases = rows('Test Catalogue').filter(r => /^(TC-|XCT-|TECH-)/.test(r[0])).map(r => ({ id: r[0], requirement: r[1], area: r[2], release: r[3], type: r[4], priority: r[5], preconditions: r[6], steps: r[7], expected: r[8], target: r[9], sprint: sprintFor(r[1]), uat: `UAT-${sprintFor(r[1])}-${r[0]}`, status: 'Not run', evidence: null }));
for (const item of cases) item.repeatEachAffectedSprint = item.requirement === 'CROSS-CUTTING' || item.requirement === 'TECHNICAL';
const controls = rows('Release Controls').filter(r => r[0]).map(r => ({ id: r[0], source: r, status: 'Not run' }));
const decisions = rows('Decisions Risks').filter(r => r[0]).map(r => ({ id: r[0], type: r[1], question: r[2], impact: r[3], requiredBy: r[4], owner: r[5], status: r[6] }));
// Consolidate scheduling only. Legacy work packages retain all original milestones
// and exit criteria; stable UAT IDs keep prior evidence links valid.
const groups = [
  ['S01', 'Platform foundations and nursery setup', ['S01', 'S02', 'S03', 'S04'], 'Working web and Flutter foundations, secure tenant/identity boundaries, nursery setup, privacy, localization and platform controls.', 'All constituent exit criteria pass; actual client builds and Windows 11/iPhone checks are evidenced.'],
  ['S02', 'Daily operations and Phase 1 release', ['S05', 'S06', 'S07'], 'Attendance, daily care, offline recovery, parent engagement, complete demo and Phase 1 release hardening.', 'A full nursery day completes in Arabic and English; security, accessibility, resilience, restoration, rollback and specialist UAT pass.'],
  ['S03', 'Safety, communication, finance and growth', ['S08', 'S09', 'S10', 'S11', 'S12'], 'Pickup, incidents, private media, messaging, billing, payments, admissions, capacity and operational analytics.', 'Safeguarding, privacy and finance journeys pass; payments reconcile and Phase 2 end-to-end acceptance is complete.'],
  ['S04', 'Advanced and optional modules', ['S13', 'S14'], 'Medication, transport, platform KPIs, staff attendance, community and commerce readiness, subject to the original separate approvals.', 'Separate product and specialist approvals precede affected implementation; all approved feature tests and web/mobile UAT pass.'],
];
const sprints = groups.map(([id, title, previousSprints, milestone, exit]) => ({
  id, title, previousSprints,
  features: legacySprints.filter(s => previousSprints.includes(s.id)).flatMap(s => s.features),
  milestone, exit,
  workPackages: legacySprints.filter(s => previousSprints.includes(s.id)),
  status: id === 'S01' ? 'In progress — environment blocked' : id === 'S04' ? 'Requires separate approval' : 'Planned',
  approval: 'Pending',
  duration: 'To be estimated from unchanged scope, team capacity and gates; no committed duration or dates',
}));
const consolidatedSprint = previous => sprints.find(s => s.previousSprints.includes(previous)).id;
for (const collection of [features, todos, technical, cases]) {
  for (const item of collection) {
    item.previousSprint = item.sprint;
    item.sprint = consolidatedSprint(item.previousSprint);
  }
}
for (const item of cases) item.currentUat = `UAT-${item.sprint}-${item.id}`;
const data = { baseline: '2026-10-23', planRevision: 'four-sprint-consolidation', previousPlan: 'baselines/14-sprint-plan.json', sprints, features, todos, technical, cases, controls, decisions };
fs.mkdirSync('docs/delivery', { recursive: true });
fs.writeFileSync('docs/delivery/plan.json', JSON.stringify(data, null, 2) + '\n');
const overview = '| Sprint | Scope | Features | Feature tasks | Technical tasks | Source tests |\n| --- | --- | ---: | ---: | ---: | ---: |\n' + sprints.map(s => `| ${s.id} | ${s.title} | ${features.filter(f => f.sprint === s.id).length} | ${todos.filter(t => t.sprint === s.id).length} | ${technical.filter(t => t.sprint === s.id).length} | ${cases.filter(t => t.sprint === s.id).length} |`).join('\n');
fs.writeFileSync('docs/delivery/SPRINTS.md', '# Four sprint milestones and itemized work\n\nSource: all four unchanged files in Document. All 41 features, 204 feature tasks, 69 technical tasks, 216 source tests, dependencies, decision gates and release controls are retained. The original 14 milestones remain ordered work packages inside four sprints. Duration is to be estimated; consolidation does not imply an eight-week commitment. Preserve dependencies within each sprint. Enabling experiments do not complete operational features. TW-006 and TW-010 remain open decisions.\n\n' + overview + '\n\n' + sprints.map(s => `## ${s.id} ${s.title}\n\n${s.milestone}\n\nExit: ${s.exit}\n\nApproval: pending. ${s.duration}.\n\n### Retained milestone work packages\n\n` + s.workPackages.map(p => `- Original ${p.id}: ${p.title}. ${p.milestone} Exit: ${p.exit}`).join('\n') + '\n\n### Features\n\n' + features.filter(f => f.sprint === s.id).map(f => `- [ ] ${f.id} ${f.title} — depends on ${f.dependencies}; branch \`${f.branch}\``).join('\n') + '\n\n### Technical tasks\n\n' + technical.filter(t => t.sprint === s.id).map(t => `- [ ] ${t.id} ${t.title} — depends on ${t.dependencies}; owner ${t.owner}`).join('\n') + '\n\n### Feature tasks\n\n' + todos.filter(t => t.sprint === s.id).map(t => `- [ ] ${t.id} ${t.title}`).join('\n')).join('\n\n') + '\n\nStable UAT identifiers and evidence links are retained. Each source case additionally has a currentUat alias for its new sprint. Cross-cutting and technical tests repeat in each affected sprint and reach final Phase 1 verification in S02. Separate approvals for advanced/future modules remain mandatory in S04.\n');
console.log(JSON.stringify({ features: features.length, todos: todos.length, technical: technical.length, cases: cases.length }));
