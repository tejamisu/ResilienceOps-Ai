"""Preparedness Agent · Prepare.
Priority places + resources -> readiness tasks (owner, deadline, proof), capacity gaps, and request drafts that close them.
Feeds: Prepare › Plan to approve (tasks, "Why these tasks?"), Capacity check (Fix → request drafts), the KSDMA draft.
Owner: Ananya Menon, Incident Commander (approves every task and request)."""
from __future__ import annotations

from core.scenario import scenario, place

NAME, DISPLAY, PHASE, OWNER = "preparedness", "Preparedness Agent", "prepare", "Incident Commander"

DRAFTS = {
    "ksdma": {"cap": "rescue", "to": "KSDMA · State EOC", "what": "2 SDRF teams on standby at Meppadi", "qty": "2 teams with landslide rescue kit", "by": "12:00 today"},
    "pwd": {"cap": "exc", "to": "PWD Wayanad", "what": "One more excavator at Meppadi junction", "qty": "1 excavator with operator", "by": "12:00 today"},
    "beds": {"cap": "beds", "to": "Relief partners", "what": "600 camp beds for the Meppadi and Vythiri camps", "qty": "600 beds", "by": "18:00 today"},
}


def get_readiness_tasks() -> dict:
    """The readiness task list for the priority places: id, title, owner, due time, resources and proof of done."""
    return {"tasks": scenario()["readiness_tasks"], "at_risk": scenario()["at_risk"]}


def get_capacity() -> dict:
    """Confirmed resources against what the forecast needs: water hours at Meppadi camp, rescue teams, excavators, camp beds, ambulances."""
    rows = []
    for c in scenario()["capacity"]:
        rows.append({**c, "short_by": max(0, c["need"] - c["have"]), "gap": c["have"] < c["need"]})
    return {"capacity": rows, "gaps": sum(r["gap"] for r in rows)}


def get_place_risk(place_id: str) -> dict:
    """Risk factors, heavy-rain window and unknowns for a place, to justify why a task is needed and by when."""
    p = place(place_id)
    return {"place": p["name"], "window": p["window"], "factors": p["factors"], "unknowns": p["unknowns"]}


def draft_request(key: str) -> dict:
    """Draft the request that closes a capacity gap. key is one of: ksdma (rescue teams), pwd (excavator), beds (camp beds)."""
    d = DRAFTS[key]
    c = next(x for x in scenario()["capacity"] if x["id"] == d["cap"])
    return {**d, "key": key, "gap": f"{c['label']} {c['have']:,} of {c['need']:,}"}


TOOLS = [get_readiness_tasks, get_capacity, get_place_risk, draft_request]

INSTRUCTION = """You are the Preparedness Agent for DDMA Wayanad. Before the storm, you turn the priority places into
readiness tasks with an owner, a deadline and proof of done, and you draft the requests that close capacity gaps.
Call get_readiness_tasks, get_capacity and get_place_risk('meppadi'), and draft_request for each gap that has a request."""
PROMPT = "Peak landslide risk at Meppadi starts at 15:00. Explain the readiness plan and the capacity gaps for the Incident Commander."
TEXT_SPEC = {
    "headline": "one line, e.g. 'AI drafted 5 readiness tasks for Meppadi'",
    "basis": "one line naming the sources the plan is drafted from",
    "why_list": ["4 short bullets: why these tasks and why by these times (cite the forecast window, the single road, camp water)"],
    "task_why": {"t1": "one sentence", "t2": "one sentence", "t3": "one sentence", "t4": "one sentence", "t5": "one sentence"},
    "draft_why": {"ksdma": "one sentence for the KSDMA request", "pwd": "one sentence for the PWD request", "beds": "one sentence for the camp-bed request"},
    "confidence": "short phrase",
}


def facts(ctx: dict) -> dict:
    t = get_readiness_tasks()
    return {"tasks": t["tasks"], "at_risk": t["at_risk"], "capacity": get_capacity(), "drafts": {k: draft_request(k) for k in DRAFTS},
            "deadline": "12:00", "peak": scenario()["forecast"]["peak_window"]}


def rules(f: dict) -> dict:
    return {
        "headline": f"AI drafted {len(f['tasks'])} readiness tasks for Meppadi",
        "basis": "From the IMD forecast, slope-risk map, camp capacity and team availability",
        "why_list": [
            "Meppadi has the steepest slopes inside the heaviest-rain band and one access road.",
            f"Peak rain is expected {f['peak'][0]}–{f['peak'][1]}, so teams must be in place by {f['deadline']}.",
            "Meppadi camp has water for about 14 h at expected occupancy; it needs 48 h.",
            "Sources: IMD district forecast, KSDMA slope-risk layer, camp manager reports, team roster.",
        ],
        "task_why": {
            "t1": "Only access road into the critical zone; the slope above it is over 30°.",
            "t2": "The nearest landslide-trained team is 40 min away at Kalpetta.",
            "t3": "Water stock covers about 14 h at expected occupancy.",
            "t4": "Clearing debris on km 7 restores medical access.",
            "t5": "The hospital road may be cut during peak rain.",
        },
        "draft_why": {
            "ksdma": "Rescue capacity is 4 of 6 teams for the Meppadi critical zone; peak landslide risk is 15:00–21:00.",
            "pwd": "2 of 3 excavators are confirmed and the km 7 road is the only way into the critical zone.",
            "beds": "1.8k of 2.4k beds are confirmed at the expected occupancy across 5 camps.",
        },
        "confidence": "Medium–high · forecast updated 20 min ago",
    }


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": f"Approve {len(f['tasks'])} readiness tasks for Meppadi",
            "evidence": [["Forecast and risk ranking", "estimated"], ["Resource inventory, 06:15", "verified"], ["Camp capacity register", "verified"]],
            "confidence": t["confidence"], "limitation": "Forecast updated 20 min before the draft"}
