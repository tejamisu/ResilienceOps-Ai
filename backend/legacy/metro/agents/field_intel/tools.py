"""
Tools for the Field Intelligence Agent.

Each function is a standalone tool the ADK agent calls. Tools implement
real logic: keyword scanning across multiple lexicons, ward geocoding from
profile data, rule-based incident classification, and forecast alignment
comparison against ward vulnerability profiles.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, List

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _load(filename: str) -> Any:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tool 1 — parse_field_report
# ---------------------------------------------------------------------------

def parse_field_report(
    report_text: str,
    source: str,
    source_trust: str,
    location_hint: str,
) -> dict:
    """
    Parse a raw field report text and extract structured incident data using
    real keyword scanning across five lexicons:

    - severity_keywords: {"trapped": 1.0, "submerged": 0.9, "collapsed": 1.0,
        "critical": 0.9, "flooded": 0.7, "blocked": 0.6, "waterlogged": 0.5,
        "overflow": 0.6, "overflowing": 0.6}
    - water_level_hints: {"chest": "very_high", "waist": "high",
        "knee": "moderate", "ankle": "low", "ground floor": "moderate"}
    - vulnerability_markers: ["elderly", "children", "disabled", "pregnant",
        "infant", "bedridden"]
    - resource_keywords: {"rescue": "rescue_team", "medical": "medical_team",
        "pump": "pump_unit", "boat": "rescue_boat", "food": "relief_food",
        "water tanker": "water_tanker"}
    - asset_keywords: ["clinic", "hospital", "school", "shelter", "substation",
        "bridge", "road", "drain"]

    Severity score = max keyword score found. Confidence = source trust score
    boosted by 0.05 per vulnerability marker found and 0.05 if water level hint
    is detected.

    Args:
        report_text:  Raw text of the field report (voice transcript or message).
        source:       Who submitted the report (e.g. "Ward Officer W19").
        source_trust: OFFICIAL / VERIFIED_PARTNER / COMMUNITY / UNVERIFIED.
        location_hint: Partial address or ward/area name for geocoding.

    Returns:
        dict: All extracted fields including severity, severity_score,
              severity_keywords_found, water_level_estimate, vulnerability_flags,
              resource_needs, assets_nearby, all_keywords_found (combined list
              for classify_incident_type), report_confidence, raw_text.
    """
    SEVERITY_KEYWORDS = {
        "trapped": 1.0,
        "submerged": 0.9,
        "collapsed": 1.0,
        "critical": 0.9,
        "flooded": 0.7,
        "blocked": 0.6,
        "waterlogged": 0.5,
        "overflow": 0.6,
        "overflowing": 0.6,
    }

    WATER_LEVEL_HINTS = {
        "chest": "very_high",
        "waist": "high",
        "knee": "moderate",
        "ankle": "low",
        "ground floor": "moderate",
    }

    VULNERABILITY_MARKERS = [
        "elderly", "children", "disabled", "pregnant", "infant", "bedridden",
    ]

    RESOURCE_KEYWORDS = {
        "rescue": "rescue_team",
        "medical": "medical_team",
        "pump": "pump_unit",
        "boat": "rescue_boat",
        "food": "relief_food",
        "water tanker": "water_tanker",
    }

    ASSET_KEYWORDS = [
        "clinic", "hospital", "school", "shelter", "substation",
        "bridge", "road", "drain",
    ]

    # Additional context tokens used by classify_incident_type
    CONTEXT_KEYWORDS = [
        "route", "highway", "underpass", "culvert", "channel",
        "access road", "relief", "supply", "distribution", "evacuation",
    ]

    TRUST_MAP = {
        "OFFICIAL": 1.0,
        "VERIFIED_PARTNER": 0.85,
        "COMMUNITY": 0.6,
        "UNVERIFIED": 0.4,
    }

    text_lower = report_text.lower()

    # --- Severity scan ---
    found_severity = {
        kw: score
        for kw, score in SEVERITY_KEYWORDS.items()
        if kw in text_lower
    }
    severity_score = max(found_severity.values()) if found_severity else 0.3

    if severity_score >= 0.9:
        severity = "CRITICAL"
    elif severity_score >= 0.7:
        severity = "HIGH"
    elif severity_score >= 0.5:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # --- Water level ---
    water_level = None
    for hint, level in WATER_LEVEL_HINTS.items():
        if hint in text_lower:
            water_level = level
            break  # use first match (listed from deepest to shallowest)

    # --- Vulnerabilities ---
    found_vulnerabilities = [m for m in VULNERABILITY_MARKERS if m in text_lower]

    # --- Resources ---
    resource_needs: list = []
    for kw, resource in RESOURCE_KEYWORDS.items():
        if kw in text_lower and resource not in resource_needs:
            resource_needs.append(resource)
    # Default: high-severity events imply rescue team if not already listed
    if severity_score >= 0.7 and "rescue_team" not in resource_needs:
        resource_needs.append("rescue_team")

    # --- Assets ---
    assets_nearby = [a for a in ASSET_KEYWORDS if a in text_lower]

    # --- Context keywords ---
    found_context = [c for c in CONTEXT_KEYWORDS if c in text_lower]

    # --- Combined keyword list for classify_incident_type ---
    raw_all_kws = (
        list(found_severity.keys())
        + assets_nearby
        + found_context
        + found_vulnerabilities
    )
    seen: set = set()
    all_keywords_found: list = []
    for kw in raw_all_kws:
        if kw not in seen:
            seen.add(kw)
            all_keywords_found.append(kw)

    # --- Confidence ---
    base_trust = TRUST_MAP.get(source_trust.upper().strip(), 0.4)
    confidence_boost = 0.05 * len(found_vulnerabilities) + (0.05 if water_level else 0.0)
    report_confidence = round(min(1.0, base_trust + confidence_boost), 3)

    return {
        "parsed_at": datetime.now().isoformat(),
        "source": source,
        "source_trust": source_trust,
        "location_hint": location_hint,
        "severity": severity,
        "severity_score": round(severity_score, 3),
        "severity_keywords_found": list(found_severity.keys()),
        "water_level_estimate": water_level,
        "vulnerability_flags": found_vulnerabilities,
        "resource_needs": resource_needs,
        "assets_nearby": assets_nearby,
        "all_keywords_found": all_keywords_found,
        "report_confidence": report_confidence,
        "raw_text": report_text,
    }


# ---------------------------------------------------------------------------
# Tool 2 — geocode_to_ward
# ---------------------------------------------------------------------------

def geocode_to_ward(location_description: str, ward_hint: str) -> dict:
    """
    Match a free-text location description and optional ward hint against
    ward profiles and known landmarks loaded from ward_profiles.json.

    Matching strategy:
    - Combined text = location_description + ward_hint (lowercased)
    - Each ward has an alias list covering its ward_id, ward_name, area names,
      drain IDs, route names, shelter names, and known landmarks.
    - Returns the ward whose alias appears in the combined text, with confidence:
        0.95 — ward_id directly matched in location or hint
        0.85 — landmark/area name in location_description
        0.70 — landmark matched only in ward_hint string
    - Returns UNKNOWN with confidence 0.1 if no ward matches.

    Args:
        location_description: Free-text location from the field report.
        ward_hint:            Optional ward code or area name (e.g. "W12").

    Returns:
        dict: ward_id, ward_name, matched_on (keyword that matched),
              confidence, ward_vulnerability_score.
    """
    data = _load("ward_profiles.json")

    WARD_ALIASES: dict = {
        "W12": [
            "sector 12", "lakeview", "old market", "w12", "ward 12", "ward12",
            "d-17", "d-18", "route a", "nh route a", "elevated road c",
            "main road sector 12", "clinic sector 12", "sector 12 clinic",
            "school w12", "sh-b", "sh-c",
        ],
        "W07": [
            "sector 7", "old quarter", "w07", "ward 7", "ward7",
            "district hospital", "st. mary", "flyover route d", "d-09", "d-10",
            "sh-d",
        ],
        "W04": [
            "sector 4", "industrial west", "w04", "ward 4", "ward4",
            "industrial zone", "industrial road", "d-03", "sh-e",
        ],
        "W19": [
            "sector 19", "north wetlands", "northern wetland", "w19", "ward 19",
            "ward19", "wetland road", "route f", "north primary school",
            "borewell", "north wetland", "d-22", "d-23", "sh-f",
        ],
    }

    combined = (location_description + " " + ward_hint).lower()

    best_ward: dict = {}
    best_alias: str = ""
    best_confidence: float = 0.0

    for ward in data["wards"]:
        wid = ward["ward_id"]
        aliases = WARD_ALIASES.get(wid, [])

        for alias in aliases:
            if alias not in combined:
                continue

            # Confidence tiers
            if wid.lower() in location_description.lower() or wid.lower() in ward_hint.lower():
                conf = 0.95
            elif alias in location_description.lower():
                conf = 0.85
            else:
                conf = 0.70

            if conf > best_confidence:
                best_confidence = conf
                best_ward = ward
                best_alias = alias

    if best_ward:
        return {
            "ward_id": best_ward["ward_id"],
            "ward_name": best_ward["ward_name"],
            "matched_on": best_alias,
            "confidence": best_confidence,
            "ward_vulnerability_score": best_ward.get("vulnerability_score", 0.0),
            "historical_flood_count_5yr": best_ward.get("historical_flood_count_5yr", 0),
        }

    return {
        "ward_id": "UNKNOWN",
        "ward_name": "Unidentified Ward",
        "matched_on": None,
        "confidence": 0.10,
        "ward_vulnerability_score": None,
        "historical_flood_count_5yr": None,
    }


# ---------------------------------------------------------------------------
# Tool 3 — classify_incident_type
# ---------------------------------------------------------------------------

def classify_incident_type(keywords_found: List[str], severity_score: float) -> dict:
    """
    Classify the incident type from extracted keywords and severity score using
    rule-based priority matching (most specific / severe rules first):

    Rules (in order):
    1. "trapped" or "collapsed"                         → trapped_residents
    2. "submerged" + severity >= 0.8                    → trapped_residents / area_inundation
    3. "blocked" or "flooded" + road context keyword    → route_blockage
    4. "blocked" or "flooded" (no road context)         → urban_flooding
    5. "overflow" or "waterlogged" + drain keyword      → drainage_failure
    6. "overflow" or "waterlogged" (no drain)           → urban_flooding / drainage_stress
    7. Critical asset keyword (clinic/hospital/school)
       + flood context                                  → critical_asset_at_risk (secondary)
    8. Relief/supply keyword + no severe flood          → relief_gap
    9. Default                                          → general_flooding

    Args:
        keywords_found: Combined keyword list from parse_field_report
                        (includes severity + asset + context + vulnerability keywords).
        severity_score: Numeric severity score from parse_field_report (0.0-1.0).

    Returns:
        dict: primary_type, secondary_type, confidence, rationale, keywords_used.
    """
    kw_set = {k.lower() for k in keywords_found}

    primary_type = "general_flooding"
    secondary_type = None
    confidence = 0.55
    rationale = "Default classification — keyword specificity insufficient for precise typing."

    road_markers = {"road", "route", "bridge", "underpass", "highway", "access road"}
    drain_markers = {"drain", "d-17", "d-22", "d-18", "d-23", "culvert", "channel"}
    asset_markers = {"clinic", "hospital", "school", "shelter", "substation"}
    relief_markers = {"food", "water tanker", "relief", "supply", "distribution"}

    # Rule 1: trapped / collapsed → life-safety emergency
    if "trapped" in kw_set or "collapsed" in kw_set:
        primary_type = "trapped_residents"
        secondary_type = "life_safety_emergency"
        confidence = 0.92
        rationale = "Trapped/collapsed keyword confirms immediate life-safety event."

    # Rule 2: submerged at high severity
    elif "submerged" in kw_set and severity_score >= 0.8:
        primary_type = "trapped_residents"
        secondary_type = "area_inundation"
        confidence = 0.85
        rationale = "Submerged keyword at high severity implies potential entrapment."

    # Rule 3: blocked/flooded + road context → route blockage
    elif ("blocked" in kw_set or "flooded" in kw_set) and bool(road_markers & kw_set):
        primary_type = "route_blockage"
        secondary_type = "access_restriction"
        confidence = 0.87
        rationale = "Road/route keyword combined with blockage/flood indicator."

    # Rule 4: blocked/flooded without road → urban flooding
    elif "blocked" in kw_set or "flooded" in kw_set:
        primary_type = "urban_flooding"
        secondary_type = None
        confidence = 0.75
        rationale = "Blockage/flooding without explicit route context — urban flood inferred."

    # Rule 5: overflow/waterlogged + drain → drainage failure
    elif ("overflow" in kw_set or "overflowing" in kw_set or "waterlogged" in kw_set) and bool(drain_markers & kw_set):
        primary_type = "drainage_failure"
        secondary_type = "urban_flooding"
        confidence = 0.85
        rationale = "Overflow combined with drain infrastructure indicates drainage failure."

    # Rule 6: overflow/waterlogged without drain → urban flooding
    elif "overflow" in kw_set or "overflowing" in kw_set or "waterlogged" in kw_set:
        primary_type = "urban_flooding"
        secondary_type = "drainage_stress"
        confidence = 0.70
        rationale = "Waterlogging/overflow without drain reference — urban flooding likely."

    # Rule 7: critical asset + flood context
    if bool(asset_markers & kw_set):
        if primary_type in ("urban_flooding", "drainage_failure", "general_flooding"):
            secondary_type = "critical_asset_at_risk"
            confidence = min(1.0, confidence + 0.05)
            rationale += " Critical infrastructure proximity elevates risk classification."
        elif primary_type == "general_flooding":
            primary_type = "critical_asset_at_risk"
            confidence = 0.80
            rationale = "Critical asset keyword in flood context overrides general classification."

    # Rule 8: relief gap
    if bool(relief_markers & kw_set) and primary_type == "general_flooding":
        primary_type = "relief_gap"
        confidence = 0.72
        rationale = "Relief/supply keywords without high-severity flood indicators — relief gap scenario."

    return {
        "primary_type": primary_type,
        "secondary_type": secondary_type,
        "confidence": round(confidence, 3),
        "rationale": rationale,
        "keywords_used": sorted(list(kw_set)),
        "severity_score_input": severity_score,
    }


# ---------------------------------------------------------------------------
# Tool 4 — check_forecast_alignment
# ---------------------------------------------------------------------------

def check_forecast_alignment(ward_id: str, severity_score: float) -> dict:
    """
    Compare the observed incident severity against the ward's predicted risk
    profile loaded from ward_profiles.json. Determines whether the field
    observation is consistent with or anomalous relative to the forecast.

    Rules:
    - If ward vulnerability_score > 0.7 AND historical_flood_count_5yr > 2:
        alignment = "CONSISTENT — high-risk ward as predicted by vulnerability profile"
        confidence_boost = +0.10
    - If severity_score > 0.7 AND ward vulnerability_score < 0.4:
        alignment = "ANOMALY — incident severity higher than expected for this ward"
        confidence_boost = -0.05 (flag for extra verification)
    - Otherwise:
        alignment = "CONSISTENT WITH FORECAST — ward risk profile matches conditions"
        confidence_boost = +0.05

    Args:
        ward_id:       Ward identifier (e.g. "W12", "W19").
        severity_score: Numeric severity from parse_field_report (0.0-1.0).

    Returns:
        dict: ward_id, ward_name, alignment string, ward_vulnerability,
              historical_flood_count_5yr, confidence_boost, notes.
    """
    data = _load("ward_profiles.json")
    ward = next((w for w in data["wards"] if w["ward_id"] == ward_id), None)

    if ward is None:
        return {
            "ward_id": ward_id,
            "ward_name": "Unknown",
            "alignment": "WARD_NOT_FOUND — cannot assess forecast alignment",
            "ward_vulnerability": None,
            "historical_flood_count_5yr": None,
            "confidence_boost": 0.0,
            "notes": f"Ward {ward_id} not present in ward_profiles.json.",
        }

    vuln = ward.get("vulnerability_score", 0.5)
    hist = ward.get("historical_flood_count_5yr", 0)

    if vuln > 0.7 and hist > 2:
        alignment = (
            "CONSISTENT — high-risk ward as predicted by vulnerability profile. "
            "Historical flood frequency and vulnerability score both confirm elevated risk."
        )
        confidence_boost = 0.10
    elif severity_score > 0.7 and vuln < 0.4:
        alignment = (
            "ANOMALY — incident severity is higher than expected for this ward. "
            "Low vulnerability score and limited flood history make this observation unexpected. "
            "Recommend additional field verification."
        )
        confidence_boost = -0.05
    else:
        alignment = (
            "CONSISTENT WITH FORECAST — ward risk profile is broadly consistent with "
            "the observed conditions. No anomaly detected."
        )
        confidence_boost = 0.05

    return {
        "ward_id": ward_id,
        "ward_name": ward["ward_name"],
        "alignment": alignment,
        "ward_vulnerability": vuln,
        "historical_flood_count_5yr": hist,
        "confidence_boost": confidence_boost,
        "last_flood_date": ward.get("last_flood_date", "N/A"),
        "avg_waterlog_depth_cm": ward.get("avg_waterlog_depth_cm", 0),
        "notes": ward.get("notes", ""),
    }


# ---------------------------------------------------------------------------
# Tool 5 — get_all_active_field_incidents
# ---------------------------------------------------------------------------

def get_all_active_field_incidents() -> dict:
    """
    Retrieve all currently active field incidents across all responder channels.
    Returns 6 incidents at different lifecycle stages:
    - 2 VERIFIED (ground-truthed by official/partner source)
    - 2 AWAITING_VERIFICATION (community or single unverified source)
    - 1 ESCALATED (incident commander notified, resources en route)
    - 1 RESOLVED (pump deployed, situation cleared)

    Primarily Ward 12 (Sector 12 – Lakeview) and Ward 19 (North Wetlands).

    Returns:
        dict: fetched_at, per-status counts, and incidents list with full detail.
    """
    now = datetime.now().isoformat()

    incidents = [
        {
            "incident_id": "FI-001",
            "type": "route_blockage",
            "severity": "CRITICAL",
            "severity_score": 0.90,
            "ward_id": "W19",
            "ward_name": "Sector 19 – North Wetlands",
            "vulnerability_flags": ["elderly", "children"],
            "resource_needs": ["rescue_boat", "rescue_team"],
            "asset_proximity": ["school", "shelter"],
            "forecast_alignment": (
                "CONSISTENT — high-risk ward as predicted by vulnerability profile."
            ),
            "confidence": 0.95,
            "source": "NGO-1 Red Cross Field Team + CWC FloodWatch Official",
            "status": "VERIFIED",
            "summary": (
                "Route F — sole access road to Ward 19 — confirmed submerged. "
                "~38,000 residents isolated. NGO-1 vehicle unable to pass. "
                "CWC DANGER-level advisory consistent. Rescue boat dispatched, ETA 45 min."
            ),
            "timestamp": "2025-07-14T07:10:00+05:30",
        },
        {
            "incident_id": "FI-002",
            "type": "drainage_failure",
            "severity": "HIGH",
            "severity_score": 0.75,
            "ward_id": "W12",
            "ward_name": "Sector 12 – Lakeview",
            "vulnerability_flags": [],
            "resource_needs": ["pump_unit"],
            "asset_proximity": ["clinic", "school", "drain"],
            "forecast_alignment": (
                "CONSISTENT — high-risk ward as predicted by vulnerability profile."
            ),
            "confidence": 0.92,
            "source": "Ward Officer W12 + Fire Service Unit 2",
            "status": "VERIFIED",
            "summary": (
                "Drain D-17 overflowing at Sector 12 main road junction. "
                "Waterlogging spreading toward old market area and clinic road. "
                "Ward officer on-site, pump unit requested. Fire unit confirms flooding."
            ),
            "timestamp": "2025-07-14T07:20:00+05:30",
        },
        {
            "incident_id": "FI-003",
            "type": "trapped_residents",
            "severity": "CRITICAL",
            "severity_score": 0.90,
            "ward_id": "W12",
            "ward_name": "Sector 12 – Lakeview",
            "vulnerability_flags": ["elderly"],
            "resource_needs": ["rescue_team", "medical_team"],
            "asset_proximity": ["clinic", "road"],
            "forecast_alignment": (
                "CONSISTENT — high-risk ward as predicted by vulnerability profile."
            ),
            "confidence": 0.65,
            "source": "Community WhatsApp — W12 Resident (unverified)",
            "status": "AWAITING_VERIFICATION",
            "summary": (
                "Community report: elderly couple trapped on ground floor near clinic "
                "in Sector 12. Water waist deep, residents unable to walk out. "
                "Single community source — field verification required before dispatch."
            ),
            "timestamp": "2025-07-14T09:00:00+05:30",
        },
        {
            "incident_id": "FI-004",
            "type": "evacuation_required",
            "severity": "HIGH",
            "severity_score": 0.72,
            "ward_id": "W19",
            "ward_name": "Sector 19 – North Wetlands",
            "vulnerability_flags": ["children", "elderly"],
            "resource_needs": ["rescue_team", "relief_food"],
            "asset_proximity": ["school", "shelter"],
            "forecast_alignment": (
                "CONSISTENT — high-risk ward as predicted by vulnerability profile."
            ),
            "confidence": 0.82,
            "source": "Ward Officer W19",
            "status": "AWAITING_VERIFICATION",
            "summary": (
                "North Primary School shelter area waterlogged. Elderly and children "
                "in adjacent informal settlement require evacuation to higher ground. "
                "Ward officer requesting support. Access by Route F currently blocked."
            ),
            "timestamp": "2025-07-14T08:30:00+05:30",
        },
        {
            "incident_id": "FI-005",
            "type": "route_blockage",
            "severity": "CRITICAL",
            "severity_score": 0.88,
            "ward_id": "W12",
            "ward_name": "Sector 12 – Lakeview",
            "vulnerability_flags": [],
            "resource_needs": ["rescue_team"],
            "asset_proximity": ["road"],
            "forecast_alignment": (
                "CONSISTENT — high-risk ward as predicted by vulnerability profile."
            ),
            "confidence": 0.92,
            "source": "Fire Service Unit 2 (VERIFIED_PARTNER)",
            "status": "ESCALATED",
            "summary": (
                "Route A NH underpass deteriorating rapidly. Water level knee to waist. "
                "Route A closure imminent — all emergency vehicles rerouting via Elevated "
                "Road C. Incident commander notified. Closure marker requested."
            ),
            "timestamp": "2025-07-14T08:00:00+05:30",
        },
        {
            "incident_id": "FI-006",
            "type": "urban_flooding",
            "severity": "MEDIUM",
            "severity_score": 0.55,
            "ward_id": "W07",
            "ward_name": "Sector 7 – Old Quarter",
            "vulnerability_flags": ["elderly"],
            "resource_needs": ["pump_unit"],
            "asset_proximity": ["hospital", "road"],
            "forecast_alignment": (
                "CONSISTENT WITH FORECAST — ward risk profile matches observed conditions."
            ),
            "confidence": 0.87,
            "source": "Ward Officer W07 + NGO-2 Local Welfare",
            "status": "RESOLVED",
            "summary": (
                "Minor waterlogging near Flyover Route D residential area. "
                "Pump deployed, drainage restored within 1.5 hours. Area now passable. "
                "Elderly residents in adjacent block advised to remain indoors until further notice."
            ),
            "timestamp": "2025-07-14T06:45:00+05:30",
        },
    ]

    critical = [i for i in incidents if i["severity"] == "CRITICAL" and i["status"] != "RESOLVED"]

    return {
        "fetched_at": now,
        "total_active": len(incidents),
        "verified_count": sum(1 for i in incidents if i["status"] == "VERIFIED"),
        "pending_count": sum(1 for i in incidents if i["status"] == "AWAITING_VERIFICATION"),
        "escalated_count": sum(1 for i in incidents if i["status"] == "ESCALATED"),
        "resolved_count": sum(1 for i in incidents if i["status"] == "RESOLVED"),
        "critical_unresolved_count": len(critical),
        "incidents": incidents,
    }
