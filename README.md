# ResilienceOps AI

A command view for a district disaster office (DDMA Wayanad, Kerala): AI agents forecast, prepare, dispatch and track
relief; a person approves every step. Demo event **WYN-2026-001**, landslide & flash flood — **simulated** (real place
names, illustrative events and figures, no casualty data).

| | |
|---|---|
| The app | `test-run/resilienceops.html` — built by `test-run/build-app.py` from the three phase pages, the views and the shell |
| Field app (phone) | `test-run/field.html` — Rescue Unit 2's task inbox, English / മലയാളം |
| Agents backend | `backend/` — 11 agents on **Google ADK + Gemini**, FastAPI, Cloud Run ready (see `backend/README.md`) |
| Design | `design-system.md`, `design-checklist.md` |
| Submission | `submission/` — deck (PDF + HTML), demo script, screenshots |
| Security tests | `backend/tests/security/` — re-runnable attack probes and the before/after report |
| Live demo | https://resilienceops-520305653218.asia-south1.run.app (simulated data) |

## Run it

```bash
# 1. the app only (built-in text): open test-run/resilienceops.html, or serve the folder
cd test-run && python3 build-app.py && python3 -m http.server 4317    # http://localhost:4317/resilienceops.html

# 2. with the agents (Gemini): see backend/README.md
cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
cp .env.example .env    # add GOOGLE_API_KEY
python -m uvicorn api:app --port 8080                                 # http://localhost:8080/
```

Phases: `?phase=prepare|respond|recover` · views: `?view=timeline|reports|audit|forecast|tasks|relief` · roles from the
avatar menu (Incident Commander, Hazard Analyst, Relief & Recovery Coordinator).

## Principles
Recommend, never act · evidence and confidence on every AI output · verified / estimated / reported always visible ·
no casualty figures · colour carries meaning only · WCAG 2.2 AA · works offline and without the AI.

Credits: agent design from the team's original multi-agent backend (`backend/legacy/metro/`).
