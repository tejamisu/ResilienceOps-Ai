"""
ResilienceOps AI — FastAPI HTTP Layer

Wraps the ADK multi-agent system with REST endpoints so judges and evaluators
can call agents directly via HTTP without needing to run the CLI.

Usage:
    pip install fastapi uvicorn
    uvicorn api:app --reload

Endpoints:
    GET  /                          Health check + available agents
    POST /run/{agent_name}          Run a specific agent with a custom prompt
    POST /demo/{agent_name}         Run an agent with the built-in demo prompt
    GET  /demo/{agent_name}/cached  Return pre-saved output (no API call)
    POST /phase/{phase_name}        Run all agents in a phase
    GET  /agents                    List all agents with metadata
"""

import os
import json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    raise SystemExit("FastAPI not installed. Run: pip install fastapi uvicorn")

from orchestrator import ResilienceOpsCoordinator
from save_demo_outputs import AGENT_PROMPTS, PHASE_LABELS, OUTPUT_DIR, DEMO_SEQUENCE

app = FastAPI(
    title="ResilienceOps AI",
    description="Multi-Agent Urban Flood Coordination Platform — Google ADK + Gemini 3.8 Flash",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PHASE_TO_AGENTS = {
    "forecast": ["risk_memory", "sentinel", "preparedness"],
    "response": ["triage", "field_intel", "dispatch", "communication"],
    "recovery": ["damage_assessment", "reconciliation"],
}

AGENT_META = {
    name: {
        "phase": PHASE_LABELS[name],
        "demo_prompt": AGENT_PROMPTS[name],
    }
    for name in DEMO_SEQUENCE
}


class RunRequest(BaseModel):
    prompt: str


class AgentResponse(BaseModel):
    agent: str
    phase: str
    prompt: str
    output: str
    model: str = "gemini-3.8-flash"
    duration_seconds: float
    timestamp: str
    source: str = "live"  # "live" | "cached"


def _coordinator() -> ResilienceOpsCoordinator:
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY not set. Add it to your .env file.",
        )
    return ResilienceOpsCoordinator()


def _load_cached(agent_name: str):
    path = os.path.join(OUTPUT_DIR, f"{agent_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    cached = [n for n in DEMO_SEQUENCE if os.path.exists(os.path.join(OUTPUT_DIR, f"{n}.json"))]
    return {
        "service": "ResilienceOps AI",
        "version": "1.0.0",
        "status": "operational",
        "api_key_configured": api_key_set,
        "agents_available": DEMO_SEQUENCE,
        "agents_with_cached_output": cached,
        "docs": "/docs",
    }


# ---------------------------------------------------------------------------
# GET /agents
# ---------------------------------------------------------------------------

@app.get("/agents")
def list_agents():
    return {
        "agents": [
            {
                "name": name,
                "phase": AGENT_META[name]["phase"],
                "has_cached_output": os.path.exists(os.path.join(OUTPUT_DIR, f"{name}.json")),
            }
            for name in DEMO_SEQUENCE
        ],
        "phases": list(PHASE_TO_AGENTS.keys()),
    }


# ---------------------------------------------------------------------------
# POST /run/{agent_name}  — live, custom prompt
# ---------------------------------------------------------------------------

@app.post("/run/{agent_name}", response_model=AgentResponse)
def run_agent(agent_name: str, body: RunRequest):
    if agent_name not in AGENT_META:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent '{agent_name}'. Available: {DEMO_SEQUENCE}",
        )
    coordinator = _coordinator()
    t0 = datetime.now()
    output = coordinator.run_agent(agent_name, body.prompt)
    elapsed = (datetime.now() - t0).total_seconds()
    return AgentResponse(
        agent=agent_name,
        phase=AGENT_META[agent_name]["phase"],
        prompt=body.prompt,
        output=output,
        duration_seconds=round(elapsed, 2),
        timestamp=datetime.now().isoformat(),
        source="live",
    )


# ---------------------------------------------------------------------------
# POST /demo/{agent_name}  — live, built-in demo prompt
# ---------------------------------------------------------------------------

@app.post("/demo/{agent_name}", response_model=AgentResponse)
def run_demo_agent(agent_name: str):
    if agent_name not in AGENT_META:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent '{agent_name}'. Available: {DEMO_SEQUENCE}",
        )
    prompt = AGENT_META[agent_name]["demo_prompt"]
    coordinator = _coordinator()
    t0 = datetime.now()
    output = coordinator.run_agent(agent_name, prompt)
    elapsed = (datetime.now() - t0).total_seconds()
    return AgentResponse(
        agent=agent_name,
        phase=AGENT_META[agent_name]["phase"],
        prompt=prompt,
        output=output,
        duration_seconds=round(elapsed, 2),
        timestamp=datetime.now().isoformat(),
        source="live",
    )


# ---------------------------------------------------------------------------
# GET /demo/{agent_name}/cached  — return pre-saved output, no API call
# ---------------------------------------------------------------------------

@app.get("/demo/{agent_name}/cached", response_model=AgentResponse)
def get_cached_output(agent_name: str):
    if agent_name not in AGENT_META:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent '{agent_name}'. Available: {DEMO_SEQUENCE}",
        )
    data = _load_cached(agent_name)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No cached output for '{agent_name}'. "
                f"Run: python save_demo_outputs.py --agent {agent_name}"
            ),
        )
    return AgentResponse(
        agent=agent_name,
        phase=data.get("phase", AGENT_META[agent_name]["phase"]),
        prompt=data.get("prompt", ""),
        output=data.get("output", ""),
        duration_seconds=0.0,
        timestamp=data.get("captured_at", ""),
        source="cached",
    )


# ---------------------------------------------------------------------------
# POST /phase/{phase_name}  — run all agents in a phase sequentially
# ---------------------------------------------------------------------------

@app.post("/phase/{phase_name}")
def run_phase(phase_name: str):
    if phase_name not in PHASE_TO_AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown phase '{phase_name}'. Available: {list(PHASE_TO_AGENTS.keys())}",
        )
    coordinator = _coordinator()
    agents = PHASE_TO_AGENTS[phase_name]
    results = {}
    for agent_name in agents:
        prompt = AGENT_META[agent_name]["demo_prompt"]
        t0 = datetime.now()
        output = coordinator.run_agent(agent_name, prompt)
        elapsed = (datetime.now() - t0).total_seconds()
        results[agent_name] = {
            "output": output,
            "duration_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
        }
    return {
        "phase": phase_name,
        "agents_run": agents,
        "results": results,
    }
