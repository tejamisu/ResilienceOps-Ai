from __future__ import annotations

"""
Tools for the Preparedness Agent.

Each function implements real computational logic for pre-season district
preparedness auditing.  Shelter and route assessments combine hardcoded
audit findings (which extend the static JSON with current field knowledge)
with dynamic population data loaded from ward_profiles.json.

Tool inventory:
  1. audit_shelter_readiness         — per-ward shelter status and coverage gap
  2. audit_evacuation_routes         — route passability and single-route risk flags
  3. audit_resource_pre_positioning  — inventory vs recommended levels
  4. get_training_status             — community drill and first-responder status
  5. generate_preparedness_action_plan — phased DDMA action plan with cost estimates
"""

import json
import os
from typing import Any, List

_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


def _load(filename: str) -> Any:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tool 1 — audit_shelter_readiness
# ---------------------------------------------------------------------------

def audit_shelter_readiness() -> dict:
    """
    Audit the readiness of district emergency shelters for the coming season.

    Shelter assessments (status, backup power, and gap descriptions) are derived
    from the most recent field inspection records.  Ward population figures are
    loaded live from ward_profiles.json to compute the district coverage ratio.

    Shelter-level data:
    - W12: capacity 2500, READY, backup power YES
    - W19: capacity 1800, NEEDS_INSPECTION (last inspection > 6 months ago),
           backup power NO
    - W07: capacity 1200, READY, backup power YES
    - W04: capacity  800, NEEDS_REPAIR (roof damage from last season),
           backup power NO

    Readiness scores: READY=1.0, NEEDS_INSPECTION=0.6, NEEDS_REPAIR=0.3

    Returns:
        dict with keys: shelters (list of per-ward audit records), summary
        (district_total_capacity, district_total_population, coverage_ratio,
        wards_ready, wards_needing_action, average_readiness_score).
    """
    ward_data = _load('ward_profiles.json')

    # Population lookup from ward profiles
    population_map: dict = {
        w['ward_id']: w.get('population', 0) for w in ward_data['wards']
    }

    # Hardcoded current audit findings (field inspection records)
    SHELTER_AUDIT_DATA: List[dict] = [
        {
            'ward_id': 'W12',
            'shelter_name': 'Sector 12 Composite Shelter',
            'capacity': 2500,
            'status': 'READY',
            'backup_power': True,
            'gap_description': '',
        },
        {
            'ward_id': 'W19',
            'shelter_name': 'North Primary School Shelter W19',
            'capacity': 1800,
            'status': 'NEEDS_INSPECTION',
            'backup_power': False,
            'gap_description': (
                'Last inspection >6 months ago — structural integrity unconfirmed.  '
                'No backup power: cannot sustain night operations or medical equipment '
                'during grid outages.  Accessibility for mobility-impaired residents '
                'not verified.'
            ),
        },
        {
            'ward_id': 'W07',
            'shelter_name': 'District Hospital Annex Shelter W07',
            'capacity': 1200,
            'status': 'READY',
            'backup_power': True,
            'gap_description': '',
        },
        {
            'ward_id': 'W04',
            'shelter_name': 'Industrial Welfare Centre Shelter W04',
            'capacity': 800,
            'status': 'NEEDS_REPAIR',
            'backup_power': False,
            'gap_description': (
                'Roof damage sustained in last season — cannot safely shelter occupants '
                'during heavy rainfall.  No backup power: cannot sustain lighting or '
                'communication equipment during extended outages.'
            ),
        },
    ]

    READINESS_SCORE_MAP = {
        'READY': 1.0,
        'NEEDS_INSPECTION': 0.6,
        'NEEDS_REPAIR': 0.3,
    }

    shelters: List[dict] = []
    total_capacity = 0
    total_population = sum(population_map.values())
    readiness_scores: List[float] = []
    wards_ready = 0
    wards_needing_action = 0

    for audit in SHELTER_AUDIT_DATA:
        status = audit['status']
        score = READINESS_SCORE_MAP.get(status, 0.5)
        readiness_scores.append(score)
        total_capacity += audit['capacity']

        if status == 'READY':
            wards_ready += 1
        else:
            wards_needing_action += 1

        shelters.append({
            'ward_id': audit['ward_id'],
            'shelter_name': audit['shelter_name'],
            'capacity': audit['capacity'],
            'status': status,
            'readiness_score': score,
            'backup_power': audit['backup_power'],
            'gap_description': audit['gap_description'],
            'ward_population': population_map.get(audit['ward_id'], 0),
        })

    coverage_ratio = (
        round(total_capacity / total_population, 4) if total_population > 0 else 0.0
    )
    avg_readiness = round(
        sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0.0, 4
    )

    return {
        'shelters': shelters,
        'summary': {
            'district_total_capacity': total_capacity,
            'district_total_population': total_population,
            'coverage_ratio': coverage_ratio,
            'coverage_ratio_pct': round(coverage_ratio * 100, 2),
            'wards_ready': wards_ready,
            'wards_needing_action': wards_needing_action,
            'average_readiness_score': avg_readiness,
        },
    }


