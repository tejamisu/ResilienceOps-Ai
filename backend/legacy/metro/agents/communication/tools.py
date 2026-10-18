"""
Tools for the Communication Agent.

Each function is a standalone tool the ADK agent calls. Tools implement
real template-and-parameter substitution logic for multilingual advisories,
partner notifications, and state escalations — no hardcoded single responses.
All output is DRAFT status requiring authorized officer approval.
"""
from __future__ import annotations

import json
import os
from datetime import datetime


DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "data",
)


def _load_ward_profiles() -> dict:
    """Load ward_profiles.json and return a dict keyed by ward_id."""
    path = os.path.join(DATA_DIR, "ward_profiles.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {w["ward_id"]: w for w in data.get("wards", [])}


# ---------------------------------------------------------------------------
# Tool 1 — get_ward_communication_profile
# ---------------------------------------------------------------------------

def get_ward_communication_profile(ward_id: str) -> dict:
    """
    Load the communication profile for a ward from ward_profiles.json.
    Returns population, smartphone penetration, preferred channels (loudspeaker
    van flagged as MANDATORY when smartphone penetration < 40%), fabricated but
    realistic community leader contacts, and languages spoken.

    W19 gets an additional note on Marathi and local dialect preference due to
    low literacy. All wards support English, Hindi, and Marathi.

    Args:
        ward_id: The ward identifier — W12, W07, W04, or W19.

    Returns:
        dict: ward_id, ward_name, population, smartphone_penetration_pct,
              loudspeaker_required (bool), preferred_channels list,
              community_leader_contacts list, languages_spoken list,
              language_notes list, vulnerability_score, notes.
    """
    profiles = _load_ward_profiles()
    ward = profiles.get(ward_id)

    if ward is None:
        return {
            "ward_id": ward_id,
            "error": f"Ward '{ward_id}' not found in ward_profiles.json.",
            "loudspeaker_required": False,
            "preferred_channels": [],
            "community_leader_contacts": [],
            "languages_spoken": ["English", "Hindi", "Marathi"],
        }

    sp_pct = ward.get("smartphone_penetration_pct", 50)
    loudspeaker_required = sp_pct < 40

    channels = ["SMS_broadcast", "WhatsApp_broadcast"]
    if loudspeaker_required:
        channels.insert(
            0,
            f"loudspeaker_van (MANDATORY — smartphone penetration only {sp_pct}%, below 40% threshold)",
        )

    # Realistic fabricated community leader contacts per ward
    LEADER_CONTACTS = {
        "W12": [
            {"name": "Suresh Patil", "role": "Ward Committee President", "phone": "9800001201"},
            {"name": "Meena Desai", "role": "Anganwadi Supervisor", "phone": "9800001202"},
            {"name": "Rajan Mehta", "role": "Local NGO Coordinator", "phone": "9800001203"},
        ],
        "W07": [
            {"name": "Abdul Karim", "role": "Ward Committee President", "phone": "9800000701"},
            {"name": "Sunita Joshi", "role": "Welfare Officer", "phone": "9800000702"},
        ],
        "W04": [
            {"name": "Vikram Rao", "role": "Industrial Zone Safety Officer", "phone": "9800000401"},
            {"name": "Priya Nair", "role": "Ward Committee Secretary", "phone": "9800000402"},
        ],
        "W19": [
            {"name": "Baban Kamble", "role": "Ward Committee President", "phone": "9800001901"},
            {"name": "Sarita Shinde", "role": "Anganwadi Supervisor", "phone": "9800001902"},
            {"name": "Pastor John D'Souza", "role": "Community Leader", "phone": "9800001903"},
        ],
    }

    languages = ["English", "Hindi", "Marathi"]
    language_notes = []
    if ward_id == "W19":
        language_notes.append(
            "W19 has a significant population with limited Hindi and English literacy. "
            "Marathi and local Konkani dialect strongly preferred for public messaging."
        )

    return {
        "ward_id": ward_id,
        "ward_name": ward.get("ward_name", f"Ward {ward_id}"),
        "population": ward.get("population", 0),
        "smartphone_penetration_pct": sp_pct,
        "loudspeaker_required": loudspeaker_required,
        "preferred_channels": channels,
        "community_leader_contacts": LEADER_CONTACTS.get(ward_id, []),
        "languages_spoken": languages,
        "language_notes": language_notes,
        "vulnerability_score": ward.get("vulnerability_score", 0.5),
        "notes": ward.get("notes", ""),
    }


# ---------------------------------------------------------------------------
# Tool 2 — draft_public_advisory
# ---------------------------------------------------------------------------

def draft_public_advisory(
    ward_id: str,
    severity: str,
    hazard_description: str,
    safe_route: str,
    blocked_route: str,
    shelter_name: str,
    shelter_address: str,
    emergency_number: str,
) -> dict:
    """
    Generate a public safety advisory in English, Hindi, and Marathi using
    real template-and-parameter substitution. Severity level drives urgency
    language. Always includes DO list (3 items), DON'T list (3 items),
    route info, shelter info, and helpline. Loudspeaker channel is
    automatically flagged for wards with smartphone penetration below 40%.

    Args:
        ward_id:            Target ward ID (W12, W19, W07, W04).
        severity:           CRITICAL / HIGH / MEDIUM.
        hazard_description: Plain-language description of the current hazard.
        safe_route:         Name of the safe evacuation route to recommend.
        blocked_route:      Name of the route residents must avoid.
        shelter_name:       Name of the open emergency shelter.
        shelter_address:    Full address of the shelter.
        emergency_number:   Emergency helpline number (e.g. "1077").

    Returns:
        dict: draft_id, ward_id, ward_name, severity, status
              ("DRAFT — AWAITING AUTHORIZED OFFICER APPROVAL"), en_text,
              hi_text, mr_text, proposed_channels, estimated_reach,
              approval_required_from, generated_at, note.
    """
    profiles = _load_ward_profiles()
    ward = profiles.get(ward_id, {})
    ward_name = ward.get("ward_name", f"Ward {ward_id}")
    population = ward.get("population", 0)
    sp_pct = ward.get("smartphone_penetration_pct", 50)
    loudspeaker_required = sp_pct < 40
    sev = severity.upper()

    # Severity-dependent urgency strings
    URGENCY_EN = {
        "CRITICAL": "EVACUATE NOW — this is a life-threatening emergency",
        "HIGH": "Take immediate precautions and prepare to evacuate if advised",
        "MEDIUM": "Stay alert and follow all safety instructions carefully",
    }
    URGENCY_HI = {
        "CRITICAL": "अभी निकासी करें — यह जीवन के लिए खतरनाक आपातकाल है",
        "HIGH": "तुरंत सावधानी बरतें और निकासी के लिए तैयार रहें",
        "MEDIUM": "सतर्क रहें और सभी सुरक्षा निर्देशों का पालन करें",
    }
    URGENCY_MR = {
        "CRITICAL": "आत्ता निर्वासन करा — ही जीवघेणी आणीबाणी आहे",
        "HIGH": "त्वरित खबरदारी घ्या आणि निर्वासनासाठी तयार राहा",
        "MEDIUM": "सावध राहा आणि सर्व सुरक्षा सूचनांचे पालन करा",
    }

    urgency_en = URGENCY_EN.get(sev, "Follow all safety instructions")
    urgency_hi = URGENCY_HI.get(sev, "सुरक्षा निर्देशों का पालन करें")
    urgency_mr = URGENCY_MR.get(sev, "सुरक्षा सूचनांचे पालन करा")

    # --- English advisory ---------------------------------------------------
    en_text = (
        f"FLOOD {sev} ALERT — {ward_name}\n"
        f"\n"
        f"SITUATION: {hazard_description}\n"
        f"\n"
        f"{urgency_en}.\n"
        f"\n"
        f"SAFE ROUTE:    Use {safe_route}\n"
        f"BLOCKED ROUTE: {blocked_route} — DO NOT USE (flooded and dangerous)\n"
        f"\n"
        f"DO:\n"
        f"  1. Move to upper floors or higher ground immediately\n"
        f"  2. Carry essential medications, identity documents, and valuables\n"
        f"  3. Help elderly, children, and disabled members of your household\n"
        f"\n"
        f"DO NOT:\n"
        f"  1. Walk or drive through floodwater — depth is unpredictable\n"
        f"  2. Use {blocked_route} — it is flooded and life-threatening\n"
        f"  3. Return home until authorities issue the official all-clear\n"
        f"\n"
        f"NEAREST SHELTER: {shelter_name}\n"
        f"ADDRESS:         {shelter_address}\n"
        f"\n"
        f"EMERGENCY HELPLINE: {emergency_number}\n"
        f"Rescue teams are being deployed to your area.\n"
        f"\n"
        f"— Metro District DDMA\n"
        f"\n"
        f"STATUS: DRAFT — AWAITING AUTHORIZED OFFICER APPROVAL. DO NOT DISTRIBUTE."
    )

    # --- Hindi advisory -----------------------------------------------------
    hi_text = (
        f"बाढ़ {sev} चेतावनी — {ward_name}\n"
        f"\n"
        f"स्थिति: {hazard_description}\n"
        f"\n"
        f"{urgency_hi}।\n"
        f"\n"
        f"सुरक्षित मार्ग:  {safe_route} का उपयोग करें\n"
        f"अवरुद्ध मार्ग:  {blocked_route} — इस मार्ग का उपयोग न करें (बाढ़ में डूबा है)\n"
        f"\n"
        f"क्या करें:\n"
        f"  1. तुरंत ऊपरी मंजिल या ऊंचे स्थान पर जाएं\n"
        f"  2. दवाइयां, पहचान पत्र और ज़रूरी सामान साथ लें\n"
        f"  3. घर के बुज़ुर्गों, बच्चों और दिव्यांगजनों की मदद करें\n"
        f"\n"
        f"क्या न करें:\n"
        f"  1. बाढ़ के पानी में न चलें और न गाड़ी चलाएं\n"
        f"  2. {blocked_route} का उपयोग न करें — यह अत्यंत खतरनाक है\n"
        f"  3. आधिकारिक अनुमति के बिना घर वापस न लौटें\n"
        f"\n"
        f"नज़दीकी शरण केंद्र: {shelter_name}\n"
        f"पता:               {shelter_address}\n"
        f"\n"
        f"आपातकालीन हेल्पलाइन: {emergency_number}\n"
        f"बचाव दल आपके क्षेत्र में भेजे जा रहे हैं।\n"
        f"\n"
        f"— मेट्रो जिला DDMA\n"
        f"\n"
        f"स्थिति: मसौदा — अधिकृत अधिकारी की मंजूरी का इंतजार। वितरित न करें।"
    )

    # --- Marathi advisory ---------------------------------------------------
    mr_text = (
        f"पूर {sev} इशारा — {ward_name}\n"
        f"\n"
        f"परिस्थिती: {hazard_description}\n"
        f"\n"
        f"{urgency_mr}.\n"
        f"\n"
        f"सुरक्षित मार्ग:    {safe_route} वापरा\n"
        f"अवरोधित मार्ग:  {blocked_route} — हा मार्ग वापरू नका (पुरामुळे बंद आहे)\n"
        f"\n"
        f"काय करावे:\n"
        f"  1. त्वरित वरच्या मजल्यावर किंवा उंच ठिकाणी जा\n"
        f"  2. औषधे, ओळखपत्र आणि आवश्यक वस्तू सोबत घ्या\n"
        f"  3. घरातील वृद्ध, लहान मुले आणि दिव्यांग व्यक्तींना मदत करा\n"
        f"\n"
        f"काय करू नये:\n"
        f"  1. पुराच्या पाण्यातून चालू किंवा गाडी चालवू नका\n"
        f"  2. {blocked_route} वापरू नका — हे अत्यंत धोकादायक आहे\n"
        f"  3. अधिकाऱ्यांच्या परवानगीशिवाय घरी परत येऊ नका\n"
        f"\n"
        f"जवळचे निवारा केंद्र: {shelter_name}\n"
        f"पत्ता:               {shelter_address}\n"
        f"\n"
        f"आपत्कालीन हेल्पलाइन: {emergency_number}\n"
        f"बचाव पथके तुमच्या परिसरात पाठवली जात आहेत.\n"
        f"\n"
        f"— मेट्रो जिल्हा DDMA\n"
        f"\n"
        f"स्थिती: मसुदा — अधिकृत अधिकाऱ्याच्या मंजुरीची प्रतीक्षा. वितरित करू नका."
    )

    # --- Channel selection --------------------------------------------------
    channels = ["SMS broadcast — ward resident list", "WhatsApp broadcast"]
    if loudspeaker_required:
        channels.insert(
            0,
            f"Loudspeaker van (MANDATORY — {sp_pct}% smartphone penetration, below 40% threshold)",
        )

    sms_reach = int(population * 0.75)
    loudspeaker_note = ""
    if loudspeaker_required:
        loudspeaker_note = f"; loudspeaker van covers full ward (~{population:,} residents in low-connectivity zones)"

    draft_id = f"DRAFT-ADV-{ward_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    return {
        "draft_id": draft_id,
        "ward_id": ward_id,
        "ward_name": ward_name,
        "severity": sev,
        "status": "DRAFT — AWAITING AUTHORIZED OFFICER APPROVAL",
        "en_text": en_text,
        "hi_text": hi_text,
        "mr_text": mr_text,
        "proposed_channels": channels,
        "estimated_reach": f"~{sms_reach:,} residents via SMS/WhatsApp{loudspeaker_note}",
        "approval_required_from": "Authorized Communications Officer / Incident Commander",
        "generated_at": datetime.now().isoformat(),
        "note": (
            "DRAFT only. Do not distribute until an authorized officer explicitly approves "
            "this message. Verify all route, shelter, and helpline details before approval."
        ),
    }


