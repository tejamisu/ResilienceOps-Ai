"""Dispatch & Delegation Agent · Respond.
A verified incident + teams + route status -> who to send, by which route, how fast, and why. Teammate's scoring kept:
availability × proximity × equipment, with the route's state applied.
Feeds: Respond › the km 7 recommendation ("AI recommends: send …", ETA, Why this?), the dispatch Edit dialog.
Owner: Ananya Menon, Incident Commander (nothing moves until she approves)."""
from __future__ import annotations

from core.scenario import scenario, team

NAME, DISPLAY, PHASE, OWNER = "dispatch", "Dispatch & Delegation Agent", "respond", "Incident Commander"

AVAIL = {"standby": 1.0, "available": .9, "on_request": .5, "en_route": .6, "on_site": .2, "delayed": .1}
# minutes to km 7 from each base by the passable route (Route C); staged at Meppadi = 11 min
MINUTES = {"fr2": 26, "fr4": 70, "jcb3": 22, "sdrf": 45, "amb": 20, "rt1": 48}


def get_teams(staged_at_meppadi: bool = False) -> dict:
    """Teams with their base, kit and status. staged_at_meppadi=True if Prepare's handover staged Rescue Unit 2 at Meppadi."""
    out = []
    for t in scenario()["teams"]:
        mins = 11 if (t["id"] == "fr2" and staged_at_meppadi) else MINUTES.get(t["id"])
        out.append({**t, "minutes_to_km7": mins, "base": "Meppadi staging point" if (t["id"] == "fr2" and staged_at_meppadi) else t["base"]})
    return {"teams": out}


def get_routes() -> dict:
    """Route status into Chooralmala: Route A (blocked at km 7), Route C (forest track, passable, not verified), NH 766."""
    return {"routes": scenario()["routes"]}


def score_teams(need: str = "landslide rescue", staged_at_meppadi: bool = False) -> dict:
    """Score every team for a need ('landslide rescue' or 'debris clearing'): availability × proximity × equipment. Highest first."""
    rows = []
    for t in get_teams(staged_at_meppadi)["teams"]:
        has_kit = any(need.split()[0] in k for k in t["kit"])
        kit = 1.0 if has_kit else .3
        prox = max(0, 1 - (t["minutes_to_km7"] or 90) / 90)
        s = round(AVAIL.get(t["status"], .5) * .4 + prox * .35 + kit * .25, 2)
        rows.append({"team": t["id"], "name": t["name"], "agency": t["agency"], "score": s, "has_kit": has_kit, "minutes": t["minutes_to_km7"], "status": t["status"], "base": t["base"]})
    return {"need": need, "ranked": sorted(rows, key=lambda r: -r["score"])}


def recommend(staged_at_meppadi: bool = False) -> dict:
    """Recommendation for the km 7 landslide: lead team, support team, route, ETA and alternatives."""
    lead = next(r for r in score_teams("landslide rescue", staged_at_meppadi)["ranked"] if r["has_kit"])
    # support: a different team that actually has the kit for the second job
    support = next(r for r in score_teams("debris clearing", staged_at_meppadi)["ranked"] if r["has_kit"] and r["team"] != lead["team"])
    route = next(r for r in scenario()["routes"] if r["id"] == "C")
    return {"lead": lead, "support": support, "route": route, "eta_min": lead["minutes"],
            "alternatives": [{"route": "A", "note": "after Excavator 3 clears the debris, about +35 min"}, {"team": "sdrf", "note": "on request from KSDMA, about 45 min"}],
            "hold": "Police to hold the closed road at km 7"}


TOOLS = [get_teams, get_routes, score_teams, recommend]

INSTRUCTION = """You are the Dispatch & Delegation Agent for DDMA Wayanad. A landslide has blocked the road at km 7 and
households in Chooralmala ward 11 may be cut off. Recommend who to send, by which route, and why — the Incident Commander
approves it. Call get_routes, score_teams for 'landslide rescue' and 'debris clearing', then recommend."""
TEXT_SPEC = {
    "recommendation": "one line starting 'AI recommends: send …' naming the lead team, the support team and the route",
    "eta_line": "e.g. 'Estimated arrival 26 min · police to hold the closed road'",
    "why": ["3–4 short bullets: why this team, why this route, what the support team does, sources"],
    "confidence": "short phrase naming what is unverified",
    "limitation": "one short sentence",
}


def prompt(ctx: dict) -> str:
    s = "Rescue Unit 2 was staged at Meppadi by Prepare (staged_at_meppadi=True)." if ctx.get("staged") else "No Prepare handover: teams are at their bases (staged_at_meppadi=False)."
    return f"Verified landslide at km 7, 12:02. {s} Recommend the dispatch."


def facts(ctx: dict) -> dict:
    staged = bool(ctx.get("staged"))
    return {"staged": staged, **recommend(staged), "routes": scenario()["routes"]}


def rules(f: dict) -> dict:
    lead, sup = f["lead"], f["support"]
    return {
        "recommendation": f"AI recommends: send {lead['agency']} {lead['name'].replace('Rescue ', '')} with {sup['agency']} {sup['name'][0].lower() + sup['name'][1:]} by Route C",
        "eta_line": f"Estimated arrival {f['eta_min']} min · {'staged at Meppadi since 10:00 · ' if f['staged'] else ''}police to hold the closed road",
        "why": [
            "Unit 2 has been on standby at Meppadi since 10:00, 7 km from the site." if f["staged"] else "Unit 2 is the nearest available team with landslide rescue kit.",
            "Route A is blocked at km 7; Route C was reported passable by the ward officer (not yet verified).",
            "The excavator can clear debris for medical access after the rescue team assesses the site.",
            "Sources: Malayalam voice note with photo, ward officer call, rainfall gauge above 15 mm/h.",
        ],
        "confidence": "Medium — Route C last checked 18 min ago",
        "limitation": "Route C is a forest track for high-clearance vehicles only.",
    }


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": f"Send {f['lead']['name']} with {f['support']['name']} by Route C",
            "evidence": [["Team availability, 12:08", "verified"], ["Route C passable (ward officer)", "reported"], [f"ETA {f['eta_min']} min", "estimated"]],
            "confidence": t["confidence"], "limitation": t["limitation"]}
