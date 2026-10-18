
/* ================= motion + interaction layer (16 Oct 2026) — pairs with motion.css ================= */
window.RO_MOTION = (() => {
  const reduce = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  // cubic-bezier easing for JS-driven movement (same curves as the CSS tokens)
  const bezier = (x1, y1, x2, y2) => t => {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    let u = t; for (let i = 0; i < 6; i++) { const f = ((ax * u + bx) * u + cx) * u - t, d = (3 * ax * u + 2 * bx) * u + cx; if (Math.abs(d) < 1e-6) break; u -= f / d; }
    return ((ay * u + by) * u + cy) * u;
  };
  const EASE = { out: bezier(0.23, 1, 0.32, 1), inOut: bezier(0.77, 0, 0.175, 1) };
  // tween a value with rAF; returns a promise (instant under reduced motion)
  const tween = (ms, fn, ease = EASE.inOut) => new Promise(res => {
    if (reduce()) { fn(1); return res(); }
    const t0 = performance.now();
    const step = now => { const k = Math.min(1, (now - t0) / ms); fn(ease(k)); k < 1 ? requestAnimationFrame(step) : res(); };
    requestAnimationFrame(step);
  });

  /* ---------- interactive charts ----------
     scrub(svg, { n, x(i), label(i), rows(i) → [{ name, value, y, color, dash }], top, bottom, band(i)?, note(i)?, start })
     x/y are in the chart's own viewBox units. Pointer snaps to the nearest point; ←/→/Home/End do the same from the keyboard,
     and a polite live region reads the point out, so the tooltip is never the only way to the numbers. */
  const scrub = (svg, cfg) => {
    if (!svg) return;
    const host = svg.parentElement;
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    let st = svg._roScrub;
    if (!st) {
      st = svg._roScrub = { i: -1 };
      st.tip = document.createElement('div'); st.tip.className = 'ro-tip jump'; st.tip.setAttribute('aria-hidden', 'true'); host.appendChild(st.tip);
      st.live = document.createElement('span'); st.live.className = 'sr-only'; st.live.setAttribute('aria-live', 'polite'); host.appendChild(st.live);
      svg.classList.add('ro-chart');
      if (!svg.hasAttribute('tabindex')) svg.setAttribute('tabindex', '0');
      if (svg.getAttribute('aria-hidden') === 'true') svg.removeAttribute('aria-hidden');
      if (!svg.getAttribute('role')) svg.setAttribute('role', 'img');
      const lab = svg.getAttribute('aria-label') || '';
      if (!/arrow keys/.test(lab)) svg.setAttribute('aria-label', (lab ? lab.replace(/\.?$/, '. ') : '') + 'Focus and use the arrow keys to read each point.');
      const at = e => { const p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY; return p.matrixTransform(svg.getScreenCTM().inverse()).x; };
      const nearest = vx => { const c = st.cfg; let b = 0, bd = Infinity; for (let i = 0; i < c.n; i++) { const d = Math.abs(c.x(i) - vx); if (d < bd) { bd = d; b = i; } } return b; };
      svg.addEventListener('pointermove', e => show(nearest(at(e))));
      svg.addEventListener('pointerdown', e => { const i = nearest(at(e)); show(i); st.cfg.pick?.(i); });   // optional: a chart can act on the picked point
      svg.addEventListener('pointerleave', () => { if (document.activeElement !== svg) hide(); });
      svg.addEventListener('focus', () => show(st.i >= 0 ? st.i : (st.cfg.start ?? st.cfg.n - 1), true));
      svg.addEventListener('blur', hide);
      svg.addEventListener('keydown', e => {
        const c = st.cfg, k = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1 }[e.key];
        if (k) { e.preventDefault(); show(Math.max(0, Math.min(c.n - 1, (st.i < 0 ? c.start ?? 0 : st.i) + k * (e.shiftKey ? 4 : 1))), true); }
        else if (e.key === 'Home') { e.preventDefault(); show(0, true); }
        else if (e.key === 'End') { e.preventDefault(); show(c.n - 1, true); }
        else if (e.key === 'Escape') hide();
        else if ((e.key === 'Enter' || e.key === ' ') && st.cfg.pick && st.i >= 0) { e.preventDefault(); st.cfg.pick(st.i); }
      });
    }
    st.cfg = cfg;
    const NS = 'http://www.w3.org/2000/svg';
    function overlay() { if (!st.g || !svg.contains(st.g)) { st.g = document.createElementNS(NS, 'g'); st.g.setAttribute('class', 'ro-scrub'); svg.appendChild(st.g); } return st.g; }
    function show(i, speak) {
      const c = st.cfg, g = overlay(), rows = c.rows(i), X = c.x(i);
      const first = !st.tip.classList.contains('on');
      st.i = i;
      let s = '';
      if (c.band) { const b = c.band(i); s += `<rect x="${b.x}" y="${c.top}" width="${b.w}" height="${c.bottom - c.top}" rx="6" fill="rgba(255,255,255,.07)"/>`; }
      else s += `<line x1="${X}" x2="${X}" y1="${c.top}" y2="${c.bottom}" stroke="rgba(242,244,242,.55)" stroke-width="1"/>`;
      rows.forEach(r => { if (r.y != null) s += `<circle cx="${X}" cy="${r.y}" r="4" fill="${r.color}" stroke="#141716" stroke-width="2"/>`; });
      g.innerHTML = s; g.classList.add('on');
      // tooltip: above the highest dot, kept inside the card
      st.tip.innerHTML = `<b>${c.label(i)}</b>` + rows.map(r => `<p><i class="${r.dash ? 'dash' : ''}" style="--c:${r.color}"></i><span>${r.name}</span><em>${r.value}</em></p>`).join('') + (c.note && c.note(i) ? `<small>${c.note(i)}</small>` : '');
      const m = svg.getScreenCTM(), hr = host.getBoundingClientRect();
      const ys = rows.map(r => r.y).filter(v => v != null), top = ys.length ? Math.min(...ys) : c.top;
      const px = m.a * X + m.e - hr.left, py = m.d * top + m.f - hr.top;
      const w = st.tip.offsetWidth, h = st.tip.offsetHeight;
      const left = Math.max(4, Math.min(hr.width - w - 4, px - w / 2));
      let tY = py - h - 12; if (hr.top + tY < 8) tY = py + 14;   // above the point unless that leaves the window
      st.tip.classList.toggle('jump', first);
      st.tip.style.transform = `translate(${left.toFixed(1)}px, ${tY.toFixed(1)}px)`;
      st.tip.classList.add('on');
      if (first) requestAnimationFrame(() => st.tip.classList.remove('jump'));
      if (speak) { clearTimeout(st.t); st.t = setTimeout(() => { st.live.textContent = `${c.label(i)}: ` + rows.map(r => `${r.name} ${r.value}`).join(', ') + (c.note && c.note(i) ? `. ${c.note(i)}` : ''); }, 120); }
    }
    function hide() { st.tip.classList.remove('on'); st.g && st.g.classList.remove('on'); }
    if (st.tip.classList.contains('on') && st.i >= 0) show(Math.min(st.i, cfg.n - 1));   // a redraw keeps the reading in place
  };

  /* ---------- numbers that change tick into place ---------- */
  const NUM = '#s-cov, #s-need, .count, .big, .pg-big b, #orb-n, .rp-n, .fbtn .n, .rp-filt .n, #pipe-open, #cap-gaps, #rtl-cov, #tg-n, .as-hero b, .rv-hero b';
  let ready = false; setTimeout(() => { ready = true; }, 1200);
  const tick = el => { if (!el) return; el.classList.remove('ro-num'); void el.offsetWidth; el.classList.add('ro-num'); };
  new MutationObserver(ms => {
    if (!ready) return;
    const seen = new Set();
    ms.forEach(m => { const n = m.target.nodeType === 3 ? m.target.parentElement : m.target; const el = n && n.closest && n.closest(NUM); if (el && !seen.has(el) && !el.closest('.tour-clone, .ro-tip')) { seen.add(el); tick(el); } });
  }).observe(document.body, { subtree: true, childList: true, characterData: true });
  document.addEventListener('animationend', e => { if (e.animationName === 'ro-num') e.target.classList.remove('ro-num'); });

  /* ---------- content swaps: report body, filtered lists ---------- */
  const SWAP = ['#rp-doc', '#tl-groups', '#tr-list', '#rp-list', '#lesson']   // #cl-detail has its own ring entrance;
  const watchSwaps = () => SWAP.forEach(sel => { const el = document.querySelector(sel); if (!el || el._roSwap) return; el._roSwap = 1;
    new MutationObserver(() => { if (!ready) return; el.classList.remove('ro-swap'); void el.offsetWidth; el.classList.add('ro-swap'); }).observe(el, { childList: true }); });
  document.addEventListener('animationend', e => { if (e.animationName === 'ro-swap') e.target.classList.remove('ro-swap'); });

  /* ---------- tooltips: once one has shown, neighbours open instantly ---------- */
  let warm;
  document.addEventListener('pointerover', e => { if (e.target.closest && e.target.closest('[data-tip]')) { clearTimeout(warm); warm = setTimeout(() => document.body.classList.add('ro-tip-warm'), 420); } });
  document.addEventListener('pointerout', e => { if (e.target.closest && e.target.closest('[data-tip]') && !(e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('[data-tip]'))) {
    clearTimeout(warm); warm = setTimeout(() => document.body.classList.remove('ro-tip-warm'), 500); } });

  // grow(el, from, to): a bar that changed value slides from the old length to the new one (transform only, 400 ms ease-in-out)
  const grow = (el, from, to, base = '') => { if (!el || reduce() || from == null || from === to || !(to > 0)) return;
    el.animate([{ transform: `${base} scaleX(${from / to})` }, { transform: `${base} scaleX(1)` }], { duration: 400, easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }); };
  return { scrub, tween, EASE, watchSwaps, reduce, grow };
})();
