"""
Tools for the Reconciliation Agent.

Each function is a standalone tool the ADK agent calls. Tools implement real
computational logic: incident log retrieval, deployment record loading,
response-time metric computation with per-incident rating, deployment-to-
incident matching with gap detection, and structured AAR draft generation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_ts(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp string to an aware datetime."""
    # Replace +05:30 with %z-compatible form
    return datetime.fromisoformat(ts)


def _response_minutes(reported: str, first_response: str) -> int:
    """Return elapsed minutes between two ISO-8601 timestamps."""
    t0 = _parse_ts(reported)
    t1 = _parse_ts(first_response)
    delta = t1 - t0
    return max(0, int(delta.total_seconds() / 60))


def _rate_response(minutes: int) -> str:
    """Map response time in minutes to a rating string."""
    if minutes < 15:
        return "EXCELLENT"
    if minutes < 30:
        return "GOOD"
    if minutes <= 60:
        return "ACCEPTABLE"
    return "DELAYED"


# ---------------------------------------------------------------------------
# Tool 1 — get_incident_log
# ---------------------------------------------------------------------------

def get_incident_log() -> dict:
    """
    Retrieve the 12 incidents logged during the flood event across wards
    W12, W19, W07, and W04. Incidents span the full lifecycle: RESOLVED,
    ESCALATED, and one ACTIVE (still open). Two incidents have response
    times exceeding 90 minutes.

    Each incident record: incident_id, ward_id, type, severity, time_reported,
    time_first_response (or null), time_resolved (or null), teams_assigned
    (list), status.

    Returns:
        dict: fetched_at, total, status_counts, and incidents list.
    """
    incidents: List[Dict[str, Any]] = [
        {
            "incident_id": "INC-001",
            "ward_id": "W12",
            "type": "STRUCTURAL_COLLAPSE",
            "severity": "CRITICAL",
            "time_reported": "2025-07-14T06:00:00+05:30",
            "time_first_response": "2025-07-14T06:12:00+05:30",
            "time_resolved": "2025-07-14T09:00:00+05:30",
            "teams_assigned": ["NDRF-T1"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-002",
            "ward_id": "W19",
            "type": "FLOOD_EVACUATION",
            "severity": "CRITICAL",
            "time_reported": "2025-07-14T05:45:00+05:30",
            "time_first_response": "2025-07-14T06:30:00+05:30",
            "time_resolved": "2025-07-14T14:00:00+05:30",
            "teams_assigned": ["SDRF-B2", "NDRF-T3"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-003",
            "ward_id": "W12",
            "type": "DRAINAGE_FAILURE",
            "severity": "HIGH",
            "time_reported": "2025-07-14T06:30:00+05:30",
            "time_first_response": "2025-07-14T06:52:00+05:30",
            "time_resolved": "2025-07-14T10:00:00+05:30",
            "teams_assigned": ["MFD-P2"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-004",
            "ward_id": "W07",
            "type": "URBAN_FLOODING",
            "severity": "MEDIUM",
            "time_reported": "2025-07-14T07:00:00+05:30",
            "time_first_response": "2025-07-14T07:18:00+05:30",
            "time_resolved": "2025-07-14T11:30:00+05:30",
            "teams_assigned": ["MFD-P4"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-005",
            "ward_id": "W19",
            "type": "MEDICAL_EMERGENCY",
            "severity": "HIGH",
            "time_reported": "2025-07-14T06:00:00+05:30",
            "time_first_response": "2025-07-14T07:35:00+05:30",
            "time_resolved": "2025-07-14T11:00:00+05:30",
            "teams_assigned": ["MED-T1"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-006",
            "ward_id": "W12",
            "type": "ROUTE_BLOCKAGE",
            "severity": "CRITICAL",
            "time_reported": "2025-07-14T07:00:00+05:30",
            "time_first_response": "2025-07-14T07:08:00+05:30",
            "time_resolved": "2025-07-14T08:30:00+05:30",
            "teams_assigned": ["MFD-E1"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-007",
            "ward_id": "W04",
            "type": "MINOR_FLOODING",
            "severity": "LOW",
            "time_reported": "2025-07-14T08:00:00+05:30",
            "time_first_response": "2025-07-14T08:35:00+05:30",
            "time_resolved": "2025-07-14T10:00:00+05:30",
            "teams_assigned": ["MFD-P3"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-008",
            "ward_id": "W19",
            "type": "SHELTER_OVERFLOW",
            "severity": "HIGH",
            "time_reported": "2025-07-14T07:30:00+05:30",
            "time_first_response": "2025-07-14T09:30:00+05:30",
            "time_resolved": None,
            "teams_assigned": ["DDMA-L2"],
            "status": "ESCALATED",
        },
        {
            "incident_id": "INC-009",
            "ward_id": "W12",
            "type": "TRAPPED_RESIDENTS",
            "severity": "CRITICAL",
            "time_reported": "2025-07-14T09:00:00+05:30",
            "time_first_response": "2025-07-14T09:25:00+05:30",
            "time_resolved": "2025-07-14T12:00:00+05:30",
            "teams_assigned": ["NDRF-T1", "MED-T1"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-010",
            "ward_id": "W07",
            "type": "INFRASTRUCTURE_DAMAGE",
            "severity": "MEDIUM",
            "time_reported": "2025-07-14T09:30:00+05:30",
            "time_first_response": "2025-07-14T10:10:00+05:30",
            "time_resolved": "2025-07-14T16:00:00+05:30",
            "teams_assigned": ["PWD-T1"],
            "status": "RESOLVED",
        },
        {
            "incident_id": "INC-011",
            "ward_id": "W19",
            "type": "WATER_CONTAMINATION",
            "severity": "HIGH",
            "time_reported": "2025-07-14T10:00:00+05:30",
            "time_first_response": "2025-07-14T11:00:00+05:30",
            "time_resolved": None,
            "teams_assigned": ["DDMA-L2", "MED-T2"],
            "status": "ESCALATED",
        },
        {
            "incident_id": "INC-012",
            "ward_id": "W12",
            "type": "RELIEF_GAP",
            "severity": "MEDIUM",
            "time_reported": "2025-07-14T11:00:00+05:30",
            "time_first_response": None,
            "time_resolved": None,
            "teams_assigned": [],
            "status": "ACTIVE",
        },
    ]

    status_counts: Dict[str, int] = {}
    for inc in incidents:
        status_counts[inc["status"]] = status_counts.get(inc["status"], 0) + 1

    return {
        "fetched_at": datetime.now().isoformat(),
        "event_id": "FL-2025-07-14",
        "total_incidents": len(incidents),
        "status_counts": status_counts,
        "incidents": incidents,
    }


# ---------------------------------------------------------------------------
# Tool 2 — get_resource_deployment_log
# ---------------------------------------------------------------------------

def get_resource_deployment_log() -> dict:
    """
    Retrieve 10 resource deployment records logged during the event.
    Two deployments have no incident_id_assigned (unmatched — potential
    recording gaps). All others are matched to logged incidents.

    Each record: deployment_id, team_id, agency, dispatched_at, arrived_at,
    departed_at, incident_id_assigned (may be null), ward_id, task_performed,
    outcome.

    Returns:
        dict: fetched_at, total, matched_count, unmatched_count, deployments list.
    """
    deployments: List[Dict[str, Any]] = [
        {
            "deployment_id": "DEP-001",
            "team_id": "NDRF-T1",
            "agency": "NDRF",
            "dispatched_at": "2025-07-14T06:05:00+05:30",
            "arrived_at": "2025-07-14T06:12:00+05:30",
            "departed_at": "2025-07-14T09:15:00+05:30",
            "incident_id_assigned": "INC-001",
            "ward_id": "W12",
            "task_performed": "Structural assessment and resident evacuation",
            "outcome": "2 unsafe buildings cordoned; 18 residents evacuated safely",
        },
        {
            "deployment_id": "DEP-002",
            "team_id": "SDRF-B2",
            "agency": "SDRF",
            "dispatched_at": "2025-07-14T05:50:00+05:30",
            "arrived_at": "2025-07-14T06:30:00+05:30",
            "departed_at": "2025-07-14T14:30:00+05:30",
            "incident_id_assigned": "INC-002",
            "ward_id": "W19",
            "task_performed": "Boat-assisted flood evacuation from North Wetlands",
            "outcome": "340 residents evacuated to SH-F and adjacent wards",
        },
        {
            "deployment_id": "DEP-003",
            "team_id": "MFD-P2",
            "agency": "Municipal Fire Department",
            "dispatched_at": "2025-07-14T06:40:00+05:30",
            "arrived_at": "2025-07-14T06:52:00+05:30",
            "departed_at": "2025-07-14T10:10:00+05:30",
            "incident_id_assigned": "INC-003",
            "ward_id": "W12",
            "task_performed": "Pump deployment at Drain D-17; debris removal",
            "outcome": "D-17 flow restored; waterlogging reduced by 60% within 3h",
        },
        {
            "deployment_id": "DEP-004",
            "team_id": "MFD-P4",
            "agency": "Municipal Fire Department",
            "dispatched_at": "2025-07-14T07:10:00+05:30",
            "arrived_at": "2025-07-14T07:18:00+05:30",
            "departed_at": "2025-07-14T11:45:00+05:30",
            "incident_id_assigned": "INC-004",
            "ward_id": "W07",
            "task_performed": "Pump deployment near D-09; road drainage clearance",
            "outcome": "Urban flooding cleared; Flyover Route D unaffected throughout",
        },
        {
            "deployment_id": "DEP-005",
            "team_id": "MFD-E1",
            "agency": "Municipal Fire Department",
            "dispatched_at": "2025-07-14T07:02:00+05:30",
            "arrived_at": "2025-07-14T07:08:00+05:30",
            "departed_at": "2025-07-14T08:45:00+05:30",
            "incident_id_assigned": "INC-006",
            "ward_id": "W12",
            "task_performed": "Route A closure management; barricade placement",
            "outcome": "Route A officially closed; traffic redirected to Route C",
        },
        {
            "deployment_id": "DEP-006",
            "team_id": "MFD-P3",
            "agency": "Municipal Fire Department",
            "dispatched_at": "2025-07-14T08:10:00+05:30",
            "arrived_at": "2025-07-14T08:35:00+05:30",
            "departed_at": "2025-07-14T10:15:00+05:30",
            "incident_id_assigned": "INC-007",
            "ward_id": "W04",
            "task_performed": "Minor flood pump deployment; D-03 check",
            "outcome": "Residential boundary zone cleared; D-03 confirmed operational",
        },
        {
            "deployment_id": "DEP-007",
            "team_id": "NDRF-T1",
            "agency": "NDRF",
            "dispatched_at": "2025-07-14T09:10:00+05:30",
            "arrived_at": "2025-07-14T09:25:00+05:30",
            "departed_at": "2025-07-14T12:20:00+05:30",
            "incident_id_assigned": "INC-009",
            "ward_id": "W12",
            "task_performed": "Trapped resident rescue near Sector 12 drain junction",
            "outcome": "4 residents including 2 elderly rescued; handed to MED-T1",
        },
        {
            "deployment_id": "DEP-008",
            "team_id": "PWD-T1",
            "agency": "Public Works Department",
            "dispatched_at": "2025-07-14T09:45:00+05:30",
            "arrived_at": "2025-07-14T10:10:00+05:30",
            "departed_at": "2025-07-14T16:30:00+05:30",
            "incident_id_assigned": "INC-010",
            "ward_id": "W07",
            "task_performed": "Road section emergency repair near D-09 junction",
            "outcome": "2 road sections stabilised with temporary fill; permanent repair scheduled",
        },
        {
            "deployment_id": "DEP-009",
            "team_id": "SDRF-A1",
            "agency": "SDRF",
            "dispatched_at": "2025-07-14T08:00:00+05:30",
            "arrived_at": "2025-07-14T08:30:00+05:30",
            "departed_at": "2025-07-14T11:00:00+05:30",
            "incident_id_assigned": None,
            "ward_id": "W19",
            "task_performed": "General area patrol and welfare check in North Wetlands",
            "outcome": "Patrol completed; no specific incident logged against this deployment",
        },
        {
            "deployment_id": "DEP-010",
            "team_id": "MED-T2",
            "agency": "District Medical Services",
            "dispatched_at": "2025-07-14T10:30:00+05:30",
            "arrived_at": "2025-07-14T11:05:00+05:30",
            "departed_at": "2025-07-14T14:00:00+05:30",
            "incident_id_assigned": None,
            "ward_id": "W12",
            "task_performed": "Medical camp setup at Shelter SH-B; general health screening",
            "outcome": "47 residents screened; 5 referred to PHC; no incident ID assigned at dispatch",
        },
    ]

    matched = sum(1 for d in deployments if d["incident_id_assigned"] is not None)
    unmatched = len(deployments) - matched

    return {
        "fetched_at": datetime.now().isoformat(),
        "event_id": "FL-2025-07-14",
        "total_deployments": len(deployments),
        "matched_count": matched,
        "unmatched_count": unmatched,
        "deployments": deployments,
    }


# ---------------------------------------------------------------------------
# Tool 3 — compute_response_time_metrics
# ---------------------------------------------------------------------------

def compute_response_time_metrics(incident_ids: List[str]) -> dict:
    """
    Compute response-time metrics for incidents that have both time_reported
    and time_first_response logged. Filters the incident log to the requested
    incident_ids (processes all incidents if the list is empty).

    Per-incident:
    - response_time_minutes: elapsed minutes from reported to first response.
    - rating: EXCELLENT < 15 min; GOOD 15–29 min; ACCEPTABLE 30–60 min;
              DELAYED > 60 min.

    Aggregate:
    - avg_response_time_minutes (rounded to 1 decimal)
    - fastest_response: {incident_id, minutes, rating}
    - slowest_response: {incident_id, minutes, rating}
    - pct_within_60_min: percentage of processed incidents within 60 min
    - incidents_with_delayed_response: list of IDs rated DELAYED

    Args:
        incident_ids: List of incident IDs to process. Pass [] to process all
                      incidents that have both timestamps populated.

    Returns:
        dict: per_incident_metrics list and aggregate_metrics dict.
    """
    log = get_incident_log()
    all_incidents = log["incidents"]

    # Filter to requested IDs (or all if empty list)
    if incident_ids:
        candidates = [i for i in all_incidents if i["incident_id"] in incident_ids]
    else:
        candidates = all_incidents

    # Only process incidents with both timestamps
    processable = [
        i for i in candidates
        if i["time_reported"] and i["time_first_response"]
    ]

    per_incident: List[Dict[str, Any]] = []
    for inc in processable:
        mins = _response_minutes(inc["time_reported"], inc["time_first_response"])
        rating = _rate_response(mins)
        per_incident.append({
            "incident_id": inc["incident_id"],
            "ward_id": inc["ward_id"],
            "type": inc["type"],
            "severity": inc["severity"],
            "response_time_minutes": mins,
            "rating": rating,
            "status": inc["status"],
            "teams_assigned": inc["teams_assigned"],
        })

    skipped = [
        i["incident_id"] for i in candidates
        if not (i["time_reported"] and i["time_first_response"])
    ]

    if not per_incident:
        return {
            "per_incident_metrics": [],
            "skipped_no_timestamps": skipped,
            "aggregate_metrics": {
                "note": "No incidents with both timestamps found in the requested set."
            },
        }

    times = [r["response_time_minutes"] for r in per_incident]
    avg_time = round(sum(times) / len(times), 1)
    fastest = min(per_incident, key=lambda x: x["response_time_minutes"])
    slowest = max(per_incident, key=lambda x: x["response_time_minutes"])
    within_60 = sum(1 for t in times if t <= 60)
    pct_within_60 = round(within_60 / len(times) * 100, 1)
    delayed = [r["incident_id"] for r in per_incident if r["rating"] == "DELAYED"]

    return {
        "per_incident_metrics": per_incident,
        "skipped_no_timestamps": skipped,
        "aggregate_metrics": {
            "incidents_evaluated": len(per_incident),
            "avg_response_time_minutes": avg_time,
            "fastest_response": {
                "incident_id": fastest["incident_id"],
                "minutes": fastest["response_time_minutes"],
                "rating": fastest["rating"],
            },
            "slowest_response": {
                "incident_id": slowest["incident_id"],
                "minutes": slowest["response_time_minutes"],
                "rating": slowest["rating"],
            },
            "pct_within_60_min": pct_within_60,
            "incidents_with_delayed_response": delayed,
            "rating_breakdown": {
                "EXCELLENT": sum(1 for r in per_incident if r["rating"] == "EXCELLENT"),
                "GOOD": sum(1 for r in per_incident if r["rating"] == "GOOD"),
                "ACCEPTABLE": sum(1 for r in per_incident if r["rating"] == "ACCEPTABLE"),
                "DELAYED": len(delayed),
            },
        },
    }


# ---------------------------------------------------------------------------
# Tool 4 — reconcile_deployments_to_incidents
# ---------------------------------------------------------------------------

def reconcile_deployments_to_incidents() -> dict:
    """
    Match deployment records to logged incidents via incident_id_assigned.
    Identifies unmatched deployments (no incident ID) and unmatched incidents
    (no time_first_response recorded), flagging both as recording or coverage
    gaps.

    Matching logic:
    - Build a lookup {incident_id_assigned: deployment} from deployments where
      incident_id_assigned is not null.
    - For each incident in the log, check if it appears in the lookup.
    - matched: incident appears in deployment lookup.
    - unmatched_incidents: incident time_first_response is null — no deployment
      recorded, or incident has no matching deployment entry.
    - unmatched_deployments: deployment records where incident_id_assigned is null.

    match_rate_pct = len(matched) / total_incidents * 100

    Returns:
        dict: matched list, unmatched_deployments list, unmatched_incidents list,
              match_rate_pct, summary counts.
    """
    incident_log = get_incident_log()
    deployment_log = get_resource_deployment_log()

    incidents = incident_log["incidents"]
    deployments = deployment_log["deployments"]

    # Build lookup: incident_id → deployment record (for matched deployments)
    deployment_by_incident: Dict[str, Dict[str, Any]] = {
        d["incident_id_assigned"]: d
        for d in deployments
        if d["incident_id_assigned"] is not None
    }

    matched: List[Dict[str, Any]] = []
    unmatched_incidents: List[Dict[str, Any]] = []

    for inc in incidents:
        iid = inc["incident_id"]
        dep = deployment_by_incident.get(iid)

        if dep is not None:
            matched.append({
                "incident_id": iid,
                "ward_id": inc["ward_id"],
                "type": inc["type"],
                "severity": inc["severity"],
                "deployment_id": dep["deployment_id"],
                "team": dep["team_id"],
                "agency": dep["agency"],
                "outcome": dep["outcome"],
                "incident_status": inc["status"],
            })
        else:
            # Determine the type of gap
            if inc["time_first_response"] is None:
                flag = "No deployment recorded — coverage gap or recording failure"
            else:
                flag = (
                    "Incident has response logged but no matching deployment record "
                    "— recording gap: deployment may have occurred but was not "
                    "logged against this incident ID"
                )
            unmatched_incidents.append({
                "incident_id": iid,
                "ward_id": inc["ward_id"],
                "type": inc["type"],
                "severity": inc["severity"],
                "status": inc["status"],
                "time_first_response": inc["time_first_response"],
                "teams_assigned": inc["teams_assigned"],
                "flag": flag,
            })

    unmatched_deployments: List[Dict[str, Any]] = [
        {
            "deployment_id": d["deployment_id"],
            "team_id": d["team_id"],
            "agency": d["agency"],
            "ward_id": d["ward_id"],
            "task_performed": d["task_performed"],
            "outcome": d["outcome"],
            "flag": (
                "Deployment without logged incident — potential recording gap: "
                "team was deployed but no incident ID was assigned at dispatch"
            ),
        }
        for d in deployments
        if d["incident_id_assigned"] is None
    ]

    total = len(incidents)
    match_rate_pct = round(len(matched) / total * 100, 1) if total > 0 else 0.0

    return {
        "event_id": "FL-2025-07-14",
        "total_incidents": total,
        "total_deployments": len(deployments),
        "matched_count": len(matched),
        "unmatched_deployments_count": len(unmatched_deployments),
        "unmatched_incidents_count": len(unmatched_incidents),
        "match_rate_pct": match_rate_pct,
        "matched": matched,
        "unmatched_deployments": unmatched_deployments,
        "unmatched_incidents": unmatched_incidents,
        "reconciliation_note": (
            "Match rate below 90% indicates recording gaps — recommend mandatory "
            "incident-ID assignment at dispatch in future events."
            if match_rate_pct < 90.0
            else "Match rate acceptable; isolated recording gaps noted for correction."
        ),
    }


# ---------------------------------------------------------------------------
# Tool 5 — generate_aar_draft
# ---------------------------------------------------------------------------

def generate_aar_draft(event_name: str, event_date: str) -> dict:
    """
    Generate a structured After-Action Review (AAR) draft for the flood event.
    Loads incident log, deployment log, response metrics, and reconciliation
    data inline (direct function calls) to derive all sections.

    Sections produced:
    - executive_summary: 3 factual bullets
    - what_worked: list of at least 3 strengths
    - gaps_identified: derived from unmatched incidents + delayed responses
    - corrective_actions: specific, actionable recommendation per gap with owner role
    - commendations: teams with EXCELLENT response ratings
    - status: "DRAFT AAR — Requires review and sign-off by District Incident Commander"

    Args:
        event_name: Name/description of the event (e.g. "Urban Flash Flood").
        event_date: Date of the event (e.g. "2025-07-14").

    Returns:
        dict: Full AAR draft with all sections and metadata.
    """
    # Load all data inline
    incident_data = get_incident_log()
    deployment_data = get_resource_deployment_log()
    metrics_data = compute_response_time_metrics([])   # all incidents
    recon_data = reconcile_deployments_to_incidents()

    incidents = incident_data["incidents"]
    agg = metrics_data.get("aggregate_metrics", {})
    per_inc = metrics_data.get("per_incident_metrics", [])

    total_incidents = incident_data["total_incidents"]
    status_counts = incident_data["status_counts"]
    resolved = status_counts.get("RESOLVED", 0)
    escalated = status_counts.get("ESCALATED", 0)
    active = status_counts.get("ACTIVE", 0)

    avg_rt = agg.get("avg_response_time_minutes", "N/A")
    delayed_ids = agg.get("incidents_with_delayed_response", [])
    pct_60 = agg.get("pct_within_60_min", "N/A")
    match_rate = recon_data["match_rate_pct"]
    unmatched_deps = recon_data["unmatched_deployments"]
    unmatched_incs = recon_data["unmatched_incidents"]

    # Commendations: EXCELLENT responders
    excellent = [
        r for r in per_inc if r["rating"] == "EXCELLENT"
    ]
    commendations: List[str] = []
    for r in excellent:
        teams = ", ".join(r["teams_assigned"]) if r["teams_assigned"] else "Team unrecorded"
        commendations.append(
            f"{teams} — {r['incident_id']} ({r['type']}, {r['ward_id']}): "
            f"{r['response_time_minutes']}-minute response rated EXCELLENT"
        )
    if not commendations:
        commendations = ["No individual team achieved EXCELLENT rating — see corrective actions."]

    # What worked
    what_worked: List[str] = [
        (
            f"Early warning and pre-positioning enabled first response within "
            f"{agg.get('fastest_response', {}).get('minutes', 'N/A')} minutes for "
            f"the fastest incident ({agg.get('fastest_response', {}).get('incident_id', 'N/A')})."
        ),
        (
            f"{pct_60}% of incidents with logged responses were resolved within "
            f"the 60-minute benchmark, indicating acceptable overall mobilisation speed."
        ),
        (
            "Multi-agency coordination (NDRF, SDRF, Municipal Fire Department, PWD, "
            "and District Medical Services) maintained operational continuity across "
            "four wards simultaneously."
        ),
        (
            "Shelter operations at W12 (SH-B and SH-C) remained functional throughout "
            "the event, providing refuge without reported capacity-linked health incidents."
        ),
        (
            "Boat-assisted evacuation in W19 (INC-002) successfully extracted "
            "displaced residents despite complete vehicle access loss on Route F."
        ),
    ]

    # Gaps identified
    gaps_identified: List[str] = []

    for d_id in delayed_ids:
        inc = next((i for i in incidents if i["incident_id"] == d_id), None)
        if inc:
            mins_rec = next(
                (r["response_time_minutes"] for r in per_inc if r["incident_id"] == d_id),
                "unknown",
            )
            gaps_identified.append(
                f"{d_id} ({inc['type']}, {inc['ward_id']}, severity {inc['severity']}): "
                f"{mins_rec}-minute response — rated DELAYED (>60 min threshold). "
                f"Teams assigned: {inc['teams_assigned'] or 'none recorded'}."
            )

    for u_inc in unmatched_incs:
        gaps_identified.append(
            f"{u_inc['incident_id']} ({u_inc['type']}, {u_inc['ward_id']}): "
            f"{u_inc['flag']}"
        )

    for u_dep in unmatched_deps:
        gaps_identified.append(
            f"{u_dep['deployment_id']} ({u_dep['team_id']}, {u_dep['ward_id']}): "
            f"{u_dep['flag']}"
        )

    if match_rate < 90.0:
        gaps_identified.append(
            f"Overall deployment-to-incident match rate was {match_rate}% — below the "
            f"90% target, indicating systemic recording gaps at dispatch."
        )

    # Corrective actions — one per gap
    corrective_actions: List[Dict[str, str]] = [
        {
            "gap_reference": "INC-005 — Delayed medical access to W19 (95 min)",
            "action": (
                "Pre-position one medical team with boat access capability at the "
                "W19 staging point at the start of any RED or ORANGE alert. "
                "Medical response to W19 must not be contingent on Route F being passable."
            ),
            "owner": "District Medical Officer + DDMA Operations Cell",
            "deadline": "Before next monsoon season (pre-monsoon briefing, May 2026)",
        },
        {
            "gap_reference": "INC-008 — Delayed shelter overflow response in W19 (120 min)",
            "action": (
                "Designate a pre-approved overflow shelter in an adjacent ward "
                "(W07 District Hospital Annex or equivalent) for W19 residents. "
                "Activate automatically when SH-F reaches 80% occupancy during "
                "any declared flood emergency."
            ),
            "owner": "DDMA + Municipal Corporation",
            "deadline": "March 2026 (before monsoon season)",
        },
        {
            "gap_reference": "INC-012 — ACTIVE relief gap in W12 with no deployment",
            "action": (
                "Establish a real-time incident queue monitored by the Emergency "
                "Operations Centre duty officer. Any ACTIVE incident older than "
                "60 minutes with no assigned team must trigger an automatic alert "
                "to the incident commander for resource reallocation."
            ),
            "owner": "Emergency Operations Centre — Duty Officer",
            "deadline": "Implement SOPs before next event (October 2025)",
        },
        {
            "gap_reference": "DEP-009 and DEP-010 — Deployments without incident IDs",
            "action": (
                "Mandate incident-ID assignment at dispatch for all deployments. "
                "Update the dispatch log form to make incident_id a required field. "
                "For patrol or standby deployments, create a dedicated incident type "
                "(PATROL / STANDBY) so all field activity is traceable."
            ),
            "owner": "DDMA Operations Cell — Dispatch Coordinator",
            "deadline": "Update SOPs and train dispatchers before next monsoon (April 2026)",
        },
        {
            "gap_reference": f"Overall match rate {match_rate}% — systemic recording gap",
            "action": (
                "Conduct a post-event data reconciliation workshop with all agency "
                "dispatch teams. Introduce a 24-hour post-event mandatory log review "
                "where all unmatched records are resolved or flagged for investigation."
            ),
            "owner": "District Incident Commander + Agency Liaison Officers",
            "deadline": "Within 7 days of each event closeout",
        },
    ]

    executive_summary: List[str] = [
        (
            f"{total_incidents} incidents logged across 4 wards during {event_name} "
            f"on {event_date}: {resolved} resolved, {escalated} escalated, {active} still active."
        ),
        (
            f"Average first-response time was {avg_rt} minutes across {agg.get('incidents_evaluated', 'N/A')} "
            f"measurable incidents; {pct_60}% met the 60-minute response benchmark. "
            f"{len(delayed_ids)} incident(s) experienced delayed response (>60 min): "
            f"{', '.join(delayed_ids) if delayed_ids else 'none'}."
        ),
        (
            f"Deployment-to-incident match rate was {match_rate}%, with "
            f"{len(unmatched_deps)} deployment(s) and {len(unmatched_incs)} incident(s) "
            f"unmatched — indicating recording gaps requiring process improvement before "
            f"the next event."
        ),
    ]

    return {
        "aar_id": f"AAR-{event_date.replace('-', '')}-01",
        "event_name": event_name,
        "event_date": event_date,
        "generated_at": datetime.now().isoformat(),
        "executive_summary": executive_summary,
        "what_worked": what_worked,
        "gaps_identified": gaps_identified,
        "corrective_actions": corrective_actions,
        "commendations": commendations,
        "data_sources": {
            "total_incidents_reviewed": total_incidents,
            "total_deployments_reviewed": deployment_data["total_deployments"],
            "incidents_with_response_metrics": agg.get("incidents_evaluated", 0),
        },
        "status": (
            "DRAFT AAR — Requires review and sign-off by District Incident Commander"
        ),
        "disclaimer": (
            "All gaps identified in this AAR are operational recommendations for "
            "process improvement, not accusations of misconduct or negligence. "
            "Individual team performance should be reviewed in context of resource "
            "availability and access constraints on the day of the event."
        ),
    }
