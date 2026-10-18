# Command dashboard — image analysis & content mapping

Reference: Ron Design Lab "Traffic Management" desktop dashboard (image 13).
Content: ResilienceOps AI brief — Wayanad, **Respond** phase, event WYN-2026-001, the moment the landslide report has been corroborated and a dispatch decision is waiting.
Method: image-to-code skill, steps 2–4 (the reference is the design source, so no image generation).

## 1. Layout read from the reference (normalised to 1440 × 900)
| Zone | Reference | Measured feel |
| --- | --- | --- |
| Top bar | Logo + pill nav, active pill filled; search/status/bell/avatar at top right over the map | 72px tall; nav floats over the map edge |
| Left rail | Solid near-black column, ~33% width: type-count pills → 2 status tiles → KPI line chart → 2×2 vehicle cards | 16px gutters, 12px gaps, 24–28px radii |
| Map | Full-bleed dark satellite + hillshade, desaturated; white roads, dashed alternates, yellow highway, hatched zone, coloured pins | Occupies everything right of the rail |
| Map title | Huge thin "Traffic Management" + chips (vehicle ▾, map ▾) | ~44px / 200 weight |
| Right panel | Glass "Warning" accordion; red-tinted alert with affected list + AI "Recommend" | ~340px, floats 20px from the edges |
| Bottom | Two glass cards: "Schedule Offset" table, "Live Passenger Volume" segmented chart | ~240px tall, spans the map width |
| Map controls | Round + / locate / − | 44px circles above the bottom card |

## 2. Content mapping (transit → Wayanad response)
| Reference element | ResilienceOps equivalent | Why |
| --- | --- | --- |
| Live Map · Fleet · Routes … | **Prepare · Respond · Recover** + Timeline · Reports · Audit | Phase-aware nav from the Codex blueprint |
| 24 Bus / 100 Taxi … | 6 Rescue · 4 Medical · 3 Road crews · 5 Camps (filters) | Resource types the commander allocates |
| Online 12 / Offline 4 | Deployed 9 / Unreachable 2 | Team readiness; offline = safety risk |
| Operational Efficiency 78.3% | Rainfall, Meppadi gauge 168.4 mm (observed vs forecast, landslide-watch threshold) | The hazard driver, with prediction vs reality |
| Bus cards (line-art bus, GPS/LTE, route, timeline) | Team cards: Fire & Rescue tender, PWD excavator, ambulance, relief truck | Same anatomy; damaged/delayed area tinted |
| Traffic Management | **Wayanad Response** + event chip + layers/legend + "Simulated scenario" | Honest framing for general viewers |
| Passenger Load 87% | Meppadi relief camp occupancy 87% | Anchored floating card on the map |
| Warning → Capacity issues → Recommend | **Needs your decision** → critical incident → affected → AI recommends → Approve / Edit / Why | Human-in-the-loop approval (P0 orchestration layer) |
| Schedule Offset ±2.5 min table | Time to dispatch 12.4 min + live task tracker (status, ETA vs plan) | Accountability: every task has an owner |
| Live Passenger Volume 142,580 | People in relief camps 1,284, per camp with capacity | Relief coverage (P1) |

## 3. Design system (extends `design-analysis.md`)
- Surfaces: page #111413 · rail #161918 · card #1E2221 · glass rgba(26 30 28 / .78) + 20px blur · hairline white 7%.
- Ink: #F2F4F2 / #B9C0BB / #8A928D (large numerals only).
- Signal colours (always with icon + text): critical #FF6B5F · warning #F0A04B · ok #7BD88F · camp pin #3B8BDD · medical pin #E07A9B · crew pin #C9D14A.
- Type: Outfit; 44/200 map title, 52/200 KPI numerals with dimmed decimal, 21/300 card titles, 13–15/400 body.
- Components: pill nav, filter pills (aria-pressed), status tiles, line-art vehicle card, accordion alert card, glass chips, round map controls, data table, toast live region, first-run guide card.

## 4. Deliberate deviations from the reference
- Thin weights only at ≥ 20px; small text at 400 (WCAG legibility on dark glass).
- The reference's red badge-only alerts gain text labels and icons (no colour-only meaning).
- Brand mark is our own (terrain contour lines), not the agency's.
- Avatar uses initials (persona is fictional), not a stock face.
