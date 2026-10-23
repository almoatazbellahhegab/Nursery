/** Display the preserved delivery baseline and append explicit human observations. */
const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const uat = [
  ['UAT-S01-01', 'Open dashboard on Windows 11', 'Open dashboard; navigate Overview, Classrooms, Activity and Settings. Confirm no clipped content or misleading operational actions.', 'TW-034 (prototype only)'],
  ['UAT-S01-02', 'Review mobile on a physical iPhone', 'Open the printed Wi-Fi URL in Safari, then Mobile preview. Switch Parent/Staff and all bottom tabs. Verify readable text and touch targets.', 'TW-035 (browser prototype only)'],
  ['UAT-S01-03', 'Switch English and Arabic', 'In both previews switch language. Check direction, focus, mixed numbers and 200% zoom. Arabic owner reviews wording.', 'TC-FEAT-036-01, TC-FEAT-036-02, XCT-09 (partial preview coverage)'],
  ['UAT-S01-04', 'Trace work to acceptance', 'Open a sprint; locate a DEV item and a source TC. Verify its exact expected result and linked UAT ID against the workbook.', 'TW-011, delivery traceability'],
  ['UAT-S01-05', 'Verify review log persistence', 'Save an observation, reload, then download the UAT log. Confirm device, case ID, time and result are preserved. Do not enter private data.', 'Sprint review process'],
  ['UAT-S01-06', 'Native iPhone build', 'Blocked: Flutter SDK/dependencies, macOS/Xcode, signing and device build are unavailable. Browser preview cannot pass this check.', 'TW-035 native build (blocked)'],
];
let records = [];
const form = document.querySelector('#result-form');
form.elements.caseId.innerHTML = uat.map(([id, title]) => `<option value="${id}">${id} · ${title}</option>`).join('');
document.querySelector('#uat-cases').innerHTML = uat.map(([id, title, steps, link]) => `<article class="uat-row" id="${id}"><strong>${id} · ${title}</strong><p>${steps}</p><small>${link}</small></article>`).join('');
async function refreshResults() {
  const response = await fetch('/review/results');
  if (!response.ok) throw new Error('Could not load saved results.');
  records = await response.json();
  document.querySelector('#results').innerHTML = `<h3>${records.length} recorded observations</h3>` + records.slice().reverse().map(r => `<article class="uat-row"><strong>${escape(r.caseId)} · ${escape(r.result)}</strong><p>${escape(r.device)} · ${escape(r.recordedAt)}</p><p>${escape(r.note)}</p></article>`).join('');
}
try {
  const response = await fetch('/review/plan');
  if (!response.ok) throw new Error('Could not load the delivery plan.');
  const plan = await response.json();
  document.querySelector('#counts').textContent = `${plan.features.length} features · ${plan.todos.length} checklist items · ${plan.cases.length} source tests`;
  document.querySelector('#sprints').innerHTML = plan.sprints.map(s => {
    const features = plan.features.filter(f => f.sprint === s.id);
    const tasks = plan.todos.filter(t => t.sprint === s.id);
    const technical = plan.technical.filter(t => t.sprint === s.id);
    const cases = plan.cases.filter(t => t.sprint === s.id);
    return `<details class="sprint" id="${s.id}"><summary><span class="sprint-id">${s.id}</span><strong>${escape(s.title)}</strong><span class="sprint-status">${escape(s.status)}</span></summary><div class="sprint-body"><p>${escape(s.milestone)}</p><p><strong>Exit milestone:</strong> ${escape(s.exit)}</p><p class="muted">${escape(s.duration)}. Approval pending.</p><h3>Feature branches</h3><ul>${features.map(f => `<li>${escape(f.id)} · ${escape(f.title)}<br><small>Depends on ${escape(f.dependencies)}</small><br><code>${escape(f.branch)}</code></li>`).join('') || '<li>Enabling work; no full product feature claimed.</li>'}</ul><h3>Itemized work</h3><ul>${[...technical, ...tasks].map(t => `<li><strong>${escape(t.id)}</strong> ${escape(t.title)} <small>· ${escape(t.status)} · depends on ${escape(t.dependencies)}</small></li>`).join('')}</ul><h3>Source tests and linked UAT</h3>${cases.map(c => `<details class="source-case" id="${escape(c.id)}"><summary>${escape(c.id)} · ${escape(c.area)} · ${escape(c.status)}</summary><p><strong>Precondition:</strong> ${escape(c.preconditions)}</p><p class="preserve">${escape(c.steps)}</p><p><strong>Expected:</strong> ${escape(c.expected)}</p><p><strong>UAT:</strong> <span id="${escape(c.uat)}">${escape(c.uat)}</span> · Pending manual acceptance</p><p>${escape(c.priority)} · ${escape(c.target)}</p></details>`).join('') || '<p>See the supplemental S01 preview checklist below. Source product tests remain Not run.</p>'}</div></details>`;
  }).join('');
  await refreshResults();
} catch (error) { document.querySelector('#counts').textContent = error.message; }
form.onsubmit = async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  const status = document.querySelector('#save-status');
  button.disabled = true;
  try {
    const result = await fetch('/review/uat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(form))) });
    if (!result.ok) throw new Error(result.status === 422 ? 'Native iPhone checks must remain Blocked until a real build is available.' : 'Result could not be saved. Please retry.');
    status.textContent = 'Observation saved. Sprint approval remains pending.';
    await refreshResults();
  } catch (error) { status.textContent = error.message; }
  finally { button.disabled = false; }
};
document.querySelector('#export').onclick = () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(records, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a'); link.href = url; link.download = 'S01-uat-observations.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
