"""The ResilienceOps agents for the Wayanad scenario, in lifecycle order."""
from . import (forecast_impact, risk_memory, preparedness, field_intel, dispatch, ground_truth,
               communications, relief_coverage, damage_assessment, reconciliation, orchestrator)

AGENTS = {m.NAME: m for m in (forecast_impact, risk_memory, preparedness, field_intel, dispatch, ground_truth,
                               communications, relief_coverage, damage_assessment, reconciliation, orchestrator)}
