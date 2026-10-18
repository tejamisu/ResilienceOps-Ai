from __future__ import annotations

"""
Tools for the Risk Memory Agent.

Each function implements real computational logic over the historical_floods.json
and ward_profiles.json data files.  No stub data — every output is derived from
the source files at call time.

Tool inventory:
  1. get_flood_history          — filtered event retrieval
  2. get_recurring_hotspots     — annotated hotspot report with priority scoring
  3. compute_ward_risk_trend    — per-ward recurrence trend + hotspot matching
  4. get_lessons_by_category    — keyword-categorised lesson aggregation
  5. generate_sentinel_calibration_inputs — risk multipliers for Sentinel agent
"""

import json
import os
from typing import Any, List

_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


def _load(filename: str) -> Any:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tool 1 — get_flood_history
# ---------------------------------------------------------------------------

def get_flood_history(ward_id: str = '') -> dict:
    """
    Load historical flood event records from historical_floods.json.

    If ward_id is provided (e.g. 'W12'), only events where that ward appears
    in peak_wards_affected are returned.  Otherwise all events are returned.

    Each event includes: event_id, date, trigger, duration_hours,
    peak_wards_affected, casualties, evacuations, homes_damaged,
    critical_infra_affected, response_time_to_first_action_hrs,
    shelters_opened, relief_gaps, lessons.

    The top-level recurring_hotspots list is always included.

    Args:
        ward_id: Optional ward filter, e.g. 'W12'.  Empty string returns all.

    Returns:
        dict with keys: ward_filter, total_events, events, recurring_hotspots,
        data_period, source.
    """
    data = _load('historical_floods.json')

    if ward_id:
        events = [
            e for e in data['events']
            if ward_id in e.get('peak_wards_affected', [])
        ]
        return {
            'ward_filter': ward_id,
            'total_events': len(events),
            'events': events,
            'recurring_hotspots': data.get('recurring_hotspots', []),
            'data_period': data.get('data_period', 'N/A'),
            'source': data.get('source', 'N/A'),
        }

    return {
        'ward_filter': None,
        'total_events': len(data['events']),
        'events': data['events'],
        'recurring_hotspots': data.get('recurring_hotspots', []),
        'data_period': data.get('data_period', 'N/A'),
        'source': data.get('source', 'N/A'),
    }


# ---------------------------------------------------------------------------
# Tool 2 — get_recurring_hotspots
# ---------------------------------------------------------------------------

def get_recurring_hotspots() -> dict:
    """
    Load and annotate all recurring flood hotspots from historical_floods.json.

    For each hotspot the tool computes:
    - hotspot_id     : generated identifier (HS-001, HS-002, …)
    - location       : textual description from the data file
    - issue_type     : mapped from the 'issue' field
    - events_affected: sorted list of calendar years extracted from event IDs
    - recurrence_count: number of flood events the hotspot appeared in
    - last_occurred  : most recent calendar year
    - recommended_mitigation: mapped from 'recommended_action'
    - priority       : CRITICAL if recurrence >= 3, HIGH if 2, MEDIUM if 1

    Also returns a summary dict with total_hotspots, critical_count, high_count.

    Returns:
        dict with keys: hotspots (list), summary.
    """
    data = _load('historical_floods.json')
    raw = data.get('recurring_hotspots', [])

    result_hotspots: List[dict] = []
    critical_count = 0
    high_count = 0

    for i, hs in enumerate(raw):
        flood_events: List[str] = hs.get('flood_events', [])
        recurrence_count = len(flood_events)

        # Extract calendar years from event IDs like "FL-2024-07"
        events_affected: List[int] = []
        for ev_id in flood_events:
            parts = ev_id.split('-')
            if len(parts) >= 2:
                try:
                    events_affected.append(int(parts[1]))
                except ValueError:
                    pass

        events_affected_sorted = sorted(set(events_affected))
        last_occurred = events_affected_sorted[-1] if events_affected_sorted else None

        if recurrence_count >= 3:
            priority = 'CRITICAL'
            critical_count += 1
        elif recurrence_count >= 2:
            priority = 'HIGH'
            high_count += 1
        else:
            priority = 'MEDIUM'

        result_hotspots.append({
            'hotspot_id': f'HS-{i + 1:03d}',
            'location': hs.get('location', ''),
            'issue_type': hs.get('issue', ''),
            'events_affected': events_affected_sorted,
            'recurrence_count': recurrence_count,
            'last_occurred': last_occurred,
            'recommended_mitigation': hs.get('recommended_action', ''),
            'priority': priority,
        })

    medium_count = len(result_hotspots) - critical_count - high_count

    return {
        'hotspots': result_hotspots,
        'summary': {
            'total_hotspots': len(result_hotspots),
            'critical_count': critical_count,
            'high_count': high_count,
            'medium_count': medium_count,
        },
    }


