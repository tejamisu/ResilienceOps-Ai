"""Forecast vs Ground Reality Agent · Respond.
Forecast onset vs what is observed -> where reality is ahead of the plan, and whether priorities should change.
Feeds: Respond › "Vythiri flooding started 3 h earlier than forecast" and the Raise priority review.
Owner: Hazard Analyst recommends · Incident Commander decides."""
from __future__ import annotations

from core.scenario import scenario, place

NAME, DISPLAY, PHASE, OWNER = "ground_truth", "Forecast vs Ground Reality Agent", "respond", "Hazard Analyst"


def compare_onsets() -> dict:
    """For each watched place: forecast onset of heavy impact vs the observed onset, the difference in hours, and the evidence."""
    return {"comparisons": scenario()["ground_truth"]}


def get_place(place_id: str) -> dict:
    """A place's hazard, exposure and heavy-rain window (vythiri, meppadi, mananthavady, kalpetta)."""
    p = place(place_id)
    return {"name": p["name"], "hazard": p["hazard"], "exposure": p["exposure"], "window": p["window"]}


TOOLS = [compare_onsets, get_place]
INSTRUCTION = """You are the Forecast vs Ground Reality Agent for DDMA Wayanad. Compare forecast onsets with what is
observed and say whether priorities should change. Meppadi has an active landslide with a dispatch waiting; be honest about
that trade-off. Call compare_onsets and get_place for the places involved."""
PROMPT = "Is anything happening earlier than forecast, and should the priority order change?"
TEXT_SPEC = {
    "finding": "one sentence: what is ahead of the forecast and by how much",
    "suggestion": "one sentence: the suggested priority change, framed as a suggestion",
    "tradeoff": "one sentence: what raising it would cost Meppadi",
    "confidence": "short phrase",
}


def facts(ctx: dict) -> dict:
    v = next(c for c in scenario()["ground_truth"] if c["place"] == "vythiri")
    return {"vythiri": v, "meppadi": next(c for c in scenario()["ground_truth"] if c["place"] == "meppadi"), "now_order": ["meppadi", "vythiri"]}


def rules(f: dict) -> dict:
    return {"finding": "Flooding at Vythiri started 3 h earlier than forecast; the river gauge is above warning and water is on NH 766.",
            "suggestion": "Consider raising Vythiri to priority 1 so the next free team goes there.",
            "tradeoff": "Meppadi still has the active landslide at km 7 with a dispatch waiting.",
            "confidence": "Medium · gauge verified, road state reported"}


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Raise Vythiri above Meppadi: flooding started 3 h early",
            "evidence": [["River gauge above warning", "verified"], ["Ward officer: water on NH 766", "reported"]],
            "confidence": t["confidence"], "limitation": "The road state is from one report"}
