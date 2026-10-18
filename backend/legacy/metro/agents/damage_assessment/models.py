"""
Pydantic models for the Damage Assessment Agent output.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class WardDamageProfile(BaseModel):
    """Structural and financial damage summary for a single ward."""

    ward_id: str
    flooded_structures: int = Field(ge=0)
    collapsed_buildings: int = Field(ge=0)
    road_sections_damaged: int = Field(ge=0)
    drainage_failures: int = Field(ge=0)
    structural_damage_severity: Literal["SEVERE", "MODERATE", "MINOR"]
    damage_pct: float = Field(ge=0.0)
    monetary_loss_estimate: float = Field(ge=0.0)
    displaced_count: int = Field(ge=0)


class DamageReport(BaseModel):
    """District-level compiled damage report for SDRF compensation submission."""

    report_id: str
    district: str
    generated_at: str
    ward_profiles: List[WardDamageProfile]
    district_totals: Dict[str, Any]
    state_compensation_eligible: bool
    report_status: str