# ---------------------------------------------------------------------------
# Tool 3 — compute_ward_risk_trend
# ---------------------------------------------------------------------------

def compute_ward_risk_trend(ward_id: str) -> dict:
    """
    Analyse the risk trend for a single ward using historical flood data and
    the ward's vulnerability profile.

    Computation:
    - event_count : how many recorded events listed ward_id in peak_wards_affected
    - trend       : WORSENING if event_count >= 3, STABLE if 2, IMPROVING if 0-1
    - vulnerability_index : vulnerability_score from ward_profiles.json
    - relevant_hotspots   : hotspot locations that mention the ward by number or ID
      (e.g. 'Ward 12' or 'W12' in the location string).  The W12-W19 shared
      stormwater channel is attributed to both W12 and W19.

    Args:
        ward_id: Ward identifier, e.g. 'W12', 'W07', 'W04', 'W19'.

    Returns:
        dict with keys: ward_id, event_count, trend, vulnerability_index,
        relevant_hotspots (list of location strings), risk_trajectory_note.
    """
    flood_data = _load('historical_floods.json')
    ward_data = _load('ward_profiles.json')

    # Count events affecting this ward
    event_count = sum(
        1 for e in flood_data['events']
        if ward_id in e.get('peak_wards_affected', [])
    )

    # Trend classification
    if event_count >= 3:
        trend = 'WORSENING'
    elif event_count >= 2:
        trend = 'STABLE'
    else:
        trend = 'IMPROVING'

    # Load vulnerability index from ward profiles
    ward_record = next(
        (w for w in ward_data['wards'] if w['ward_id'] == ward_id), None
    )
    vulnerability_index = (
        ward_record.get('vulnerability_score', 0.5) if ward_record else 0.5
    )

    # Match relevant hotspots: look for ward_id number or 'W<digits>' in location text
    # e.g. Ward 12, Ward 19, W12, W19
    ward_num_str = ward_id[1:].lstrip('0') or '0'   # 'W12' → '12', 'W07' → '7'
    ward_raw_digits = ward_id[1:]                    # 'W12' → '12', 'W07' → '07'

    relevant_hotspots: List[str] = []
    for hs in flood_data.get('recurring_hotspots', []):
        loc_lower = hs.get('location', '').lower()
        # Match "Ward <N>" or "W<digits>" variants
        if (
            f'ward {ward_num_str}' in loc_lower
            or f'w{ward_raw_digits}' in loc_lower.replace(' ', '').replace('–', '').replace('-', '')
        ):
            location = hs['location']
            if location not in relevant_hotspots:
                relevant_hotspots.append(location)

    # Trajectory note
    if trend == 'WORSENING':
        note = (
            f'{ward_id} appears in {event_count} of {len(flood_data["events"])} '
            f'recorded flood events — highest recurrence tier.  Compound vulnerability '
            f'likely.  Immediate pre-season mitigation priority.'
        )
    elif trend == 'STABLE':
        note = (
            f'{ward_id} appears in {event_count} recorded flood events.  '
            f'Risk is real but not clearly escalating.  Monitor closely for pattern shifts '
            f'and maintain resource pre-positioning.'
        )
    else:
        note = (
            f'{ward_id} appears in only {event_count} recorded event(s).  '
            f'Lower recurrence.  Maintain baseline preparedness; review if rainfall '
            f'patterns shift toward this ward.'
        )

    return {
        'ward_id': ward_id,
        'event_count': event_count,
        'trend': trend,
        'vulnerability_index': vulnerability_index,
        'relevant_hotspots': relevant_hotspots,
        'risk_trajectory_note': note,
    }


