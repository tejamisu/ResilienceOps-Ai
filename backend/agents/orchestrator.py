"""Command Orchestrator · phase changes.
Phase status + what each agent reports -> when to move phase, and the handover (done, carried over, assumptions).
Feeds: Prepare › Response activation recommended / handover; Respond › Recovery mode recommended / handover.
Owner: Ananya Menon, Incident Commander (every phase change is hers)."""
from __future__ import annotations

from core.scenario import scenario

NAME, DISPLAY, PHASE, OWNER = "orchestrator", "Command Orchestrator", "all", "Incident Commander"


def get_respond_status() -> dict:
    """Respond phase status at Day 1, 07:50: rescues open, rain against the watch level, roads, open relief and restoration items."""
    s = scenario()
    return {"rescues_open": 0, "rain_below_watch_h": 6, "roads": s["routes"], "restoration": s["restoration"], "need_gaps": s["need_gaps"],
            "missing_open": s["impact"]["missing_open"], "quiet_communities": ["Chooralmala ward 11 (phone tower down)"]}


TOOLS = [get_respond_status]
INSTRUCTION = """You are the Command Orchestrator for DDMA Wayanad. Decide whether the event should move from Respond to Recover,
and write the handover: what is done, what carries over, what to keep watching. The Incident Commander decides.
Call get_respond_status."""
PROMPT = "Day 1, 07:50. Should we move to Recover? Write the handover."
TEXT_SPEC = {"recommendation": "one line: recommend recovery mode and why",
             "done": ["3 short items done in Respond"], "carried": ["4 short items carried into Recover"], "assumptions": ["2 assumptions to monitor"]}


def facts(ctx: dict) -> dict:
    return get_respond_status()


def rules(f: dict) -> dict:
    return {"recommendation": "Recovery mode recommended: rescue complete at km 7 and rain below the watch level for 6 h.",
            "done": ["Rescue complete at km 7", "Rescue Unit 2 and Excavator 3 dispatched by Route C", "Road at km 7 open with restrictions"],
            "carried": ["Chooralmala ward 11: needs not verified", "Meppadi camp water below plan", "Power out in 3 wards", "3 missing-person cases open"],
            "assumptions": ["No new slides expected", "Route C stays open for relief trucks"]}


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Move the event from Respond to Recover", "evidence": [["0 rescues open", "verified"], ["Rain below 15 mm/h for 6 h", "verified"]],
            "confidence": "High", "limitation": "Pozhuthana not yet assessed"}
