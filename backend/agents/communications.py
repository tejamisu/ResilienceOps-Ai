"""Communications Agent · all phases.
Facts -> public advisory (English + Malayalam), situation report text, partner requests. Nothing is sent until approved.
Feeds: Prepare › Public advisory review; Reports › Situation report #4 (headline and summary).
Owner: Ananya Menon, Incident Commander (approves every outgoing message)."""
from __future__ import annotations

from core.scenario import scenario

NAME, DISPLAY, PHASE, OWNER = "communications", "Communications Agent", "all", "Incident Commander"

ADVISORY_EN = ("Red alert: extremely heavy rain is expected from 15:00 today. If you live on a steep slope or near the river in "
               "Meppadi, Vythiri or Mananthavady, move to your nearest relief camp before 14:00. Helpline 1077.")


def get_advisory_facts() -> dict:
    """What the public advisory must say: alert, peak time, places, deadline to move, helpline, channels and reach."""
    f = scenario()["forecast"]
    return {"alert": f["alert"], "from": f["peak_window"][0], "move_before": "14:00", "places": ["Meppadi", "Vythiri", "Mananthavady"],
            "helpline": "1077", "channels": ["SMS", "WhatsApp", "panchayat loudspeakers", "All India Radio Kozhikode"], "reach": "about 4,100 people",
            "languages": ["Malayalam", "English"], "low_connectivity": ["Chooralmala ward 11 (phone tower down)", "Pozhuthana hill settlements"]}


def get_situation_facts() -> dict:
    """Day 2, 09:00 situation for the KSDMA report: severity, coverage, verified impact, resources, gaps and decisions needed."""
    s = scenario()
    i = s["impact"]
    return {"time": "Day 2 · 09:00", "severity": "Moderate, down from critical at 12:02 Day 0", "phase": "Recovery",
            "in_need": sum(c["in_need"] for c in s["communities"]), "coverage_pct": 68,
            "missing_open": i["missing_open"], "in_camps": i["in_camps"], "injuries_treated": i["injuries_treated"],
            "households_assessed": i["households_assessed"], "gaps": s["need_gaps"], "restoration": s["restoration"],
            "decisions_needed": ["Verify needs in Chooralmala ward 11 (phone tower down)", "Approve 8,000 L/day water for Meppadi camp"]}


TOOLS = [get_advisory_facts, get_situation_facts]

INSTRUCTION = """You are the Communications Agent for DDMA Wayanad. You draft messages people will act on: a public
advisory in English and Malayalam, and the situation report for KSDMA. Short, calm, specific. Call get_advisory_facts
and get_situation_facts. Malayalam must say exactly what the English says (it is checked by the DEOC language officer)."""
PROMPT = "Draft the public advisory for the red alert, and the headline and summary for Situation report #4."
TEXT_SPEC = {
    "advisory_en": "the advisory in English, under 60 words, with the time to move and the helpline",
    "advisory_ml": "the same advisory in Malayalam script",
    "sitrep_headline": "one line for KSDMA: phase, coverage, the biggest open gap",
    "sitrep_summary": "three sentences: situation now, verified impact (no deaths figures), what needs a decision",
}


def facts(ctx: dict) -> dict:
    return {"advisory": get_advisory_facts(), "situation": get_situation_facts()}


def rules(f: dict) -> dict:
    s = f["situation"]
    return {
        "advisory_en": ADVISORY_EN,
        "advisory_ml": "",   # left empty without Gemini: the language officer translates by hand
        "sitrep_headline": f"Recovery under way · verified coverage {s['coverage_pct']}% · Chooralmala ward 11 may be missed",
        "sitrep_summary": (f"Severity is {s['severity'].lower()}. {s['in_camps'][0]:,} people are in relief camps and {s['missing_open'][0]} of {s['missing_open'][1]} "
                           f"missing-person cases are open (police register). Decisions needed: {s['decisions_needed'][0].lower()}, and {s['decisions_needed'][1].lower()}."),
    }


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Send the public advisory in Malayalam and English to 3 areas",
            "evidence": [["IMD red alert, 06:00", "verified"], ["Place ranking", "estimated"]],
            "confidence": "High for content · Malayalam to be checked", "limitation": "Low-connectivity wards need loudspeakers, not SMS"}
