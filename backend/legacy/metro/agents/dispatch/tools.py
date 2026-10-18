"""
Tools for the Dispatch & Resource Agent.

Each function is a standalone tool the ADK agent calls. Tools implement
real multi-factor scoring logic: availability, proximity, equipment match,
route safety, and workload — no hardcoded single-path responses.
"""
from __future__ import annotations

from datetime import datetime


# ---------------------------------------------------------------------------
# Private helpers — shared roster and route data
# ---------------------------------------------------------------------------

def _build_roster() -> list:
    """Return the canonical responder roster as a list of team dicts."""
    return [
        {
            "team_id": "FIRE-1",
            "agency": "Fire Department",
            "crew_count": 6,
            "status": "AVAILABLE",
            "current_location": "Central Fire Station",
            "equipment": ["rescue_kit", "high_clearance_vehicle"],
            "last_checkin": "2025-07-14T08:45:00+05:30",
            "ward_proximity": {"W12": 8, "W07": 12, "W04": 18, "W19": 25},
        },
        {
            "team_id": "FIRE-2",
            "agency": "Fire Department",
            "crew_count": 6,
            "status": "STANDBY",
            "current_location": "Central Fire Station",
            "equipment": ["rescue_boat", "pump"],
            "last_checkin": "2025-07-14T08:50:00+05:30",
            "ward_proximity": {"W12": 10, "W07": 14, "W04": 20, "W19": 22},
        },
        {
            "team_id": "SDRF-1",
            "agency": "SDRF",
            "crew_count": 12,
            "status": "AVAILABLE",
            "current_location": "District Staging Area",
            "equipment": ["rescue_boat", "rescue_kit", "medical_kit"],
            "last_checkin": "2025-07-14T08:30:00+05:30",
            "ward_proximity": {"W12": 20, "W07": 25, "W04": 30, "W19": 35},
        },
        {
            "team_id": "POLICE-1",
            "agency": "Police",
            "crew_count": 4,
            "status": "AVAILABLE",
            "current_location": "District Police HQ",
            "equipment": ["high_clearance_vehicle"],
            "last_checkin": "2025-07-14T09:00:00+05:30",
            "ward_proximity": {"W12": 10, "W07": 8, "W04": 15, "W19": 30},
        },
        {
            "team_id": "POLICE-2",
            "agency": "Police",
            "crew_count": 4,
            "status": "EN_ROUTE",
            "current_location": "En route Ward 12 Sector 8",
            "equipment": ["high_clearance_vehicle"],
            "last_checkin": "2025-07-14T09:05:00+05:30",
            "ward_proximity": {"W12": 5, "W07": 18, "W04": 22, "W19": 40},
        },
        {
            "team_id": "MED-1",
            "agency": "Medical",
            "crew_count": 4,
            "status": "AVAILABLE",
            "current_location": "District Hospital",
            "equipment": ["medical_kit"],
            "last_checkin": "2025-07-14T08:55:00+05:30",
            "ward_proximity": {"W12": 12, "W07": 10, "W04": 20, "W19": 45},
        },
        {
            "team_id": "MED-2",
            "agency": "Medical",
            "crew_count": 4,
            "status": "STANDBY",
            "current_location": "District Hospital",
            "equipment": ["medical_kit"],
            "last_checkin": "2025-07-14T09:00:00+05:30",
            "ward_proximity": {"W12": 14, "W07": 10, "W04": 22, "W19": 45},
        },
        {
            "team_id": "DRAIN-1",
            "agency": "Municipal Drainage",
            "crew_count": 5,
            "status": "OPERATING",
            "current_location": "Ward 12 — Drain D-17",
            "equipment": ["pump"],
            "last_checkin": "2025-07-14T09:10:00+05:30",
            "ward_proximity": {"W12": 3, "W07": 20, "W04": 25, "W19": 50},
        },
        {
            "team_id": "DRAIN-2",
            "agency": "Municipal Drainage",
            "crew_count": 5,
            "status": "AVAILABLE",
            "current_location": "Municipal Depot East",
            "equipment": ["pump", "high_clearance_vehicle"],
            "last_checkin": "2025-07-14T08:40:00+05:30",
            "ward_proximity": {"W12": 15, "W07": 18, "W04": 12, "W19": 35},
        },
        {
            "team_id": "NGO-RC",
            "agency": "NGO Red Cross",
            "crew_count": 10,
            "status": "AVAILABLE",
            "current_location": "NGO Warehouse",
            "equipment": ["medical_kit", "rescue_kit"],
            "last_checkin": "2025-07-14T09:00:00+05:30",
            "ward_proximity": {"W12": 18, "W07": 15, "W04": 25, "W19": 28},
        },
    ]


