"""Run one ResilienceOps agent.

Every agent has two halves:
  facts()  deterministic tools over the scenario -> the structured data the app shows (scores, tasks, gaps, routes).
  text     what a person reads (why, recommendation, drafts). Gemini writes it through Google ADK, calling the
           agent's tools itself; if Gemini is not configured or fails, rules() writes it from the same facts.
The app always gets the same JSON shape, with `source` saying who wrote the text: "gemini" or "rules".
"""
from __future__ import annotations

import json
import os
import re
import time
import uuid
from datetime import datetime, timezone

from . import store

APP = "resilienceops_ai"
DEFAULT_MODEL = "gemini-3.8-flash"   # what the team built on; GEMINI_MODEL overrides it
_model_cache: dict = {}


def has_key() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY")) or os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true")


def model_name() -> str:
    """GEMINI_MODEL if set and available; otherwise the newest available Flash model on this key."""
    if "name" in _model_cache:
        return _model_cache["name"]
    want = os.getenv("GEMINI_MODEL", "").strip()
    chosen = want or DEFAULT_MODEL
    try:
        from google import genai
        names = [m.name.split("/")[-1] for m in genai.Client().models.list()]
        if want and want in names:
            chosen = want
        else:
            flash = sorted((n for n in names if re.fullmatch(r"gemini-\d+(\.\d+)?-flash", n)),
                           key=lambda n: float(re.findall(r"\d+(?:\.\d+)?", n)[0]))
            if flash:
                chosen = flash[-1]
    except Exception as e:  # no network or no key: keep the configured name; a run that hits a retired model switches itself
        print(f"[model] couldn't list models ({type(e).__name__}: {str(e)[:160]}); using {chosen}")
    print(f"[model] using {chosen}")
    _model_cache["name"] = chosen
    return chosen


def _json_from(text: str) -> dict:
    """The agent is told to answer with one JSON object; accept it bare or in a ```json fence."""
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S) or re.search(r"(\{.*\})", text, re.S)
    if not m:
        raise ValueError("no JSON object in the answer")
    return json.loads(m.group(1))


def _merge(rules_text: dict, model_text: dict) -> dict:
    """Take the model's text where it gave a usable value of the same shape; keep the rules text elsewhere."""
    out = {}
    for k, v in rules_text.items():
        m = model_text.get(k)
        if isinstance(v, dict) and isinstance(m, dict):
            out[k] = _merge(v, m)
        elif isinstance(v, list) and isinstance(m, list) and m and all(isinstance(x, str) for x in m):
            out[k] = m
        elif isinstance(v, str) and isinstance(m, str) and m.strip():
            out[k] = m.strip()
        else:
            out[k] = v
    return out


def _envelope(mod, facts: dict, text: dict, source: str, model: str | None, t0: float, calls: list, error: str | None = None) -> dict:
    return {
        "run_id": uuid.uuid4().hex[:12],
        "agent": mod.NAME, "display": mod.DISPLAY, "phase": mod.PHASE, "owner": mod.OWNER,
        "source": source, "model": model, "error": error,
        "generated_at": datetime.now(timezone.utc).isoformat(), "duration_s": round(time.time() - t0, 2),
        "tool_calls": calls,
        "facts": facts, "text": text,
        "trace": mod.trace(facts, text),
    }


def run_rules(mod, ctx: dict | None = None) -> dict:
    t0 = time.time()
    facts = mod.facts(ctx or {})
    return _envelope(mod, facts, mod.rules(facts), "rules", None, t0, [])


async def run_gemini(mod, ctx: dict | None = None) -> dict:
    """Gemini through Google ADK: the agent calls its own tools, then writes the text as JSON."""
    ctx = ctx or {}
    t0 = time.time()
    facts = mod.facts(ctx)
    base = mod.rules(facts)
    if not has_key():
        return _envelope(mod, facts, base, "rules", None, t0, [], "GOOGLE_API_KEY not set")
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    contract = json.dumps(mod.TEXT_SPEC, ensure_ascii=False, indent=2)
    prompt = mod.prompt(ctx) if hasattr(mod, "prompt") else mod.PROMPT
    calls, parts = [], []
    last_err = None
    swapped = False
    for attempt in range(3):
        model = model_name()
        agent = LlmAgent(
            name=mod.NAME, model=model, description=mod.DISPLAY, tools=mod.TOOLS,
            instruction=mod.INSTRUCTION + COMMON_RULES + f"\n\nWhen you have what you need, answer with ONE JSON object and nothing else, "
                        f"with exactly these keys (values are what each key should contain):\n{contract}",
            generate_content_config=types.GenerateContentConfig(temperature=0.3),
        )
        sessions = InMemorySessionService()
        session = await sessions.create_session(app_name=APP, user_id="deoc")
        runner = Runner(agent=agent, app_name=APP, session_service=sessions)
        calls, parts = [], []
        try:
            async for ev in runner.run_async(user_id="deoc", session_id=session.id,
                                             new_message=types.Content(role="user", parts=[types.Part(text=prompt)])):
                for fc in ev.get_function_calls() or []:
                    calls.append(fc.name)
                if ev.is_final_response() and ev.content and ev.content.parts:
                    parts += [p.text for p in ev.content.parts if getattr(p, "text", None)]
            break
        except Exception as e:  # 429 / 503: back off and retry; anything else: fall back to rules
            last_err = f"{type(e).__name__}: {e}"
            # a retired model: Google's error names the replacement ("use models/gemini-…"); switch to it once and retry
            new = re.search(r"use models/(gemini-[\w.\-]+)", str(e))
            if "NOT_FOUND" in str(e) and new and not swapped:
                swapped = True
                print(f"[model] {model} is not available; switching to {new.group(1)}")
                _model_cache["name"] = new.group(1).rstrip(".")
                continue
            if any(s in str(e) for s in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")) and attempt < 2:
                import asyncio
                await asyncio.sleep(4 * (attempt + 1))
                continue
            return _envelope(mod, facts, base, "rules", model, t0, calls, last_err[:300])
    try:
        text = _merge(base, _json_from("\n".join(parts)))
        return _envelope(mod, facts, text, "gemini", model, t0, calls)
    except Exception as e:
        return _envelope(mod, facts, base, "rules", model, t0, calls, f"Could not read the model's answer: {e}"[:300])


COMMON_RULES = """

RULES FOR EVERY ResilienceOps AGENT (Wayanad, Kerala · DDMA):
- You recommend; people decide. Never say an action has been taken. Say who must approve (usually Ananya Menon, Incident Commander).
- Use only figures your tools return. Do not invent numbers, names or places. Ranges stay ranges.
- No casualty or death figures, ever. Say "people potentially exposed" or "life-safety risk".
- Say what is verified, estimated or reported, and name the source and time when it matters.
- Plain, calm English for a district control room. Short sentences. No markdown inside JSON strings.
"""


def cached_or_rules(mod, ctx: dict | None = None) -> dict:
    """What the app loads first: the last saved run (Gemini or rules) for the default context, else rules now."""
    if not ctx:
        saved = store.load_run(mod.NAME)
        if saved:
            saved["cached"] = True
            return saved
    return run_rules(mod, ctx)
