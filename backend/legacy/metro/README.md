# ResilienceOps AI

**Multi-Agent Urban Flood Coordination Platform**
*Hack2Skill Google Hackathon — Sustainability & Social Impact*

---

## The Problem

Urban flooding in India affects tens of millions annually. During a live flood event, city Emergency Operations Centres (EOCs) face:

- Fragmented information arriving from dozens of sources (IMD, CWC, ward officers, NGOs, community WhatsApp groups) with no unified view
- No systematic way to prioritize which ward to send rescue teams to first
- Advisories drafted manually in multiple languages under time pressure
- Responder teams dispatched without route-safety awareness
- Post-event damage reports compiled weeks later, too slow for state compensation claims
- Lessons from each flood never systematically fed back into next-season planning

**ResilienceOps AI** replaces this fragmented process with nine coordinated AI agents that span the full disaster lifecycle — from pre-event forecasting to post-event reconciliation.

---

## Architecture

### Three-Phase Disaster Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: FORECAST & PREPARE                                        │
│                                                                     │
│  ┌──────────────┐   ┌─────────────┐   ┌──────────────┐             │
│  │  Risk Memory │   │   Sentinel  │   │ Preparedness │             │
│  │  (History)   │──▶│ (Forecast & │──▶│  (Pre-season │             │
│  │              │   │  Risk Score)│   │   Planning)  │             │
│  └──────────────┘   └──────┬──────┘   └──────────────┘             │
│                            │                                        │
│                    Ward Risk Briefing                               │
│                            │                                        │
├────────────────────────────▼────────────────────────────────────────┤
│  PHASE 2: LIVE RESPONSE                                             │
│                                                                     │
│  ┌──────────┐   ┌────────────┐   ┌──────────┐   ┌───────────────┐  │
│  │  Triage  │──▶│ Field Intel│──▶│ Dispatch │──▶│ Communication │  │
│  │(Dedup &  │   │(Geocode &  │   │(Team-    │   │ (Multilingual │  │
│  │ Priorit.)│   │ Classify)  │   │ Match)   │   │  Advisories)  │  │
│  └──────────┘   └────────────┘   └──────────┘   └───────────────┘  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  PHASE 3: RECOVER & IMPROVE                                         │
│                                                                     │
│  ┌──────────────────┐   ┌─────────────────┐                        │
│  │ Damage Assessment│──▶│ Reconciliation  │                        │
│  │ (SDRF Claims)    │   │ (AAR + Lessons) │                        │
│  └──────────────────┘   └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Sources

| Source | What it provides | Agents that use it |
|--------|-----------------|-------------------|
| IMD (India Meteorological Department) | Rainfall forecasts, RED/ORANGE/YELLOW alerts | Sentinel |
| CWC (Central Water Commission) | Water body levels, breach timelines | Sentinel |
| Ward profiles | Population, vulnerability index, infrastructure, shelters, routes | All agents |
| Historical flood records | Past events, casualties, lessons, recurring hotspots | Risk Memory, Sentinel |

---

## Agents

### Phase 1 — Forecast & Prepare

| Agent | Human Owner | What it does |
|-------|-------------|-------------|
| **Sentinel** | City Incident Commander | Converts IMD/CWC forecasts + ward vulnerability data into a ward-level risk score (0–1), priority ranking, population exposure estimate, and time-sequenced preparedness plan |
| **Risk Memory** | DDMA Planner | Surfaces historical flood patterns, recurring hotspot scores, and calibration parameters for Sentinel (risk multiplier, hotspot adjustment, vulnerability weight) |
| **Preparedness** | DDMA / Municipal Engineer | Audits shelter readiness, evacuation routes, resource pre-positioning, and community drill status; outputs a phased action plan with cost estimates |

### Phase 2 — Live Response

| Agent | Human Owner | What it does |
|-------|-------------|-------------|
| **Triage** | EOC Watch Officer | Deduplicates multi-source reports using keyword + time-window clustering; scores each cluster by hazard, confidence, vulnerability, and asset risk |
| **Field Intel** | Ward Officer / Field Supervisor | Parses raw field reports (text/voice transcripts); extracts severity, water level, vulnerability flags, geocodes to a ward, classifies incident type, checks forecast alignment |
| **Dispatch** | Incident Commander | Scores every available responder team against each incident (availability × proximity × equipment × workload); recommends primary + backup team with route and ETA |
| **Communication** | Authorized Communications Officer | Drafts multilingual public advisories (English/Hindi/Marathi) and partner notifications using parameterised templates; flags loudspeaker channel for low-connectivity wards |

### Phase 3 — Recover & Improve

