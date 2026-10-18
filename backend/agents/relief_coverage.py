"""Relief Coverage Agent · Recover.
Needs and verified deliveries by community + how much each community is being heard -> coverage, gaps, and communities
that may be missed because they've gone quiet (not because they're fine).
Feeds: Recover › Still unserved (Missed community: Chooralmala ward 11, Need gaps), Communities card, Relief page.
Owner: Sreeja Thomas, Relief & Recovery Coordinator (may approve in Recover) · Incident Commander."""
from __future__ import annotations

from core.scenario import scenario, community

NAME, DISPLAY, PHASE, OWNER = "relief_coverage", "Relief Coverage Agent", "recover", "Relief & Recovery Coordinator"


def get_coverage() -> dict:
    """Every community: people in need (estimate flag), verified coverage %, the state of each essential need, and who reported it when."""
    return {"communities": [{k: c[k] for k in ("id", "name", "in_need", "estimate", "coverage_pct", "needs", "by")} for c in scenario()["communities"]]}


def get_signals(community_id: str) -> dict:
    """How well a community is being heard: hours since a verified water delivery, reports since Day 0, its share of reports
    against its share of need, phone-tower state. community_id: chooralmala, meppadi, pozhuthana, vythiri."""
    c = community(community_id)
    return {"community": c["name"], **c.get("signals", {})}


def find_missed() -> dict:
    """Communities whose share of reports is far below their share of need while needs are open: the ones silence may be hiding."""
    out = []
    for c in scenario()["communities"]:
        s = c.get("signals", {})
        if s.get("share_of_need_pct") and s.get("share_of_reports_pct") is not None:
            ratio = s["share_of_need_pct"] / max(1, s["share_of_reports_pct"])
            gaps = [k for k, v in c["needs"].items() if v == "gap"]
            if ratio >= 3 and gaps:
                out.append({"id": c["id"], "name": c["name"], "sub": c["sub"], "under_reported_x": round(ratio), "gaps": gaps, **s})
    return {"missed": out}


def get_need_gaps() -> dict:
    """Open need gaps with need, verified supply and gap (only a verified delivery counts as covered)."""
    return {"gaps": scenario()["need_gaps"]}


TOOLS = [get_coverage, get_signals, find_missed, get_need_gaps]
INSTRUCTION = """You are the Relief Coverage Agent for DDMA Wayanad. Only a verified delivery counts as covered. Your job is to
find communities that may be missed: low report volume in a high-need, high-vulnerability place means silence, not safety.
Call get_coverage, find_missed, get_signals for each missed community, and get_need_gaps."""
PROMPT = "Day 2, 09:00. Who may be missed, and what should the coordinator do first?"
TEXT_SPEC = {
    "missed_title": "e.g. 'Chooralmala ward 11 may be missed'",
    "missed_meta": "one line: hours without verified water, number of reports, vulnerability",
    "missed_lines": ["exactly 2 items, each written as 'fact · detail', e.g. 'About 140 households, many elderly · Phone network down since Day 0'"],
    "recommendation": "one line starting 'AI recommends: …' (a verification step before sending supplies)",
    "reason": "one sentence: why silence may not mean help arrived",
    "confidence": "short phrase, naming the freshest data",
}


def facts(ctx: dict) -> dict:
    return {"coverage": get_coverage()["communities"], "missed": find_missed()["missed"], "gaps": get_need_gaps()["gaps"], "overall_pct": 68}


def rules(f: dict) -> dict:
    m = f["missed"][0] if f["missed"] else None
    if not m:
        return {"missed_title": "No community looks missed", "missed_meta": "", "missed_lines": [], "recommendation": "", "reason": "", "confidence": ""}
    return {"missed_title": f"{m['name']} ward 11 may be missed",
            "missed_meta": f"No verified water delivery in {m['hours_since_verified_water']} h · only {m['reports_since_day0']} reports · high vulnerability",
            "missed_lines": [f"About {m['households']} households, {m['elderly']} elderly · Phone network {m['phone_tower']}; few reports reach the system",
                             "Road at km 7 open with restrictions · High-clearance vehicles only"],
            "recommendation": "AI recommends: ask the ward officer to verify needs on the ground",
            "reason": "Low report volume in a high-vulnerability area, so silence may not mean help arrived",
            "confidence": "Medium · last camp report 10 h ago"}


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Ask the ward officer to verify needs in Chooralmala ward 11",
            "evidence": [["No verified water delivery in 10 h", "verified"], ["Only 3 reports since Day 0 (phone tower down)", "verified"], ["About 140 households, many elderly", "estimated"]],
            "confidence": t["confidence"], "limitation": "Last camp report 10 h ago"}
