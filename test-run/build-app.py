#!/usr/bin/env python3
"""Build resilienceops.html: one app holding Prepare, Respond and Recover.

Sources are the three phase pages (kept as references). Each phase's styles, markup and
script go into the app unchanged except for the navigation changes agreed on 15 Oct 2026:
- the phases leave the top nav (it keeps Timeline · Reports · Audit),
- the event chip shows only the event; the current phase is a quiet tag on the map,
- the avatar opens the role and phase switch (Incident Commander · Hazard Analyst · Relief & Recovery Coordinator).

Run from this folder:  python3 build-app.py
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = {'prepare': 'prepare-mockup.html', 'respond': 'wayanad-dashboard.html', 'recover': 'recover-mockup.html'}
TITLE = {'prepare': 'Wayanad Readiness', 'respond': 'Wayanad Response', 'recover': 'Wayanad Recovery'}
ORDER = ['prepare', 'respond', 'recover']
LABEL = {'prepare': 'Prepare', 'respond': 'Respond', 'recover': 'Recover'}

NAV = ('<nav class="nav" aria-label="Views">'
       '<a href="?view=timeline">Timeline</a><a href="?view=reports">Reports</a><a href="?view=audit">Audit</a></nav>')
EVENT_ID = 'WYN-2026-001'
VIEW_ORDER = ['timeline', 'reports', 'audit', 'forecast', 'tasks', 'relief', 'risk']  # the last four sit behind the cards' ↗ and links, not in the nav



def split(page):
    s = (HERE / SRC[page]).read_text()
    style = re.search(r'<style>.*?</style>', s, re.S).group(0)
    body_cls = re.search(r'<body([^>]*)>', s).group(1)
    body_cls = re.search(r'class="([^"]*)"', body_cls).group(1) if 'class=' in body_cls else ''
    b0 = s.index('>', s.index('<body')) + 1
    b1 = s.index('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet')
    body = s[b0:b1]
    js = s[s.index('<script>', b1) + len('<script>'):s.rindex('</script>')]
    return style, body_cls, body, js


def must_sub(pattern, repl, text, flags=0, count=1):
    out, n = re.subn(pattern, repl, text, count=count, flags=flags)
    assert n, f'no match: {pattern[:70]}'
    return out


OPEN_LINKS = {
    'Open forecast detail': '?view=forecast#rain', 'Open full forecast timeline': '?view=forecast#outlook', 'Open capacity detail': '?view=tasks#resources',
    'Open rainfall and forecast detail': '?view=forecast#rain', 'Open all tasks': '?view=tasks#board', 'Open relief camps': '?view=relief#camps',
    'Open all relief requests': '?view=relief#requests', 'Open full recovery timeline': '?view=timeline&f=recover', 'Open forecast versus outcome': '?view=forecast#outcome',
}
TOUR_HINT = ' Switch role or phase from your initials at the top right.'

parts = []
for ph in ORDER:
    style, cls, body, js = split(ph)
    # top nav: phases out
    body = must_sub(r'<nav class="nav" aria-label="Operational phase">.*?</nav>', NAV, body, re.S)
    # event chip shows the event only; the phase is a tag on the map (beside the map controls)
    chip = r'<button type="button" class="pill-btn glass" data-toast="Event switcher[^"]*">.*?</button>'
    body = must_sub(r'\s*' + chip, '', body, re.S)  # one event, a dropdown that did nothing: the ID moves to the subline
    body = must_sub(r'<p class="sub"([^>]*)>', lambda m: f'<p class="sub"{m.group(1)}>{EVENT_ID} · ', body)
    # scripts: drop the old nav handlers, point cross-phase links at the app
    js = re.sub(r"  document\.querySelectorAll\('\.nav button'\)\.forEach\(b => b\.addEventListener\('click', \(\) => \{\n.*?\n  \}\)\);\n", '', js, count=1, flags=re.S)
    js = js.replace("  document.querySelectorAll('.nav [data-href]').forEach(b => b.addEventListener('click', () => { location.href = b.dataset.href; }));\n", '')
    js = js.replace("location.href = 'wayanad-dashboard.html'", "location.href = '?phase=respond'")
    js = js.replace("location.href = 'recover-mockup.html'", "location.href = '?phase=recover'")
    # cards' ↗ : real pages instead of placeholder toasts
    for lab, href in OPEN_LINKS.items():
        body = re.sub(r'<a class="open" href="#" aria-label="' + re.escape(lab) + r'" data-toast="[^"]*">', f'<a class="open" href="{href}" aria-label="{lab}">', body)
    js = js.replace("    $('#event-phase').textContent = 'Respond';\n", "    $('#nav-respond')?.classList.add('live');\n")
    # tours: mention the role switch on the first step
    js = must_sub(r"(const TOUR = \[\n    \{ t: '[^']*', p: '[^']*)(')", lambda m: m.group(1) + TOUR_HINT + m.group(2), js)
    assert '</script' not in js
    parts.append((ph, style, cls, body, js))

# ---------- Timeline · Reports · Audit (views-src.html) ----------
VS = (HERE / 'views-src.html').read_text()
views_css = re.search(r'<style>(.*?)</style>', VS, re.S).group(1)
views_js = VS[VS.index('<script>') + len('<script>'):VS.rindex('</script>')]
base_style = parts[ORDER.index('recover')][1]          # the shared stylesheet as it ships in Recover
rbody = parts[ORDER.index('recover')][3]
topbar = re.search(r'<header class="topbar">.*?</header>', rbody, re.S).group(0)
SECTIONS = {m.group(1): (m.group(2), m.group(3)) for m in
            re.finditer(r'<section data-view="(\w+)" data-title="([^"]*)">\n(.*?)\n</section>\n\n(?=<!-- =|<script>)', VS, re.S)}
assert sorted(SECTIONS) == sorted(VIEW_ORDER), SECTIONS.keys()
views = []
for v in VIEW_ORDER:
    title, inner = SECTIONS[v]
    vbody = ('<a class="skip" href="#vmain">Skip to content</a>\n<div class="app view-app">\n  ' + topbar + inner +
             '\n</div>\n<div class="toast glass" id="toast" role="status" aria-live="polite"></div>\n')
    views.append((v, title, base_style.replace('</style>', views_css + '</style>'), vbody))

SHELL_CSS = (HERE / 'app-shell.css').read_text()
SHELL_JS = (HERE / 'switcher-art.js').read_text() + '\n' + (HERE / 'app-shell.js').read_text()
MOTION_CSS = (HERE / 'motion.css').read_text()   # appended last in every page's styles so it extends them
MOTION_JS = (HERE / 'motion.js').read_text()
STATE_JS = (HERE / 'state.js').read_text()     # shared handovers, review dialog, event log (before the views and phases)
API_JS = (HERE / 'api-client.js').read_text()   # the agents' backend (falls back silently when it isn't there)

out = ['<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>ResilienceOps · Wayanad</title>\n'
       '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
       '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500&family=Noto+Sans+Malayalam:wght@400&display=swap" rel="stylesheet">\n'
       '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n'
       '<style>\n' + SHELL_CSS + '</style>\n</head>\n<body>\n'
       '<!-- Built by build-app.py from prepare-mockup.html, wayanad-dashboard.html and recover-mockup.html. -->\n']
for ph, style, cls, body, js in parts:
    out.append(f'<template id="ph-{ph}" data-body-class="{cls}" data-title="{TITLE[ph]}">\n{style.replace("</style>", MOTION_CSS + "</style>")}\n{body}</template>\n')
for v, title, style, vbody in views:
    out.append(f'<template id="view-{v}" data-title="{title}">\n{style.replace("</style>", MOTION_CSS + "</style>")}\n{vbody}</template>\n')
out.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n<script>\nwindow.PHASES = {};\n')
out.append(STATE_JS + '\n' + API_JS + '\n')
# the scenario the agents use (backend/data/wayanad.json), so pages that explain the agents show the same numbers
SCEN = HERE.parent / 'backend' / 'data' / 'wayanad.json'
out.append('window.RO_SCENARIO = ' + (SCEN.read_text() if SCEN.exists() else 'null') + ';\n')
out.append(views_js + '\n')
for ph, style, cls, body, js in parts:
    out.append(f'PHASES.{ph} = function () {{\n{js}\n}};\n')
out.append(MOTION_JS + '\n' + SHELL_JS + '</script>\n</body>\n</html>\n')
(HERE / 'resilienceops.html').write_text(''.join(out))
# the field responder app (phone): its own page, with the shared event state and API client inlined
FS = (HERE / 'field-src.html').read_text()
(HERE / 'field.html').write_text(FS.replace('<script>\n/* ---------- field app', '<script>\n' + STATE_JS + '\n' + API_JS + '\n/* ---------- field app', 1))
print('built resilienceops.html')
