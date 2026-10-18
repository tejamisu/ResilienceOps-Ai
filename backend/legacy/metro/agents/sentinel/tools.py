"""
Tools for the Sentinel (Forecast & Impact) Agent.

Each function is a tool the ADK agent can call. They load from the
simulated data files that represent IMD/CWC/DDMA feeds in a real deployment.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, List

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _load(filename: str) -> dict | list:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)


def get_weather_forecast() -> dict:
    """
    Fetch the latest IMD rainfall and weather forecast for the district.

    Returns the current official forecast including alert level, rainfall
    expected per time period, confidence, and agency remarks. In production
    this connects to the IMD API or authorized meteorological data feed.

    Returns:
        dict: Weather forecast with alert level, rainfall amounts, confidence.
    """
    data = _load("mock_imd_forecast.json")
    return {
        "source": data["source"],
        "issued_at": data["issued_at"],
        "alert_level": data["alert_level"],
        "alert_type": data["alert_type"],
        "forecast_periods": data["forecast_periods"],
        "cumulative_24h_mm": data["cumulative_24h_mm"],
        "extreme_heavy_threshold_mm": data["extreme_heavy_threshold_mm"],
        "confidence_level": data["confidence_level"],
        "agency_remarks": data["agency_remarks"],
        "data_quality": data["data_quality"],
    }


def get_flood_advisory() -> dict:
    """
    Fetch the latest CWC flood advisory and water body status for the district.

    Returns current water levels, danger level status, rate of rise, and
    which wards are at risk from each water body. In production this connects
    to CWC FloodWatch API or authorized state flood-monitoring feeds.

    Returns:
        dict: Water body statuses, danger levels, affected wards, and trend.
    """
    data = _load("mock_cwc_advisory.json")
    return {
        "source": data["source"],
        "issued_at": data["issued_at"],
        "advisory_id": data["advisory_id"],
        "water_bodies": data["water_bodies"],
        "district_flood_advisory": data["district_flood_advisory"],
        "confidence_level": data["confidence_level"],
        "data_quality": data["data_quality"],
    }


def get_all_ward_profiles() -> dict:
    """
    Retrieve demographic, infrastructure, and vulnerability profiles for
    all wards in the city. Includes population, elevation, drainage capacity,
    informal settlements, elderly/child population, critical infrastructure,
    shelter locations, and historical flood frequency.

    Returns:
        dict: City name and list of all ward profiles with full detail.
    """
    data = _load("ward_profiles.json")
    return {
        "city": data["city"],
        "district": data["district"],
        "wards": data["wards"],
    }


def get_ward_profile(ward_id: str) -> dict:
    """
    Retrieve detailed profile for a specific ward by its ID.

    Args:
        ward_id: The ward identifier, e.g. 'W12', 'W19'.

    Returns:
        dict: Full ward profile, or error if ward not found.
    """
    data = _load("ward_profiles.json")
    for ward in data["wards"]:
        if ward["ward_id"] == ward_id:
            return ward
    return {"error": f"Ward {ward_id} not found"}


def get_historical_flood_patterns() -> dict:
    """
    Retrieve historical flood events and recurring hotspot patterns for the city.
    Includes past casualties, evacuation numbers, infrastructure damage, response
    times, relief gaps, and lessons learned. Essential for calibrating risk scores
    and identifying areas with proven, repeated flood exposure.

    Returns:
        dict: Historical events, recurring hotspots, and lessons.
    """
    data = _load("historical_floods.json")
    return {
        "data_period": data["data_period"],
        "source": data["source"],
        "events": data["events"],
        "recurring_hotspots": data["recurring_hotspots"],
    }


def calculate_ward_risk_score(
    ward_id: str,
    forecast_rainfall_24h_mm: float,
    water_body_status: str,
) -> dict:
    """
    Calculate a composite flood risk priority score for a ward based on:
    - Hazard severity (forecast rainfall vs drain capacity, water body status)
    - Population exposure (density × low-lying area factor)
    - Vulnerability (poverty, informal settlements, elderly, children, disability)
    - Infrastructure risk (critical assets, evacuation route viability)
    - Historical flood frequency weight

    The score uses the formula:
      score = 0.35*hazard + 0.25*exposure + 0.20*vulnerability + 0.15*infra_risk + 0.05*history_weight

    Args:
        ward_id: Ward identifier.
        forecast_rainfall_24h_mm: Total forecast rainfall in mm for next 24 hours.
        water_body_status: Status from CWC advisory — 'NORMAL', 'WARNING', 'DANGER'.

    Returns:
        dict: Component scores, composite score, priority level, and rationale.
    """
    data = _load("ward_profiles.json")
    ward = next((w for w in data["wards"] if w["ward_id"] == ward_id), None)
    if not ward:
        return {"error": f"Ward {ward_id} not found"}

    # Hazard severity: rainfall vs drain capacity + water body
    drain_multiplier = {"adequate": 0.5, "undersized": 0.8, "severely undersized": 1.0}.get(
        ward["drainage_capacity"], 0.7
    )
    condition_multiplier = {"good": 0.8, "maintained": 0.9, "partially blocked": 1.1, "blocked": 1.3}.get(
        ward["drainage_condition"], 1.0
    )
    rainfall_score = min(forecast_rainfall_24h_mm / 350.0, 1.0)
    water_body_bonus = {"DANGER": 0.25, "WARNING": 0.12, "WATCH": 0.06, "NORMAL": 0.0}.get(water_body_status, 0.0)
    hazard_score = min(rainfall_score * drain_multiplier * condition_multiplier + water_body_bonus, 1.0)

    # Population exposure: density × elevation penalty
    density_score = min(ward["population_density_per_sqkm"] / 25000.0, 1.0)
    elevation_penalty = max(0.0, 1.0 - (ward["elevation_m"] / 15.0))
    exposure_score = min((density_score * 0.6) + (elevation_penalty * 0.4), 1.0)

    # Vulnerability: weighted composite
    vuln = ward["vulnerability_score"]
    # Cross-check with sub-indicators
    computed_vuln = (
        ward["informal_settlements_pct"] / 100 * 0.30
        + ward["below_poverty_line_pct"] / 100 * 0.25
        + ward["elderly_population_pct"] / 100 * 0.15
        + ward["child_population_pct"] / 100 * 0.10
        + (1 - ward["smartphone_penetration_pct"] / 100) * 0.10
        + ward["disability_population_pct"] / 100 * 0.10
    )
    vulnerability_score = (vuln * 0.5) + (computed_vuln * 0.5)

    # Infrastructure risk
    infra_items = ward["critical_infrastructure"]
    high_risk_assets = sum(1 for a in infra_items if a.get("ground_floor_risk") or a.get("flood_vulnerable"))
    infra_score = min(high_risk_assets / max(len(infra_items), 1), 1.0)
    pump_penalty = 0.0 if ward["pump_capacity_adequate"] else 0.25
    infra_score = min(infra_score + pump_penalty, 1.0)

    # Historical weight
    history_score = min(ward["historical_flood_count_5yr"] / 5.0, 1.0)

    # Composite
    composite = (
        0.35 * hazard_score
        + 0.25 * exposure_score
        + 0.20 * vulnerability_score
        + 0.15 * infra_score
        + 0.05 * history_score
    )

    if composite >= 0.75:
        priority = "CRITICAL"
    elif composite >= 0.55:
        priority = "HIGH"
    elif composite >= 0.35:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Population at risk estimate
    at_risk_pct = min(elevation_penalty * hazard_score, 0.85)
    pop_low = int(ward["population"] * at_risk_pct * 0.7)
    pop_high = int(ward["population"] * at_risk_pct * 1.0)

    return {
        "ward_id": ward_id,
        "ward_name": ward["ward_name"],
        "composite_score": round(composite, 3),
        "priority": priority,
        "component_scores": {
            "hazard_severity": round(hazard_score, 3),
            "population_exposure": round(exposure_score, 3),
            "vulnerability": round(vulnerability_score, 3),
            "infrastructure_risk": round(infra_score, 3),
            "historical_weight": round(history_score, 3),
        },
        "population_exposure_estimate": {
            "low": pop_low,
            "high": pop_high,
        },
        "notes": ward["notes"],
    }


def get_available_resources() -> dict:
    """
    Retrieve current district emergency resource inventory including teams,
    vehicles, pumps, shelter capacity, medical kits, and relief stock.
    In production this connects to the DDMA resource management system.

    Returns:
        dict: Available resources by category with quantities and locations.
    """
    return {
        "source": "DDMA Resource Inventory (Simulated)",
        "last_updated": datetime.now().isoformat(),
        "rescue_teams": [
            {"team_id": "RT-1", "agency": "Fire Service", "crew": 6, "status": "available", "equipment": ["high-clearance vehicle", "rescue kit", "life jackets"]},
            {"team_id": "RT-2", "agency": "Fire Service", "crew": 6, "status": "available", "equipment": ["rescue boat", "pump", "rescue kit"]},
            {"team_id": "RT-3", "agency": "SDRF", "crew": 12, "status": "standby", "equipment": ["inflatable boat", "rescue equipment", "medical kit"]},
        ],
        "medical_teams": [
            {"team_id": "MT-1", "agency": "Health Dept", "crew": 4, "status": "available", "equipment": ["ambulance", "emergency medical kit"]},
            {"team_id": "MT-2", "agency": "Health Dept", "crew": 4, "status": "available", "equipment": ["ambulance", "emergency medical kit"]},
        ],
        "pumps": {"total": 6, "available": 6, "capacity_each_lph": 50000},
        "shelter_beds_total": 1750,
        "shelter_beds_available": 1750,
        "water_tankers": 3,
        "food_kits": 2000,
        "medical_kits": 500,
        "sanitation_kits": 300,
        "police_units": 8,
        "ngo_teams": [
            {"team_id": "NGO-1", "name": "Red Cross District Unit", "crew": 10, "status": "on-call", "capability": "relief distribution, first aid"},
            {"team_id": "NGO-2", "name": "Local Welfare Society", "crew": 6, "status": "on-call", "capability": "community outreach, food distribution"},
        ],
        "gaps_vs_worst_case": {
            "pumps_needed_for_critical_wards": 10,
            "pump_shortfall": 4,
            "shelter_beds_needed_critical_scenario": 2500,
            "shelter_shortfall": 750,
        },
    }


def generate_preparedness_plan(ward_risk_summaries: List[Any]) -> dict:
    """
    Generate a prioritized preparedness action plan based on ward risk rankings
    and available resources. Produces a time-sequenced list of actions (0-4h,
    4-12h, 12-24h windows) for the incident commander to review and approve.

    Args:
        ward_risk_summaries: List of ward risk assessment dicts, each with
                             ward_id, ward_name, priority, and composite_score.

    Returns:
        dict: Time-sequenced action plan with owner, deadline, and resource needed.
    """
    critical = [w for w in ward_risk_summaries if w.get("priority") == "CRITICAL"]
    high = [w for w in ward_risk_summaries if w.get("priority") == "HIGH"]

    immediate_actions = []
    for w in critical:
        immediate_actions.extend([
            {
                "action": f"Deploy field verification team to {w['ward_name']}",
                "owner": "Ward Officer + Fire Service",
                "deadline_hrs": 1,
                "resource": "RT-1 or RT-2",
                "ward": w["ward_id"],
            },
            {
                "action": f"Activate and staff shelters for {w['ward_name']} — verify accessibility",
                "owner": "DDMA Shelter Coordinator",
                "deadline_hrs": 2,
                "resource": "Shelter staff + NGO-1",
                "ward": w["ward_id"],
            },
            {
                "action": f"Pre-stage 2 pumps at critical drain points in {w['ward_name']}",
                "owner": "Municipal Drainage Team",
                "deadline_hrs": 1.5,
                "resource": "2 pumps from inventory",
                "ward": w["ward_id"],
            },
            {
                "action": f"Notify ward officer and community leaders in {w['ward_name']} — request door-to-door alert for low-connectivity residents",
                "owner": "DDMA Communications + Ward Office",
                "deadline_hrs": 1,
                "resource": "Community volunteers, loudspeaker vans",
                "ward": w["ward_id"],
            },
        ])

    medium_actions = []
    for w in high:
        medium_actions.extend([
            {
                "action": f"Prepare shelter readiness for {w['ward_name']} — place on standby",
                "owner": "DDMA Shelter Coordinator",
                "deadline_hrs": 4,
                "resource": "Shelter staff",
                "ward": w["ward_id"],
            },
            {
                "action": f"Pre-position 1 pump and 1 medical kit at {w['ward_name']}",
                "owner": "Municipal + Health Dept",
                "deadline_hrs": 4,
                "resource": "1 pump, MT-1 or MT-2",
                "ward": w["ward_id"],
            },
        ])

    escalation_needed = len(critical) >= 2 or any(
        w.get("composite_score", 0) > 0.85 for w in critical
    )

    return {
        "plan_generated_at": datetime.now().isoformat(),
        "critical_wards_count": len(critical),
        "high_wards_count": len(high),
        "escalation_recommended": escalation_needed,
        "escalation_reason": (
            "Multiple critical wards detected. District resource inventory shows shortfall "
            "in pumps and shelter beds. Recommend requesting SDMA support for additional "
            "rescue boats, 4 pumps, and 750 shelter beds."
            if escalation_needed else ""
        ),
        "immediate_actions_0_to_4h": immediate_actions,
        "medium_term_actions_4_to_12h": medium_actions,
        "standing_advisory": [
            "Draft multilingual public advisory for commander review and approval before dispatch",
            "Brief all agency heads at EOC within 1 hour",
            "Activate NGO coordination channel — share incident ID and ward priorities",
            "Ensure offline field-report capability is distributed to all Ward 19 volunteers",
        ],
    }
