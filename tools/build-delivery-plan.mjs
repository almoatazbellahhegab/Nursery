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
const sprints = definitions.map(([id, title, numbers, milestone, exit]) => ({ id, title, features: numbers.map(featureId), milestone, exit, status: id === 'S01' ? 'In progress — environment blocked' : Number(id.slice(1)) > 12 ? 'Requires separate approval' : 'Planned', approval: 'Pending', duration: 'Planning envelope: 2 weeks; re-estimate after refinement; no committed dates' }));
const sprintFor = id => sprints.find(s => s.features.includes(id))?.id ?? 'S07';
const features = rows('Release Roadmap').filter(r => /^FEAT-/.test(r[0])).map(r => ({ id: r[0], title: r[1], release: r[2], dependencies: r[4], sprint: sprintFor(r[0]), branch: `feat/${r[0]}-${r[1].toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-$/, '')}`, status: 'Not started' }));
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
const cases = rows('Test Catalogue').filter(r => /^(TC-|XCT-|TECH-)/.test(r[0])).map(r => ({ id: r[0], requirement: r[1], area: r[2], release: r[3], type: r[4], priority: r[5], preconditions: r[6], steps: r[7], expected: r[8], target: r[9], sprint: sprintFor(r[1]), uat: `UAT-${sprintFor(r[1])}-${r[0]}`, status: 'Not run', evidence: null }));
const controls = rows('Release Controls').filter(r => r[0]).map(r => ({ id: r[0], source: r, status: 'Not run' }));
const decisions = rows('Decisions Risks').filter(r => r[0]).map(r => ({ id: r[0], type: r[1], question: r[2], impact: r[3], requiredBy: r[4], owner: r[5], status: r[6] }));
const data = { baseline: '2026-10-23', sprints, features, todos, technical, cases, controls, decisions };
fs.mkdirSync('docs/delivery', { recursive: true });
fs.writeFileSync('docs/delivery/plan.json', JSON.stringify(data, null, 2) + '\n');
fs.writeFileSync('docs/delivery/SPRINTS.md', '# Sprint milestones and itemized work\n\nSource: all four unchanged files in Document. Two-week planning envelopes are provisional; no dates are committed. Preserve dependencies inside each sprint. Enabling localization and UI experiments in S01 do not complete FEAT-036, TW-034 or TW-035. TW-006 and TW-010 remain open decisions.\n\n' + sprints.map(s => `## ${s.id} ${s.title}\n\n${s.milestone}\n\nExit: ${s.exit}\n\nApproval: pending. ${s.duration}.\n\n` + features.filter(f => f.sprint === s.id).map(f => `- [ ] ${f.id} ${f.title} — depends on ${f.dependencies}; branch \`${f.branch}\``).join('\n') + '\n\n' + technical.filter(t => t.sprint === s.id).map(t => `- [ ] ${t.id} ${t.title} — depends on ${t.dependencies}; owner ${t.owner}`).join('\n') + '\n\n' + todos.filter(t => t.sprint === s.id).map(t => `- [ ] ${t.id} ${t.title}`).join('\n')).join('\n\n') + '\n');
console.log(JSON.stringify({ features: features.length, todos: todos.length, technical: technical.length, cases: cases.length }));
