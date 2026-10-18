"""
Tools for the Alert & Triage Agent.

Each function is a standalone tool the ADK agent calls. Tools implement
real logic: keyword scanning, time-window deduplication, trust-weighted
confidence scoring, and multi-factor priority ranking.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, List


# ---------------------------------------------------------------------------
# Tool 1 — get_incoming_reports
# ---------------------------------------------------------------------------

def get_incoming_reports() -> dict:
    """
    Fetch all incoming raw reports from multi-source channels: official IMD/CWC
    feeds, ward officer updates, NGO field reports, community WhatsApp messages,
    and fire service radio transcripts. Returns 10 reports representing a
    realistic live-response ingest window during an active flood event.

    Returns:
        dict: fetched_at timestamp, total_reports count, and reports list.
              Each report has: report_id, source, trust_level
              (OFFICIAL/VERIFIED_PARTNER/COMMUNITY/UNVERIFIED), content,
              ward_hint, timestamp, channel.
    """
    return {
        "fetched_at": datetime.now().isoformat(),
        "total_reports": 10,
        "reports": [
            {
                "report_id": "RPT-001",
                "source": "IMD Official Feed",
                "trust_level": "OFFICIAL",
                "content": (
                    "RED alert issued — extremely heavy rainfall forecast next 18 hours. "
                    "Cumulative 24h rainfall expected 210-250 mm. Flash flood risk for "
                    "low-lying wards. All district agencies activate emergency protocols."
                ),
                "ward_hint": "DISTRICT",
                "timestamp": "2025-07-14T06:00:00+05:30",
                "channel": "official_api",
            },
            {
                "report_id": "RPT-002",
                "source": "CWC FloodWatch Official",
                "trust_level": "OFFICIAL",
                "content": (
                    "Northern Wetland Drain at DANGER level. Current water level 3.8 m "
                    "above MSL, danger threshold 3.5 m. Rate of rise: 12 cm/hr. "
                    "Overflow imminent. Ward 19 North Wetlands directly threatened."
                ),
                "ward_hint": "W19",
                "timestamp": "2025-07-14T07:00:00+05:30",
                "channel": "official_api",
            },
            {
                "report_id": "RPT-003",
                "source": "Ward Officer W12",
                "trust_level": "VERIFIED_PARTNER",
                "content": (
                    "Drain D-17 overflow signs confirmed. Water level rising near "
                    "Sector 12 main road. Waterlogged condition spreading toward old "
                    "market area. Flooding increasing. Requesting pump deployment."
                ),
                "ward_hint": "W12",
                "timestamp": "2025-07-14T07:15:00+05:30",
                "channel": "ward_officer_app",
            },
            {
                "report_id": "RPT-004",
                "source": "Community WhatsApp — Sector 12 Residents",
                "trust_level": "COMMUNITY",
                "content": (
                    "Ground floor flooding near old market Sector 12. People moving "
                    "upstairs. Water coming in from drain side. Flooding getting worse."
                ),
                "ward_hint": "W12",
                "timestamp": "2025-07-14T07:20:00+05:30",
                "channel": "social_monitoring",
            },
            {
                "report_id": "RPT-005",
                "source": "Community WhatsApp — Sector 12 Residents",
                "trust_level": "COMMUNITY",
                "content": (
                    "Same flooding in Sector 12 old market area. Water knee deep now. "
                    "Waterlogged in the lane, same place as before. Flooding not stopping."
                ),
                "ward_hint": "W12",
                "timestamp": "2025-07-14T07:30:00+05:30",
                "channel": "social_monitoring",
            },
            {
                "report_id": "RPT-006",
                "source": "NGO-1 Red Cross Field Team",
                "trust_level": "VERIFIED_PARTNER",
                "content": (
                    "Ward 19 North Wetlands access road severely waterlogged. Vehicle "
                    "cannot pass Route F. Residents appear stranded. Requesting rescue "
                    "boat for access to isolated community."
                ),
                "ward_hint": "W19",
                "timestamp": "2025-07-14T07:10:00+05:30",
                "channel": "ngo_partner_app",
            },
            {
                "report_id": "RPT-007",
                "source": "Community WhatsApp — Ward 19 Residents",
                "trust_level": "COMMUNITY",
                "content": (
                    "Route F to Ward 19 completely submerged. No vehicles can enter. "
                    "People are stuck. Elderly and children need help urgently. "
                    "Water is very high and rising."
                ),
                "ward_hint": "W19",
                "timestamp": "2025-07-14T07:15:00+05:30",
                "channel": "social_monitoring",
            },
            {
                "report_id": "RPT-008",
                "source": "Field Responder — Fire Service Unit 2",
                "trust_level": "VERIFIED_PARTNER",
                "content": (
                    "Route A NH highway near underpass partially flooded. Water level "
                    "ankle to knee near culvert. Road passable with caution currently "
                    "but deteriorating rapidly. Route A may close within 2 hours."
                ),
                "ward_hint": "W12",
                "timestamp": "2025-07-14T08:00:00+05:30",
                "channel": "responder_radio_transcribed",
            },
            {
                "report_id": "RPT-009",
                "source": "Community WhatsApp — W12 Resident",
                "trust_level": "COMMUNITY",
                "content": (
                    "Elderly couple trapped on ground floor near the clinic in Sector 12. "
                    "Water waist deep in their house. They cannot walk out. Need rescue "
                    "team urgently. Clinic road also flooded."
                ),
                "ward_hint": "W12",
                "timestamp": "2025-07-14T09:00:00+05:30",
                "channel": "social_monitoring",
            },
            {
                "report_id": "RPT-010",
                "source": "Ward Officer W19",
                "trust_level": "VERIFIED_PARTNER",
                "content": (
                    "North Primary School shelter in Ward 19 at risk. Area around school "
                    "waterlogged. Children and elderly at nearby informal settlement need "
                    "evacuation to higher ground immediately. Shelter access blocked."
                ),
                "ward_hint": "W19",
                "timestamp": "2025-07-14T08:30:00+05:30",
                "channel": "ward_officer_app",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Tool 2 — calculate_source_trust_score
# ---------------------------------------------------------------------------

def calculate_source_trust_score(trust_level: str) -> float:
    """
    Return the numerical trust weight for a given source trust level.
    Scores represent calibrated confidence in the source's historical accuracy
    and verification status. Used when computing cluster composite confidence.

    Args:
        trust_level: One of OFFICIAL, VERIFIED_PARTNER, COMMUNITY, UNVERIFIED.
                     Case-insensitive. Unknown values default to UNVERIFIED (0.4).

    Returns:
        float: Trust score between 0.0 and 1.0.
    """
    trust_map = {
        "OFFICIAL": 1.0,
        "VERIFIED_PARTNER": 0.85,
        "COMMUNITY": 0.6,
        "UNVERIFIED": 0.4,
    }
    return trust_map.get(trust_level.upper().strip(), 0.4)


# ---------------------------------------------------------------------------
# Tool 3 — deduplicate_and_cluster_reports
# ---------------------------------------------------------------------------

def deduplicate_and_cluster_reports(reports: List[Any]) -> dict:
    """
    Deduplicate and cluster incoming reports into incident groups using
    real keyword-overlap and time-window logic:

    1. Group all reports by ward_hint.
    2. Within each ward group, find reports that are within 20 minutes of
       each other AND share at least one flood-related keyword
       (flooding, flood, trapped, blocked, overflow, waterlogged, submerged).
       These form one cluster — duplicates of the same incident.
    3. For each cluster: composite_confidence =
          min(1.0, max_trust_score_in_cluster + 0.1 * (source_count - 1))
       where max_trust_score is taken from calculate_source_trust_score().

    Args:
        reports: List of raw report dicts from get_incoming_reports().

    Returns:
        dict: total_reports_processed, clusters_created,
              total_duplicates_merged, and clusters list.
              Each cluster has: cluster_id, ward, incident_type,
              merged_summary, sources_list, source_count, duplicate_count,
              composite_confidence, report_ids, earliest_timestamp.
    """
    FLOOD_KEYWORDS = [
        "flooding", "flood", "flooded", "trapped", "blocked", "block",
        "overflow", "overflowing", "waterlogged", "submerged", "water rising",
    ]

    TRUST_MAP = {
        "OFFICIAL": 1.0,
        "VERIFIED_PARTNER": 0.85,
        "COMMUNITY": 0.6,
        "UNVERIFIED": 0.4,
    }

    def _parse_ts(ts_str: str):
        try:
            return datetime.strptime(ts_str[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return None

    def _get_flood_keywords(text: str) -> set:
        lower = text.lower()
        return {kw for kw in FLOOD_KEYWORDS if kw in lower}

    def _time_diff_minutes(ts1: Any, ts2: Any) -> float:
        if ts1 is None or ts2 is None:
            return 9999.0
        return abs((ts2 - ts1).total_seconds()) / 60.0

    # Step 1: group by ward_hint
    by_ward: dict = {}
    for r in reports:
        ward = r.get("ward_hint", "UNKNOWN")
        by_ward.setdefault(ward, []).append(r)

    clusters = []
    cluster_counter = 1

    # Step 2: cluster within each ward
    for ward in sorted(by_ward.keys()):
        ward_reports = by_ward[ward]

        # Sort by timestamp ascending
        ward_reports.sort(key=lambda r: r.get("timestamp", ""))

        assigned: set = set()

        for i, seed in enumerate(ward_reports):
            if i in assigned:
                continue

            cluster = [seed]
            assigned.add(i)

            seed_ts = _parse_ts(seed.get("timestamp", ""))
            seed_kws = _get_flood_keywords(seed.get("content", ""))

            for j, candidate in enumerate(ward_reports):
                if j <= i or j in assigned:
                    continue

                cand_ts = _parse_ts(candidate.get("timestamp", ""))
                cand_kws = _get_flood_keywords(candidate.get("content", ""))

                diff = _time_diff_minutes(seed_ts, cand_ts)
                overlap = seed_kws & cand_kws

                if diff <= 20.0 and len(overlap) >= 1:
                    cluster.append(candidate)
                    assigned.add(j)

            # Step 3: build cluster record
            all_content = " ".join(r.get("content", "") for r in cluster).lower()
            source_count = len(cluster)
            duplicate_count = max(0, source_count - 1)

            # Composite confidence
            trust_scores = [
                TRUST_MAP.get(r.get("trust_level", "UNVERIFIED").upper(), 0.4)
                for r in cluster
            ]
            base_trust = max(trust_scores)
            composite_confidence = min(1.0, base_trust + 0.1 * (source_count - 1))

            # Incident type from content
            if any(kw in all_content for kw in ["trapped", "collapsed", "rescue urgently"]):
                incident_type = "trapped_residents"
            elif any(kw in all_content for kw in ["submerged", "cannot pass", "no vehicles", "access road", "route f"]):
                incident_type = "route_blockage"
            elif any(kw in all_content for kw in ["overflow", "drain", "d-17", "d-22", "d-18"]):
                incident_type = "drainage_overflow"
            elif any(kw in all_content for kw in ["shelter", "evacuation", "evacuate", "higher ground"]):
                incident_type = "evacuation_required"
            elif any(kw in all_content for kw in ["flooded", "flooding", "waterlogged"]):
                incident_type = "urban_flooding"
            else:
                incident_type = "general_alert"

            # Merged summary
            primary_content = cluster[0].get("content", "")
            if source_count > 1:
                extra = [r.get("source", "Unknown") for r in cluster[1:]]
                merged_summary = (
                    primary_content
                    + f" — Corroborated by {source_count - 1} additional source(s): "
                    + "; ".join(extra)
                )
            else:
                merged_summary = primary_content

            sources_list = [r.get("source", "Unknown") for r in cluster]

            clusters.append({
                "cluster_id": f"CLU-{cluster_counter:03d}",
                "ward": ward,
                "incident_type": incident_type,
                "merged_summary": merged_summary,
                "sources_list": sources_list,
                "source_count": source_count,
                "duplicate_count": duplicate_count,
                "composite_confidence": round(composite_confidence, 3),
                "report_ids": [r.get("report_id") for r in cluster],
                "earliest_timestamp": min(r.get("timestamp", "") for r in cluster),
                # keep all_content for downstream priority scoring
                "all_content": all_content,
            })
            cluster_counter += 1

    return {
        "total_reports_processed": len(reports),
        "clusters_created": len(clusters),
        "total_duplicates_merged": sum(c["duplicate_count"] for c in clusters),
        "clusters": clusters,
    }


# ---------------------------------------------------------------------------
# Tool 4 — prioritize_incident_queue
# ---------------------------------------------------------------------------

def prioritize_incident_queue(clusters: List[Any]) -> dict:
    """
    Score and rank each incident cluster by operational priority using a
    four-factor weighted formula:

        priority_score = (hazard_score * 0.4)
                       + (confidence   * 0.3)
                       + (vuln_score   * 0.2)
                       + (asset_risk   * 0.1)

    Where:
        hazard_score:  1.0 if "trapped"/"submerged"/"collapsed" in summary
                       0.7 if "flooded"/"blocked"/"overflow"/"waterlogged"
                       0.4 otherwise
        confidence:    cluster composite_confidence from deduplication step
        vuln_score:    1.0 if "elderly"/"children"/"child"/"disabled"
                           /"pregnant"/"infant" in summary, else 0.6
        asset_risk:    1.0 if "clinic"/"hospital"/"school"/"shelter"
                           /"substation"/"water treatment" in summary, else 0.5

    Priority tiers:
        CRITICAL >= 0.75 | HIGH >= 0.55 | MEDIUM >= 0.35 | LOW otherwise

    Args:
        clusters: List of cluster dicts from deduplicate_and_cluster_reports().

    Returns:
        dict: total_clusters_ranked, per-tier counts, and ranked incident_queue.
              Each entry adds: rank, priority, priority_score, component_scores,
              recommended_action.
    """
    ACTIONS = {
        "CRITICAL": (
            "Dispatch rescue/response team immediately. "
            "Notify incident commander. Field-verify within 30 minutes."
        ),
        "HIGH": (
            "Dispatch field verification team within 1 hour. "
            "Pre-stage required resources. Monitor for escalation."
        ),
        "MEDIUM": (
            "Schedule field check within 2 hours. "
            "Add to monitoring queue. Alert ward officer."
        ),
        "LOW": (
            "Log for situational awareness. "
            "Review if any follow-up report arrives. No immediate dispatch."
        ),
    }

    scored: list = []

    for cluster in clusters:
        # Use all_content when available; fall back to merged_summary
        text = (cluster.get("all_content") or cluster.get("merged_summary", "")).lower()

        # Hazard score
        if any(kw in text for kw in ["trapped", "submerged", "collapsed", "cannot evacuate"]):
            hazard_score = 1.0
        elif any(kw in text for kw in ["flooded", "flooding", "blocked", "overflow", "waterlogged"]):
            hazard_score = 0.7
        else:
            hazard_score = 0.4

        confidence = cluster.get("composite_confidence", 0.5)

        # Vulnerability score
        if any(kw in text for kw in ["elderly", "children", "child", "disabled", "pregnant", "infant", "bedridden"]):
            vuln_score = 1.0
        else:
            vuln_score = 0.6

        # Asset risk
        if any(kw in text for kw in ["clinic", "hospital", "school", "shelter", "substation", "water treatment"]):
            asset_risk = 1.0
        else:
            asset_risk = 0.5

        priority_score = round(
            hazard_score * 0.4
            + confidence * 0.3
            + vuln_score * 0.2
            + asset_risk * 0.1,
            3,
        )

        if priority_score >= 0.75:
            priority = "CRITICAL"
        elif priority_score >= 0.55:
            priority = "HIGH"
        elif priority_score >= 0.35:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        scored.append({
            "cluster_id": cluster["cluster_id"],
            "priority": priority,
            "priority_score": priority_score,
            "incident_type": cluster["incident_type"],
            "ward_hint": cluster["ward"],
            "composite_confidence": cluster["composite_confidence"],
            "source_count": cluster["source_count"],
            "duplicate_count": cluster["duplicate_count"],
            "merged_summary": cluster["merged_summary"],
            "sources": cluster["sources_list"],
            "recommended_action": ACTIONS[priority],
            "component_scores": {
                "hazard": hazard_score,
                "confidence": confidence,
                "vulnerability": vuln_score,
                "asset_risk": asset_risk,
            },
        })

    # Sort by priority_score descending, then by cluster_id for tie-breaking
    scored.sort(key=lambda x: (-x["priority_score"], x["cluster_id"]))
    for rank, item in enumerate(scored, 1):
        item["rank"] = rank

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in scored:
        counts[item["priority"]] += 1

    return {
        "total_clusters_ranked": len(scored),
        "critical_count": counts["CRITICAL"],
        "high_count": counts["HIGH"],
        "medium_count": counts["MEDIUM"],
        "low_count": counts["LOW"],
        "incident_queue": scored,
    }


# ---------------------------------------------------------------------------
# Tool 5 — get_source_reliability_history
# ---------------------------------------------------------------------------

def get_source_reliability_history() -> dict:
    """
    Return historical accuracy statistics for each source type based on
    post-event verification records from past flood events in the district.
    Provides calibration context for interpreting incoming report trust levels.

    Returns:
        dict: data_period, source attribution, per-source reliability stats,
              and operational guidance for trust-weighting decisions.
    """
    return {
        "data_period": "2019-2024 (5 years, 12 major flood events)",
        "source": "DDMA Post-Event Verification Records (Simulated)",
        "source_reliability": {
            "OFFICIAL_IMD_CWC": {
                "accuracy_pct": 99,
                "false_positive_pct": 1,
                "notes": (
                    "Official IMD/CWC feeds are primary ground truth. Rare "
                    "miscalibration in localized micro-watershed events not "
                    "covered by the district-level forecast grid."
                ),
                "average_lead_time_hrs": 12,
                "trust_level": "OFFICIAL",
            },
            "WARD_OFFICER": {
                "accuracy_pct": 92,
                "false_positive_pct": 4,
                "notes": (
                    "Ward officers are trained and on-ground. High reliability "
                    "for location-specific drain and road observations. "
                    "Occasional over-reporting under high-stress conditions."
                ),
                "average_lead_time_hrs": 1,
                "trust_level": "VERIFIED_PARTNER",
            },
            "FIRE_SERVICE": {
                "accuracy_pct": 95,
                "false_positive_pct": 3,
                "notes": (
                    "Fire service field reports are highly reliable for route "
                    "and access conditions. Strong ground truth for blockage "
                    "and rescue requirement assessments."
                ),
                "average_lead_time_hrs": 0.5,
                "trust_level": "VERIFIED_PARTNER",
            },
            "NGO_VERIFIED_PARTNER": {
                "accuracy_pct": 88,
                "false_positive_pct": 6,
                "notes": (
                    "Verified partner NGOs (Red Cross, welfare orgs) have good "
                    "ground presence. Slight over-reporting bias in crisis "
                    "conditions due to urgency and communication gaps."
                ),
                "average_lead_time_hrs": 1,
                "trust_level": "VERIFIED_PARTNER",
            },
            "COMMUNITY_WHATSAPP": {
                "accuracy_pct": 61,
                "false_positive_pct": 28,
                "notes": (
                    "Community WhatsApp frequently duplicates the same event. "
                    "High false positive rate due to panic, forwarded messages, "
                    "and exaggeration. Valuable for early detection and "
                    "corroboration; never use as sole basis for life-safety decisions."
                ),
                "average_lead_time_hrs": 0.25,
                "trust_level": "COMMUNITY",
            },
            "UNVERIFIED_SOCIAL_MEDIA": {
                "accuracy_pct": 43,
                "false_positive_pct": 41,
                "notes": (
                    "Unverified social media has very high noise. Useful only "
                    "as a weak signal when multiple posts describe the same "
                    "location independently."
                ),
                "average_lead_time_hrs": 0.1,
                "trust_level": "UNVERIFIED",
            },
        },
        "operational_guidance": (
            "Anchor cluster confidence on official and verified-partner sources. "
            "Community reports increase confidence through corroboration but must "
            "not trigger life-safety resource deployment without at least one "
            "verified-partner or official source confirming the same incident. "
            "Ward 19 low-connectivity wards may have fewer community reports — "
            "absence of community confirmation should not downgrade official alerts."
        ),
    }