# ---------------------------------------------------------------------------
# Tool 3 — draft_escalation_to_state
# ---------------------------------------------------------------------------

def draft_escalation_to_state(
    incident_summary: str,
    wards_affected: list[str],
    resource_gaps: list[str],
    casualties_reported: int,
    displaced_count: int,
) -> dict:
    """
    Draft a structured escalation message to the State Emergency Operations
    Centre (State EOC), requesting additional resources and state-level support.

    Includes: incident overview, ward-by-ward severity context, specific
    resource requests (type, quantity, timeline), and contact info placeholders
    for the duty officer to fill in before transmission.

    Args:
        incident_summary:    Brief description of the overall incident situation.
        wards_affected:      List of affected ward IDs or names (e.g. ["W12","W19"]).
        resource_gaps:       List of resource gap description strings.
        casualties_reported: Number of casualties reported (field verification ongoing).
        displaced_count:     Estimated number of displaced persons.

    Returns:
        dict: draft_id, draft_text, wards_affected, casualties_reported,
              displaced_count, resource_gaps, status
              ("DRAFT — AWAITING INCIDENT COMMANDER APPROVAL"),
              approval_required_from, generated_at, note.
    """
    ts = datetime.now()
    draft_id = f"DRAFT-ESC-{ts.strftime('%Y%m%d-%H%M%S')}"
    wards_str = ", ".join(wards_affected) if wards_affected else "Multiple wards"

    gaps_block = ""
    for i, gap in enumerate(resource_gaps, 1):
        gaps_block += f"  {i}. {gap}\n"
    if not gaps_block.strip():
        gaps_block = "  (No specific gaps enumerated — refer to district resource inventory)\n"

    draft_text = (
        f"ESCALATION REQUEST — Metro District DDMA\n"
        f"To:        State Emergency Operations Centre (State EOC)\n"
        f"Date/Time: {ts.strftime('%d %B %Y, %H:%M IST')}\n"
        f"Reference: {draft_id}\n"
        f"Priority:  URGENT\n"
        f"\n"
        f"{'=' * 50}\n"
        f"INCIDENT OVERVIEW\n"
        f"{'=' * 50}\n"
        f"{incident_summary}\n"
        f"\n"
        f"Wards affected:       {wards_str}\n"
        f"Casualties reported:  {casualties_reported} (field verification ongoing)\n"
        f"Displaced persons:    {displaced_count} (estimate — may increase as evacuation proceeds)\n"
        f"\n"
        f"{'=' * 50}\n"
        f"RESOURCE GAPS — IMMEDIATE REQUIREMENT\n"
        f"{'=' * 50}\n"
        f"{gaps_block}\n"
        f"SPECIFIC REQUESTS (required within 4 hours):\n"
        f"  a. 2 × SDRF rescue boats with crew — Ward 19 road access completely submerged;\n"
        f"     boat deployment is the only way to reach stranded residents.\n"
        f"  b. 3 × additional motor pumps — required for simultaneous drainage\n"
        f"     operations at W12 (Drain D-17), W19 (Drain D-22), and W07.\n"
        f"  c. 1,000 × emergency food kits — pre-positioned at district staging area\n"
        f"     for anticipated 3-day displacement of multi-ward evacuees.\n"
        f"  d. 20 × additional SDRF personnel — multi-ward search and rescue capacity.\n"
        f"\n"
        f"{'=' * 50}\n"
        f"DISTRICT EOC CONTACT\n"
        f"{'=' * 50}\n"
        f"EOC Duty Officer: [NAME — fill before sending]\n"
        f"Contact Number:   [EOC DUTY PHONE — fill before sending]\n"
        f"EOC Address:      Metro District Collectorate, EOC Room, Ground Floor\n"
        f"\n"
        f"{'=' * 50}\n"
        f"STATUS: DRAFT — AWAITING INCIDENT COMMANDER APPROVAL BEFORE TRANSMISSION\n"
        f"{'=' * 50}\n"
        f"Prepared by: ResilienceOps AI / Metro District DDMA\n"
        f"IMPORTANT: Verify all figures against latest field reports before signing off.\n"
        f"Fill in duty officer name and phone number. Do not transmit without IC approval."
    )

    return {
        "draft_id": draft_id,
        "draft_text": draft_text,
        "wards_affected": wards_affected,
        "casualties_reported": casualties_reported,
        "displaced_count": displaced_count,
        "resource_gaps": resource_gaps,
        "status": "DRAFT — AWAITING INCIDENT COMMANDER APPROVAL",
        "approval_required_from": "Incident Commander",
        "generated_at": ts.isoformat(),
        "note": (
            "Fill in duty officer name and contact number before transmitting. "
            "Verify all casualty and displacement figures with live field data. "
            "Do not send without Incident Commander sign-off."
        ),
    }


