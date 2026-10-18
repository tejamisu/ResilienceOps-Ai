/* ---------- shared event state: what each phase hands to the next, and a log the Timeline reads ----------
   Kept for this visit (sessionStorage). Every page still works without it (private windows, blocked storage). */
window.RO_STATE = (() => {
  const K = 'ro.state';
  const read = () => { try { return JSON.parse(sessionStorage.getItem(K)) || {}; } catch (e) { return {}; } };
  const write = s => { try { sessionStorage.setItem(K, JSON.stringify(s)); } catch (e) {} };
  return {
    get: k => read()[k],
    set: (k, v) => { const s = read(); s[k] = v; write(s); },
    // log entry: { id, day, t, phase, kind, title, detail, actor, who, src, verify, link }
    log: () => read().log || [],
    add: e => { const s = read(), l = s.log || []; if (!l.some(x => x.id === e.id)) l.push(e); s.log = l; write(s);
      // people's decisions also go to the backend's decision log (the Audit trail), when it is there
      if (e.who === 'human') window.RO_API?.decide({ action: 'decide', item: e.title, by: e.actor, phase: e.phase, detail: `Day ${e.day} ${e.t} · ${e.detail || ''}`.trim() }); },
    reset: () => write({})
  };
})();

/* ---------- review dialog: one panel for drafts and handovers, on every page ----------
   RO_REVIEW.open({ title, sub, ai, fields: [[label, value]], lists: [{ h, tone: 'ok'|'warn'|'ink', items: [[text, small]] }],
                    edit: [{ id, label, type: 'text'|'textarea'|'select'|'check', value, options: [[value, label]] }],
                    note, approve, cancel, phase, anyone, onApprove(values), onCancel })
   anyone: personal settings that need no approval.
   Approval follows the role: only the Incident Commander approves (the coordinator can in Recover); others send it to the IC. */
