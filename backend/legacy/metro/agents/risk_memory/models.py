from __future__ import annotations

"""
Data models for the Risk Memory Agent.

Defines typed records for hotspot analysis, ward risk trends,
Sentinel calibration parameters, and the top-level agent output.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class HotspotRecord:
    """A recurring flood-failure hotspot derived from historical event data."""

    hotspot_id: str
    location: str
    issue_type: str
    recurrence_count: int
    priority: str  # CRITICAL | HIGH | MEDIUM
    recommended_mitigation: str


@dataclass
class WardRiskTrend:
    """Risk trend analysis for a single ward over the recorded event window."""

    ward_id: str
    event_count: int
    trend: str  # WORSENING | STABLE | IMPROVING
    vulnerability_index: float
    relevant_hotspots: List[str]
    risk_trajectory_note: str


@dataclass
class SentinelCalibration:
    """Calibration parameters passed to the Sentinel agent for a specific ward."""

    ward_id: str
    historical_risk_multiplier: float
    hotspot_adjustment: float
    suggested_vulnerability_weight: float
    data_confidence: str  # HIGH | MEDIUM | LOW
    calibration_note: str


@dataclass
class RiskMemoryOutput:
    """Top-level summary of a complete Risk Memory Agent analysis run."""

    wards_analyzed: List[str]
    hotspots_total: int
    critical_hotspots: int
    lessons_extracted: int
    calibration_outputs: List[SentinelCalibration]
