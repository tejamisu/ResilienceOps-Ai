"""Damage Assessment Agent · Recover.
Assessment forms, camp registry, police and health records -> verified impact for the Recover card and the KSDMA report,
with what is verified vs still being assessed. No fatality figures.
Feeds: Recover › Verified impact; Reports › Verified impact section.
Owner: District Collector countersigns before any claim is submitted."""
from __future__ import annotations

from core.scenario import scenario

NAME, DISPLAY, PHASE, OWNER = "damage_assessment", "Damage Assessment Agent", "recover", "District Collector"


def get_verified_impact() -> dict:
    """Verified impact figures with sources: households assessed, people in camps against capacity, open missing-person cases, injuries treated."""
    return scenario()["impact"]


def get_assessment_progress() -> dict:
    """Households assessed by panchayat, and where assessment is blocked and why."""
    i = scenario()["impact"]
    return {"by_panchayat": [{"panchayat": p[0], "assessed": p[1], "of": p[2], "note": p[3] if len(p) > 3 else ""} for p in i["by_panchayat"]]}


TOOLS = [get_verified_impact, get_assessment_progress]
INSTRUCTION = """You are the Damage Assessment Agent for DDMA Wayanad. Summarise verified impact for the Incident Commander and
the District Collector: what is verified, what is still being assessed and why. Never give fatality figures.
Call get_verified_impact and get_assessment_progress."""
PROMPT = "Summarise verified impact at Day 2, 09:00, and what is still not assessed."
TEXT_SPEC = {"summary": "two sentences: verified figures with sources", "blocked": "one sentence: where assessment is blocked and why"}


def facts(ctx: dict) -> dict:
    return {"impact": get_verified_impact(), "progress": get_assessment_progress()["by_panchayat"]}


def rules(f: dict) -> dict:
    i = f["impact"]
    return {"summary": f"{i['households_assessed'][0]} of {i['households_assessed'][1]} households assessed; {i['in_camps'][0]:,} people in relief camps "
                       f"(camp registry) and {i['missing_open'][0]} of {i['missing_open'][1]} missing-person cases open (police register).",
            "blocked": "Pozhuthana hill settlements are not reached yet, and Chooralmala is slow because its phone tower is down."}


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Publish verified impact for Day 2, 09:00", "evidence": [["Panchayat assessment forms", "verified"], ["Camp registry, 08:40", "verified"], ["Police register, 08:30", "verified"]],
            "confidence": "High for counted figures", "limitation": "Pozhuthana not assessed"}