# ---------------------------------------------------------------------------
# Tool 2 — audit_evacuation_routes
# ---------------------------------------------------------------------------

def audit_evacuation_routes() -> dict:
    """
    Audit the current passability status of all district evacuation routes.

    Route assessments extend the static ward_profiles.json with current
    field-observed conditions (debris, seasonal flooding, bridge load limits).

    Route statuses:
    - W12: Route C — CLEAR; Route E — NEEDS_CLEARANCE (debris from last event)
    - W19: Route F — BOAT_ONLY (road submerged seasonally);
           Route G — CLEAR
    - W07: Route D — CLEAR; Route H — AT_RISK (bridge load limit exceeded)
    - W04: Route B — CLEAR

    Wards with only one road-accessible route are flagged as HIGH priority for
    alternate-route development.

    Returns:
        dict with keys: routes (list of per-route audit records), summary
        (routes_clear, routes_at_risk, wards_with_single_route).
    """
    # Current route audit data (combines ward_profiles knowledge with field inspection)
    ROUTE_AUDIT_DATA: List[dict] = [
        {
            'ward_id': 'W12',
            'route_id': 'Route-C',
            'route_name': 'Elevated Road C',
            'status': 'CLEAR',
            'passable_by': 'road vehicle',
            'action_needed': 'None — route operational.',
        },
        {
            'ward_id': 'W12',
            'route_id': 'Route-E',
            'route_name': 'Sector 12 Eastern Link E',
            'status': 'NEEDS_CLEARANCE',
            'passable_by': 'road vehicle (pending clearance)',
            'action_needed': (
                'Clear debris deposited by last flood event.  '
                'PWD crew and mechanical equipment required.  '
                'Until cleared, Route C is the only reliable road egress for W12.'
            ),
        },
        {
            'ward_id': 'W19',
            'route_id': 'Route-F',
            'route_name': 'Wetland Road F (primary access)',
            'status': 'BOAT_ONLY',
            'passable_by': 'rescue boat',
            'action_needed': (
                'Road submerges at >80mm rainfall.  '
                'Pre-position rescue boat at Ward 19 entry before monsoon peak.  '
                'Identify high-ground assembly points accessible without road access.'
            ),
        },
        {
            'ward_id': 'W19',
            'route_id': 'Route-G',
            'route_name': 'North Wetlands Elevated Track G',
            'status': 'CLEAR',
            'passable_by': 'road vehicle (light)',
            'action_needed': (
                'Route G is clear but load-rated for light vehicles only.  '
                'Heavy relief trucks must use boat relay.  '
                'Formalise Route G as official alternate to Route F.'
            ),
        },
        {
            'ward_id': 'W07',
            'route_id': 'Route-D',
            'route_name': 'Flyover Route D',
            'status': 'CLEAR',
            'passable_by': 'road vehicle',
            'action_needed': 'None — route operational.',
        },
        {
            'ward_id': 'W07',
            'route_id': 'Route-H',
            'route_name': 'Old Quarter Bridge Route H',
            'status': 'AT_RISK',
            'passable_by': 'road vehicle (restricted)',
            'action_needed': (
                'Bridge load limit exceeded by current traffic — structural risk '
                'during heavy vehicle relief operations.  Engineering assessment '
                'and load-restriction signage required immediately.  '
                'Long-term: bridge reinforcement works.'
            ),
        },
        {
            'ward_id': 'W04',
            'route_id': 'Route-B',
            'route_name': 'Industrial Road B',
            'status': 'CLEAR',
            'passable_by': 'road vehicle',
            'action_needed': (
                'Route B is the sole evacuation route for W04.  '
                'Identify and formally designate an alternate route — '
                'single-route dependency is a preparedness gap.'
            ),
        },
    ]

    # Status → clear/at-risk classification
    AT_RISK_STATUSES = {'NEEDS_CLEARANCE', 'BOAT_ONLY', 'AT_RISK'}

    routes: List[dict] = []
    routes_clear = 0
    routes_at_risk = 0
    ward_route_counts: dict = {}
    ward_road_accessible_counts: dict = {}

    for r in ROUTE_AUDIT_DATA:
        wid = r['ward_id']
        status = r['status']

        ward_route_counts[wid] = ward_route_counts.get(wid, 0) + 1

        if status == 'CLEAR':
            routes_clear += 1
            ward_road_accessible_counts[wid] = (
                ward_road_accessible_counts.get(wid, 0) + 1
            )
        else:
            routes_at_risk += 1
            if status != 'BOAT_ONLY':
                # NEEDS_CLEARANCE and AT_RISK are temporarily road-accessible
                ward_road_accessible_counts[wid] = (
                    ward_road_accessible_counts.get(wid, 0) + 1
                )

        routes.append({
            'ward_id': wid,
            'route_id': r['route_id'],
            'route_name': r['route_name'],
            'status': status,
            'passable_by': r['passable_by'],
            'action_needed': r['action_needed'],
        })

    # Flag wards with only one viable road-accessible route
    wards_with_single_route: List[str] = []
    for wid, total in ward_route_counts.items():
        road_count = ward_road_accessible_counts.get(wid, 0)
        if total == 1 or road_count <= 1:
            if wid not in wards_with_single_route:
                wards_with_single_route.append(wid)

    return {
        'routes': routes,
        'summary': {
            'total_routes_audited': len(routes),
            'routes_clear': routes_clear,
            'routes_at_risk': routes_at_risk,
            'wards_with_single_route': wards_with_single_route,
            'single_route_priority_note': (
                'Wards with a single viable road evacuation route face critical '
                'access failure risk during extreme events.  Alternate route '
                'development must be treated as CRITICAL priority.'
                if wards_with_single_route else ''
            ),
        },
    }


