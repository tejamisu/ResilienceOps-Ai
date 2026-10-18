"""
Pydantic models for the Field Intelligence Agent output.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ExtractedIncident(BaseModel):
    incident_id: str
    type: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    severity_score: float = Field(ge=0.0, le=1.0)
    ward_id: str
    ward_name: str
    vulnerability_flags: List[str]
    resource_needs: List[str]
    asset_proximity: List[str]
    forecast_alignment: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str
    status: Literal["VERIFIED", "AWAITING_VERIFICATION", "ESCALATED", "RESOLVED"]
    summary: str
    timestamp: str


class FieldIntelOutput(BaseModel):
    total_active: int
    verified_count: int
    pending_count: int
    escalated_count: int
    resolved_count: int
    critical_incidents: List[ExtractedIncident]
    all_incidents: List[ExtractedIncident]
    generated_at: str
    disclaimer: str = (
        "Field intelligence output is AI-generated from raw text reports. "
        "Severity scores, ward geocoding, and resource recommendations require "
        "review by an authorized field supervisor or ward officer before action. "
        "AWAITING_VERIFICATION incidents must be field-confirmed before "
        "committing life-safety resources."
    )
