/** Presentation-only experiments; never infer authorization from selected tabs. */
const response = await fetch('/messages.json');
const messages = await response.json();
const app = document.querySelector('#app');
const mobile = document.body.dataset.view === 'mobile';
const query = new URLSearchParams(location.search);
let locale = query.get('lang') === 'ar' ? 'ar' : 'en';
let tab = 'overview';
let role = 'parent';
const numbers = ['48', '42', '8', '3'];
const icons = { overview: '◫', classrooms: '✳', activity: '◷', settings: '⚙', home: '⌂', timeline: '◷', notices: '◇' };
function render() {
  const t = messages[locale];
  document.documentElement.lang = locale;
  document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr';
  const language = `<button class="language" id="language">${t.language}</button>`;
  const navigation = keys => keys.map(key => `<button data-tab="${key}" class="nav-item ${tab === key ? 'selected' : ''}" aria-current="${tab === key ? 'page' : 'false'}"><span aria-hidden="true">${icons[key]}</span>${t[key]}</button>`).join('');
  const rooms = `<div class="room-grid">${[1, 2, 3].map((n) => `<article class="room"><div class="room-art art-${n}" aria-hidden="true">${['☀', '✿', '❋'][n - 1]}</div><div class="room-body"><span class="eyebrow">${t[`age${n}`]}</span><h3>${t[`room${n}`]}</h3><p>${t.roomCount}</p></div></article>`).join('')}</div>`;
  const activity = `<div class="activity-list">${[1, 2, 3].map(n => `<article><span class="event-dot" aria-hidden="true">${['☀', '✎', '☾'][n - 1]}</span><div><h3>${t[`event${n}`]}</h3><p>${t.sampleEvent}</p></div></article>`).join('')}</div>`;
  const empty = `<div class="empty"><span aria-hidden="true">✳</span><h2>${t.empty}</h2><p>${t.emptySub}</p></div>`;
  if (!mobile) {
    app.innerHTML = `<div class="dashboard"><aside class="sidebar"><a href="/dashboard" class="brand">n<span class="brand-dot">✳</span> ${t.brand}</a><div class="org-block"><span class="org-icon" aria-hidden="true">H</span><div><strong>${t.org}</strong><small>${t.branch}</small></div></div><nav aria-label="${t.menu}">${navigation(['overview', 'classrooms', 'activity', 'settings'])}</nav><div class="sidebar-foot"><span class="leaf" aria-hidden="true">✳</span><p>${t.welcome}</p><small>${t.welcomeSub}</small><a href="/">← ${t.back}</a></div></aside><div class="workspace"><header class="topbar"><span>${t[tab]}</span><div>${language}<a href="/">${t.back} ↗</a></div></header><main class="dashboard-main"><p class="preview-label">${t.demo}</p><div class="page-title"><div><p class="eyebrow">${t.date}</p><h1>${tab === 'overview' ? t.greeting : t[tab]}</h1><p>${t.today}</p></div><span class="sun-mark" aria-hidden="true">☀</span></div>${tab === 'overview' ? `<section class="stats" aria-label="${t.sample}">${['children', 'present', 'team', 'rooms'].map((key, i) => `<article><span>${t[key]}</span><strong>${new Intl.NumberFormat(locale).format(Number(numbers[i]))}</strong><small>${t.sample}</small></article>`).join('')}</section>` : ''}${tab === 'overview' || tab === 'classrooms' ? `<section><div class="section-heading"><div><h2>${t.classroomTitle}</h2><p>${t.classroomSub}</p></div><span class="pill">${t.sample}</span></div>${rooms}</section>` : ''}${tab === 'overview' || tab === 'activity' ? `<section class="section"><h2>${t.activityTitle}</h2>${activity}</section>` : ''}${tab === 'settings' ? `<section class="settings-card"><h2>${t.settingsTitle}</h2><p>${t.settingsSub}</p><span class="pill">${t.coming}</span></section>` : ''}</main></div></div>`;
  } else {
    const selectedTab = tab === 'overview' ? 'home' : tab;
    tab = selectedTab;
    app.innerHTML = `<div class="mobile-shell"><header class="mobile-header"><a href="/" class="brand">✳ ${t.brand}</a>${language}</header><main class="mobile-main"><p class="preview-label">${t.demo}</p><label class="role-picker">${t.role}<select id="role"><option value="parent" ${role === 'parent' ? 'selected' : ''}>${t.parent}</option><option value="staff" ${role === 'staff' ? 'selected' : ''}>${t.staff}</option></select></label><div class="mobile-greeting"><p>${role === 'parent' ? t.hello : t.staffHello}</p><h1>${role === 'parent' ? t.parentHeading : t.staffHeading}</h1><p>${role === 'parent' ? t.parentSub : t.staffSub}</p><span aria-hidden="true">☀</span></div>${selectedTab === 'home' ? `<article class="child-card"><span class="avatar" aria-hidden="true">✿</span><div><h2>${role === 'parent' ? t.child : t.room1}</h2><p>${t.childRoom}</p></div></article><section class="section"><h2>${role === 'parent' ? t.day : t.staffDay}</h2>${activity}</section>` : selectedTab === 'notices' ? `<section class="notice"><h2>${t.noticeTitle}</h2><p>${t.noticeText}</p></section>` : empty}<p class="connectivity" role="status">${navigator.onLine ? t.online : t.offline}</p><a class="mobile-review" href="/">← ${t.back}</a></main><nav class="bottom-nav" aria-label="${t.menu}">${navigation(['home', 'timeline', 'notices'])}</nav></div>`;
  }
  document.querySelector('#language').onclick = () => {
    locale = locale === 'en' ? 'ar' : 'en';
    history.replaceState(null, '', `${location.pathname}?lang=${locale}`);
    render();
    document.querySelector('#language').focus();
  };
  for (const item of document.querySelectorAll('[data-tab]')) item.onclick = () => { tab = item.dataset.tab; render(); document.querySelector(`[data-tab="${tab}"]`).focus(); };
  const selector = document.querySelector('#role');
  if (selector) selector.onchange = () => { role = selector.value; render(); document.querySelector('#role').focus(); };
}
render();
window.addEventListener('online', render);
window.addEventListener('offline', render);