window.RO_REVIEW = (() => {
  const ROLE = (() => { try { return localStorage.getItem('ro.role') || 'ic'; } catch (e) { return 'ic'; } })();
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const IC = {
    ok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7"/></svg>',
    warn: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 22 20H2z" fill="currentColor"/></svg>',
    ink: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg>',
    ai: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5 13.8 10 20.5 12l-6.7 2-1.8 6.5-1.8-6.5L3.5 12l6.7-2z"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
  };
  const toast = msg => { const t = document.getElementById('toast'); if (!t) return; t.textContent = msg; t.classList.add('show'); clearTimeout(t._rv); t._rv = setTimeout(() => t.classList.remove('show'), 3200); };
  let el, scrim, last, cfg;
  const close = (why) => {
    if (!el || el.hidden) return;
    el.hidden = true; scrim.hidden = true;
    if (why === 'cancel') cfg.onCancel?.();
    last?.focus?.({ preventScroll: true });
  };
  const open = c => {
    cfg = c; last = document.activeElement;
    if (!el) {
      document.body.insertAdjacentHTML('beforeend', '<div class="rv-scrim" id="rv-scrim" hidden></div><div class="rv" id="rv" role="dialog" aria-modal="true" aria-labelledby="rv-h" hidden></div>');
      el = document.getElementById('rv'); scrim = document.getElementById('rv-scrim');
      scrim.addEventListener('click', () => close('cancel'));
      el.addEventListener('keydown', e => {
        if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close('cancel'); }
        if (e.key === 'Tab') {
          const f = [...el.querySelectorAll('button:not([disabled]), [href], input, textarea, select')], a = f[0], z = f[f.length - 1];
          if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); } else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
        }
      });
    }
    const can = c.anyone || ROLE === 'ic' || (ROLE === 'coord' && c.phase === 'recover');
    const fid = f => 'rv-e-' + f.id;
    const input = f => f.type === 'textarea' ? `<textarea id="${fid(f)}" rows="3" required>${esc(f.value ?? '')}</textarea>`
      : f.type === 'select' ? `<select id="${fid(f)}">${f.options.map(([v, l]) => `<option value="${esc(v)}"${String(v) === String(f.value) ? ' selected' : ''}>${esc(l)}</option>`).join('')}</select>`
      : f.type === 'check' ? `<input type="checkbox" id="${fid(f)}"${f.value ? ' checked' : ''}>`
      : `<input id="${fid(f)}" value="${esc(f.value ?? '')}" autocomplete="off" required>`;
    const approve = can ? c.approve : (ROLE === 'analyst' ? 'Recommend to IC' : 'Send to IC');
    el.innerHTML = `<header class="rv-top"><div><h2 id="rv-h">${esc(c.title)}</h2>${c.sub ? `<p>${esc(c.sub)}</p>` : ''}</div>
        <button type="button" class="rv-x" data-rv="cancel" aria-label="Close without approving">${IC.x}</button></header>
      <div class="rv-body">
        ${c.ai ? `<p class="rv-ai">${IC.ai}<span>${c.ai}</span></p>` : ''}
        ${c.fields ? `<dl class="rv-f">${c.fields.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${v}</dd></div>`).join('')}</dl>` : ''}
        ${c.edit ? `<div class="rv-e">${c.edit.map(f => f.type === 'check'
          ? `<label class="rv-c" for="${fid(f)}">${input(f)}<span>${esc(f.label)}${f.hint ? `<small>${esc(f.hint)}</small>` : ''}</span></label>`
          : `<label class="rv-in" for="${fid(f)}"><span>${esc(f.label)}</span>${input(f)}</label>`).join('')}<p class="rv-err" role="alert" hidden></p></div>` : ''}
        ${(c.lists || []).map(l => `<section class="rv-l rv-${l.tone || 'ink'}"><h3>${IC[l.tone || 'ink']}${esc(l.h)}</h3>
          <ul>${l.items.length ? l.items.map(([a, b]) => `<li><span>${a}${b ? `<small>${b}</small>` : ''}</span></li>`).join('') : '<li class="rv-none">None</li>'}</ul></section>`).join('')}
      </div>
      <footer class="rv-foot">${c.note ? `<p class="rv-note">${c.note}</p>` : ''}${can ? '' : '<p class="rv-note">Approval sits with Ananya Menon, Incident Commander.</p>'}
        <div class="rv-acts"><button type="button" class="btn" data-rv="cancel">${esc(c.cancel || 'Not now')}</button><button type="button" class="btn primary" data-rv="ok">${esc(approve)}</button></div></footer>`;
    el.querySelectorAll('[data-rv]').forEach(b => b.addEventListener('click', () => {
      if (b.dataset.rv === 'cancel') return close('cancel');
      const vals = {}; let bad = null;
      (c.edit || []).forEach(f => { const x = document.getElementById(fid(f)); vals[f.id] = f.type === 'check' ? x.checked : x.value.trim();
        const empty = f.type !== 'check' && f.type !== 'select' && !vals[f.id]; x.setAttribute('aria-invalid', empty); if (empty && !bad) bad = [x, f.label]; });
      if (bad) { const er = el.querySelector('.rv-err'); er.hidden = false; er.textContent = `${bad[1]} can't be empty.`; bad[0].focus(); return; }
      close('ok');
      if (can) c.onApprove?.(vals); else { c.onRecommend?.(vals); toast(`Sent to Ananya Menon, Incident Commander, for approval`); }
    }));
    el.hidden = false; scrim.hidden = false;
    if (!reduce) { el.classList.add('enter'); scrim.classList.add('enter'); requestAnimationFrame(() => requestAnimationFrame(() => { el.classList.remove('enter'); scrim.classList.remove('enter'); })); }
    (c.edit ? el.querySelector('.rv-e input, .rv-e select, .rv-e textarea') : el.querySelector('[data-rv="ok"]')).focus();
  };
  return { open, close, can: phase => ROLE === 'ic' || (ROLE === 'coord' && phase === 'recover'), toast };
})();

