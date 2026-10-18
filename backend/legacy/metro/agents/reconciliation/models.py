"""
Pydantic models for the Reconciliation Agent output.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class IncidentResponseRecord(BaseModel):
    """Per-incident response time and rating record."""

    incident_id: str
    ward_id: str
    type: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    response_time_minutes: int = Field(ge=0)
    rating: Literal["EXCELLENT", "GOOD", "ACCEPTABLE", "DELAYED"]
    status: Literal["RESOLVED", "ESCALATED", "ACTIVE"]
    teams_assigned: List[str]


class AARSection(BaseModel):
    """A single named section of the After-Action Review."""

    section_name: str
    items: List[str]


class AARDraft(BaseModel):
    """Structured After-Action Review draft for District Incident Commander review."""

    event_name: str
    event_date: str
    generated_at: str
    summary_bullets: List[str]
    what_worked: List[str]
    gaps_identified: List[str]
    corrective_actions: List[AARSection]
    commendations: List[str]
    status: str
