"""Recovery & Reconciliation Agent · Recover → Prepare.
Plan vs what happened -> lessons for the next Prepare cycle, each with an owner.
Feeds: Recover › Learn → Prepare; Forecast page › Forecast vs outcome; Audit.
Owner: Incident Commander accepts a lesson into the next Prepare plan."""
from __future__ import annotations

from core.scenario import scenario

NAME, DISPLAY, PHASE, OWNER = "reconciliation", "Recovery & Reconciliation Agent", "recover", "Incident Commander"


def get_plan_vs_actual() -> dict:
    """Where the plan and the event differed: planned value, actual value, the gap, and the owner."""
    return {"items": scenario()["plan_vs_actual"]}


def get_forecast_vs_outcome() -> dict:
    """Forecast onset vs observed onset per place."""
    return {"onsets": scenario()["ground_truth"]}


TOOLS = [get_plan_vs_actual, get_forecast_vs_outcome]
INSTRUCTION = """You are the Recovery & Reconciliation Agent for DDMA Wayanad. Compare the plan with what happened and turn each
difference into one lesson for the next Prepare cycle, with an owner. Call get_plan_vs_actual and get_forecast_vs_outcome."""
PROMPT = "What should change before next monsoon? One lesson per difference."
TEXT_SPEC = {"lessons": {"l1": "one short imperative lesson", "l2": "one short imperative lesson", "l3": "one short imperative lesson"},
             "summary": "two sentences on how the forecast compared with what happened"}


def facts(ctx: dict) -> dict:
    return {"items": get_plan_vs_actual()["items"], "onsets": get_forecast_vs_outcome()["onsets"]}


def rules(f: dict) -> dict:
    return {"lessons": {i["id"]: i["lesson"] for i in f["items"]},
            "summary": "The landslide came at 12:02 inside the forecast critical zone, about 3 h before the forecast peak; Vythiri flooded 3 h early too. Plans that waited for the peak were late."}


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Add a Prepare task: 48 h water stock at every camp before monsoon",
            "evidence": [["Plan: 48 h at Meppadi camp", "verified"], ["Actual: ran out at 14 h", "verified"]], "confidence": "High", "limitation": ""}