| Agent | Human Owner | What it does |
|-------|-------------|-------------|
| **Damage Assessment** | District Collector | Aggregates post-event field reports; computes structural damage, monetary loss (NDMA unit costs), displacement status, and SDRF compensation eligibility |
| **Reconciliation** | District Incident Commander | Reconciles deployed resources against logged incidents, computes response-time metrics, identifies coverage gaps, and drafts the After-Action Review |

### Human Approval Gates

Every agent output is a **recommendation, not an autonomous action**. Critical gates:

- Dispatch recommendations → **Incident Commander must approve** before any team is deployed
- Public advisories → **Authorized Communications Officer must approve** before any message is sent
- State escalation requests → **Incident Commander must approve** before transmission
- Damage reports → **District Collector countersignature** required before SDRF submission

---

## Risk Scoring Formula (Sentinel)

```
composite_score = 0.35 × hazard_severity
                + 0.25 × exposure
                + 0.20 × vulnerability
                + 0.15 × infrastructure_risk
                + 0.05 × historical_weight

CRITICAL ≥ 0.70  |  HIGH ≥ 0.50  |  MEDIUM ≥ 0.30  |  LOW < 0.30
```

---

## Quickstart

### Prerequisites

- Python 3.9+ (Python 3.11+ recommended — avoids Google library FutureWarnings)
- A Google AI Studio API key ([get one here](https://aistudio.google.com))

### Installation

```bash
git clone <repo-url>
cd ResilienceOpsAI
pip install -r requirements.txt
```

### Configure API Key

```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
```

> **Never commit `.env` to version control.**

### Run

```bash
# Full 9-agent lifecycle demo (all three phases)
python3 main.py

# Run a single agent
python3 main.py --agent sentinel
python3 main.py --agent triage
python3 main.py --agent dispatch

# List all available agents
python3 main.py --list
```

---

## Project Structure

```
ResilienceOpsAI/
├── agents/
│   ├── sentinel/          # Forecast & risk scoring (P0)
│   ├── risk_memory/       # Historical pattern analysis
│   ├── preparedness/      # Pre-season audit & planning
│   ├── triage/            # Alert deduplication & prioritization
│   ├── field_intel/       # Field report parsing & geocoding
│   ├── dispatch/          # Responder team matching
│   ├── communication/     # Multilingual advisory drafting
│   ├── damage_assessment/ # Post-event loss quantification
│   └── reconciliation/    # After-action review
├── orchestrator/
│   └── coordinator.py     # ADK Runner management, retry logic
├── data/
│   ├── ward_profiles.json         # 4 wards with vulnerability data
│   ├── mock_imd_forecast.json     # Simulated IMD RED alert
│   ├── mock_cwc_advisory.json     # Simulated CWC water body advisory
│   └── historical_floods.json     # 3 historical flood events
├── main.py                # CLI entry point
├── save_demo_outputs.py   # Capture all 9 agent outputs to demo_outputs/
├── show_demo_output.py    # View pre-saved outputs offline (no API needed)
├── api.py                 # FastAPI HTTP endpoints (optional)
├── DEMO.md                # Judge-facing walkthrough
├── LICENSE
├── requirements.txt
└── demo_outputs/          # Pre-saved agent outputs (JSON)
    ├── sentinel.json
    ├── risk_memory.json
    └── ...
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent framework | [Google ADK](https://google.github.io/adk-docs/) (`google-adk`) |
| LLM | Gemini 3.8 Flash (`gemini-3.8-flash`) |
| Data models | Pydantic v2 |
| CLI output | Rich |
| Runtime | Python 3.9+ |

---

## Scenario: Metro District Flash Flood

The demo scenario simulates a real-world event:

- **Trigger:** IMD RED alert — 335 mm cumulative rainfall / 24h (threshold: 204 mm)
- **Water bodies:** Northern Wetland Drain at DANGER (breach in 0.8 hours); Metro Seasonal Canal at WARNING (breach in 2.2 hours)
- **Critical ward:** W19 (North Wetlands) — single road access, 33% smartphone penetration, zero municipal pump stations, 38,000 population
- **District resource gap:** 4 pumps, 2 rescue boats, 750 shelter beds

Running `python3 main.py` walks through all three phases and shows each agent's output in sequence.

---

## Impact

| Metric | Traditional EOC | ResilienceOps AI |
|--------|----------------|-----------------|
| Ward risk assessment | 45–90 min (manual) | < 3 min (Sentinel) |
| Alert deduplication | Manual, often missed | Automatic, confidence-scored |
| Advisory drafting (3 languages) | 30–60 min per advisory | < 1 min per advisory |
| Dispatch recommendation | Experience-dependent | Scored across all teams + routes |
| Post-event damage report | 2–4 weeks | Hours after event |

---

## Team

Built for the **Hack2Skill Google Hackathon — Sustainability & Social Impact** track.

Contact: via the repository owner