# ---------------------------------------------------------------------------
# Tool 3 — audit_resource_pre_positioning
# ---------------------------------------------------------------------------

def audit_resource_pre_positioning() -> dict:
    """
    Compare current pre-season resource inventory against recommended levels
    for district-wide flood response.

    Returns the gap for each resource category, the responsible agency,
    procurement lead time, and pre-positioned ward locations.  Also computes
    an overall_readiness_pct as the unweighted mean of (current / recommended)
    ratios across all resource categories.

    Returns:
        dict with keys: resources (list), overall_readiness_pct, summary.
    """
    RESOURCES: List[dict] = [
        {
            'resource': 'pumps',
            'current': 8,
            'recommended': 12,
            'unit': 'units',
            'pre_positioned_wards': ['W12', 'W07'],
            'procurement_lead_time_days': 21,
            'responsible_agency': 'Municipal Engineering Department',
        },
        {
            'resource': 'rescue_boats',
            'current': 3,
            'recommended': 5,
            'unit': 'units',
            'pre_positioned_wards': ['W12'],
            'procurement_lead_time_days': 45,
            'responsible_agency': 'DDMA / State SDRF',
        },
        {
            'resource': 'emergency_food_kits',
            'current': 850,
            'recommended': 1500,
            'unit': 'kits',
            'pre_positioned_wards': ['W12', 'W07'],
            'procurement_lead_time_days': 14,
            'responsible_agency': 'District Food & Civil Supplies',
        },
        {
            'resource': 'medical_kits',
            'current': 120,
            'recommended': 200,
            'unit': 'kits',
            'pre_positioned_wards': ['W12', 'W07'],
            'procurement_lead_time_days': 10,
            'responsible_agency': 'District Health Officer',
        },
        {
            'resource': 'shelter_beds_ready',
            'current': 3700,
            'recommended': 6300,
            'unit': 'beds',
            'pre_positioned_wards': ['W12', 'W07'],
            'procurement_lead_time_days': 30,
            'responsible_agency': 'Municipal Corporation / DDMA',
        },
        {
            'resource': 'generator_sets',
            'current': 2,
            'recommended': 4,
            'unit': 'units',
            'pre_positioned_wards': ['W12', 'W07'],
            'procurement_lead_time_days': 35,
            'responsible_agency': 'Municipal Electrical Division',
        },
    ]

    resources: List[dict] = []
    ratio_sum = 0.0

    for r in RESOURCES:
        gap = r['recommended'] - r['current']
        ratio = r['current'] / r['recommended'] if r['recommended'] > 0 else 1.0
        ratio_sum += ratio

        resources.append({
            'resource': r['resource'],
            'current': r['current'],
            'recommended': r['recommended'],
            'gap': gap,
            'unit': r['unit'],
            'coverage_pct': round(ratio * 100, 1),
            'pre_positioned_wards': r['pre_positioned_wards'],
            'procurement_lead_time_days': r['procurement_lead_time_days'],
            'responsible_agency': r['responsible_agency'],
            'gap_critical': gap > 0,
        })

    overall_readiness_pct = round((ratio_sum / len(RESOURCES)) * 100, 1) if RESOURCES else 0.0

    gaps_list = [
        f'{r["resource"].replace("_", " ").title()}: {r["gap"]} {r["unit"]} short'
        for r in resources
        if r['gap_critical']
    ]

    return {
        'resources': resources,
        'overall_readiness_pct': overall_readiness_pct,
        'summary': {
            'total_categories_audited': len(resources),
            'categories_at_gap': sum(1 for r in resources if r['gap_critical']),
            'categories_fully_stocked': sum(1 for r in resources if not r['gap_critical']),
            'key_gaps': gaps_list,
        },
    }