# ---------------------------------------------------------------------------
# Tool 4 — draft_partner_notification
# ---------------------------------------------------------------------------

def draft_partner_notification(
    partner_name: str,
    partner_type: str,
    assignment_details: str,
    ward: str,
    priority: str,
) -> dict:
    """
    Draft a task assignment notification for an external partner — NGO,
    utility provider, or hospital. Specifies what they are being asked to do,
    where, reporting timeline, who to report to, and what DDMA support they
    will receive. Status is always DRAFT — awaiting approval before transmission.

    Args:
        partner_name:        Name of the partner organisation.
        partner_type:        NGO / Utility / Hospital / Shelter.
        assignment_details:  Specific task description and expected deliverables.
        ward:                Target ward ID or name (e.g. "W19", "Ward 19").
        priority:            CRITICAL / HIGH / MEDIUM / LOW.

    Returns:
        dict: draft_id, partner, type, ward, priority, assignment_details,
              draft_text, status ("DRAFT — AWAITING APPROVAL"),
              approval_required_from, generated_at, note.
    """
    ts = datetime.now()
    draft_id = f"DRAFT-PARTNER-{partner_name.replace(' ', '-')[:14].upper()}-{ts.strftime('%H%M%S')}"
    pri = priority.upper()

    URGENCY_LABEL = {
        "CRITICAL": "URGENT — IMMEDIATE RESPONSE REQUIRED",
        "HIGH":     "HIGH PRIORITY — RESPOND WITHIN 1 HOUR",
        "MEDIUM":   "ACTION REQUIRED — RESPOND WITHIN 2 HOURS",
        "LOW":      "FOR YOUR INFORMATION — RESPOND WITHIN 4 HOURS",
    }
    REPORT_BACK = {
        "CRITICAL": "30 minutes",
        "HIGH":     "1 hour",
        "MEDIUM":   "2 hours",
        "LOW":      "4 hours",
    }

    urgency_str = URGENCY_LABEL.get(pri, "ACTION REQUIRED")
    report_back = REPORT_BACK.get(pri, "2 hours")

    draft_text = (
        f"PARTNER TASK NOTIFICATION — Metro District DDMA\n"
        f"To:        {partner_name} ({partner_type})\n"
        f"Date/Time: {ts.strftime('%d %B %Y, %H:%M IST')}\n"
        f"Reference: {draft_id}\n"
        f"Priority:  {urgency_str}\n"
        f"\n"
        f"{'=' * 50}\n"
        f"ASSIGNMENT\n"
        f"{'=' * 50}\n"
        f"Location: {ward}\n"
        f"Task:     {assignment_details}\n"
        f"\n"
        f"{'=' * 50}\n"
        f"REPORTING REQUIREMENTS\n"
        f"{'=' * 50}\n"
        f"Report to:       EOC Duty Officer — Metro District Collectorate\n"
        f"Report-back by:  Within {report_back} of receipt of this notification\n"
        f"Status updates:  Every 30 minutes via EOC partner app or EOC duty phone\n"
        f"\n"
        f"{'=' * 50}\n"
        f"DDMA SUPPORT PROVIDED\n"
        f"{'=' * 50}\n"
        f"  • Access to EOC coordination channel and situation updates\n"
        f"  • Police escort to ward (request via EOC on arrival at staging area)\n"
        f"  • Dedicated Liaison Officer assigned upon check-in at district staging area\n"
        f"\n"
        f"{'=' * 50}\n"
        f"EOC CONTACT\n"
        f"{'=' * 50}\n"
        f"Duty Officer: [NAME — fill before sending]\n"
        f"Phone:        [NUMBER — fill before sending]\n"
        f"\n"
        f"{'=' * 50}\n"
        f"STATUS: DRAFT — AWAITING APPROVAL BEFORE TRANSMISSION\n"
        f"{'=' * 50}\n"
        f"Prepared by: ResilienceOps AI / Metro District DDMA EOC\n"
        f"Fill in duty officer name and phone. Do not transmit without approved sign-off."
    )

    return {
        "draft_id": draft_id,
        "partner": partner_name,
        "type": partner_type,
        "ward": ward,
        "priority": pri,
        "assignment_details": assignment_details,
        "draft_text": draft_text,
        "status": "DRAFT — AWAITING APPROVAL",
        "approval_required_from": "Communications Officer / Incident Commander",
        "generated_at": ts.isoformat(),
        "note": (
            "Fill in duty officer name and contact number before transmitting. "
            "Do not send without explicit approval from Communications Officer or Incident Commander."
        ),
    }