# ---------------------------------------------------------------------------
# Tool 4 — get_lessons_by_category
# ---------------------------------------------------------------------------

def get_lessons_by_category() -> dict:
    """
    Aggregate all operational lessons from every historical flood event and
    categorise them using keyword matching across five categories:

    - early_warning   : lessons about prediction, alerting, and forecast triggers
    - resource_deployment : lessons about pump/boat/team pre-positioning and dispatch
    - communication   : lessons about public messaging, signage, and connectivity gaps
    - infrastructure  : lessons about drainage, roads, shelters, and access routes
    - coordination    : lessons about inter-agency and state-level coordination

    Each category entry records the lesson text and its source event ID and year.
    Categories are checked in the order listed above; each lesson goes into the
    first matching category.  Unmatched lessons fall back to resource_deployment.

    Returns:
        dict with keys: categories (per-category lesson lists), total_lessons_extracted,
        events_analyzed.
    """
    data = _load('historical_floods.json')

    # Keyword sets per category (checked in priority order)
    CATEGORY_KEYWORDS: dict = {
        'early_warning': [
            'early warning', 'forecast', 'sdrf', '200mm', 'prediction', 'advisory',
            'trigger', 'alert threshold',
        ],
        'resource_deployment': [
            'pre-position', 'pre position', 'pump', 'boat', 'deploy', 'stage',
            'equipment', 'tanker', 'kit', 'stockpile',
        ],
        'communication': [
            'loudspeaker', 'signage', 'smartphone', 'penetration', 'sign',
            'notification', 'broadcast', 'sms', 'whatsapp',
        ],
        'infrastructure': [
            'route', 'drain', 'shelter', 'road', 'channel', 'accessibility',
            'upgrade', 'alternate', 'bridge', 'sluice',
        ],
        'coordination': [
            'support', 'state-level', 'inter-agency', 'elderly', 'assisted',
            'mobility', 'sdrf request', 'district collector', 'ngo',
        ],
    }

    categories: dict = {cat: [] for cat in CATEGORY_KEYWORDS}
    total_lessons = 0

    for event in data['events']:
        event_id = event.get('event_id', '')
        year = event.get('date', '0000')[:4]

        for lesson in event.get('lessons', []):
            lesson_lower = lesson.lower()
            placed = False
            for cat, keywords in CATEGORY_KEYWORDS.items():
                if any(kw in lesson_lower for kw in keywords):
                    categories[cat].append({
                        'lesson': lesson,
                        'source_event': event_id,
                        'source_year': year,
                    })
                    placed = True
                    break

            if not placed:
                # Fallback category
                categories['resource_deployment'].append({
                    'lesson': lesson,
                    'source_event': event_id,
                    'source_year': year,
                })

            total_lessons += 1

    return {
        'categories': categories,
        'total_lessons_extracted': total_lessons,
        'events_analyzed': len(data['events']),
    }


# ---------------------------------------------------------------------------
# Tool 5 — generate_sentinel_calibration_inputs
# ---------------------------------------------------------------------------