/* ---------- handover note: "From Prepare · …" at the top of a phase's decision panel ---------- */
window.RO_HANDNOTE = (ref, { from, when, by, done, open }) => {   // inserted right after ref (e.g. the panel header)
  if (!ref) return;
  const id = 'ho-' + from.toLowerCase();
  ref.insertAdjacentHTML('afterend', `<div class="ro-ho" data-sk-t="Handover from ${from}" data-sk-m="${when}" data-sk-k="Handover">
    <button type="button" class="ro-ho-t" aria-expanded="false" aria-controls="${id}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h12M12 6l6 6-6 6"/></svg>
      <span><b>Handed over from ${from}</b><small>${when} · ${by} · ${done.length} done · ${open.length} carried over</small></span>
      <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>
    <div class="ro-ho-b" id="${id}" hidden>
      ${open.length ? `<p class="k">Carried over</p><ul>${open.map(([a, b]) => `<li class="warn"><span>${a}${b ? `<small>${b}</small>` : ''}</span></li>`).join('')}</ul>` : ''}
      ${done.length ? `<p class="k">Done in ${from}</p><ul>${done.map(([a, b]) => `<li class="ok"><span>${a}${b ? `<small>${b}</small>` : ''}</span></li>`).join('')}</ul>` : ''}
    </div></div>`);
  const t = document.querySelector(`[aria-controls="${id}"]`);
  t.addEventListener('click', () => { const o = t.getAttribute('aria-expanded') !== 'true'; t.setAttribute('aria-expanded', o); document.getElementById(id).hidden = !o; });
};

/* ---------- actions behind buttons: data-act="key" → review (or do it directly) → state line + event log ----------
   RO_ACT(root, { key: cfg | (button) => cfg }) — cfg is an RO_REVIEW config plus:
     direct (no dialog: reminders and checks) · keep (leave the button: edits) · done: text | (values) => text
     log: { day, t, phase, kind, title, detail, actor, who, src, verify } · after(values, button) */
window.RO_ACT = (root, map) => {
  const OKI = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7"/></svg>';
  let n = 0;
  root.addEventListener('click', e => {
    const b = e.target.closest('[data-act]'); if (!b || !map[b.dataset.act]) return;
    e.preventDefault();
    const a = typeof map[b.dataset.act] === 'function' ? map[b.dataset.act](b) : map[b.dataset.act];
    const finish = vals => {
      const msg = typeof a.done === 'function' ? a.done(vals) : a.done;
      if (!a.keep) {
        const chip = b.closest('.draft');
        const line = chip ? `<span class="chip ok">${a.chip || 'Sent'}</span>` : `<p class="ro-done" role="status">${OKI}<span>${msg}</span></p>`;
        b.insertAdjacentHTML('afterend', line); const next = b.nextElementSibling; b.remove();
        next?.setAttribute('tabindex', '-1'); next?.focus?.({ preventScroll: true });
      }
      if (a.log) window.RO_STATE?.add(Object.assign({ id: 'lv-act-' + b.dataset.act + '-' + (b.dataset.k || n++) + '-' + Date.now().toString(36), detail: '', who: 'human', actor: 'Ananya Menon', verify: 'verified', src: 'Approval record' }, a.log));
      a.after?.(vals, b);
      RO_REVIEW.toast(a.toast || msg);
    };
    if (a.direct) return finish({});
    RO_REVIEW.open(Object.assign({}, a, { onApprove: finish }));
  });
};

/* ---------- maps: offline fallback and searchable map-only places ---------- */
// If the satellite tiles can't load (no internet, blocked), switch the map to a plain dark ground with a note;
// zones, routes and pins are drawn by the app and keep working.
window.RO_TILEGUARD = (map, layer) => {
  let ok = 0, bad = 0, shown = false;
  layer.on('tileload', () => { ok++; });
  layer.on('tileerror', () => {
    bad++;
    if (shown || ok > 0 || bad < 4) return;
    shown = true;
    const c = map.getContainer(); c.classList.add('ro-offline');
    c.insertAdjacentHTML('beforeend', '<p class="ro-offline-note" role="status">Map imagery can’t load (offline). Zones, routes and teams still show.</p>');
  });
  return layer;
};
// Places that are only on the map (camps, roads, the hospital, outages) join the top-bar search: picking one flies there.
window.RO_MAPPLACES = (map, items) => {
  window.RO_MAP = { items: items.map(([t, m, ll, z]) => ({ t, m, k: 'Map', go: () => {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    reduce ? map.setView(ll, z || 13.5) : map.flyTo(ll, z || 13.5, { duration: .8 });
    map.getContainer().focus?.({ preventScroll: true });
  } })) };
};
