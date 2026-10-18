from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class CriticalAsset(BaseModel):
    type: str
    name: str
    flood_risk: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    notes: str = ""


class EvacuationRoute(BaseModel):
    route_id: str
    name: str
    status: Literal["OPEN", "AT_RISK", "LIKELY_BLOCKED", "BLOCKED"]
    recommended: bool
    notes: str = ""


class RecommendedAction(BaseModel):
    priority: int
    action: str
    owner: str
    deadline_hrs: float
    resource_required: str = ""


class WardRiskAssessment(BaseModel):
    ward_id: str
    ward_name: str
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    priority_score: float = Field(ge=0.0, le=1.0)
    hazard_severity_score: float = Field(ge=0.0, le=1.0)
    vulnerability_score: float = Field(ge=0.0, le=1.0)
    infrastructure_risk_score: float = Field(ge=0.0, le=1.0)
    data_confidence: Literal["HIGH", "MEDIUM_HIGH", "MEDIUM", "LOW"]
    population_exposure_estimate_low: int
    population_exposure_estimate_high: int
    life_safety_risk: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    rationale: str
    critical_assets_at_risk: list[CriticalAsset]
    evacuation_routes: list[EvacuationRoute]
    recommended_actions: list[RecommendedAction]
    historical_context: str


class ResourceGap(BaseModel):
    resource_type: str
    quantity_needed: int
    quantity_available: int
    gap: int
    notes: str = ""


class EscalationRequest(BaseModel):
    required: bool
    reason: str = ""
    resources_to_request: list[str] = []
    escalate_to: str = ""


class SentinelOutput(BaseModel):
    incident_id: str
    generated_at: str
    trigger_source: str
    trigger_summary: str
    forecast_period_hrs: int
    overall_district_risk: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    total_wards_assessed: int
    wards_critical: int
    wards_high: int
    wards_medium: int
    wards_low: int
    total_population_at_risk_low: int
    total_population_at_risk_high: int
    ward_assessments: list[WardRiskAssessment]
    resource_gaps: list[ResourceGap]
    escalation: EscalationRequest
    data_sources: list[str]
    confidence: Literal["HIGH", "MEDIUM_HIGH", "MEDIUM", "LOW"]
    important_disclaimer: str = (
        "This is AI-generated decision support. All priority rankings, "
        "population estimates, and recommendations require review and approval "
        "by an authorized incident commander before action is taken. "
        "Estimates are ranges based on available data, not exact predictions."
    )