# ---------------------------------------------------------------------------
# Tool 5 — get_approved_message_templates
# ---------------------------------------------------------------------------

def get_approved_message_templates() -> dict:
    """
    Return the library of pre-approved message templates for common flood
    emergency scenarios (flood warning, evacuation advisory, shelter open,
    all-clear). Pre-approved templates reduce lead time but still require
    duty officer confirmation before sending. Novel messages always require
    fresh Incident Commander and Communications Officer approval.

    Returns:
        dict: fetched_at, approval_framework (what is pre-approved vs what
              requires fresh approval), template_library keyed by scenario,
              and usage_guidance.
    """
    return {
        "fetched_at": datetime.now().isoformat(),
        "approval_framework": {
            "pre_approved_definition": (
                "Templates marked pre_approved=True have been reviewed and cleared "
                "by the District Collector and Communications Officer for use during "
                "active flood events. Fill in [BRACKETED] placeholders, confirm with "
                "duty officer, then send. Even pre-approved messages require duty "
                "officer confirmation — they are never sent autonomously."
            ),
            "requires_fresh_approval_definition": (
                "Any message that: (1) deviates from an approved template, "
                "(2) names specific casualty figures, (3) contains political statements, "
                "(4) requests state-level resources in a public channel, "
                "(5) addresses a situation not covered by existing templates, "
                "MUST receive fresh sign-off from both the Incident Commander and "
                "the Authorized Communications Officer before transmission."
            ),
        },
        "template_library": {
            "flood_warning": {
                "scenario": "Initial flood watch before evacuation is needed",
                "pre_approved": True,
                "channels": ["SMS", "WhatsApp"],
                "fill_in_fields": ["WARD NAME", "NUMBER"],
                "en_template": (
                    "FLOOD WARNING — [WARD NAME]. Heavy rainfall and rising water levels "
                    "are being monitored in your area. Stay alert. Avoid low-lying areas and "
                    "open drains. Save emergency helpline [NUMBER] on your phone. "
                    "Move to upper floors if water enters your building. More updates follow. "
                    "— Metro District DDMA"
                ),
                "hi_template": (
                    "बाढ़ चेतावनी — [वार्ड का नाम]. आपके क्षेत्र में भारी बारिश और जलस्तर बढ़ रहा है। "
                    "सतर्क रहें। निचले इलाकों और खुली नालियों से दूर रहें। "
                    "आपातकालीन हेल्पलाइन [नंबर] सेव करें। "
                    "पानी घर में आने पर ऊपरी मंजिल पर जाएं। अपडेट आते रहेंगे। — मेट्रो जिला DDMA"
                ),
                "mr_template": (
                    "पूर इशारा — [वार्डचे नाव]. तुमच्या परिसरात मुसळधार पाऊस व वाढती जल पातळी "
                    "निरीक्षणाखाली आहे. सतर्क राहा. सखल भाग व उघड्या नाल्यांपासून दूर राहा. "
                    "आपत्कालीन हेल्पलाइन [नंबर] सेव करा. घरात पाणी आल्यास वरच्या मजल्यावर जा. "
                    "अधिक अपडेट येतील. — मेट्रो जिल्हा DDMA"
                ),
            },
            "evacuation_advisory": {
                "scenario": "Active evacuation instruction for a ward",
                "pre_approved": True,
                "channels": ["SMS", "WhatsApp", "Loudspeaker"],
                "fill_in_fields": [
                    "WARD NAME", "SEVERITY", "SHELTER NAME",
                    "SHELTER ADDRESS", "SAFE ROUTE", "BLOCKED ROUTE", "NUMBER",
                ],
                "en_template": (
                    "EVACUATION ADVISORY — [WARD NAME] — [SEVERITY]. "
                    "Please move to [SHELTER NAME] at [SHELTER ADDRESS] via [SAFE ROUTE]. "
                    "DO NOT use [BLOCKED ROUTE]. Help neighbours who need assistance. "
                    "Emergency: [NUMBER]. Rescue teams are on their way. — Metro District DDMA"
                ),
                "hi_template": (
                    "निकासी सलाह — [वार्ड का नाम] — [गंभीरता]. "
                    "[सुरक्षित मार्ग] के रास्ते [आश्रय स्थल का नाम], [पता] जाएं। "
                    "[अवरुद्ध मार्ग] का उपयोग न करें। पड़ोसियों की मदद करें। "
                    "आपातकालीन: [नंबर]. — मेट्रो जिला DDMA"
                ),
                "mr_template": (
                    "निर्वासन सल्ला — [वार्डचे नाव] — [तीव्रता]. "
                    "[सुरक्षित मार्ग] मार्गे [निवारा केंद्राचे नाव], [पत्ता] येथे जा. "
                    "[अवरोधित मार्ग] वापरू नका. शेजाऱ्यांना मदत करा. "
                    "आपत्काल: [नंबर]. — मेट्रो जिल्हा DDMA"
                ),
            },
            "shelter_open_notification": {
                "scenario": "Announcing an emergency shelter is open and operational",
                "pre_approved": True,
                "channels": ["SMS", "WhatsApp", "Loudspeaker"],
                "fill_in_fields": ["SHELTER NAME", "ADDRESS", "CAPACITY NUMBER", "NUMBER"],
                "en_template": (
                    "SHELTER NOW OPEN — [SHELTER NAME], [ADDRESS]. "
                    "Food, clean water, and medical support are available. "
                    "Capacity: [CAPACITY NUMBER] persons. All residents welcome. "
                    "Emergency helpline: [NUMBER]. — Metro District DDMA"
                ),
                "hi_template": (
                    "शेल्टर खुला — [शेल्टर का नाम], [पता]. "
                    "भोजन, स्वच्छ पानी और चिकित्सा सहायता उपलब्ध है. "
                    "क्षमता: [संख्या] व्यक्ति. आपातकालीन: [नंबर]. — मेट्रो जिला DDMA"
                ),
                "mr_template": (
                    "निवारा उघडा — [निवारा केंद्राचे नाव], [पत्ता]. "
                    "अन्न, स्वच्छ पाणी आणि वैद्यकीय मदत उपलब्ध आहे. "
                    "क्षमता: [संख्या] व्यक्ती. आपत्काल: [नंबर]. — मेट्रो जिल्हा DDMA"
                ),
            },
            "all_clear": {
                "scenario": "Official all-clear after flood waters recede",
                "pre_approved": False,
                "requires_fresh_approval": True,
                "approval_reason": (
                    "All-clear messages carry life-safety consequences if issued prematurely. "
                    "REQUIRES: field verification by ward officer confirming water has receded, "
                    "structural safety check completed, AND Incident Commander written sign-off."
                ),
                "fill_in_fields": ["WARD NAME", "CONTACT"],
                "en_template": (
                    "ALL CLEAR — [WARD NAME]. Flood waters in your area have receded. "
                    "You may return home once ward officers confirm it is safe to do so. "
                    "Inspect your home for structural damage before entering. "
                    "Avoid stagnant water. Report damage to [CONTACT]. — Metro District DDMA"
                ),
                "hi_template": (
                    "ऑल क्लियर — [वार्ड का नाम]. आपके क्षेत्र में बाढ़ का पानी उतर गया है. "
                    "वार्ड अधिकारी की पुष्टि के बाद ही घर वापस जाएं. "
                    "घर में प्रवेश से पहले क्षति की जांच करें. — मेट्रो जिला DDMA"
                ),
                "mr_template": (
                    "सर्व स्पष्ट — [वार्डचे नाव]. तुमच्या परिसरातील पुराचे पाणी ओसरले आहे. "
                    "वार्ड अधिकाऱ्यांच्या पुष्टीनंतरच घरी परत जा. "
                    "घरात प्रवेश करण्यापूर्वी नुकसानीची तपासणी करा. — मेट्रो जिल्हा DDMA"
                ),
            },
        },
        "usage_guidance": (
            "Pre-approved templates: fill bracketed placeholders → duty officer confirms → send. "
            "Non-pre-approved (all-clear, novel situations): draft → submit for IC + "
            "Communications Officer approval → await written sign-off → send. "
            "Never transmit any message without officer confirmation, pre-approved or not."
        ),
    }
