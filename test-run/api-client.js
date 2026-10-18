/* ---------- ResilienceOps API client: the agents behind the AI text on each page ----------
   Finds the backend (same origin on Cloud Run; localhost:8080 while developing on the :4317 preview; or ?api=<url>),
   loads each agent's latest result fast, and lets people regenerate it on Gemini. If the backend can't be reached,
   nothing changes: the page keeps its built-in (simulated) text. */
window.RO_API = (() => {
  // dev only: on a deployed (non-local) page we ignore ?api= and any saved override, so a crafted link
  // can't repoint the console's backend at another server. In production the app always uses its own origin.
  const isDev = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || location.protocol === 'file:';
  const q = isDev ? new URLSearchParams(location.search).get('api') : null;
  const saved = isDev ? (() => { try { return localStorage.getItem('ro.api'); } catch (e) { return null; } })() : null;
  if (isDev && q) { try { localStorage.setItem('ro.api', q); } catch (e) {} }
  const base = (q || saved || (location.port === '4317' || location.protocol === 'file:' ? 'http://localhost:8080' : '')).replace(/\/$/, '');
  const timed = (url, opt = {}, ms = 2500) => { const c = new AbortController(), t = setTimeout(() => c.abort(), ms);
    return fetch(base + url, { ...opt, signal: c.signal }).finally(() => clearTimeout(t)); };
  let health = null;
  const ready = timed('/api/health').then(r => r.ok ? r.json() : null).then(h => (health = h)).catch(() => null);
  return {
    base, ready, health: () => health,
    agent: async (name, ctx = {}) => { if (!(await ready)) return null;
      try { const r = await timed(`/api/agents/${name}${ctx.staged ? '?staged=1' : ''}`); return r.ok ? r.json() : null; } catch (e) { return null; } },
    run: async (name, ctx = {}) => { if (!(await ready)) return null;
      try { const r = await timed(`/api/agents/${name}/run`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ context: ctx }) }, 120000); return r.ok ? r.json() : null; } catch (e) { return null; } },
    // human decisions go to the backend's log (the Audit trail); fire and forget
    decide: d => { ready.then(h => h && fetch(base + '/api/decisions', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(d) }).catch(() => {})); }
  };
})();

/* RO_AI.bind(agent, { ctx, host, apply }) — load the agent's result, apply(text, facts, result) to the page, and show
   a provenance line in host: "✦ Gemini 2.5 Flash · 3 min ago · Regenerate" or "Built-in text · Gemini not connected". */
window.RO_AI = (() => {
  const esc = t => String(t ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const ago = iso => { const s = Math.max(0, (Date.now() - new Date(iso)) / 1000); return s < 60 ? 'just now' : s < 3600 ? `${Math.round(s / 60)} min ago` : s < 86400 ? `${Math.round(s / 3600)} h ago` : `${Math.round(s / 86400)} d ago`; };
  const SPARK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5 13.8 10 20.5 12l-6.7 2-1.8 6.5-1.8-6.5L3.5 12l6.7-2z"/></svg>';
  const model = m => (m || '').replace(/^gemini-/, 'Gemini ').replace(/-flash/, ' Flash').replace(/-pro/, ' Pro');
  const chip = (el, res, state) => {
    if (!el) return;
    const h = RO_API.health(), live = h && h.gemini_configured;
    const what = state === 'busy' ? `${SPARK}<span>Asking Gemini… this can take up to a minute</span>`
      : res.source === 'gemini' ? `${SPARK}<span>${esc(model(res.model))} · ${ago(res.generated_at)}</span>`
      : `<span>Built-in text${live ? (res.error ? ' · Gemini didn’t answer, try again' : ' · not generated yet') : ' · Gemini not connected'}</span>`;
    el.innerHTML = `<span class="ro-src-t" role="status">${what}</span>${state === 'busy' ? '' : `<button type="button" class="ro-src-b"${live ? '' : ' disabled title="Add GOOGLE_API_KEY to backend/.env to use Gemini"'} aria-label="Regenerate with Gemini: ${esc(res.display)}">Regenerate</button>`}`;
    el.dataset.src = state === 'busy' ? 'busy' : res.source;
  };
  const bind = async (name, { ctx = {}, host, apply }) => {
    const res = await RO_API.agent(name, ctx);
    if (!res) return null;            // no backend: keep the page's own text
    const el = typeof host === 'function' ? host() : host;
    if (el && !el.classList.contains('ro-src')) { el.classList.add('ro-src'); }
    // only Gemini's own words replace the page's text; otherwise the page keeps its built-in wording
    if (res.source === 'gemini') { try { apply(res.text, res.facts, res); } catch (e) { console.warn('RO_AI', name, e); } }
    chip(el, res);
    el?.addEventListener('click', async e => {
      if (!e.target.closest('.ro-src-b')) return;
      chip(el, res, 'busy');
      const nx = await RO_API.run(name, ctx);
      if (nx) { if (nx.source === 'gemini') { try { apply(nx.text, nx.facts, nx); } catch (err) { console.warn('RO_AI', name, err); } } Object.assign(res, nx); }
      chip(el, res); el.querySelector('.ro-src-b')?.focus();
    });
    return res;
  };
  return { bind, esc };
})();
