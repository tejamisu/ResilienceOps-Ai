# Incident Report sheet — image analysis & extracted design system

Source: Ron Design Lab reference (`references/rondesignlab/`, image 12 + companion image 9).
Method: image-to-code skill, steps 2–4. Step 1 skipped: the reference image is the design source.

## 1. Reading the photo correctly
| Observation in photo | What it means in the UI |
| --- | --- |
| Whole screen slopes ~5° down to the right; bottom rows blurred | Camera tilt + depth of field. Not UI. Labels/arrows share baselines. |
| "Bus 4120" ghosted at the very top, ✕ half visible | Sheet is **scrolled**; header fades out under a top mask. |
| No Bus pill / bell visible | Top bar scrolled away with content. |
| Cards sit on one continuous glass surface | Single full-bleed sheet; no card-in-card. |

## 2. Layout (390 × 844 device, 12px bezel)
- Sheet: full width, top corners 36px radius, inner gutter 12px.
- Card stack gap: 12px. Card radius: 30px. Address pill radius: fully round, height 68px.
- Damage card: title row → 18px → gauge row. Gauge column ≈ 50% of card, readout ≈ 24%, 14px gap.
- Telemetry: title row → 18px → 3 rows, 14px row gap; label left, value right-aligned.
- Shadow beneath each card: soft dark band (≈ 0 14px 30px -12px, 50% black).

## 3. Typography — Outfit (closest open match to the reference geometric sans)
| Role | Size / weight | Colour |
| --- | --- | --- |
| Sheet title | 24 / 300 | ink |
| Card title | 21 / 300 | ink |
| Address, values | 15.5–16 / 400 | ink |
| Labels, caption | 13–15 / 400 | ink-2 |
| Gauge axis labels | 13 / 400 italic | ink-2 |
| Readout numeral | 52 / 200, tabular, −0.02em | ink; final digit ink-3 |
| Unit "%" | 18 / 300, baseline-aligned | ink-2 |
Reference uses ~300 for small text; raised to 400 below 20px for legibility (WCAG / quality bar).

## 4. Colour tokens (contrast verified on worst-case map patch)
| Token | Value | Use | Contrast |
| --- | --- | --- | --- |
| ink | #F4F6F4 | primary text | ≥ 7.2:1 |
| ink-2 | #D0D6D2 | secondary text | ≥ 5.3:1 |
| ink-3 | #B0B8B3 | dimmed numeral digit (large only) | ≥ 3.9:1 |
| critical | #FF7D71 | critical segments, alert dot | ≥ 3.2:1 |
| track | white @ 30% | gauge track (decorative) | n/a — meaning carried by text |
| sheet | rgb(58 67 63) @ 78% + blur 24px | glass surface | — |
| card | white @ 5.5% over sheet, 1px white @ 8% hairline | cards | — |

## 5. Components
- **Glass pill** (address): text + 44px copy button; copies with a polite live-region confirmation.
- **Card header**: title + 44px ↗ link (accessible name names the destination).
- **Damage gauge**: axis labels · 6px rounded track with red / dark / white segments · 6px tick ruler (every 6px) with red and white overlay dashes. Exposed to AT as one image with a text description.
- **Readout**: split numeral (integer bright, decimal dim) + small unit + caption.
- **Definition list** for telemetry (`dl/dt/dd`).

## 6. Interaction
- Content scrolls under a 64px top fade mask; header title opacity tracks scroll.
- Loads at the reference's scroll position; scroll up to reveal title, Bus pill and bell.
- Focus: 2px white ring, 3px offset. Targets ≥ 44px. Motion disabled under reduced-motion.
