# ResilienceOps AI — agents backend (Wayanad)

Eleven AI agents on **Google ADK + Gemini** that write the recommendations, explanations and drafts in the ResilienceOps
app, for the simulated Wayanad landslide and flash flood (event WYN-2026-001). Every output is a **recommendation**;
a person approves it in the app (Incident Commander; the Relief & Recovery Coordinator in Recover).

Built from the original multi-agent design in `legacy/metro/` (Sentinel, Triage, Field Intel, Dispatch, Communication,
Damage Assessment, Reconciliation, Risk Memory, Preparedness), re-grounded in the app's Wayanad scenario.

## How an agent works

```
data/wayanad.json ──► tools (deterministic Python) ──► facts: scores, tasks, gaps, routes   ─┐
                         ▲                                                                  ├─► JSON the app binds
                         └── Gemini (Google ADK LlmAgent) calls the tools, writes the text ─┘
                                 why · recommendation · drafts · confidence · limitation
```

* `facts` are computed by code, so the numbers on screen are the same with or without Gemini.
* `text` is written by Gemini through ADK (the agent decides which tools to call). If Gemini isn't configured or
  doesn't answer, rule-written text from the same facts is returned, and `source` says which: `gemini` or `rules`.
* The app swaps in Gemini's text and shows its source ("✦ Gemini … · 3 min ago · Regenerate"); without the backend
  the app keeps its built-in text, so a demo never breaks.

| Agent (`name`) | Phase | Feeds in the app | Was |
|---|---|---|---|
| Forecast & Impact (`forecast_impact`) | Prepare | place ranking and risk factors | Sentinel |
| Risk Memory (`risk_memory`) | Prepare | past events behind the place factors | Risk Memory |
| Preparedness (`preparedness`) | Prepare | Plan to approve, "Why these tasks?", request drafts | Preparedness |
| Field Intelligence (`field_intel`) | Respond | the km 7 incident and other alerts | Triage + Field Intel |
| Dispatch & Delegation (`dispatch`) | Respond | "AI recommends: send …", ETA, Why this? | Dispatch |
| Forecast vs Ground Reality (`ground_truth`) | Respond | Vythiri "3 h earlier than forecast", Raise priority | new |
| Communications (`communications`) | all | public advisory (English + Malayalam), Situation report #4 | Communication |
| Relief Coverage (`relief_coverage`) | Recover | "Chooralmala ward 11 may be missed", need gaps | new |
| Damage Assessment (`damage_assessment`) | Recover | verified impact | Damage Assessment |
| Recovery & Reconciliation (`reconciliation`) | Recover | Learn → Prepare lessons | Reconciliation |
| Command Orchestrator (`orchestrator`) | all | Respond → Recover handover | new (was the coordinator) |

## Run locally

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then put your Google AI Studio key in .env
python main.py --list         # the agents
python main.py dispatch       # one agent (Gemini if the key is set)
python -m uvicorn api:app --port 8080
```

Open the app at http://localhost:8080/ (the API serves it), or keep using the :4317 preview — the app finds the API at
localhost:8080 by itself. Then `curl -X POST localhost:8080/api/warm` once to run every agent on Gemini and cache the
results (about a minute per agent on the free tier). Tests: `python tests/test_agents.py` (no key needed).

`GEMINI_MODEL` pins a model; left empty, the backend uses the newest Gemini Flash model your key can call.

## API

| | |
|---|---|
| `GET /api/health` | Gemini configured? agents, app file |
| `GET /api/agents/{name}` | fast: last saved run, else rule-written now (`?staged=1` for dispatch after Prepare's handover) |
| `POST /api/agents/{name}/run` | run on Gemini now (body `{"context": {...}}`) |
| `POST /api/warm`, `GET /api/warm` | run all agents on Gemini in the background; progress |
| `GET /api/decisions`, `POST /api/decisions` | the human decision log (approvals, edits, sends) |
| `GET /api/scenario` | the Wayanad scenario data |
| `GET /` | the app |

## Deploy to Cloud Run (one service: API + app)

You need a Google Cloud project with billing, and the `gcloud` CLI signed in as you.

```bash
cd backend && ./prepare_web.sh                              # builds the app into web/index.html
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
printf '%s' 'PASTE-YOUR-KEY' | gcloud secrets create gemini-api-key --data-file=-
gcloud run deploy resilienceops --source . --region asia-south1 --allow-unauthenticated \
  --set-secrets GOOGLE_API_KEY=gemini-api-key:latest
curl -X POST https://<your-service-url>/api/warm            # cache every agent's text once
```

The decision log and cached runs live in the container (`runs/`), so they reset on redeploy; swap `core/store.py`
for Firestore to keep them.

## Rules every agent follows
Recommend, never act · use only figures the tools return · no casualty or death figures · say what is verified,
estimated or reported · plain English · Malayalam drafts are checked by the DEOC language officer before sending.

Simulated scenario. Place names are real; events and numbers are illustrative.
