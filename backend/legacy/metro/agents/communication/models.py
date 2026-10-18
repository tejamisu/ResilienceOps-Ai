"""
Pydantic models for the Communication Agent output.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AdvisoryDraft(BaseModel):
    """A multilingual public safety advisory draft awaiting officer approval."""

    draft_id: str
    ward_id: str
    severity: str
    status: str  # always "DRAFT — AWAITING AUTHORIZED OFFICER APPROVAL"
    en_text: str
    hi_text: str
    mr_text: str
    proposed_channels: List[str]
    estimated_reach: str
    approval_required_from: str
    generated_at: str


class PartnerNotification(BaseModel):
    """A task assignment notification draft for an external partner organisation."""

    draft_id: str
    partner: str
    type: str
    purpose: str
    draft_text: str
    status: str  # always "DRAFT — AWAITING APPROVAL"
    approval_required_from: str


class EscalationDraft(BaseModel):
    """A structured escalation message to the State EOC, awaiting Incident Commander approval."""

    draft_id: str
    draft_text: str
    wards_affected: List[str]
    casualties_reported: int
    displaced_count: int
    status: str  # always "DRAFT — AWAITING INCIDENT COMMANDER APPROVAL"
    approval_required_from: str
    generated_at: str


class CommunicationOutput(BaseModel):
    """Full communication output for one response cycle — all items are DRAFTS."""

    total_drafts: int
    public_advisories: List[AdvisoryDraft]
    partner_notifications: List[PartnerNotification]
    escalation_draft: Optional[EscalationDraft] = None
    important_note: str = (
        "ALL messages in this output are DRAFTS. None have been sent. "
        "Each item requires explicit approval from the named authorized officer "
        "before any transmission. Never distribute without officer sign-off."
    )
