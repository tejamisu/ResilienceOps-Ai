# ResilienceOps AI — Demo Walkthrough

A step-by-step guide for judges and evaluators to reproduce the full flood coordination lifecycle.

**Scenario:** IMD has just issued a RED alert for Metro District — 335 mm of rainfall expected over 18 hours. Two wards are CRITICAL. The system must assess risk, coordinate response, and compile after-action learnings — all with human approval gates in place.

---

## Prerequisites

```bash
git clone <repo-url>
cd ResilienceOpsAI
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key_here" > .env
```

Requires Python 3.9+ and a Google AI Studio API key ([get one free at aistudio.google.com](https://aistudio.google.com)).

---

## Quick Demo (Pre-saved outputs — no API needed)

If you want to see agent outputs immediately without an API key, pre-saved outputs are in `demo_outputs/`:

```bash
python3 show_demo_output.py                   # Print all 9 agents in sequence
python3 show_demo_output.py --agent sentinel  # Print one agent
```

---

## Live Demo — Run All 9 Agents

```bash
python3 main.py
```

Runs all 9 agents in disaster lifecycle order. Each agent calls real tools (reads JSON data files, computes scores, generates structured output) and makes live calls to Gemini 3.8 Flash via Google ADK.

Expected runtime: ~8–12 minutes (free-tier API rate limits).

---

## Live Demo — Run Individual Agents

```bash
python3 main.py --list                         # List all agents + phases
python3 main.py --agent risk_memory            # Phase 1: Historical patterns
python3 main.py --agent sentinel               # Phase 1: Ward risk assessment (P0)
python3 main.py --agent preparedness           # Phase 1: Pre-season audit
python3 main.py --agent triage                 # Phase 2: Alert deduplication
python3 main.py --agent field_intel            # Phase 2: Field report geocoding
python3 main.py --agent dispatch               # Phase 2: Team dispatch recommendation
python3 main.py --agent communication          # Phase 2: Multilingual advisories
python3 main.py --agent damage_assessment      # Phase 3: SDRF eligibility
python3 main.py --agent reconciliation         # Phase 3: After-Action Review
```

---

## What to Watch For

### Phase 1 — Forecast & Prepare

**Sentinel Agent** is the most important to show:

- Calls `get_weather_forecast()` → IMD RED alert, 335 mm / 24h
- Calls `get_flood_advisory()` → Northern Wetland Drain within 0.1 m of danger level
- Calls `calculate_ward_risk_score()` for each of 4 wards
- Produces: **W19 CRITICAL (0.804)**, **W12 CRITICAL (0.783)**, W07 MEDIUM, W04 Low
- Calls `generate_preparedness_plan()` → time-sequenced 0–4h, 4–12h actions
- Flags W19's 33% smartphone penetration → **loudspeaker van mandatory**

### Phase 2 — Live Response

**Dispatch Agent** shows the human gate in action:

- Scores all responder teams on availability × proximity × equipment
- Identifies that only FIRE-2 and SDRF-1 have boat access to W19
- Outputs: `⚠ STATUS: AWAITING COMMANDER APPROVAL`
- **No team is deployed without explicit Incident Commander approval**

**Communication Agent** shows multilingual output:

- Drafts advisory in English, Hindi, and Marathi
- Flags W19 for Konkani/Marathi preference (low Hindi literacy)
- Outputs: `DRAFT — AWAITING AUTHORIZED OFFICER APPROVAL`
- **No advisory is sent without Communications Officer sign-off**

### Phase 3 — Recovery

**Reconciliation Agent** closes the feedback loop:

- Compares Sentinel's pre-event predictions against actual outcomes
- Identifies where the model was accurate and where it missed
- Generates corrective actions that feed back into Risk Memory next season

---

## Architecture

See [architecture_masterwork.html](architecture_masterwork.html) for the interactive diagram showing all 9 agents, data flows, human approval gates, and the lessons-learned feedback loop.

---

## Project Structure

```
ResilienceOpsAI/
├── agents/
│   ├── sentinel/          # P0 — ward risk scoring
│   ├── risk_memory/       # Historical flood patterns
│   ├── preparedness/      # Pre-season audit
│   ├── triage/            # Alert deduplication
│   ├── field_intel/       # Field report geocoding
│   ├── dispatch/          # Team matching & dispatch
│   ├── communication/     # Multilingual advisories
│   ├── damage_assessment/ # SDRF eligibility
│   └── reconciliation/    # After-Action Review
├── orchestrator/
│   └── coordinator.py     # ADK Runner manager
├── data/
│   ├── ward_profiles.json
│   ├── historical_floods.json
│   ├── mock_imd_forecast.json
│   └── mock_cwc_advisory.json
├── demo_outputs/          # Pre-saved agent outputs (offline demo)
├── main.py                # Entry point
├── save_demo_outputs.py   # Capture fresh outputs
└── architecture_masterwork.html  # System diagram
```

---

## Key Design Decisions

| Decision | Why |
|---|---|
| Human-in-the-loop for dispatch | No team ever deployed without Incident Commander approval |
| Human-in-the-loop for communications | No advisory sent without Communications Officer sign-off |
| Multilingual output (EN/HI/MR) | Ward 19 has 33% smartphone penetration and low Hindi literacy |
| Loudspeaker channel flag | Digital alerts alone would miss the majority of W19 residents |
| Risk score components | 0.35×hazard + 0.25×exposure + 0.25×vulnerability + 0.15×infrastructure risk |
| Lessons-learned feedback loop | Reconciliation outputs feed back into Risk Memory for next season |
| Google ADK + Gemini 3.8 Flash | Native multi-agent orchestration with structured tool calling |
