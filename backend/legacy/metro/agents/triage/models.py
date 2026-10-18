"""
Pydantic models for the Triage Agent output.
"""
from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class IncidentCluster(BaseModel):
    cluster_id: str
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    priority_score: float = Field(ge=0.0, le=1.0)
    incident_type: str
    ward_hint: str
    composite_confidence: float = Field(ge=0.0, le=1.0)
    source_count: int
    duplicate_count: int
    merged_summary: str
    sources: List[str]
    recommended_action: str


class TriageOutput(BaseModel):
    total_reports_received: int
    clusters_created: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    incident_queue: List[IncidentCluster]
    processing_timestamp: str
    disclaimer: str = (
        "This triage output is AI-generated decision support. "
        "All incident prioritizations and confidence scores require "
        "review by an authorized control-room operator before action is taken. "
        "Community-sourced reports must be field-verified before committing "
        "life-safety resources."
    )
