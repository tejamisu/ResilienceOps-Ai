"""ResilienceOps AI — HTTP API for the app (FastAPI). Serves the app too, so one Cloud Run service is the whole product.

  GET  /api/health                  is Gemini configured, which agents exist
  GET  /api/agents                  agent list (name, display name, phase, owner, last run)
  GET  /api/agents/{name}           fast: the last saved run, else rule-written now   (?staged=1 for dispatch)
  POST /api/agents/{name}/run       slow: run the agent on Gemini through ADK now and save it   (body: context)
  POST /api/warm                    run every agent on Gemini in the background (call once after deploy)
  GET  /api/warm                    progress of that warm-up
  GET  /api/scenario                the Wayanad scenario data
  GET  /api/decisions · POST        the human decision log (approvals, edits, sends) behind the Audit view
  GET  /                            the app (test-run/resilienceops.html, or web/index.html in the container)
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

load_dotenv()

from agents import AGENTS  # noqa: E402
from core import guard, runner, store  # noqa: E402
from core.scenario import scenario  # noqa: E402

app = FastAPI(title="ResilienceOps AI", version="2.0.0",
              description="Wayanad disaster-coordination agents on Google ADK + Gemini. Every output is a recommendation a person approves.")
# CORS: the app is served from the same origin as the API (one Cloud Run service), so it needs no cross-origin access.
# Default to the local dev origins only; set CORS_ORIGINS (comma-separated) to add any extra origin. Never "*".
_DEV_ORIGINS = ["http://localhost:4317", "http://127.0.0.1:4317", "http://localhost:8080", "http://127.0.0.1:8080"]
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()] or _DEV_ORIGINS
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["GET", "POST"], allow_headers=["content-type", "x-admin-token"])

HERE = Path(__file__).resolve().parent
FRONTEND = Path(os.getenv("FRONTEND_FILE", HERE / "web" / "index.html"))
if not FRONTEND.exists():
    FRONTEND = HERE.parent / "test-run" / "resilienceops.html"
WARM = {"running": False, "done": [], "failed": {}, "total": 0}


def _agent(name: str):
    if name not in AGENTS:
        raise HTTPException(404, f"Unknown agent '{name}'. Available: {list(AGENTS)}")
    return AGENTS[name]


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_configured": runner.has_key(), "model_setting": os.getenv("GEMINI_MODEL") or "auto (newest Flash)",
            "agents": list(AGENTS), "frontend": FRONTEND.exists()}


@app.get("/api/agents")
def agents():
    out = []
    for n, m in AGENTS.items():
        r = store.load_run(n)
        out.append({"name": n, "display": m.DISPLAY, "phase": m.PHASE, "owner": m.OWNER,
                    "last_run": r and {"source": r["source"], "generated_at": r["generated_at"], "model": r.get("model")}})
    return {"agents": out}


@app.get("/api/agents/{name}")
def get_agent(name: str, staged: int = 0):
    return runner.cached_or_rules(_agent(name), {"staged": True} if staged else None)


class RunBody(BaseModel):
    model_config = ConfigDict(extra="forbid")   # reject unknown top-level fields
    context: dict = {}

    @field_validator("context")
    @classmethod
    def _small_context(cls, v: dict) -> dict:
        import json as _json
        if len(_json.dumps(v, default=str)) > 4096:
            raise ValueError("context too large (max 4 KB)")
        return v


@app.post("/api/agents/{name}/run")
async def run_agent(name: str, request: Request, body: Optional[RunBody] = None):
    # user-facing (the Regenerate button), but each call can spend Gemini quota: rate-limit per client
    await guard.body_size_ok(request)
    guard.rate_limit(request, "run", per_min=float(os.getenv("RUN_PER_MIN", "10")))
    mod, ctx = _agent(name), (body.context if body else {})
    res = await runner.run_gemini(mod, ctx)
    if not ctx and res["source"] == "gemini":
        store.save_run(name, res)
    return res


async def _warm(force: bool = False):
    WARM.update(running=True, done=[], failed={}, total=len(AGENTS))
    pause = float(os.getenv("WARM_PAUSE", "20"))   # seconds between agents: each agent makes several Gemini calls
    for n, m in AGENTS.items():
        saved = store.load_run(n)
        if not force and saved and saved.get("source") == "gemini":   # already on Gemini: keep it, save the quota
            WARM["done"].append(n)
            continue
        res = await runner.run_gemini(m, {})
        if res["source"] == "gemini":
            store.save_run(n, res)
            WARM["done"].append(n)
        else:
            WARM["failed"][n] = res.get("error") or "fell back to rules"
        await asyncio.sleep(pause)   # stay under free-tier per-minute limits
    WARM["running"] = False


@app.post("/api/warm")
async def warm(bg: BackgroundTasks, request: Request, force: int = 0):
    """Run on Gemini every agent that doesn't have a saved Gemini run yet (?force=1 reruns all).
    Owner-only: it spends the owner's Gemini quota, so it needs X-Admin-Token (or localhost)."""
    guard.require_admin(request)
    if not runner.has_key():
        raise HTTPException(503, "Gemini is not configured: set GOOGLE_API_KEY in backend/.env (local) or as a Cloud Run secret.")
    if WARM["running"]:
        return JSONResponse(WARM, status_code=202)
    bg.add_task(_warm, bool(force))
    return JSONResponse({**WARM, "running": True, "total": len(AGENTS)}, status_code=202)