def _build_routes() -> list:
    """Return current status of all routes used during the active flood event."""
    return [
        {
            "route_id": "RT-A",
            "name": "NH Route A",
            "status": "BLOCKED",
            "last_updated": "2025-07-14T08:15:00+05:30",
            "passable_by": [],
            "notes": "Underpass flooded — water 1.2 m deep. Impassable for all vehicles.",
            "serves_wards": ["W12"],
        },
        {
            "route_id": "RT-B",
            "name": "Inner Bypass B",
            "status": "AT_RISK",
            "last_updated": "2025-07-14T08:45:00+05:30",
            "passable_by": ["high_clearance"],
            "notes": "Ankle-deep waterlogging in two sections. High clearance only. Rapidly deteriorating.",
            "serves_wards": ["W12", "W07"],
        },
        {
            "route_id": "RT-C",
            "name": "Elevated Road C",
            "status": "OPEN",
            "last_updated": "2025-07-14T09:00:00+05:30",
            "passable_by": ["high_clearance", "standard_vehicle", "ambulance", "foot"],
            "notes": "Designated alternate for Route A. Clear and passable for all vehicles.",
            "serves_wards": ["W12"],
        },
        {
            "route_id": "RT-D",
            "name": "Flyover Route D",
            "status": "OPEN",
            "last_updated": "2025-07-14T08:50:00+05:30",
            "passable_by": ["high_clearance", "standard_vehicle", "ambulance", "foot"],
            "notes": "Open and clear. Best route for Ward 7 access.",
            "serves_wards": ["W07"],
        },
        {
            "route_id": "RT-E",
            "name": "Industrial Road E",
            "status": "OPEN",
            "last_updated": "2025-07-14T08:30:00+05:30",
            "passable_by": ["high_clearance", "standard_vehicle", "ambulance", "foot"],
            "notes": "Open. Elevated road, unaffected by current flooding.",
            "serves_wards": ["W04"],
        },
        {
            "route_id": "RT-F",
            "name": "Wetland Road F (W19 single access)",
            "status": "BLOCKED",
            "last_updated": "2025-07-14T07:30:00+05:30",
            "passable_by": ["boat"],
            "notes": "Only access road to Ward 19 is completely submerged. Boat deployment mandatory.",
            "serves_wards": ["W19"],
        },
    ]


def _get_safest_route_for_ward(incident_ward: str, routes: list) -> dict:
    """Return the safest available route serving the given ward."""
    STATUS_ORDER = {"OPEN": 0, "AT_RISK": 1, "LIKELY_BLOCKED": 2, "BLOCKED": 3}
    ward_routes = [r for r in routes if incident_ward in r.get("serves_wards", [])]
    if not ward_routes:
        return {
            "route_id": "UNKNOWN",
            "name": "No route data for this ward",
            "status": "UNKNOWN",
            "passable_by": [],
            "notes": "",
        }
    ward_routes.sort(key=lambda r: STATUS_ORDER.get(r["status"], 9))
    return ward_routes[0]


# ---------------------------------------------------------------------------
# Tool 1 — get_responder_roster
# ---------------------------------------------------------------------------

