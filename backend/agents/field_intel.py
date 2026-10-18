"""Field Intelligence Agent (was: Triage + Field Intel) · Respond.
Incoming reports (a Malayalam voice note, calls, police, gauges) -> clustered, trust-scored incidents with a severity.
Feeds: Respond › Needs your decision (the km 7 landslide, camp water, Vythiri), the notification feed.
Owner: DEOC watch officer · the Incident Commander confirms a critical incident."""
from __future__ import annotations

import math

from core.scenario import scenario

NAME, DISPLAY, PHASE, OWNER = "field_intel", "Field Intelligence Agent", "respond", "DEOC watch officer"

TRUST = {"high": .9, "medium": .6, "low": .3}
CLUSTERS = {  # reports that describe the same thing (same place, same 10-minute window)
    "km7": {"reports": ["r1", "r2", "r3", "r4"], "title": "Landslide blocks the Meppadi–Chooralmala road", "kind": "landslide", "place": "meppadi"},
    "camp-water": {"reports": ["r5"], "title": "Meppadi camp: drinking water runs out in under 6 h", "kind": "relief_gap", "place": "meppadi"},
    "vythiri": {"reports": ["r6"], "title": "Vythiri flooding started 3 h earlier than forecast", "kind": "flood", "place": "vythiri"},
}


def get_incoming_reports() -> dict:
    """All reports received since 11:40 with their source, trust level and text (the Malayalam voice note is summarised)."""
    return {"reports": scenario()["incoming_reports"]}


def cluster_reports() -> dict:
    """Group reports that describe the same event (place + time window) and score each cluster by source trust."""
    reps = {r["id"]: r for r in scenario()["incoming_reports"]}
    out = []
    for cid, c in CLUSTERS.items():
        rs = [reps[i] for i in c["reports"]]
        independent = len({r["kind"] for r in rs})
        trust = round(1 - math.prod(1 - TRUST[r["trust"]] for r in rs), 2)
        out.append({"id": cid, "title": c["title"], "kind": c["kind"], "place": c["place"], "reports": c["reports"],
                    "sources": [r["source"] for r in rs], "independent_source_types": independent, "trust": trust,
                    "first_seen": min(r["t"] for r in rs)})
    return {"clusters": out}


def assess_incident(cluster_id: str) -> dict:
    """Severity and verification for one cluster: km7, camp-water or vythiri. Critical needs a life-safety risk and 2+ independent sources."""
    c = next(x for x in cluster_reports()["clusters"] if x["id"] == cluster_id)
    life = c["kind"] in ("landslide",)
    verified = c["independent_source_types"] >= 2 and c["trust"] >= .9
    severity = "Critical" if life and verified else "High" if c["kind"] == "relief_gap" else "Watch"
    affected = {
        "km7": [["Chooralmala, ward 11", "About 10–18 households may be cut off"], ["Meppadi–Chooralmala road", "Debris across the road at km 7"]],
        "camp-water": [["412 people at 87% of capacity", "Relief truck 1 is delayed 22 min at Kalpetta"]],
        "vythiri": [["NH 766 near Vythiri", "Water on the road; traffic slowed, not closed"]],
    }[cluster_id]
    return {**c, "severity": severity, "verified": verified, "affected": affected}


TOOLS = [get_incoming_reports, cluster_reports, assess_incident]

INSTRUCTION = """You are the Field Intelligence Agent for the Wayanad DEOC. Read incoming reports (one is a Malayalam voice
note, summarised), group the ones about the same event, and say how sure we are and how severe each event is.
Call get_incoming_reports, cluster_reports, then assess_incident for km7, camp-water and vythiri."""
PROMPT = "Reports are coming in from Meppadi and Vythiri. What is happening, how sure are we, and what is critical?"
TEXT_SPEC = {
    "km7_title": "short incident title",
    "km7_meta": "e.g. 'Critical · corroborated by 3 sources'",
    "km7_summary": "two sentences: what happened, who may be cut off, how it was corroborated",
    "voice_note_en": "one sentence: the Malayalam voice note in plain English",
    "camp_water_summary": "one sentence",
    "vythiri_summary": "one sentence",
    "confidence": "short phrase",
    "limitation": "one short sentence",
}


def facts(ctx: dict) -> dict:
    return {"incidents": [assess_incident(c) for c in CLUSTERS], "reports": scenario()["incoming_reports"]}


def rules(f: dict) -> dict:
    km7 = f["incidents"][0]
    return {
        "km7_title": km7["title"],
        "km7_meta": f"{km7['severity']} · corroborated by {len(km7['reports']) - 1} sources",
        "km7_summary": "Debris across the road at km 7 blocks the only way into Chooralmala; about 10–18 households in ward 11 may be cut off. "
                       "A resident's Malayalam voice note with a photo, the ward officer's call and the police all report it within two minutes.",
        "voice_note_en": "The hillside came down onto the road near km 7; houses beyond it cannot get out.",
        "camp_water_summary": "Meppadi camp (412 people) runs out of drinking water in under 6 h; the second tanker is late.",
        "vythiri_summary": "Flooding at Vythiri started about 3 h earlier than forecast; NH 766 is slowed, not closed.",
        "confidence": "High · 3 independent sources within 2 minutes",
        "limitation": "The household count comes from the ward register, not a headcount.",
    }


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": "Treat the km 7 landslide report as verified and critical",
            "evidence": [["Resident voice note with photo, 12:02", "reported"], ["Ward officer call, 12:03", "verified"], ["Police control room, 12:04", "verified"]],
            "confidence": t["confidence"], "limitation": t["limitation"]}