def generate_sentinel_calibration_inputs(ward_id: str) -> dict:
    """
    Compute calibration parameters for the Sentinel agent based on a ward's
    historical flood recurrence and proximity to critical hotspots.

    All logic is computed inline from the source data files — this tool does not
    call compute_ward_risk_trend or get_recurring_hotspots by name.

    Calibration formula:
    - historical_risk_multiplier  : 1.0 + (event_count * 0.15)
    - hotspot_adjustment          : +0.05 per CRITICAL hotspot in/adjacent to ward
                                    +0.02 per HIGH hotspot in/adjacent to ward
    - suggested_vulnerability_weight : 0.22 if trend is WORSENING, else 0.20
    - data_confidence             : HIGH if event_count >= 3, MEDIUM if 2, LOW if < 2

    Hotspot proximity is determined by matching ward number or ward ID string in
    the hotspot location text (same algorithm as compute_ward_risk_trend).

    Args:
        ward_id: Ward identifier, e.g. 'W12', 'W07', 'W04', 'W19'.

    Returns:
        dict with all calibration parameters plus a calibration_note.
    """
    flood_data = _load('historical_floods.json')
    ward_data = _load('ward_profiles.json')

    # --- Inline: event count and trend ---
    event_count = sum(
        1 for e in flood_data['events']
        if ward_id in e.get('peak_wards_affected', [])
    )

    if event_count >= 3:
        trend = 'WORSENING'
    elif event_count >= 2:
        trend = 'STABLE'
    else:
        trend = 'IMPROVING'

    # --- Inline: vulnerability index ---
    ward_record = next(
        (w for w in ward_data['wards'] if w['ward_id'] == ward_id), None
    )
    vulnerability_index = (
        ward_record.get('vulnerability_score', 0.5) if ward_record else 0.5
    )

    # --- Inline: hotspot proximity and priority counts ---
    ward_num_str = ward_id[1:].lstrip('0') or '0'
    ward_raw_digits = ward_id[1:]

    critical_hotspot_count = 0
    high_hotspot_count = 0
    adjacent_hotspot_ids: List[str] = []

    for i, hs in enumerate(flood_data.get('recurring_hotspots', [])):
        loc_lower = hs.get('location', '').lower()
        if (
            f'ward {ward_num_str}' in loc_lower
            or f'w{ward_raw_digits}' in (
                loc_lower.replace(' ', '').replace('–', '').replace('-', '')
            )
        ):
            flood_events = hs.get('flood_events', [])
            recurrence = len(flood_events)
            hotspot_id = f'HS-{i + 1:03d}'
            adjacent_hotspot_ids.append(hotspot_id)

            if recurrence >= 3:
                critical_hotspot_count += 1
            elif recurrence >= 2:
                high_hotspot_count += 1

    # --- Calibration formula ---
    historical_risk_multiplier = round(1.0 + (event_count * 0.15), 4)
    hotspot_adjustment = round(
        (critical_hotspot_count * 0.05) + (high_hotspot_count * 0.02), 4
    )
    suggested_vulnerability_weight = 0.22 if trend == 'WORSENING' else 0.20

    if event_count >= 3:
        data_confidence = 'HIGH'
    elif event_count >= 2:
        data_confidence = 'MEDIUM'
    else:
        data_confidence = 'LOW'

    # --- Plain-English calibration note ---
    hotspot_detail = (
        f'{critical_hotspot_count} CRITICAL, {high_hotspot_count} HIGH'
        if adjacent_hotspot_ids
        else 'none identified in ward vicinity'
    )
    calibration_note = (
        f'{ward_id} has been affected in {event_count} recorded events (trend: {trend}). '
        f'Adjacent hotspots: {hotspot_detail}. '
        f'Historical risk multiplier set to {historical_risk_multiplier:.2f} '
        f'and hotspot adjustment to +{hotspot_adjustment:.2f}. '
        f'Vulnerability weight recommended at {suggested_vulnerability_weight} '
        f'based on recurrence trajectory.  '
        f'Data confidence: {data_confidence} — '
        + (
            'sufficient event history for high-confidence calibration.'
            if data_confidence == 'HIGH'
            else 'moderate history — review after each new event.'
            if data_confidence == 'MEDIUM'
            else 'limited history — treat calibration as provisional.'
        )
    )

    return {
        'ward_id': ward_id,
        'event_count': event_count,
        'trend': trend,
        'vulnerability_index': vulnerability_index,
        'adjacent_hotspot_ids': adjacent_hotspot_ids,
        'critical_hotspot_count': critical_hotspot_count,
        'high_hotspot_count': high_hotspot_count,
        'historical_risk_multiplier': historical_risk_multiplier,
        'hotspot_adjustment': hotspot_adjustment,
        'suggested_vulnerability_weight': suggested_vulnerability_weight,
        'data_confidence': data_confidence,
        'calibration_note': calibration_note,
    }