def get_responder_roster() -> dict:
    """
    Retrieve the full roster of all responder teams across agencies.
    Returns 10 teams: Fire (2), SDRF (1), Police (2), Medical (2),
    Municipal Drainage (2), NGO Red Cross (1). Each team includes
    team_id, agency, crew_count, status, current_location, equipment list,
    last_checkin, and ward_proximity dict {ward_id: eta_minutes}.

    Returns:
        dict: fetched_at timestamp, total_teams count, and teams list.
    """
    teams = _build_roster()
    # Summarise availability counts for quick overview
    by_status: dict = {}
    for t in teams:
        by_status[t["status"]] = by_status.get(t["status"], 0) + 1

    return {
        "fetched_at": datetime.now().isoformat(),
        "total_teams": len(teams),
        "availability_summary": by_status,
        "teams": teams,
    }


# ---------------------------------------------------------------------------
# Tool 2 — get_route_status
# ---------------------------------------------------------------------------

def get_route_status() -> dict:
    """
    Retrieve current operational status of all evacuation and access routes.
    Includes Route A (BLOCKED — W12 primary), Route C (OPEN — W12 alternate),
    Route F W19 (BLOCKED — boat only), and Route D W7 (OPEN).

    Returns:
        dict: fetched_at timestamp, total_routes count, and routes list.
              Each route has route_id, name, status (OPEN/AT_RISK/
              LIKELY_BLOCKED/BLOCKED), last_updated, passable_by list,
              notes, and serves_wards list.
    """
    routes = _build_routes()
    by_status: dict = {}
    for r in routes:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    return {
        "fetched_at": datetime.now().isoformat(),
        "total_routes": len(routes),
        "status_summary": by_status,
        "routes": routes,
    }


# ---------------------------------------------------------------------------
# Tool 3 — score_team_incident_match
# ---------------------------------------------------------------------------