# ---------------------------------------------------------------------------
# Tool 4 — get_training_status
# ---------------------------------------------------------------------------

def get_training_status() -> dict:
    """
    Return community training and emergency drill status for each ward,
    plus first-responder refresher obligations and volunteer count.

    Status definitions:
    - CURRENT     : drill conducted within last 12 months, meets standard
    - DUE_SOON    : drill due within next 3 months
    - OVERDUE     : last drill >12 months ago — must be scheduled immediately

    Returns:
        dict with keys: wards (list of per-ward drill records), summary
        (overdue_wards, current_wards, first_responder_refresher_due,
        community_volunteers_trained_count).
    """
    WARD_TRAINING: List[dict] = [
        {
            'ward_id': 'W12',
            'last_drill': '2024-03-15',
            'drill_type': 'Evacuation + Shelter',
            'participants': 420,
            'status': 'CURRENT',
            'status_note': (
                'Drill conducted within 12 months.  Community familiar with '
                'Route C as alternate and SH-B as primary shelter.  '
                'Next drill due March 2025.'
            ),
        },
        {
            'ward_id': 'W19',
            'last_drill': '2023-09-10',
            'drill_type': 'Evacuation only',
            'participants': 180,
            'status': 'OVERDUE',
            'status_note': (
                'Last drill >12 months ago.  Evacuation-only drill covered '
                'Route F but not the boat-only scenario or Route G.  '
                'Low smartphone penetration (33%) means community relies on '
                'loudspeaker alerts — drill must include loudspeaker activation '
                'test.  Schedule immediately.'
            ),
        },
        {
            'ward_id': 'W07',
            'last_drill': '2024-05-20',
            'drill_type': 'Evacuation + Shelter',
            'participants': 310,
            'status': 'CURRENT',
            'status_note': (
                'Drill conducted within 12 months.  High elderly population (18%) '
                'flagged — mobility-assisted evacuation practised.  '
                'Route H load restriction must be communicated in next drill.'
            ),
        },
        {
            'ward_id': 'W04',
            'last_drill': '2024-04-08',
            'drill_type': 'Awareness session',
            'participants': 95,
            'status': 'DUE_SOON',
            'status_note': (
                'Awareness session only — not a full evacuation drill.  '
                'Single-route dependency (Route B) was not exercised.  '
                'Full evacuation and shelter drill with IWC shelter activation '
                'must be scheduled within 3 months.  Roof repair must be '
                'completed before shelter can be included in the drill.'
            ),
        },
    ]

    FIRST_RESPONDER_REFRESHER_DUE: List[str] = [
        'FR-TEAM-W19-01',  # W19 first-responder team — overdue refresher
        'FR-TEAM-W04-01',  # W04 first-responder team — due soon
        'MEDICAL-UNIT-03',  # District medical unit 03 — flood trauma refresher due
    ]

    COMMUNITY_VOLUNTEERS_TRAINED = 847

    overdue_wards = [w['ward_id'] for w in WARD_TRAINING if w['status'] == 'OVERDUE']
    current_wards = [w['ward_id'] for w in WARD_TRAINING if w['status'] == 'CURRENT']
    due_soon_wards = [w['ward_id'] for w in WARD_TRAINING if w['status'] == 'DUE_SOON']
    total_participants = sum(w['participants'] for w in WARD_TRAINING)

    return {
        'wards': WARD_TRAINING,
        'summary': {
            'overdue_wards': overdue_wards,
            'due_soon_wards': due_soon_wards,
            'current_wards': current_wards,
            'total_drill_participants_last_cycle': total_participants,
            'first_responder_refresher_due': FIRST_RESPONDER_REFRESHER_DUE,
            'community_volunteers_trained_count': COMMUNITY_VOLUNTEERS_TRAINED,
        },
    }


