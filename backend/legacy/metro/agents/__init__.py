from .sentinel import sentinel_agent
from .triage import triage_agent
from .field_intel import field_intel_agent
from .dispatch import dispatch_agent
from .communication import communication_agent
from .damage_assessment import damage_assessment_agent
from .reconciliation import reconciliation_agent
from .risk_memory import risk_memory_agent
from .preparedness import preparedness_agent

ALL_AGENTS = {
    "sentinel": sentinel_agent,
    "triage": triage_agent,
    "field_intel": field_intel_agent,
    "dispatch": dispatch_agent,
    "communication": communication_agent,
    "damage_assessment": damage_assessment_agent,
    "reconciliation": reconciliation_agent,
    "risk_memory": risk_memory_agent,
    "preparedness": preparedness_agent,
}
