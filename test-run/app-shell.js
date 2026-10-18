/* ---------- app shell: role and phase menu, phase tag, top-bar tools, permissions ---------- */
(() => {
  // three roles on one event (brief: one event, three phase lenses; "Role switch or delegated role")
  const ROLES = {
    ic: { name: 'Ananya Menon', role: 'Incident Commander', org: 'DDMA Wayanad', ini: 'AM', home: 'respond', scope: 'all phases, approves' },
    analyst: { name: 'Dr. Rahul Nair', role: 'Hazard Analyst', org: 'DEOC Wayanad', ini: 'RN', home: 'prepare', scope: 'recommends to the IC' },
    coord: { name: 'Sreeja Thomas', role: 'Relief & Recovery Coordinator', org: 'DDMA Wayanad', ini: 'ST', home: 'recover', scope: 'escalates to the IC' }
  };
  const RKEY = 'ro.role';
  const ls = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  const roleId = ROLES[ls.get(RKEY)] ? ls.get(RKEY) : 'ic', R = ROLES[roleId];

  // phase: from the link, else the role's home
  // a view (Timeline · Reports · Audit) or a phase; views are event-wide
  const qs = new URLSearchParams(location.search);
  const view = window.VIEWS && VIEWS[qs.get('view')] ? qs.get('view') : null;
  const asked = qs.get('phase');
  const phase = view ? null : (PHASES[asked] ? asked : R.home);
  const ORDER = ['prepare', 'respond', 'recover'];
  const PH = {
    prepare: { label: 'Prepare', sub: 'Before the storm · readiness plan' },
    respond: { label: 'Respond', sub: 'During the event · rescue and dispatch' },
    recover: { label: 'Recover', sub: 'After · relief, restoration, lessons' }
  };
  // under each tile: name, a short purpose, one status chip. The current phase's count keeps the id each phase script updates
  const NOW = {
    prepare: '<span class="rs-tail"> · <span id="nav-count">5</span> to approve</span>',
    respond: '<span class="rs-tail"> · 3 critical</span>',
    recover: '<span class="rs-tail"> · <span id="nav-count">6</span> unserved</span>'
  };
  const DONE = { prepare: 'Day 0, 07:05', respond: 'Day 1, 08:00' };
  const PURPOSE = { prepare: 'Before the storm', respond: 'During the event', recover: 'After the event' };
  const RS = {  // one chip: what the role can do, and where
    ic: { short: 'Commander', can: 'Approves · all phases', note: 'You can approve tasks.' },
    analyst: { short: 'Analyst', can: 'Recommends · Prepare, Respond', note: 'You can recommend; the IC approves.' },
    coord: { short: 'Coordinator', can: 'Escalates · Recover', note: 'You can escalate to the IC.' }
  };

  /* ---------- account menu (small) → phase or role dialog over the blurred app ---------- */
  // built before the phase runs: phase scripts badge the tiles (#nav-prepare, #nav-respond, #nav-count)
  const cur = ORDER.indexOf(phase || window.RO_ASOF?.phase || 'recover');  // on a view, the phase it's shown as of
  const curPh = ORDER[cur];
  const OK = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5.5 10.4 8.6 13.4 14.6 7"/></svg>';
  const X = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
  const art = k => (window.RO_ART?.[k] || '').replace(/ role="img" aria-label="[^"]*"/, ' aria-hidden="true" focusable="false"');
  const phaseTile = (ph, j) => {
    const st = j < cur ? 'done' : j === cur ? 'now' : 'next';
    const status = st === 'done' ? `${OK}Done · ${DONE[ph]}` : st === 'now' ? `<b>Now</b>${NOW[ph]}` : 'Next · not active yet';
    return `<li><button class="rs-tile" type="button" id="nav-${ph}" data-pick="${ph}" data-accent="${ph}" style="--i:${j}"${st === 'now' ? ' aria-current="true"' : ''} aria-describedby="nav-${ph}-d">
      <span class="rs-stage">${st === 'now' ? `<span class="rs-here">${view ? 'Current phase' : 'You’re here'}</span>` : ''}${art(ph)}</span>
      <span class="rs-name"><i class="dot" aria-hidden="true"></i>${PH[ph].label}<span class="sr-only" id="nav-${ph}-sr"></span></span>
      <span class="rs-desc" id="nav-${ph}-d"><span>${PURPOSE[ph]}</span><span class="rs-status rs-${st}">${status}</span></span></button></li>`;
  };
  const roleTile = ([id, r], j) => `<li><button class="rs-tile" type="button" data-pick="${id}" data-accent="${id}" style="--i:${j}"${id === roleId ? ' aria-current="true"' : ''} aria-describedby="rs-${id}-d">
      <span class="rs-stage">${id === roleId ? '<span class="rs-here">You’re signed in</span>' : ''}${art(id)}</span>
      <span class="rs-name"><span class="rs-ini" aria-hidden="true">${r.ini}</span>${r.name}</span>
      <span class="rs-desc" id="rs-${id}-d"><span>${r.role}</span><span class="rs-status rs-can">${RS[id].can}</span></span></button></li>`;
  const dlg = (kind, title, lede, tiles, foot, closeLabel) => `<div class="rs-scrim" id="rs-${kind}" aria-hidden="true">
    <section class="rs-dlg" role="dialog" aria-modal="true" aria-labelledby="rs-${kind}-h" aria-describedby="rs-${kind}-l">
      <button class="rs-x" type="button" data-close aria-label="${closeLabel}">${X}</button>
      <p class="rs-eyebrow">${kind === 'phase' ? 'WYN-2026-001 · Landslide &amp; flash flood' : 'Role · event WYN-2026-001'}</p>
      <h2 id="rs-${kind}-h">${title}</h2><p class="rs-lede" id="rs-${kind}-l">${lede}</p>
      <ul class="rs-tiles">${tiles}</ul><footer class="rs-foot">${foot}</footer></section></div>`;
  document.body.insertAdjacentHTML('beforeend', `<div class="role-menu am" id="role-menu" role="menu" aria-label="Account" hidden>
    <div class="am-who" aria-hidden="true"><b>${R.name}</b><span>${R.role} · ${R.org}</span></div>
    <button class="am-item" type="button" role="menuitem" tabindex="-1" data-open="phase" aria-haspopup="dialog">Switch phase<small id="am-phase">${PH[curPh].label}</small></button>
    <button class="am-item" type="button" role="menuitem" tabindex="-1" data-open="role" aria-haspopup="dialog">Switch role<small>${RS[roleId].short}</small></button>
    <div class="am-sep" role="separator"></div>
    <a class="am-item" role="menuitem" tabindex="-1" href="field.html">Open the field app (phone)</a></div>`
    + dlg('phase', 'Which phase?', 'Same event, a different lens. You can switch back at any time.', ORDER.map(phaseTile).join(''),
      `<span><b>${R.name}</b> · ${R.role}</span><button type="button" data-swap="role">Switch role</button>`, `Close and stay in ${view ? 'this page' : PH[curPh].label}`)
    + dlg('role', 'Who’s working?', 'Each role sees the event its own way and can do different things.', Object.entries(ROLES).map(roleTile).join(''),
      `<span>Viewing <b>${view ? (document.getElementById('view-' + view)?.dataset.title || 'this page') : PH[curPh].label}</b></span><button type="button" data-swap="phase">Switch phase</button>`, `Close and stay as ${R.name}`));

  const tpl = document.getElementById(view ? 'view-' + view : 'ph-' + phase);
  document.title = tpl.dataset.title + ' · ResilienceOps';
  if (tpl.dataset.bodyClass) document.body.className = tpl.dataset.bodyClass;
  document.body.prepend(tpl.content.cloneNode(true));
  document.querySelectorAll('body > template').forEach(t => t.remove());
  view ? VIEWS[view]() : PHASES[phase]();
  window.RO_MOTION?.watchSwaps();
  if (view) document.querySelector(`.nav a[href="?view=${view}"]`)?.setAttribute('aria-current', 'page');
  // way back: remember the last phase you worked in; the logo and a back link on views return there
  const LAST = 'ro.lastPhase', ss = { get: k => { try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) {} } };
  if (phase) ss.set(LAST, phase);
  const back = PHASES[ss.get(LAST)] ? ss.get(LAST) : R.home;
  const brand = document.querySelector('.brand');
  if (brand) { brand.href = '?phase=' + (phase || back); brand.setAttribute('aria-label', `ResilienceOps, back to ${(phase || back)[0].toUpperCase() + (phase || back).slice(1)}`); }
  // Timeline, Reports and Audit show the event as of the phase you came from (RO_ASOF); the switch changes the moment
  if (['timeline', 'reports', 'audit'].includes(view) && window.RO_ASOF) {
    const A = window.RO_ASOF, clock = document.querySelector('.topbar .live span:last-child');
    if (clock) clock.textContent = `Simulated · ${A.clock} IST`;
    document.querySelector('.v-head .sub')?.insertAdjacentHTML('afterend', `<nav class="v-asof" aria-label="Show the event as of"><span>Showing the event as of</span>${
      ['prepare', 'respond', 'recover'].map(p => `<a href="?view=${view}&asof=${p}"${p === A.phase ? ' aria-current="true"' : ''}>${A.AT[p][1]} · ${p === 'recover' ? 'now' : A.AT[p][2].split(', ')[1]}</a>`).join('')}</nav>`);
  }
  if (view) document.querySelector('.v-head > div')?.insertAdjacentHTML('afterbegin',
    `<a class="v-back" href="?phase=${back}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>Back to ${back[0].toUpperCase() + back.slice(1)}</a>`);

  const $ = s => document.querySelector(s);
  const toastEl = $('#toast'); let tt;
  const toast = msg => { toastEl.textContent = msg; toastEl.classList.add('show'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('show'), 3200); };
  if (view) document.addEventListener('click', e => { const t = e.target.closest('[data-toast]'); if (t) { e.preventDefault(); toast(t.dataset.toast); } });

  // current phase: a status line just above the page title, on the title's left edge (not a control)
  if (phase) document.querySelector('.map-head h1')?.insertAdjacentHTML('beforebegin',
    `<p class="ph-stat ph-${phase}"><span>Current phase</span><b><i aria-hidden="true"></i>${PH[phase].label}</b></p>`);

  // full map: the expand control fades every card away (top bar and map controls stay); again or Esc brings them back
  const ctrls = document.querySelector('.controls');
  if (phase && ctrls && document.getElementById('map')) {
    ctrls.insertAdjacentHTML('beforeend', `<button class="round glass" type="button" id="full-map" aria-pressed="false" aria-label="Show the full map" data-tip="Full map">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path class="fm-in" d="M14 10l6-6M15 4h5v5M10 14l-6 6M9 20H4v-5"/><path class="fm-out" d="M20 4l-6 6M14 4.5V10h5.5M4 20l6-6M10 19.5V14H4.5"/></svg></button>`);
    const fm = document.getElementById('full-map');
    const setFull = on => {
      document.body.classList.toggle('ro-fullmap', on);
      fm.setAttribute('aria-pressed', on); fm.setAttribute('aria-label', on ? 'Bring the cards back' : 'Show the full map'); fm.dataset.tip = on ? 'Show cards' : 'Full map';
      // the map widens with the rail; let Leaflet (and charts) re-measure once the column has moved
      setTimeout(() => dispatchEvent(new Event('resize')), 380);
    };
    fm.addEventListener('click', () => setFull(!document.body.classList.contains('ro-fullmap')));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('ro-fullmap') && !document.querySelector('.ro-pop:not([hidden]), .role-menu:not([hidden]), .rs-scrim.rs-on, #tour:not([hidden])')) setFull(false); });
  }

  /* ---------- avatar opens the small menu; a dot on it (and on Switch phase) when another phase has something waiting ---------- */
  const av = $('.avatar');
  av.innerHTML = `${R.ini}<span class="av-dot" aria-hidden="true" hidden></span>`;
  av.setAttribute('aria-label', `${R.name}, account menu`);
  av.title = `${R.name} · ${R.role}, ${R.org}`;
  av.setAttribute('aria-haspopup', 'menu'); av.setAttribute('aria-expanded', 'false'); av.setAttribute('aria-controls', 'role-menu');
  const menu = $('#role-menu'), items = [...menu.querySelectorAll('[role="menuitem"]')];
  const scrims = { phase: $('#rs-phase'), role: $('#rs-role') };
  const waiting = () => {
    const n = [...scrims.phase.querySelectorAll('.rs-tile:not([aria-current])')].filter(t => t.querySelector('.count:not([hidden]), .dot-alert')).length;
    av.querySelector('.av-dot').hidden = !n;
    const ph = $('#am-phase'); ph.innerHTML = PH[curPh].label + (n ? '<i aria-hidden="true"></i>' : '');
    av.setAttribute('aria-label', `${R.name}, account menu${n ? `, ${n} ${n > 1 ? 'phases need' : 'phase needs'} attention` : ''}`);
    menu.querySelector('[data-open="phase"]').setAttribute('aria-label', `Switch phase, now ${PH[curPh].label}${n ? `, ${n} other ${n > 1 ? 'phases need' : 'phase needs'} attention` : ''}`);
  };
  new MutationObserver(waiting).observe(scrims.phase, { childList: true, subtree: true });
  const place = () => { const r = av.getBoundingClientRect(); menu.style.top = r.bottom + 10 + 'px'; menu.style.right = Math.max(12, innerWidth - r.right) + 'px'; };
  const setMenu = open => {
    menu.hidden = !open; av.setAttribute('aria-expanded', open);
    if (open) { place(); items[0].focus(); }
  };
  av.addEventListener('click', e => { e.stopPropagation(); setMenu(menu.hidden); });
  document.addEventListener('pointerdown', e => { if (!menu.hidden && !menu.contains(e.target) && !av.contains(e.target)) setMenu(false); });
  addEventListener('resize', () => { if (!menu.hidden) place(); });
  menu.addEventListener('keydown', e => {
    const i = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); items[(i + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length].focus(); }
    else if (e.key === 'Home') { e.preventDefault(); items[0].focus(); }
    else if (e.key === 'End') { e.preventDefault(); items[items.length - 1].focus(); }
    else if (e.key === 'Escape') { e.preventDefault(); setMenu(false); av.focus(); }
    else if (e.key === 'Tab') setMenu(false);
    else if (e.key === ' ' && document.activeElement.matches('a')) { e.preventDefault(); document.activeElement.click(); }
  });
  menu.addEventListener('click', e => { const b = e.target.closest('[data-open]'); if (b) { setMenu(false); openDlg(b.dataset.open); } });

  // the dialogs: the app behind blurs, dims and steps back; focus stays inside; Esc, ✕ or the backdrop closes
  let openKind = null;
  const outside = () => [...document.body.children].filter(el => !el.classList.contains('rs-scrim') && el.id !== 'toast');
  const tilesOf = k => [...scrims[k].querySelectorAll('.rs-tile')];
  const openDlg = (k, swap) => {
    if (openKind && openKind !== k) { scrims[openKind].classList.remove('rs-on'); scrims[openKind].setAttribute('aria-hidden', 'true'); }
    openKind = k;
    outside().forEach(el => el.inert = true); document.body.classList.add('rs-open');
    const s = scrims[k]; s.classList.remove('rs-leaving'); s.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(() => s.classList.add('rs-on'));
    const t = tilesOf(k); (t.find(b => b.hasAttribute('aria-current')) || t[0]).focus({ preventScroll: true });
  };
  const closeDlg = () => {
    if (!openKind) return;
    const s = scrims[openKind]; s.classList.remove('rs-on'); s.setAttribute('aria-hidden', 'true'); openKind = null;
    outside().forEach(el => el.inert = false); document.body.classList.remove('rs-open'); av.focus();
  };
  const NOTE = 'ro.toast';
  const choose = (k, b) => {
    const id = b.dataset.pick;
    if (b.hasAttribute('aria-current') && !(k === 'phase' && view)) { closeDlg(); return; }  // on a view, the current phase still opens it
    let to;
    if (k === 'phase') { to = '?phase=' + id; ss.set(NOTE, `Switched to ${PH[id].label}. Same event, ${PH[id].label.toLowerCase()} view.`); }
    else {
      ls.set(RKEY, id); ss.set(NOTE, `You’re now ${ROLES[id].name}, ${ROLES[id].role}. ${RS[id].note}`);
      // the IC keeps the phase in view; the other roles land on their own phase; views are for every role
      const target = id === 'ic' ? phase : ROLES[id].home;
      to = view ? '?view=' + view + location.hash : '?phase=' + target + (target === 'recover' ? location.hash : '');
    }
    const s = scrims[k]; b.classList.add('rs-picked'); s.classList.add('rs-leaving');
    setTimeout(() => { location.href = to; }, matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 420);
  };
  Object.entries(scrims).forEach(([k, s]) => {
    s.addEventListener('click', e => {
      if (e.target === s || e.target.closest('[data-close]')) return closeDlg();
      const sw = e.target.closest('[data-swap]'); if (sw) return openDlg(sw.dataset.swap, true);
      const b = e.target.closest('.rs-tile'); if (b) choose(k, b);
    });
    s.addEventListener('keydown', e => {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); return closeDlg(); }
      const t = tilesOf(k), i = t.indexOf(document.activeElement);
      if (i > -1 && ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'].includes(e.key)) {
        e.preventDefault();
        const j = e.key === 'Home' ? 0 : e.key === 'End' ? t.length - 1 : (i + (/Right|Down/.test(e.key) ? 1 : -1) + t.length) % t.length;
        t[j].focus();
      } else if (e.key === 'Tab') {
        const f = [...s.querySelectorAll('button')], a = f[0], z = f[f.length - 1];
        if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
        else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
      }
    });
  });
  const arrived = ss.get(NOTE); if (arrived) { ss.set(NOTE, ''); setTimeout(() => toast(arrived), 500); }

  /* ---------- permissions: approvals the role can't make go to the IC ---------- */
  const LOCK = { prepare: ['#approve', '#ho-activate', '.pp-detail [data-approve]', '.pp-detail [data-approve-all]'], respond: ['#approve'], recover: ['#m-assign', '#m-approve', '#lesson [data-accept]'],
    timeline: [], reports: ['#rp-approve'], audit: [], forecast: [], tasks: [], relief: [] };
  const CAN = { ic: () => true, analyst: () => false, coord: sel => phase === 'recover' && sel !== '#lesson [data-accept]' };
  const locked = LOCK[view || phase].filter(sel => !CAN[roleId](sel));
  const label = roleId === 'analyst' ? 'Recommend to IC' : 'Send to IC';
  const relabel = () => locked.forEach(sel => document.querySelectorAll(sel).forEach(b => {
    if (b.textContent.trim() !== label) b.textContent = label;
    if (!b.dataset.locked) { b.dataset.locked = '1'; b.setAttribute('aria-label', `${label}: approval sits with Ananya Menon, Incident Commander`); b.title = 'Approval sits with Ananya Menon, Incident Commander'; }
  }));
  if (locked.length) {
    relabel();
    new MutationObserver(relabel).observe(document.body, { childList: true, subtree: true, characterData: true });
    document.addEventListener('click', e => {
      if (!locked.some(sel => e.target.closest(sel))) return;
      e.preventDefault(); e.stopImmediatePropagation();
      toast(`Sent to Ananya Menon, Incident Commander, for approval · from ${R.name}`);
    }, true);
  }

  /* ---------- top-bar popovers: one open at a time ---------- */
  const pops = [];  // { el, btn, close }
  const closeOthers = keep => { pops.forEach(p => { if (p.el !== keep && !p.el.hidden) p.close(); }); if (keep !== menu && !menu.hidden) setMenu(false); };
  av.addEventListener('click', () => closeOthers(menu), true);
  const placeUnder = (el, anchor, alignRight) => {
    const r = anchor.getBoundingClientRect(); el.style.top = r.bottom + 10 + 'px';
    if (alignRight) { el.style.right = Math.max(12, innerWidth - r.right) + 'px'; el.style.left = 'auto'; } else { el.style.left = r.left + 'px'; el.style.right = 'auto'; }
  };
  const hit = el => { if (!el) return; el.classList.remove('ro-hit'); void el.offsetWidth; el.classList.add('ro-hit'); setTimeout(() => el.classList.remove('ro-hit'), 1700); };
  // open an item in the decision panel (expanding the panel and the item if needed)
  const openPanelItem = el => {
    const panel = el.closest('.decisions');
    if (panel && panel.classList.contains('collapsed')) $('#plan-pill')?.click();
    const t = el.querySelector('.alert-toggle, .task-more');
    if (t && t.getAttribute('aria-expanded') === 'false') t.click();
    el.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    hit(el); (t || el.querySelector('button') || el).focus({ preventScroll: true });
  };
  const KIND = { prepare: 'Place', respond: 'Team', recover: 'Community' }[phase];
  const txt = (el, sel) => (el.querySelector(sel)?.textContent || '').replace(/\s+/g, ' ').trim();
  // everything searchable on this phase, read from the page itself
  const searchIndex = () => [
    ...[...document.querySelectorAll('.rail .card.team')].map(el => ({ t: txt(el, 'h3'), m: txt(el, '.when'), k: KIND, go: () => { (el.querySelector('.team-hit') || el).click(); (el.querySelector('.team-hit') || el).focus(); hit(el); } })),
    ...[...document.querySelectorAll('.decisions .alert, .decisions .task, .decisions .row-item')].filter(el => !el.closest('[hidden]')).map(el => ({
      t: txt(el, '.alert-title, .task-title, .t'), m: txt(el, '.alert-meta, .task-meta, .m'),
      k: el.classList.contains('task') ? 'Task' : el.classList.contains('row-item') ? 'Need' : 'Decision', go: () => openPanelItem(el) })),
    // map-only places (camps, roads, outages) registered by the phase's map
    ...(window.RO_MAP?.items || []),
    ...[...document.querySelectorAll('[data-sk-t]')].filter(el => !el.closest('[hidden]')).map(el => ({ t: el.dataset.skT, m: el.dataset.skM || '', k: el.dataset.skK || 'Item', go: () => {
      const b = el.querySelector('[aria-expanded]');
      if (b && b.getAttribute('aria-expanded') === 'false') b.click();
      el.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); hit(el); (b || el).focus?.({ preventScroll: true });
    } }))
  ].filter(x => x.t);

  /* ---------- search ---------- */
  const sLabel = $('.search'), sIn = $('.search input');
  if (sIn) {
    sIn.setAttribute('role', 'combobox'); sIn.setAttribute('aria-autocomplete', 'list'); sIn.setAttribute('aria-expanded', 'false'); sIn.setAttribute('aria-controls', 'search-list');
    sIn.setAttribute('autocomplete', 'off'); sIn.setAttribute('spellcheck', 'false');
    sLabel.querySelector('kbd').insertAdjacentHTML('beforebegin', '<button type="button" class="s-clear" aria-label="Clear search" hidden><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>');
    const clr = sLabel.querySelector('.s-clear');
    document.body.insertAdjacentHTML('beforeend', '<div class="ro-pop search-pop" id="search-pop" hidden><ul role="listbox" id="search-list" aria-label="Search results"></ul><p class="sp-empty" role="status" hidden></p></div>');
    const sp = $('#search-pop'), list = $('#search-list'), empty = sp.querySelector('.sp-empty');
    let found = [], act = -1;
    const esc = t => t.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
    const mark = (t, words) => { let h = esc(t); words.forEach(w => { if (w) h = h.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); }); return h; };
    const setAct = i => {
      act = i; [...list.children].forEach((li, j) => li.setAttribute('aria-selected', j === i));
      if (i >= 0) { sIn.setAttribute('aria-activedescendant', 'sr-' + i); list.children[i].scrollIntoView({ block: 'nearest' }); } else sIn.removeAttribute('aria-activedescendant');
    };
    const closeSearch = () => { sp.hidden = true; sIn.setAttribute('aria-expanded', 'false'); setAct(-1); };
    const render = () => {
      const q = sIn.value.trim().toLowerCase(), words = q.split(/\s+/).filter(Boolean);
      clr.hidden = !sIn.value;
      found = searchIndex().filter(x => words.every(w => (x.t + ' ' + x.m + ' ' + x.k).toLowerCase().includes(w))).slice(0, 8);
      list.innerHTML = found.map((x, i) => `<li role="option" id="sr-${i}" aria-selected="false"><b>${mark(x.t, words)}</b><span class="m">${mark(x.m, words)}</span><span class="k">${x.k}</span></li>`).join('');
      empty.hidden = !!found.length; empty.textContent = found.length ? '' : `Nothing matches "${sIn.value.trim()}". Try a place, team or need.`;
      sp.style.width = Math.max(380, sLabel.offsetWidth) + 'px'; placeUnder(sp, sLabel, false);
      closeOthers(sp); sp.hidden = false; sIn.setAttribute('aria-expanded', 'true'); setAct(found.length && q ? 0 : -1);
    };
    const choose = i => { const x = found[i]; if (!x) return; closeSearch(); sIn.value = x.t; clr.hidden = false; x.go(); };
    sIn.addEventListener('focus', render);
    sIn.addEventListener('input', render);
    sIn.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); if (sp.hidden) render(); if (found.length) setAct((act + (e.key === 'ArrowDown' ? 1 : -1) + found.length) % found.length); }
      else if (e.key === 'Enter') { e.preventDefault(); choose(act >= 0 ? act : 0); }
      else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); if (!sp.hidden) closeSearch(); else { sIn.value = ''; clr.hidden = true; } }
      else if (e.key === 'Tab') closeSearch();
    });
    list.addEventListener('mousedown', e => e.preventDefault());  // keep focus in the field while clicking a result
    list.addEventListener('click', e => { const li = e.target.closest('li'); if (li) choose([...list.children].indexOf(li)); });
    clr.addEventListener('click', e => { e.preventDefault(); sIn.value = ''; sIn.focus(); render(); });
    pops.push({ el: sp, btn: sIn, close: closeSearch });
    document.addEventListener('pointerdown', e => { if (!sp.hidden && !sp.contains(e.target) && !sLabel.contains(e.target)) closeSearch(); });
    addEventListener('resize', () => { if (!sp.hidden) placeUnder(sp, sLabel, false); });
  }

  /* ---------- helpline and alerts: list popovers on the round top-bar buttons ---------- */
  const listPop = (btn, id, label, build) => {
    btn.removeAttribute('data-toast');
    btn.setAttribute('aria-haspopup', 'dialog'); btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', id);
    document.body.insertAdjacentHTML('beforeend', `<div class="ro-pop list-pop" id="${id}" role="dialog" aria-label="${label}" hidden></div>`);
    const el = $('#' + id);
    const close = (refocus) => { el.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (refocus) btn.focus(); };
    const open = () => { closeOthers(el); build(el, close); el.hidden = false; btn.setAttribute('aria-expanded', 'true'); placeUnder(el, btn, true); (el.querySelector('.nt-main') || el.querySelector('button'))?.focus(); };
    btn.addEventListener('click', e => { e.stopPropagation(); el.hidden ? open() : close(); });
    el.addEventListener('keydown', e => {
      const rows = [...el.querySelectorAll('button')], i = rows.indexOf(document.activeElement);
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(true); }
      else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); rows[(i + (e.key === 'ArrowDown' ? 1 : -1) + rows.length) % rows.length]?.focus(); }
    });
    document.addEventListener('pointerdown', e => { if (!el.hidden && !el.contains(e.target) && !btn.contains(e.target)) close(); });
    addEventListener('resize', () => { if (!el.hidden) placeUnder(el, btn, true); });
    pops.push({ el, btn, close: () => close() });
  };

  // helpline: district contacts and the radio net (simulated for the demo)
  const PHONE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>';
  const RADIO = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="8" width="14" height="13" rx="2"/><path d="M8 8 16 3M9 13h6M9 17h6"/></svg>';
  const CONTACTS = [
    ['DEOC Wayanad control room', 'District emergency operations centre', '1077'],
    ['KSDMA State EOC', 'Kerala State Disaster Management Authority', '1070'],
    ['Police', 'Emergency response', '112'],
    ['Fire & Rescue', 'Kalpetta station', '101'],
    ['Ambulance', 'Medical emergencies', '108']
  ];
  const helpBtn = $('.tools [aria-label="District helpline and radio"]');
  if (helpBtn) listPop(helpBtn, 'help-pop', 'District helpline and radio', (el, close) => {
    el.style.width = '360px';
    el.innerHTML = `<div class="pop-h"><b>Helpline and radio</b><span>Simulated</span></div>
      ${CONTACTS.map(([n, d, num]) => `<button type="button" class="row" data-call="${n}|${num}">${PHONE}<b>${n}</b><span class="m">${d}</span><span class="num">${num}</span></button>`).join('')}
      <button type="button" class="row" data-call="DEOC radio net|VHF channel 3">${RADIO}<b>DEOC radio net</b><span class="m">Teams in the field · VHF channel 3</span><span class="go">Open</span></button>
      <p class="pop-f">In the live product these connect through the DEOC console. Here they only show what would happen.</p>`;
    el.querySelectorAll('[data-call]').forEach(b => b.addEventListener('click', () => { const [n, num] = b.dataset.call.split('|'); close(true); toast(`Connecting to ${n} (${num}) · simulated`); }));
  });

  // alerts: what needs attention on this phase, read from the page; each one takes you there
  const read = new Set();
  const bell = $('#bell'), badge = bell?.querySelector('.badge');
  const EXTRA = { prepare: [{ t: 'IMD red alert for Wayanad', m: '06:00 · extremely heavy rain in the next 24 h', sev: 'crit', go: () => { const c = $('#rain-h')?.closest('.card'); c?.scrollIntoView({ block: 'nearest' }); hit(c); } }] };
  const alerts = () => [
    ...(EXTRA[phase] || []),
    ...(view ? (window.RO_ALERTS || []) : []),
    ...[...document.querySelectorAll('.decisions .alert')].filter(el => !el.closest('[hidden]')).map(el => ({
      t: txt(el, '.alert-title, .t'), m: txt(el, '.alert-meta, .m'), sev: el.classList.contains('crit') ? 'crit' : 'warn', go: () => openPanelItem(el),
      // an alert with a filled state line ("Approved by…", "Accepted by…") is resolved
      done: !!el.querySelector('[role="status"]:not([hidden])')?.textContent.trim() }))
  ].filter(a => a.t);
  const syncBadge = () => {
    if (!badge) return;
    const n = alerts().filter(a => !a.done && !read.has(a.t)).length;
    badge.textContent = n; badge.hidden = !n;
    bell.setAttribute('aria-label', n ? `Alerts, ${n} unread` : 'Alerts, all read');
  };
  // notifications read like a feed: actor + verb + object, time and age, then a quote, an attachment or an action
  const RICH = [
    ['Landslide blocks', { actor: 'Field Intelligence Agent', who: 'ai', verb: 'flagged a critical incident on', obj: 'Meppadi–Chooralmala road', when: 'Day 0 · 12:04', ago: '6 min ago',
      quote: 'Debris across the road at km 7. About 10–18 households in Chooralmala ward 11 may be cut off.', acts: [['Why this?', () => $('#why-btn')?.click()], ['Approve dispatch', () => $('#approve')?.click(), 1]] }],
    ['Meppadi camp: drinking water', { actor: 'Camp manager', who: 'agency', verb: 'reported a shortage at', obj: 'Meppadi camp', when: 'Day 0 · 11:58', ago: '12 min ago',
      quote: 'Drinking water runs out in under 6 h. 412 people in camp; the second tanker is late.' }],
    ['Vythiri flooding', { actor: 'Forecast vs Ground Reality Agent', who: 'ai', verb: 'spotted a change in', obj: 'Vythiri', when: 'Day 0 · 11:50', ago: '20 min ago',
      quote: 'Flooding started 3 h earlier than forecast. Teams already on site.' }],
    ['IMD red alert', { actor: 'IMD', who: 'agency', verb: 'issued a red alert for', obj: 'Wayanad', when: 'Day 0 · 06:00', ago: '20 min ago',
      quote: 'Extremely heavy rain in the next 24 hours; 234.6 mm expected at the Meppadi gauge.' }],
    ['Response activation', { actor: 'Command Orchestrator', who: 'ai', verb: 'recommends moving to', obj: 'Respond', when: 'Day 0 · 12:02', ago: 'just now',
      acts: [['Review handover', () => $('#open-handover')?.click(), 1]] }],
    ['Chooralmala ward 11 may be missed', { actor: 'Relief Coverage Agent', who: 'ai', verb: 'flagged a missed community in', obj: 'Chooralmala ward 11', when: 'Day 2 · 09:00', ago: '5 min ago',
      quote: 'No verified water delivery in 10 h and only 3 reports since the phone tower went down.' }],
    ['Situation report #4', { actor: 'Communications Agent', who: 'ai', verb: 'drafted', obj: 'Situation report #4', when: 'Day 2 · 09:00', ago: '5 min ago',
      file: ['Situation report #4', 'For KSDMA · 8 sections · awaiting your approval'] }],
    ['Lesson: 48 h water', { actor: 'Recovery & Reconciliation Agent', who: 'ai', verb: 'drafted a lesson for', obj: 'Prepare', when: 'Day 2 · 09:05', ago: 'just now',
      quote: '48 h water stock at every camp: water ran out at 14 h against a 48 h plan.' }]
  ];
  const rich = a => { const r = RICH.find(([k]) => a.t.startsWith(k)); return Object.assign({ actor: 'ResilienceOps', who: 'ai', verb: 'flagged', obj: a.t, when: a.m, ago: '' }, r ? r[1] : {}); };
  const AV = { ai: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5 13.8 10 20.5 12l-6.7 2-1.8 6.5-1.8-6.5L3.5 12l6.7-2z"/></svg>',
    agency: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M4 20V9l8-5 8 5v11zM9 20v-6h6v6M4 20h16"/></svg>',
    human: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/></svg>' };
  const DOC = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></svg>';
  const DBL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m2 13 4.5 4.5L15 9M10 16l1.5 1.5L22 7"/></svg>';
  const GEAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.1-1.2L14 3h-4l-.5 2.7a7 7 0 0 0-2.1 1.2l-2.3-1-2 3.4 2 1.5a7 7 0 0 0 0 2.4l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2.1 1.2L10 21h4l.5-2.7a7 7 0 0 0 2.1-1.2l2.3 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/></svg>';
  let tab = 'all';
  if (bell) {
    listPop(bell, 'alert-pop', 'Your notifications', (el, close) => {
      const all = alerts(), unread = a => !a.done && !read.has(a.t);
      const list = tab === 'crit' ? all.filter(a => a.sev === 'crit') : tab === 'unread' ? all.filter(unread) : all;
      el.style.width = '440px'; el.classList.add('nt-pop');
      const T = (k, l, n) => `<button type="button" class="nt-tab" data-tab="${k}" aria-pressed="${tab === k}">${l}${n != null ? `<span>${n}</span>` : ''}</button>`;
      el.innerHTML = `<div class="nt-h"><b id="nt-h">Your notifications</b>
          <span class="nt-ic"><button type="button" data-all aria-label="Mark all as read" title="Mark all as read">${DBL}</button><button type="button" data-set aria-label="Notification settings" title="Notification settings">${GEAR}</button></span></div>
        <div class="nt-tabs" role="group" aria-label="Show">${T('all', 'View all', all.length)}${T('crit', 'Critical')}${T('unread', 'Unread', all.filter(unread).length)}</div>
        <ul class="nt-list">${list.map(a => { const r = rich(a), i = all.indexOf(a), on = unread(a);
          return `<li class="nt${on ? '' : ' read'}">
            <span class="nt-av av-${r.who}" aria-hidden="true">${AV[r.who]}<i class="sev-${a.sev}"></i></span>
            <div class="nt-b">
              <button type="button" class="nt-main" data-i="${i}"><span class="nt-s"><b>${r.actor}</b> ${r.verb} <b>${r.obj}</b></span>
                <span class="nt-t"><span>${r.when}</span><span>${a.done ? 'Done' : r.ago}</span></span>${on ? '<i class="nt-dot" aria-label="Unread"></i>' : ''}</button>
              ${r.quote ? `<p class="nt-q">${r.quote}</p>` : ''}
              ${r.file ? `<button type="button" class="nt-file" data-i="${i}">${DOC}<span><b>${r.file[0]}</b><small>${r.file[1]}</small></span></button>` : ''}
              ${r.acts && !a.done ? `<p class="nt-acts">${r.acts.map(([l, , pri], k) => `<button type="button" class="btn${pri ? ' primary' : ''}" data-act="${i}:${k}">${l}</button>`).join('')}</p>` : ''}
            </div></li>`; }).join('') || `<li class="nt-empty">Nothing here. You're up to date.</li>`}</ul>`;
      const go = i => { const a = all[i]; read.add(a.t); syncBadge(); close(); a.go(); };
      el.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', () => go(+b.dataset.i)));
      el.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', () => { const [i, k] = b.dataset.act.split(':').map(Number), a = all[i];
        read.add(a.t); syncBadge(); close(); a.go(); setTimeout(() => rich(a).acts[k][1](), 350); }));
      el.querySelectorAll('[data-tab]').forEach(b => b.addEventListener('click', () => { tab = b.dataset.tab; bell.click(); bell.click(); el.querySelector(`[data-tab="${tab}"]`)?.focus(); }));
      el.querySelector('[data-all]').addEventListener('click', () => { all.forEach(a => read.add(a.t)); syncBadge(); toast('All notifications marked as read'); bell.click(); bell.click(); el.querySelector('[data-all]')?.focus(); });
      el.querySelector('[data-set]').addEventListener('click', () => {   // personal settings: no approval needed, kept in this browser
        let N = {}; try { N = JSON.parse(localStorage.getItem('ro.notify')) || {}; } catch (e) {}
        const v = (k, d) => N[k] ?? d;
        close(); window.RO_REVIEW?.open({ title: 'Notification settings', sub: `${R.name} · ${R.role}`, anyone: true, approve: 'Save settings', cancel: 'Cancel',
          edit: [{ id: 'crit', label: 'Critical alerts', hint: 'Sound and a banner on every page', type: 'check', value: v('crit', true) },
            { id: 'high', label: 'High alerts', hint: 'A banner, no sound', type: 'check', value: v('high', true) },
            { id: 'watch', label: 'Watch items', hint: 'In this list only', type: 'check', value: v('watch', true) },
            { id: 'digest', label: 'Email digest', hint: 'Every 6 hours to your DDMA address', type: 'check', value: v('digest', false) },
            { id: 'quiet', label: 'Quiet hours', type: 'select', value: v('quiet', 'never'), options: [['never', 'Never: I am on duty'], ['night', '23:00–05:00, critical still comes through']] }],
          note: 'Critical alerts always reach the Incident Commander, whatever is set here.',
          onApprove: vals => { try { localStorage.setItem('ro.notify', JSON.stringify(vals)); } catch (e) {} toast('Notification settings saved'); } });
      });
      el.setAttribute('aria-labelledby', 'nt-h');
    });
    // phase scripts still set the count when new alerts arrive (e.g. the Prepare demo); keep it honest
    new MutationObserver(() => { const want = alerts().filter(a => !a.done && !read.has(a.t)).length; if (badge && +badge.textContent !== want && document.activeElement !== bell) syncBadge(); })
      .observe($('.decisions') || document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['hidden', 'class'] });
    syncBadge();
  }

  if (!view && asked && asked !== phase) toast(`${asked} isn't a phase · showing ${phase}`);
})();
