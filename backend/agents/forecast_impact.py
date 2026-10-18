"""Forecast & Impact Agent (was: Sentinel) · Prepare.
IMD forecast + place risk factors -> ranked priority places with an explainable risk score.
Feeds: Prepare › Rainfall forecast, the four place tiles and their detail cards, the Forecast and risk page.
Owner: Dr. Rahul Nair, Hazard Analyst (recommends) · Ananya Menon, Incident Commander (decides)."""
from __future__ import annotations

from core.scenario import scenario, place

NAME, DISPLAY, PHASE, OWNER = "forecast_impact", "Forecast & Impact Agent", "prepare", "Hazard Analyst"

# composite = 0.35 hazard + 0.25 exposure + 0.20 vulnerability + 0.15 access + 0.05 history (teammate's Sentinel weights,
# with landslide terms): hazard = strongest of rain, slope, dam, river; access = how cut off the place can get
W = {"hazard": .35, "exposure": .25, "vulnerability": .20, "access": .15, "history": .05}
LEVELS = [(.7, "Critical"), (.5, "High"), (.3, "Moderate"), (0, "Low")]


def get_forecast() -> dict:
    """Latest IMD district forecast for Wayanad: alert level, 24 h rainfall at the Meppadi gauge, the landslide-watch
    threshold, the expected peak window, and the forecast's confidence and limitation."""
    f = scenario()["forecast"]
    return {k: f[k] for k in ("source", "issued", "alert", "headline", "gauge", "rain_24h_mm", "landslide_watch_mm_h", "peak_window", "confidence", "limitation")}


def list_places() -> dict:
    """All places watched in Wayanad with their hazard, exposure range and heavy-rain window."""
    return {"places": [{"id": p["id"], "name": p["name"], "hazard": p["hazard"], "exposure": p["exposure"], "window": p["window"]} for p in scenario()["places"]]}


def score_place(place_id: str) -> dict:
    """Explainable risk score (0–1) for one place: each component, the weights, the level and the factors behind it.
    place_id is one of: meppadi, vythiri, mananthavady, kalpetta."""
    p = place(place_id)
    f = {x["id"]: x for x in p["factors"]}
    hazard = max(f[k]["score"] for k in ("rain", "slope", "dam", "river") if k in f)
    comp = {
        "hazard": hazard,
        "exposure": round(min(1, p["exposure"][1] / 3500), 2),
        "vulnerability": f.get("people", {}).get("score", .5),
        "access": f.get("road", {}).get("score", .5),
        "history": f.get("history", {}).get("score", .3),
    }
    score = round(sum(W[k] * v for k, v in comp.items()), 2)
    level = next(l for t, l in LEVELS if score >= t)
    top = sorted(p["factors"], key=lambda x: -x["score"])[:3]
    return {"place": p["id"], "name": p["name"], "score": score, "level": level, "components": comp, "weights": W,
            "exposure": p["exposure"], "window": p["window"], "hazard": p["hazard"],
            "top_factors": [{"label": x["label"], "value": x["value"], "score": x["score"], "source": x["src"]} for x in top],
            "unknowns": p["unknowns"]}


def get_place_history(place_id: str) -> dict:
    """Past events and lessons recorded for a place (no casualty figures)."""
    return {"place": place_id, "history": [h for h in scenario()["history"] if place_id in h["places"]]}


TOOLS = [get_forecast, list_places, score_place, get_place_history]

INSTRUCTION = """You are the Forecast & Impact Agent for DDMA Wayanad. Turn the IMD forecast and each place's risk factors
into a ranked list of priority places, and explain each ranking in one plain sentence a district officer can check.
Call get_forecast, list_places, then score_place for every place (and get_place_history where history matters)."""
PROMPT = "IMD has issued a red alert for Wayanad. Rank the priority places for the next 24 hours and explain why each one ranks where it does."
TEXT_SPEC = {
    "summary": "two sentences: the alert, the peak window, which place leads and why",
    "why": {"meppadi": "one sentence, the main drivers for Meppadi", "vythiri": "one sentence for Vythiri",
            "mananthavady": "one sentence for Mananthavady", "kalpetta": "one sentence for Kalpetta"},
    "confidence": "short phrase, e.g. 'Medium–high · forecast updated 20 min ago'",
    "limitation": "one short sentence on what could change the ranking",
}


def facts(ctx: dict) -> dict:
    ranked = sorted((score_place(p["id"]) for p in scenario()["places"]), key=lambda x: -x["score"])
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    return {"forecast": get_forecast(), "places": ranked, "district_level": ranked[0]["level"]}


def rules(f: dict) -> dict:
    fc, lead = f["forecast"], f["places"][0]
    why = {}
    for p in f["places"]:
        a, b = p["top_factors"][:2]
        why[p["place"]] = f"{p['name']} ranks {p['level'].lower()} ({p['score']:.2f}). Main drivers: {a['label'].lower()} ({a['value']}) and {b['label'].lower()} ({b['value']})."
    return {
        "summary": f"IMD {fc['alert'].lower()} alert: {fc['rain_24h_mm']} mm expected at the {fc['gauge']} gauge, peak {fc['peak_window'][0]}–{fc['peak_window'][1]}. "
                   f"{lead['name']} leads because {lead['top_factors'][0]['label'].lower()} and {lead['top_factors'][1]['label'].lower()} combine with {lead['exposure'][0]:,}–{lead['exposure'][1]:,} people potentially exposed.",
        "why": why,
        "confidence": f"{fc['confidence']} · forecast issued {fc['issued']}",
        "limitation": fc["limitation"] + "; exposure is a range from census and panchayat lists.",
    }


def trace(f: dict, t: dict) -> dict:
    return {"recommendation": f"Prepare {f['places'][0]['name']} first; it is {f['places'][0]['level'].lower()}",
            "evidence": [[f"IMD district forecast, {f['forecast']['issued']}", "verified"], ["KSDMA slope-risk layer", "verified"],
                         [f"Exposure {f['places'][0]['exposure'][0]:,}–{f['places'][0]['exposure'][1]:,} people", "estimated"]],
            "confidence": t["confidence"], "limitation": t["limitation"]}
