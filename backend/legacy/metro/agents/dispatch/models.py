"""
Pydantic models for the Dispatch & Resource Agent output.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TeamScore(BaseModel):
    """Score breakdown for a single responder team assessed against one incident."""

    team_id: str
    agency: str
    composite_score: float = Field(ge=0.0, le=1.0)
    availability_score: float = Field(ge=0.0, le=1.0)
    proximity_score: float = Field(ge=0.0, le=1.0)
    equipment_match_score: float = Field(ge=0.0, le=1.0)
    workload_score: float = Field(ge=0.0, le=1.0)
    recommended_route: str
    eta_minutes: int
    rationale: str


class DispatchRecommendation(BaseModel):
    """Dispatch recommendation for a single incident — always awaiting commander approval."""

    incident_id: str
    status: str = "AWAITING_COMMANDER_APPROVAL"
    primary_team: Optional[TeamScore] = None
    secondary_team: Optional[TeamScore] = None
    resource_gap_flagged: bool = False
    gap_description: str = ""
    commander_action_required: bool = True


class DispatchOutput(BaseModel):
    """Full dispatch output covering all active incidents in one assessment cycle."""

    total_incidents_assessed: int
    recommendations: List[DispatchRecommendation]
    resource_inventory: dict
    escalation_needed: bool
    escalation_reason: str
    disclaimer: str = (
        "All dispatch recommendations are AI-generated decision support. "
        "Every assignment requires explicit Incident Commander approval. "
        "Resource gaps require immediate escalation to SDMA. "
        "Field conditions may have changed since roster was last updated."
    )