# ---------------------------------------------------------------------------
# Tool 5 — generate_preparedness_action_plan
# ---------------------------------------------------------------------------

def generate_preparedness_action_plan(pre_season: bool = True) -> dict:
    """
    Generate a phased, time-bound district preparedness action plan for the DDMA.

    The plan aggregates inline gap computations from shelter, route, resource, and
    training audits into three action horizons.  This tool does not call the other
    audit tool functions by name — it computes the relevant gaps directly.

    Action horizons:
    - immediate_actions (0–30 days)   : life-safety critical gaps
    - medium_term      (30–90 days)   : resource procurement and drill scheduling
    - long_term        (90–180 days)  : infrastructure and structural improvements

    Args:
        pre_season: True (default) for a standard pre-season plan.
                    False generates a post-event review plan (not yet implemented).

    Returns:
        dict with keys: immediate_actions, medium_term, long_term,
        total_estimated_budget_lakhs, approval_required_from, status.
    """
    # --- Inline: shelter gaps ---
    # W19: NEEDS_INSPECTION, no backup power
    # W04: NEEDS_REPAIR, no backup power
    # W19 and W04 lack backup generators

    # --- Inline: route gaps ---
    # Route E (W12): NEEDS_CLEARANCE — debris
    # Route F (W19): BOAT_ONLY — rescue boat must be pre-positioned
    # Route H (W07): AT_RISK — bridge load limit exceeded
    # W04: single route only (Route B)

    # --- Inline: resource gaps ---
    # pumps: gap 4 units  (recommended 12, current 8)
    # rescue_boats: gap 2 units (recommended 5, current 3)

    # --- Inline: training gaps ---
    # W19: OVERDUE
    # W04: DUE_SOON (awareness only — needs full drill)

    immediate_actions: List[dict] = [
        {
            'action': (
                'Conduct structural inspection of W19 shelter (North Primary School) — '
                'verify roof, floor, and structural integrity; confirm accessibility '
                'for mobility-impaired residents; document backup power absence.'
            ),
            'owner': 'Municipal Corporation — Building Dept',
            'deadline_days': 14,
            'priority': 'CRITICAL',
            'estimated_cost_lakhs': 0.5,
        },
        {
            'action': (
                'Clear debris from Route E (Sector 12 Eastern Link) — '
                'mobilise PWD crew with mechanical equipment; certify route passable '
                'before monsoon onset.'
            ),
            'owner': 'PWD / Roads Department',
            'deadline_days': 7,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 1.0,
        },
        {
            'action': (
                'Repair roof of W04 Industrial Welfare Centre shelter — '
                'assess full damage, replace roofing, waterproof, and certify shelter '
                'structurally sound for 800-person capacity.'
            ),
            'owner': 'Municipal Corporation — Works Dept',
            'deadline_days': 21,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 3.5,
        },
        {
            'action': (
                'Procure 2 rescue boats (gap vs. recommended 5) — '
                'issue emergency tender; pre-position 1 unit at Ward 19 entry '
                'and 1 unit at District Emergency Store.'
            ),
            'owner': 'DDMA / State SDRF',
            'deadline_days': 30,
            'priority': 'CRITICAL',
            'estimated_cost_lakhs': 8.0,
        },
    ]

    medium_term: List[dict] = [
        {
            'action': (
                'Procure 4 additional pump units (gap vs. recommended 12) — '
                'issue tender; pre-position 2 at W19 and 2 at W12 D-17 junction '
                'before monsoon peak.'
            ),
            'owner': 'Municipal Engineering Department',
            'deadline_days': 60,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 12.0,
        },
        {
            'action': (
                'Commission feasibility study for alternate road access to Ward 19 — '
                'Route F is seasonally boat-only; evaluate elevated track options '
                'and formalise Route G for light vehicles.'
            ),
            'owner': 'PWD / DDMA',
            'deadline_days': 90,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 2.5,
        },
        {
            'action': (
                'Schedule and conduct full evacuation + shelter drill for W19 (OVERDUE) — '
                'include loudspeaker alert activation test, boat-evacuation scenario, '
                'and Route G as alternate path.'
            ),
            'owner': 'DDMA + Ward Office W19',
            'deadline_days': 45,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 0.3,
        },
        {
            'action': (
                'Schedule full evacuation and shelter drill for W04 (currently DUE_SOON, '
                'awareness session only) — include IWC shelter activation and single-route '
                'contingency scenario.  Contingent on W04 roof repair completion.'
            ),
            'owner': 'DDMA + Ward Office W04',
            'deadline_days': 60,
            'priority': 'MEDIUM',
            'estimated_cost_lakhs': 0.3,
        },
    ]

    long_term: List[dict] = [
        {
            'action': (
                'Install generator set at W19 shelter (North Primary School) — '
                'size for lighting, communication equipment, and medical device load; '
                'include auto-transfer switch and fuel storage.'
            ),
            'owner': 'Municipal Electrical Division / DDMA',
            'deadline_days': 120,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 4.5,
        },
        {
            'action': (
                'Install generator set at W04 Industrial Welfare Centre shelter — '
                'same specification as W19 unit; schedule after roof repair is complete.'
            ),
            'owner': 'Municipal Electrical Division',
            'deadline_days': 120,
            'priority': 'MEDIUM',
            'estimated_cost_lakhs': 4.5,
        },
        {
            'action': (
                'Reinforce Route H bridge (Old Quarter Bridge, W07) — '
                'current load limit exceeded; commission structural engineering '
                'assessment; execute reinforcement works; install load-limit signage '
                'pending works completion.'
            ),
            'owner': 'PWD — Bridges Division',
            'deadline_days': 180,
            'priority': 'HIGH',
            'estimated_cost_lakhs': 25.0,
        },
    ]

    total_budget = round(
        sum(a['estimated_cost_lakhs'] for a in immediate_actions)
        + sum(a['estimated_cost_lakhs'] for a in medium_term)
        + sum(a['estimated_cost_lakhs'] for a in long_term),
        2,
    )

    return {
        'plan_type': 'pre_season' if pre_season else 'post_event',
        'immediate_actions': immediate_actions,
        'medium_term': medium_term,
        'long_term': long_term,
        'total_actions': (
            len(immediate_actions) + len(medium_term) + len(long_term)
        ),
        'total_estimated_budget_lakhs': total_budget,
        'approval_required_from': 'DDMA / District Collector',
        'status': 'DRAFT — Awaiting DDMA review and budget allocation approval',
    }
