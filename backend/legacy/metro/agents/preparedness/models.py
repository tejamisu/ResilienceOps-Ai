from __future__ import annotations

"""
Data models for the Preparedness Agent.

Defines typed records for shelter audits, route assessments, action plan items,
and the top-level district preparedness output.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ShelterAudit:
    """Readiness assessment for a single ward shelter."""

    ward_id: str
    shelter_name: str
    capacity: int
    status: str             # READY | NEEDS_INSPECTION | NEEDS_REPAIR
    readiness_score: float  # READY=1.0, NEEDS_INSPECTION=0.6, NEEDS_REPAIR=0.3
    gap_description: str    # Empty string if READY
    backup_power: bool


@dataclass
class RouteAudit:
    """Current passability assessment for a single evacuation route."""

    ward_id: str
    route_id: str
    route_name: str
    status: str        # CLEAR | NEEDS_CLEARANCE | BOAT_ONLY | AT_RISK
    passable_by: str   # e.g. 'road vehicle', 'boat', 'road vehicle (limited)'
    action_needed: str


@dataclass
class PreparednessPlanAction:
    """A single time-bound action item in the preparedness plan."""

    action: str
    owner: str
    deadline_days: int
    priority: str               # CRITICAL | HIGH | MEDIUM
    estimated_cost_lakhs: float


@dataclass
class PreparednessOutput:
    """Top-level summary of the district preparedness status."""

    district_readiness_score: float   # 0.0–1.0 average across resource categories
    shelter_coverage_ratio: float     # total shelter capacity / total population
    routes_clear: int
    routes_at_risk: int
    resource_gaps: List[str]          # Human-readable gap descriptions
    overdue_drills: List[str]         # Ward IDs with OVERDUE drill status
    action_plan_status: str