@app.get("/api/warm")
def warm_status():
    return WARM


@app.get("/api/scenario")
def get_scenario():
    return scenario()


# Note: there is no login — the role/author are a demo switch the client sends, so this log is a
# record of the demo, not an authenticated audit trail. We constrain the values (so no junk or markup
# can be stored) and bound the sizes, but the log is never rendered back into the page or trusted as truth.
_ACTIONS = {"approve", "edit", "send", "recommend", "escalate", "assign", "reject", "note"}
_ROLES = {"Incident Commander", "Hazard Analyst", "Relief & Recovery Coordinator"}
_PHASES = {"", "prepare", "respond", "recover"}


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    action: str = Field(max_length=32)
    item: str = Field(max_length=200)
    by: str = Field(default="Ananya Menon", max_length=80)
    role: str = Field(default="Incident Commander", max_length=60)
    phase: str = Field(default="", max_length=16)
    agent: str = Field(default="", max_length=60)
    run_id: str = Field(default="", max_length=40)
    detail: str = Field(default="", max_length=500)

    @field_validator("action")
    @classmethod
    def _known_action(cls, v: str) -> str:
        if v not in _ACTIONS:
            raise ValueError(f"unknown action; one of {sorted(_ACTIONS)}")
        return v

    @field_validator("role")
    @classmethod
    def _known_role(cls, v: str) -> str:
        if v not in _ROLES:
            raise ValueError("unknown role")
        return v

    @field_validator("phase")
    @classmethod
    def _known_phase(cls, v: str) -> str:
        if v not in _PHASES:
            raise ValueError("unknown phase")
        return v


@app.post("/api/decisions")
async def add_decision(d: Decision, request: Request):
    await guard.body_size_ok(request)
    guard.rate_limit(request, "decisions", per_min=float(os.getenv("DECISIONS_PER_MIN", "30")))
    return store.add_decision(d.model_dump())


@app.get("/api/decisions")
def list_decisions():
    return {"decisions": store.decisions()}


@app.get("/field.html", include_in_schema=False)
def field():
    p = FRONTEND.parent / "field.html"
    if not p.exists():
        raise HTTPException(404, "Field app not built; run test-run/build-app.py")
    return FileResponse(p, media_type="text/html")


@app.get("/", include_in_schema=False)
def index():
    if not FRONTEND.exists():
        return JSONResponse({"service": "ResilienceOps AI", "docs": "/docs", "note": "App file not found; build it with test-run/build-app.py"})
    return FileResponse(FRONTEND, media_type="text/html")