def score_team_incident_match(
    team_id: str,
    incident_priority: str,
    incident_type: str,
    incident_ward: str,
    affected_count: int,
) -> dict:
    """
    Score a specific responder team for a specific incident using a four-factor
    weighted composite model.

    Scoring components:
      availability_score: AVAILABLE=1.0, STANDBY=0.8, EN_ROUTE=0.3,
                          OPERATING=0.1, NEEDS_ASSISTANCE=0.0
      proximity_score:    max(0, 1 - eta_minutes/60)  [from ward_proximity dict]
      equipment_match:    1.0 if team carries required equipment, 0.0 otherwise.
                          Requirements by incident type:
                            trapped_residents     → rescue_kit OR rescue_boat
                            drainage_failure      → pump
                            critical_asset_at_risk → medical_kit OR rescue_kit
                            route_blockage        → high_clearance_vehicle OR pump
      workload_score:     AVAILABLE=1.0, STANDBY=0.9, EN_ROUTE=0.5,
                          OPERATING=0.2, NEEDS_ASSISTANCE=0.0

    composite = 0.35*availability + 0.25*proximity + 0.25*equipment + 0.15*workload

    A route penalty applies when the only access to incident_ward is BLOCKED
    and the team lacks the required mode (e.g. boat for W19).

    Args:
        team_id:            Unique team identifier.
        incident_priority:  CRITICAL / HIGH / MEDIUM / LOW.
        incident_type:      trapped_residents / drainage_failure /
                            critical_asset_at_risk / route_blockage.
        incident_ward:      Target ward ID (W12, W19, W07, W04).
        affected_count:     Estimated number of people affected.

    Returns:
        dict: team_id, agency, all four component scores, composite_score,
              recommended_route, eta_minutes, rationale, scored_at.
    """
    roster = _build_roster()
    routes = _build_routes()

    team = next((t for t in roster if t["team_id"] == team_id), None)
    if team is None:
        return {
            "team_id": team_id,
            "error": f"Team {team_id} not found in roster.",
            "composite_score": 0.0,
            "availability_score": 0.0,
            "proximity_score": 0.0,
            "equipment_match_score": 0.0,
            "workload_score": 0.0,
            "recommended_route": "N/A",
            "eta_minutes": 999,
            "rationale": f"Team {team_id} not found.",
            "scored_at": datetime.now().isoformat(),
        }

    # ---- Availability score ------------------------------------------------
    avail_map = {
        "AVAILABLE": 1.0,
        "STANDBY": 0.8,
        "EN_ROUTE": 0.3,
        "OPERATING": 0.1,
        "NEEDS_ASSISTANCE": 0.0,
    }
    availability_score = avail_map.get(team["status"], 0.0)

    # ---- Workload score ----------------------------------------------------
    workload_map = {
        "AVAILABLE": 1.0,
        "STANDBY": 0.9,
        "EN_ROUTE": 0.5,
        "OPERATING": 0.2,
        "NEEDS_ASSISTANCE": 0.0,
    }
    workload_score = workload_map.get(team["status"], 0.0)

    # ---- Proximity score ---------------------------------------------------
    ward_proximity = team.get("ward_proximity", {})
    eta_minutes = ward_proximity.get(incident_ward, 60)
    proximity_score = max(0.0, 1.0 - eta_minutes / 60.0)

    # ---- Equipment match score ---------------------------------------------
    # Each incident type needs ANY ONE item from its required list
    EQUIPMENT_REQS = {
        "trapped_residents": ["rescue_kit", "rescue_boat"],
        "drainage_failure": ["pump"],
        "critical_asset_at_risk": ["medical_kit", "rescue_kit"],
        "route_blockage": ["high_clearance_vehicle", "pump"],
    }
    team_equip = set(team.get("equipment", []))
    required_options = EQUIPMENT_REQS.get(incident_type, [])

    if not required_options:
        equipment_match_score = 0.5  # Unknown type — partial credit
    elif any(e in team_equip for e in required_options):
        equipment_match_score = 1.0
    else:
        equipment_match_score = 0.0

    # ---- Composite (pre-route-penalty) ------------------------------------
    composite_raw = (
        0.35 * availability_score
        + 0.25 * proximity_score
        + 0.25 * equipment_match_score
        + 0.15 * workload_score
    )

    # ---- Route analysis and penalty ----------------------------------------
    best_route = _get_safest_route_for_ward(incident_ward, routes)
    route_id = best_route.get("route_id", "UNKNOWN")
    route_name = best_route.get("name", "Unknown route")
    route_status = best_route.get("status", "UNKNOWN")
    passable_by = best_route.get("passable_by", [])
    route_notes = best_route.get("notes", "")

    route_penalty = 1.0
    route_note = f"{route_name} — {route_status}"

    if route_status == "BLOCKED":
        if "boat" in passable_by:
            # Boat-only access (e.g. W19)
            if "rescue_boat" in team_equip:
                route_note = f"{route_name} — BLOCKED (boat only). Team has rescue_boat — can access."
            else:
                route_note = (
                    f"{route_name} — BLOCKED (boat only). "
                    "Team lacks rescue_boat — significantly reduced effectiveness."
                )
                route_penalty = 0.35
        else:
            # Completely impassable
            route_note = f"{route_name} — BLOCKED. No viable access mode for this team."
            route_penalty = 0.15
    elif route_status == "AT_RISK":
        if "high_clearance_vehicle" in team_equip or "rescue_boat" in team_equip:
            route_note = f"{route_name} — AT_RISK but team equipment suitable. Proceed with caution."
        else:
            route_note = f"{route_name} — AT_RISK. Standard-vehicle teams may not pass."
            route_penalty = 0.75

    composite_score = round(composite_raw * route_penalty, 4)

    # ---- Rationale string --------------------------------------------------
    rationale = (
        f"Status={team['status']} (avail={availability_score}, workload={workload_score}) | "
        f"ETA to {incident_ward}={eta_minutes}min (proximity={round(proximity_score, 2)}) | "
        f"Equipment={list(team_equip)} — match for '{incident_type}'={equipment_match_score} | "
        f"Route: {route_note}"
    )
    if route_penalty < 1.0:
        rationale += f" | Route penalty applied: ×{route_penalty}"

    return {
        "team_id": team_id,
        "agency": team["agency"],
        "composite_score": composite_score,
        "availability_score": availability_score,
        "proximity_score": round(proximity_score, 4),
        "equipment_match_score": equipment_match_score,
        "workload_score": workload_score,
        "recommended_route": route_note,
        "recommended_route_id": route_id,
        "eta_minutes": eta_minutes,
        "rationale": rationale,
        "scored_at": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Tool 4 — recommend_dispatch
# ---------------------------------------------------------------------------

def recommend_dispatch(
    incident_id: str,
    incident_priority: str,
    incident_type: str,
    incident_ward: str,
    affected_count: int,
) -> dict:
    """
    Generate a ranked dispatch recommendation for a specific incident by
    calling score_team_incident_match for EVERY team in the roster, then
    ranking by composite score.

    Primary recommendation: highest-scoring team.
    Secondary recommendation: second-highest-scoring team.
    Resource gap: flagged if no team scores above 0.4 — triggers escalation.

    Status is always "AWAITING_COMMANDER_APPROVAL" — autonomous dispatch
    is never performed.

    Args:
        incident_id:       Unique incident identifier (e.g. "INC-007").
        incident_priority: CRITICAL / HIGH / MEDIUM / LOW.
        incident_type:     trapped_residents / drainage_failure /
                           critical_asset_at_risk / route_blockage.
        incident_ward:     Target ward ID (W12, W19, W07, W04).
        affected_count:    Estimated number of people affected.

    Returns:
        dict: incident details, primary_recommendation, secondary_recommendation,
              all_team_scores (ranked), resource_gap_flagged, gap_description,
              escalation_needed, commander_action_required, status, generated_at.
    """
    roster = _build_roster()
    GAP_THRESHOLD = 0.4

    # Score ALL teams
    all_scores = []
    for team in roster:
        result = score_team_incident_match(
            team_id=team["team_id"],
            incident_priority=incident_priority,
            incident_type=incident_type,
            incident_ward=incident_ward,
            affected_count=affected_count,
        )
        # Attach current status for the summary table
        result["current_status"] = team["status"]
        all_scores.append(result)

    # Sort by composite_score descending; ties broken by team_id for determinism
    all_scores.sort(key=lambda s: (-s.get("composite_score", 0.0), s["team_id"]))

    # Separate viable teams (score > 0)
    viable = [s for s in all_scores if s.get("composite_score", 0.0) > 0.0]
    primary_raw = viable[0] if len(viable) >= 1 else None
    secondary_raw = viable[1] if len(viable) >= 2 else None

    def _build_rec(score: dict) -> dict:
        if score is None:
            return None
        return {
            "team_id": score["team_id"],
            "agency": score["agency"],
            "composite_score": score["composite_score"],
            "availability_score": score["availability_score"],
            "proximity_score": score["proximity_score"],
            "equipment_match_score": score["equipment_match_score"],
            "workload_score": score["workload_score"],
            "recommended_route": score["recommended_route"],
            "eta_minutes": score["eta_minutes"],
            "rationale": score["rationale"],
        }

    primary = _build_rec(primary_raw)
    secondary = _build_rec(secondary_raw)

    # Resource gap assessment
    resource_gap_flagged = (primary is None or primary["composite_score"] <= GAP_THRESHOLD)
    escalation_needed = resource_gap_flagged

    if primary is None:
        gap_description = (
            f"No team available for '{incident_type}' at {incident_ward}. "
            "Immediate state-level resource request required — contact SDMA."
        )
    elif primary["composite_score"] <= GAP_THRESHOLD:
        gap_description = (
            f"Best available team ({primary['team_id']}) scores only "
            f"{primary['composite_score']:.3f} — below acceptable threshold of {GAP_THRESHOLD}. "
            f"Likely cause: inadequate equipment or blocked route access to {incident_ward}. "
            "Recommend requesting dedicated resources from SDMA immediately."
        )
    else:
        gap_description = ""

    return {
        "incident_id": incident_id,
        "incident_priority": incident_priority,
        "incident_type": incident_type,
        "incident_ward": incident_ward,
        "affected_count": affected_count,
        "status": "AWAITING_COMMANDER_APPROVAL",
        "primary_recommendation": primary,
        "secondary_recommendation": secondary,
        "all_team_scores": [
            {
                "rank": i + 1,
                "team_id": s["team_id"],
                "agency": s["agency"],
                "current_status": s["current_status"],
                "composite_score": s["composite_score"],
                "equipment_match_score": s["equipment_match_score"],
                "eta_minutes": s["eta_minutes"],
            }
            for i, s in enumerate(all_scores)
        ],
        "resource_gap_flagged": resource_gap_flagged,
        "gap_description": gap_description,
        "escalation_needed": escalation_needed,
        "commander_action_required": True,
        "generated_at": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Tool 5 — get_current_resource_inventory
# ---------------------------------------------------------------------------

def get_current_resource_inventory() -> dict:
    """
    Return the current status of all critical response resources in the
    district inventory, with available vs. total counts, worst-case demand
    scenario, and gap severity classification.

    Returns:
        dict: fetched_at, per-resource breakdown (available, in_use, total,
              worst_case_demand, gap, gap_severity, notes), high_level_summary,
              and escalation_recommendation.
    """
    return {
        "fetched_at": datetime.now().isoformat(),
        "inventory": {
            "pumps": {
                "available": 3,
                "in_use": 2,
                "total": 5,
                "worst_case_demand": 8,
                "gap": 5,
                "gap_severity": "HIGH",
                "notes": (
                    "2 pumps active at D-17 (W12) and D-22 (W19). "
                    "Worst-case simultaneous drainage at W12+W19+W07 requires 8."
                ),
            },
            "rescue_boats": {
                "available": 1,
                "in_use": 0,
                "total": 1,
                "worst_case_demand": 3,
                "gap": 2,
                "gap_severity": "CRITICAL",
                "notes": (
                    "Only 1 rescue boat in the entire district. "
                    "Ward 19 is completely road-inaccessible — boat is mandatory. "
                    "Need minimum 2 additional from SDMA urgently."
                ),
            },
            "shelter_beds": {
                "available": 1750,
                "in_use": 0,
                "total": 1750,
                "worst_case_demand": 3500,
                "gap": 1750,
                "gap_severity": "HIGH",
                "notes": (
                    "Current capacity covers ~1,750 displaced persons. "
                    "Full evacuation of W12 + W19 could displace up to 45,000 at-risk residents."
                ),
            },
            "water_tankers": {
                "available": 3,
                "in_use": 0,
                "total": 3,
                "worst_case_demand": 5,
                "gap": 2,
                "gap_severity": "MEDIUM",
                "notes": (
                    "W19 borewell water point is flood-vulnerable. "
                    "2 extra tankers needed as backup potable water source."
                ),
            },
            "food_kits": {
                "available": 400,
                "in_use": 0,
                "total": 400,
                "worst_case_demand": 1200,
                "gap": 800,
                "gap_severity": "HIGH",
                "notes": (
                    "Sufficient for ~400 persons for 3 days. "
                    "Worst-case multi-ward displacement scenario requires 1,200."
                ),
            },
            "medical_kits": {
                "available": 8,
                "in_use": 2,
                "total": 10,
                "worst_case_demand": 12,
                "gap": 4,
                "gap_severity": "MEDIUM",
                "notes": (
                    "2 kits deployed with active medical teams. "
                    "4 additional needed for simultaneous multi-ward response."
                ),
            },
        },
        "high_level_summary": (
            "CRITICAL GAP: Only 1 rescue boat district-wide — Ward 19 road-inaccessible, "
            "boat mandatory for any W19 response. "
            "HIGH GAPS: Pumps (need 5 more), shelter beds (need 1,750 more), food kits (need 800 more). "
            "MEDIUM GAPS: Water tankers (need 2 more), medical kits (need 4 more)."
        ),
        "escalation_recommendation": (
            "Recommend immediate escalation to SDMA for: "
            "(1) 2 additional rescue boats with crew for Ward 19, "
            "(2) 3 additional pumps for simultaneous drainage operations, "
            "(3) pre-positioning of 1,000 emergency food kits at district staging area."
        ),
    }
