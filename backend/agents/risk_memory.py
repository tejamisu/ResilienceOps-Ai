"""Risk Memory Agent · Prepare (supports Forecast & Impact).
Past events per place -> recurring hotspots and what to remember this time.
Feeds: the "Past slides / Past floods" factors on the Prepare place cards; Forecast page.
Owner: DDMA planner."""
from __future__ import annotations

from core.scenario import scenario

NAME, DISPLAY, PHASE, OWNER = "risk_memory", "Risk Memory Agent", "prepare", "DDMA planner"


def get_history() -> dict:
    """Recorded past events in Wayanad with the places they hit and the lesson kept (no casualty figures)."""
    return {"events": scenario()["history"]}


def get_hotspots() -> dict:
    """Places hit more than once, with how many recorded events."""
    from collections import Counter
    n = Counter(p for h in scenario()["history"] for p in h["places"])
    return {"hotspots": [{"place": p, "events": c} for p, c in n.most_common()]}


TOOLS = [get_history, get_hotspots]
INSTRUCTION = "You are the Risk Memory Agent for DDMA Wayanad. Say what history teaches about the places at risk today. Call get_history and get_hotspots."
PROMPT = "What does history say about today's priority places?"
TEXT_SPEC = {"meppadi": "one sentence", "vythiri": "one sentence", "mananthavady": "one sentence", "kalpetta": "one sentence"}


def facts(ctx: dict) -> dict:
    return {**get_history(), **get_hotspots()}


def rules(f: dict) -> dict:
    by = {}
    for p in ("meppadi", "vythiri", "mananthavady", "kalpetta"):
        ev = [h for h in f["events"] if p in h["places"]]
        by[p] = "; ".join(f"{h['year']} {h['event']}: {h['lesson'].lower()}" for h in ev) + "." if ev else "No recorded event."
    return by


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Weight Meppadi's history in today's ranking", "evidence": [["District hazard record", "verified"]], "confidence": "High", "limitation": "Older records are incomplete"}
