"""
Tools for the Damage Assessment Agent.

Each function is a standalone tool the ADK agent calls. Tools implement real
computational logic: field report aggregation, vulnerability-driven structural
damage scoring, NDMA unit-cost monetary estimation, displacement status
derivation from ward profiles, and district-level report compilation.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _load(filename: str) -> Any:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)


def _get_ward(ward_id: str) -> Dict[str, Any]:
    """Return the ward profile dict for ward_id, or empty dict if not found."""
    data = _load("ward_profiles.json")
    return next((w for w in data["wards"] if w["ward_id"] == ward_id), {})


def _damage_category(vuln: float, hist_count: int) -> str:
    """Map vulnerability score + historical flood count to a damage category."""
    if vuln > 0.75 and hist_count >= 3:
        return "CRITICAL"
    if vuln >= 0.45:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Tool 1 — get_post_event_field_reports
# ---------------------------------------------------------------------------

def get_post_event_field_reports() -> dict:
    """
    Retrieve 8 simulated post-event damage reports submitted within 72 hours
    of the flood from municipal inspectors, SDRF teams, NGOs, and community
    coordinators across wards W12, W19, W07, and W04.

    Returns:
        dict: reports list with fields: report_id, ward_id, reporter,
              reporter_type (OFFICIAL/NGO/COMMUNITY), timestamp, raw_text,
              verified (bool). Also includes collection_window and
              per-ward report counts.
    """
    reports: List[Dict[str, Any]] = [
        {
            "report_id": "RPT-2025-001",
            "ward_id": "W12",
            "reporter": "Ward Inspector Ramesh Kulkarni",
            "reporter_type": "OFFICIAL",
            "timestamp": "2025-07-14T08:30:00+05:30",
            "raw_text": (
                "Ground-level survey complete for Sector 12 Lakeview. Over 230 "
                "residential structures have water ingress at ground floor level. "
                "Drain D-17 is fully blocked and overflowing onto the main road. "
                "Route A impassable — water knee to waist deep. Electricity "
                "substation W12 shut down as precaution. PHC operations "
                "suspended — ground floor flooded. Three buildings showing "
                "visible wall cracking near the drain channel. Requesting two "
                "pump units urgently."
            ),
            "verified": True,
        },
        {
            "report_id": "RPT-2025-002",
            "ward_id": "W12",
            "reporter": "SDRF Team B2 — Sub-Inspector Pawar",
            "reporter_type": "OFFICIAL",
            "timestamp": "2025-07-14T10:15:00+05:30",
            "raw_text": (
                "SDRF B2 on-ground assessment for Sector 12. Confirmed: "
                "approximately 245 structures affected by inundation. Five "
                "buildings at the D-17 junction have partial collapse of "
                "boundary walls — two are structurally unsafe. Shelter SH-B "
                "at School W12-A is operational with 380 displaced persons. "
                "Shelter SH-C Community Hall has 215 persons. Route C Elevated "
                "Road is accessible and being used as alternate. Pump deployment "
                "from Fire Service ongoing — D-17 partially cleared."
            ),
            "verified": True,
        },
        {
            "report_id": "RPT-2025-003",
            "ward_id": "W19",
            "reporter": "Red Cross Field Team — Coordinator Sunita Rao",
            "reporter_type": "NGO",
            "timestamp": "2025-07-14T09:00:00+05:30",
            "raw_text": (
                "NGO field assessment for Sector 19 North Wetlands — access by "
                "boat only as Route F is fully submerged. Borewell W19 visually "
                "contaminated — brownish water, not fit for consumption. "
                "Estimated 220 informal settlement structures under water — many "
                "single-storey, high collapse risk. Community reports suggest "
                "6 to 8 structures fully collapsed. Residents on upper floors "
                "or rooftops awaiting rescue. Shelter SH-F at North Primary "
                "School is at full capacity (200 persons). Approximately 890 "
                "residents still displaced with no road access for relief."
            ),
            "verified": True,
        },
        {
            "report_id": "RPT-2025-004",
            "ward_id": "W19",
            "reporter": "Community Coordinator Bashir Ahmed — Ward 19",
            "reporter_type": "COMMUNITY",
            "timestamp": "2025-07-14T07:45:00+05:30",
            "raw_text": (
                "Ward 19 is completely cut off since early morning. Hundreds of "
                "homes are flooded — chest-deep water in the low areas near the "
                "wetland. Several elderly people and small children are stranded "
                "on rooftops. Two families with pregnant women need immediate "
                "medical help. Route F is completely blocked. We have had no "
                "food or water for over 12 hours. Borewell water smells bad. "
                "Please send boats and medical teams immediately."
            ),
            "verified": False,
        },
        {
            "report_id": "RPT-2025-005",
            "ward_id": "W19",
            "reporter": "SDRF District Team — Inspector Nair",
            "reporter_type": "OFFICIAL",
            "timestamp": "2025-07-14T13:00:00+05:30",
            "raw_text": (
                "SDRF aerial observation and boat-assisted assessment for Ward 19. "
                "Approximately 240 structures confirmed flooded; 7 confirmed "
                "collapsed or structurally compromised. Route F remains submerged "
                "under 1.2 metres of water — no vehicle access possible. Drainage "
                "channels D-22 and D-23 are blocked and overflowing. No pump "
                "stations in ward — drainage entirely gravity dependent. Boat "
                "evacuation ongoing. Assessment is preliminary — full ground "
                "survey pending when water recedes."
            ),
            "verified": True,
        },
        {
            "report_id": "RPT-2025-006",
            "ward_id": "W07",
            "reporter": "Ward Inspector Meena Joshi",
            "reporter_type": "OFFICIAL",
            "timestamp": "2025-07-14T09:30:00+05:30",
            "raw_text": (
                "Sector 7 Old Quarter survey complete. Moderate waterlogging "
                "in the lower old-city construction zone — approximately 65 "
                "residential units affected with ankle to knee-deep water. "
                "District Hospital W7 operations normal — building is elevated. "
                "Drain D-09 partially blocked; pump mobilised by municipal team. "
                "Flyover Route D remains operational as primary route. Two road "
                "sections near the drain junction damaged by erosion. High elderly "
                "population in this ward — some assistance needed for evacuation."
            ),
            "verified": True,
        },
        {
            "report_id": "RPT-2025-007",
            "ward_id": "W07",
            "reporter": "NGO-3 Local Welfare Society — Field Lead Kavita Sharma",
            "reporter_type": "NGO",
            "timestamp": "2025-07-14T11:00:00+05:30",
            "raw_text": (
                "NGO-3 assessment for W07: flooding is moderate and localised to "
                "the old market and drain junction zones. About 55 to 65 units "
                "affected. Elderly residents in the dense old-city blocks require "
                "assistance moving to upper floors — 18 percent of population is "
                "elderly. District Hospital Annex shelter has capacity and is "
                "receiving displaced persons. No structural collapses observed. "
                "Route D flyover is operational."
            ),
            "verified": True,
        },
        {
            "report_id": "RPT-2025-008",
            "ward_id": "W04",
            "reporter": "Ward Inspector Prakash Desai",
            "reporter_type": "OFFICIAL",
            "timestamp": "2025-07-14T10:00:00+05:30",
            "raw_text": (
                "Sector 4 Industrial West — minor flooding in the residential "
                "boundary zone adjacent to the industrial area. Approximately "
                "10 to 12 residential structures affected with ankle-deep water. "
                "Industrial Road E fully operational. Drainage D-03 is functioning "
                "normally. Three pump stations active and performing adequately. "
                "No structural damage identified. Industrial Welfare Centre "
                "shelter is on standby — not yet activated. Situation is under "
                "control; monitoring continues."
            ),
            "verified": True,
        },
    ]

    ward_report_counts: Dict[str, int] = {}
    for r in reports:
        ward_report_counts[r["ward_id"]] = ward_report_counts.get(r["ward_id"], 0) + 1

    return {
        "collection_window": "Post-flood 0–72h",
        "fetched_at": datetime.now().isoformat(),
        "total_reports": len(reports),
        "verified_count": sum(1 for r in reports if r["verified"]),
        "unverified_count": sum(1 for r in reports if not r["verified"]),
        "reports_by_ward": ward_report_counts,
        "reports": reports,
    }


# ---------------------------------------------------------------------------
# Tool 2 — assess_structural_damage
# ---------------------------------------------------------------------------

def assess_structural_damage(ward_id: str) -> dict:
    """
    Compute the post-flood structural damage profile for a ward using its
    vulnerability score, historical flood frequency, area, and drainage
    infrastructure loaded from ward_profiles.json.

    Methodology:
    - damage_category: CRITICAL if vulnerability_score > 0.75 AND
      historical_flood_count_5yr >= 3; MEDIUM if vulnerability >= 0.45;
      LOW otherwise.
    - flooded_structures: CRITICAL 180–250 (scaled by vuln within 0.75–1.0);
      MEDIUM 40–80 (scaled by vuln within 0.45–0.75); LOW 5–15 (scaled).
    - total_structures: ward population / avg_household_size (4 persons).
    - damage_pct: flooded / total * 100.
    - structural_damage_severity: SEVERE if damage_pct > 30%, MODERATE if
      10–30%, MINOR if < 10%.
    - collapsed_buildings: CRITICAL 3–8; MEDIUM/LOW 0–2.
    - road_sections_damaged: area_sq_km (int) × category multiplier
      (CRITICAL=4, MEDIUM=2, LOW=1) + baseline 2/1/0.
    - drainage_failures: len(main_drain_ids) × category multiplier
      (CRITICAL=2, MEDIUM=1, LOW=0).

    Args:
        ward_id: Ward identifier (e.g. "W12", "W19").

    Returns:
        dict: All computed damage values with ward metadata and
              calculation_method explanation.
    """
    AVG_HOUSEHOLD_SIZE = 4

    ward = _get_ward(ward_id)
    if not ward:
        return {
            "error": f"Ward {ward_id} not found in ward_profiles.json",
            "ward_id": ward_id,
        }

    vuln: float = ward.get("vulnerability_score", 0.5)
    hist: int = ward.get("historical_flood_count_5yr", 0)
    population: int = ward.get("population", 0)
    area: float = ward.get("area_sq_km", 1.0)
    drain_ids: List[str] = ward.get("main_drain_ids", [])

    total_structures = max(1, population // AVG_HOUSEHOLD_SIZE)
    category = _damage_category(vuln, hist)

    if category == "CRITICAL":
        # Scale within vuln range 0.75–1.0 → 180–250
        scale = min(1.0, max(0.0, (vuln - 0.75) / 0.25))
        flooded_structures = int(180 + scale * 70)
        # Collapsed: scale 0.75–1.0 → 3–8
        collapsed_buildings = int(3 + scale * 5)
        road_sections_damaged = int(area) * 4 + 2
        drainage_failures = len(drain_ids) * 2
    elif category == "MEDIUM":
        # Scale within vuln range 0.45–0.75 → 40–80
        scale = min(1.0, max(0.0, (vuln - 0.45) / 0.30))
        flooded_structures = int(40 + scale * 40)
        collapsed_buildings = max(0, int(vuln * 2))
        road_sections_damaged = int(area) * 2 + 1
        drainage_failures = len(drain_ids)
    else:  # LOW
        # Scale within vuln 0–0.45 → 5–15
        scale = min(1.0, max(0.0, vuln / 0.45))
        flooded_structures = int(5 + scale * 10)
        collapsed_buildings = 0
        road_sections_damaged = max(1, int(area))
        drainage_failures = 0

    damage_pct = round(flooded_structures / total_structures * 100, 2)

    if damage_pct > 30.0:
        structural_damage_severity = "SEVERE"
    elif damage_pct >= 10.0:
        structural_damage_severity = "MODERATE"
    else:
        structural_damage_severity = "MINOR"

    return {
        "ward_id": ward_id,
        "ward_name": ward.get("ward_name", ward_id),
        "damage_category": category,
        "flooded_structures": flooded_structures,
        "total_structures": total_structures,
        "damage_pct": damage_pct,
        "structural_damage_severity": structural_damage_severity,
        "collapsed_buildings": collapsed_buildings,
        "road_sections_damaged": road_sections_damaged,
        "drainage_failures": drainage_failures,
        "vulnerability_score_used": vuln,
        "historical_flood_count_5yr": hist,
        "calculation_method": (
            f"Damage category '{category}' derived from vulnerability score "
            f"({vuln}) and historical flood frequency ({hist} events/5yr). "
            f"Flooded structures scaled within category range. "
            f"Total structures estimated as population ({population}) "
            f"/ avg household size ({AVG_HOUSEHOLD_SIZE}) = {total_structures}. "
            f"Road sections = int(area {area} sq_km) × multiplier + baseline. "
            f"Drainage failures = {len(drain_ids)} drain IDs × multiplier."
        ),
    }


# ---------------------------------------------------------------------------
# Tool 3 — estimate_monetary_loss
# ---------------------------------------------------------------------------

def estimate_monetary_loss(
    ward_id: str,
    flooded_structures: int,
    collapsed_buildings: int,
    road_sections_damaged: int,
) -> dict:
    """
    Estimate monetary flood damage using standard NDMA unit costs embedded
    in this tool. Drainage failures are derived internally from the ward
    profile to complete infrastructure loss calculations.

    NDMA Unit Costs:
    - Residential repair (per flooded structure):  INR 85,000
    - Residential rebuild (per collapsed building): INR 4,50,000
    - Road section repair (per section):            INR 1,25,000
    - Drainage failure repair (per failure):        INR 75,000
    - Livelihood loss: 35% of flooded structures × INR 15,000 avg

    Args:
        ward_id:               Ward identifier.
        flooded_structures:    Number of flooded structures (from assess_structural_damage).
        collapsed_buildings:   Number of fully/partially collapsed buildings.
        road_sections_damaged: Number of damaged road sections.

    Returns:
        dict: Itemised loss components, total, unit costs, confidence_level,
              and disclaimer note.
    """
    # NDMA unit costs (INR)
    UNIT_REPAIR = 85_000        # residential repair per flooded structure
    UNIT_REBUILD = 4_50_000     # residential rebuild per collapsed building
    UNIT_ROAD = 1_25_000        # road section repair
    UNIT_DRAINAGE = 75_000      # drainage failure repair
    LIVELIHOOD_RATIO = 0.35     # fraction of flooded households losing livelihoods
    LIVELIHOOD_UNIT = 15_000    # avg livelihood loss per affected household

    # Derive drainage_failures from ward profile (same logic as assess_structural_damage)
    ward = _get_ward(ward_id)
    if ward:
        vuln = ward.get("vulnerability_score", 0.5)
        hist = ward.get("historical_flood_count_5yr", 0)
        drain_ids = ward.get("main_drain_ids", [])
        cat = _damage_category(vuln, hist)
        drainage_failures = (
            len(drain_ids) * 2 if cat == "CRITICAL"
            else len(drain_ids) if cat == "MEDIUM"
            else 0
        )
        # Confidence: OFFICIAL if ward has verified OFFICIAL field reports
        confidence_level = (
            "OFFICIAL" if ward_id in ("W12", "W19", "W07", "W04") else "ESTIMATE"
        )
    else:
        drainage_failures = 0
        confidence_level = "ESTIMATE"

    residential_loss = (
        flooded_structures * UNIT_REPAIR + collapsed_buildings * UNIT_REBUILD
    )
    infrastructure_loss = (
        road_sections_damaged * UNIT_ROAD + drainage_failures * UNIT_DRAINAGE
    )
    livelihoods_loss = int(flooded_structures * LIVELIHOOD_RATIO) * LIVELIHOOD_UNIT
    total_estimated_loss = residential_loss + infrastructure_loss + livelihoods_loss

    return {
        "ward_id": ward_id,
        "flooded_structures": flooded_structures,
        "collapsed_buildings": collapsed_buildings,
        "road_sections_damaged": road_sections_damaged,
        "drainage_failures": drainage_failures,
        "residential_loss": residential_loss,
        "infrastructure_loss": infrastructure_loss,
        "livelihoods_loss": livelihoods_loss,
        "total_estimated_loss": total_estimated_loss,
        "unit_costs_used": {
            "residential_repair_per_structure_inr": UNIT_REPAIR,
            "rebuild_per_collapsed_building_inr": UNIT_REBUILD,
            "road_section_repair_inr": UNIT_ROAD,
            "drainage_failure_repair_inr": UNIT_DRAINAGE,
            "livelihood_affected_ratio": LIVELIHOOD_RATIO,
            "livelihood_loss_per_unit_inr": LIVELIHOOD_UNIT,
        },
        "confidence_level": confidence_level,
        "note": (
            "Estimates pending detailed engineering survey — "
            "for compensation claim initiation only"
        ),
    }


# ---------------------------------------------------------------------------
# Tool 4 — get_displacement_status
# ---------------------------------------------------------------------------

def get_displacement_status(ward_id: str) -> dict:
    """
    Return current displacement and shelter status for a ward. Displaced
    persons counts are event-sourced from field reports; shelter capacity
    and names are loaded from ward_profiles.json.

    Displacement figures (from consolidated field reports):
    - W12: 1,240 displaced | W19: 890 | W07: 340 | W04: 45 | others: 0

    In-shelter count = min(displaced × 0.85, total_shelter_capacity).
    Shelter utilisation = in_shelters / total_capacity × 100.
    needs_additional_shelter = True if utilisation > 85%.

    Args:
        ward_id: Ward identifier (e.g. "W12").

    Returns:
        dict: ward_id, ward_name, currently_displaced, in_shelters,
              with_relatives, shelter_names, shelter_capacity,
              shelter_utilization_pct, needs_additional_shelter,
              return_timeline.
    """
    DISPLACED_MAP: Dict[str, int] = {
        "W12": 1240,
        "W19": 890,
        "W07": 340,
        "W04": 45,
    }

    ward = _get_ward(ward_id)
    ward_name = ward.get("ward_name", ward_id) if ward else ward_id

    currently_displaced = DISPLACED_MAP.get(ward_id, 0)

    # Load shelters from ward profile
    shelters = ward.get("shelters", []) if ward else []
    if shelters:
        shelter_names = [s["name"] for s in shelters]
        shelter_capacity = sum(s.get("capacity", 0) for s in shelters)
    else:
        shelter_names = ["Government School Shelter"]
        shelter_capacity = 200  # default minimal assumption

    # Compute in-shelter and with-relatives
    in_shelters = min(
        int(currently_displaced * 0.85),
        shelter_capacity,
    )
    with_relatives = max(0, currently_displaced - in_shelters)

    # Utilisation
    if shelter_capacity > 0:
        shelter_utilization_pct = round(in_shelters / shelter_capacity * 100, 1)
    else:
        shelter_utilization_pct = 0.0

    needs_additional_shelter = shelter_utilization_pct > 85.0

    return {
        "ward_id": ward_id,
        "ward_name": ward_name,
        "currently_displaced": currently_displaced,
        "in_shelters": in_shelters,
        "with_relatives": with_relatives,
        "shelter_names": shelter_names,
        "shelter_capacity": shelter_capacity,
        "shelter_utilization_pct": shelter_utilization_pct,
        "needs_additional_shelter": needs_additional_shelter,
        "return_timeline": (
            "48–72h for accessible areas with receding water; "
            "5–7 days for still-submerged zones pending pump clearance"
        ),
    }


# ---------------------------------------------------------------------------
# Tool 5 — compile_damage_report
# ---------------------------------------------------------------------------

def compile_damage_report(ward_ids: List[str]) -> dict:
    """
    Compile a district-level damage report aggregating structural damage,
    monetary loss, and displacement data for each listed ward.

    Calls assess_structural_damage, estimate_monetary_loss, and
    get_displacement_status inline (as direct Python function calls —
    not via ADK tool dispatch) for each ward_id in ward_ids.

    Aggregates:
    - district_totals: flooded_structures, collapsed_buildings,
      total_monetary_loss, total_displaced.
    - highest_damage_ward: ward_id with the largest monetary loss.
    - state_compensation_eligibility: YES if total loss > INR 5 crore
      (SDRF threshold).
    - report_status: always DRAFT — requires countersignature.

    Args:
        ward_ids: List of ward IDs to include (e.g. ["W12","W19","W07","W04"]).

    Returns:
        dict: Full compiled report with ward_summaries, district_totals,
              eligibility determination, and report metadata.
    """
    SDRF_THRESHOLD = 5_00_00_000  # INR 5 crore

    ward_summaries: List[Dict[str, Any]] = []
    district_flooded = 0
    district_collapsed = 0
    district_monetary_loss: float = 0.0
    district_displaced = 0

    for wid in ward_ids:
        # Inline calls — direct Python function invocations
        damage = assess_structural_damage(wid)
        if "error" in damage:
            ward_summaries.append({"ward_id": wid, "error": damage["error"]})
            continue

        monetary = estimate_monetary_loss(
            ward_id=wid,
            flooded_structures=damage["flooded_structures"],
            collapsed_buildings=damage["collapsed_buildings"],
            road_sections_damaged=damage["road_sections_damaged"],
        )
        displacement = get_displacement_status(wid)

        summary: Dict[str, Any] = {
            "ward_id": wid,
            "ward_name": damage["ward_name"],
            "damage_category": damage["damage_category"],
            "structural_damage_severity": damage["structural_damage_severity"],
            "flooded_structures": damage["flooded_structures"],
            "total_structures": damage["total_structures"],
            "damage_pct": damage["damage_pct"],
            "collapsed_buildings": damage["collapsed_buildings"],
            "road_sections_damaged": damage["road_sections_damaged"],
            "drainage_failures": damage["drainage_failures"],
            "residential_loss_inr": monetary["residential_loss"],
            "infrastructure_loss_inr": monetary["infrastructure_loss"],
            "livelihoods_loss_inr": monetary["livelihoods_loss"],
            "total_monetary_loss_inr": monetary["total_estimated_loss"],
            "monetary_confidence": monetary["confidence_level"],
            "currently_displaced": displacement["currently_displaced"],
            "in_shelters": displacement["in_shelters"],
            "shelter_capacity": displacement["shelter_capacity"],
            "shelter_utilization_pct": displacement["shelter_utilization_pct"],
            "needs_additional_shelter": displacement["needs_additional_shelter"],
        }

        ward_summaries.append(summary)
        district_flooded += damage["flooded_structures"]
        district_collapsed += damage["collapsed_buildings"]
        district_monetary_loss += monetary["total_estimated_loss"]
        district_displaced += displacement["currently_displaced"]

    # Find highest-damage ward (by monetary loss)
    valid = [s for s in ward_summaries if "error" not in s]
    highest_damage_ward = (
        max(valid, key=lambda x: x["total_monetary_loss_inr"])["ward_id"]
        if valid else "N/A"
    )

    state_eligible = district_monetary_loss > SDRF_THRESHOLD
    eligibility_str = (
        "YES — damage exceeds SDRF threshold (INR 5 crore)"
        if state_eligible
        else "UNDER REVIEW — damage may not meet SDRF threshold; full survey required"
    )

    return {
        "report_id": f"DA-RPT-{datetime.now().strftime('%Y%m%d-%H%M')}",
        "district": "Metro District",
        "state": "Maharashtra (Simulated)",
        "generated_at": datetime.now().isoformat(),
        "wards_assessed": ward_ids,
        "district_totals": {
            "flooded_structures": district_flooded,
            "collapsed_buildings": district_collapsed,
            "total_monetary_loss_inr": district_monetary_loss,
            "total_displaced": district_displaced,
        },
        "ward_summaries": ward_summaries,
        "highest_damage_ward": highest_damage_ward,
        "state_compensation_eligibility": eligibility_str,
        "report_status": (
            "DRAFT — Requires District Collector countersignature before submission"
        ),
        "disclaimer": (
            "All monetary estimates are preliminary, based on NDMA unit costs applied "
            "to field-assessed structural counts. Figures are for SDRF compensation "
            "claim initiation only. Final loss certification requires detailed "
            "engineering survey by qualified assessors."
        ),
    }
