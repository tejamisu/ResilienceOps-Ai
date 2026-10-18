# ResilienceOps AI — Design System

**Version 1.0 · 12 Oct 2026** · Extracted from the shipped Respond view (`test-run/wayanad-dashboard.html`) and the phone test screen (`test-run/incident-report-v2.html`).
Use this to build **Prepare, Respond and Recover** so they read as one product.

- Visual direction: Ron Design Lab — dark terrain map, frosted glass, thin geometric type, colour only for meaning.
- Quality bar: WCAG 2.2 AA, Nielsen's 10 heuristics, Shneiderman's 8 golden rules, Google PAIR / Microsoft HAX for human-in-the-loop AI.
- Context: Wayanad, Kerala · DDMA / DEOC Wayanad · persona Ananya Menon, Incident Commander.

---

## 1. Principles

| # | Principle | What it means on screen |
| --- | --- | --- |
| 1 | **The map is the stage** | The full-bleed terrain map is the background of every desktop phase view; panels float on it. |
| 2 | **Surface the next decision** | Each phase has exactly one decision panel ("Needs your decision"). Everything else is supporting context. |
| 3 | **AI recommends, a person approves** | Every AI output shows: recommendation → evidence → confidence → Approve / Edit / Why. Nothing executes on its own. |
| 4 | **Colour means something** | The UI is monochrome. Red, amber and green appear only to signal state, and always with an icon and a word. |
| 5 | **Quiet until it matters** | Thin type, low-contrast chrome and soft glass, so the one critical item is the loudest thing on screen. |
| 6 | **Honest data** | Every value carries a source, a time and a confidence; simulated data is labelled "Simulated scenario". |

---

## 2. Colour

### 2.1 Surfaces (dark theme — the only theme)

| Token | Value | Use |
| --- | --- | --- |
| `--page` | `#111413` | App background, behind everything |
| `--rail` | `#161918` | Left rail (solid, not glass) |
| `--card` | `#1E2221` | Cards in the rail |
| `--card-hi` | `#252A28` | Hover state, active nav pill |
| `--glass` | `rgba(26, 30, 28, 0.78)` + blur | Anything floating over the map |
| `--glass-hi` | `rgba(40, 45, 42, 0.82)` | Hover on glass controls |
| `--hair` | `rgba(255, 255, 255, 0.07)` | Default 1px border on cards and glass |
| `--hair-2` | `rgba(255, 255, 255, 0.12)` | Stronger border: hover, selected, secondary buttons, table rules |
| Map base | `#0E1211` | Shown while tiles load |

### 2.2 Ink (text and icons)

| Token | Value | Use | Rule |
| --- | --- | --- | --- |
| `--ink` | `#F2F4F2` | Primary text, values, icons, primary button fill | Any size |
| `--ink-2` | `#B9C0BB` | Secondary text, labels, meta, axis text, placeholders | Any size |
| `--ink-3` | `#8A928D` | The **dimmed part of a split numeral** only (e.g. ".4" in 168.4) | **Large text only (≥ 24px)** |
| Dark ink | `#141716` | Text on the white primary button | — |

### 2.3 Signal colours

| Token | Value | Meaning | On-colour text |
| --- | --- | --- | --- |
| `--critical` | `#FF6B5F` | Life-safety, blocked, awaiting a critical decision | `#1B0F0E` |
| `--warning` | `#F0A04B` | At risk, delayed, near capacity, medium confidence, threshold lines, simulated marker | `#24160A` |
| `--ok` | `#7BD88F` | Done, on site, en route, connected, readiness ✓ | `#10301A` |
| `--critical-bg` | `rgba(110, 38, 33, 0.55)` | Critical alert card fill (border `rgba(255,107,95,.22)`) | — |
| Warning alert fill | `rgba(110, 72, 30, 0.42)` | Warning alert card fill (border `rgba(240,160,75,.2)`) | — |

### 2.4 Map category colours (pins only)

| Token | Value | Category |
| --- | --- | --- |
| `--camp` | `#3B8BDD` | Relief camp / shelter |
| `--medical` | `#E07A9B` | Hospital, clinic, ambulance post |
| `--crew` | `#C9D14A` | Road / engineering crew (icon in `#1A1C10`) |
| Place dot | `#D9DDD9` with `#3A403C` centre | Town / locality reference (non-interactive) |
| Highway | `#C9B04A` @ 85% | National highway (NH 766) |
| Road | `#E6E9E6` @ 60% | Secondary road |

### 2.5 Measured contrast (WCAG 2.2)

| Background | ink | ink-2 | ink-3 | critical | warning | ok |
| --- | --- | --- | --- | --- | --- | --- |
| page `#111413` | 16.8 | 10.0 | 5.8 | 6.6 | 8.7 | 10.6 |
| rail `#161918` | 16.0 | 9.5 | 5.5 | 6.3 | 8.3 | 10.2 |
| card `#1E2221` | 14.6 | 8.7 | 5.0 | 5.8 | 7.5 | 9.2 |
| card-hi `#252A28` | 13.2 | 7.9 | 4.6 | 5.2 | 6.8 | 8.4 |
| glass over brightest map | 11.5 | 6.9 | 4.0 | 4.6 | 6.0 | 7.3 |
| critical alert fill | 11.3 | 6.8 | 3.9 | 4.5 | 5.9 | 7.2 |
| warning alert fill | 10.2 | 6.1 | 3.5 | **4.05** | 5.3 | 6.5 |

Other pairs: primary button `#141716` on `#F2F4F2` = 16.3 · count badge `#1B0F0E` on critical = 6.7 · amber severity dot text `#24160A` on warning = 8.2.

**Usage rules from the table**
- `ink-3` never for body text; only the dim half of a large numeral.
- Never put critical-red **text** on a warning alert fill (4.05:1). Use ink or warning instead.
- Map labels sitting directly on imagery need the label text-shadow (§5.4); contrast against the brightest tiles is still unverified (see `design-checklist.md`).

---

## 3. Gradients, overlays and effects

| Name | Value | Where |
| --- | --- | --- |
| Map tile treatment | `filter: saturate(.6) brightness(.86) contrast(1.08)` on the tile pane | Turns green satellite imagery into the reference's grey-green terrain |
| Hillshade | Esri World Hillshade, `opacity .4`, `mix-blend-mode: multiply` | Adds relief to mountains |
| Top scrim | `linear-gradient(180deg, rgba(17,20,19,.82) 0%, transparent 18%)` | Keeps the nav readable over the map |
| Bottom scrim | `linear-gradient(0deg, rgba(17,20,19,.60) 0%, transparent 22%)` | Seats the bottom cards |
| Left scrim | `linear-gradient(90deg, rgba(22,25,24,.55) 0%, transparent 12%)` | Blends the map into the rail |
| Selected card glow | `radial-gradient(120% 90% at 0% 0%, #6F7A70 0%, #343B37 38%, var(--card) 72%)` | The selected team card (the reference's "Bus 6023" highlight) |
| Avatar fill | `linear-gradient(140deg, #7C8A7D, #3B443E)` | Initials avatar |
| Glass blur | `backdrop-filter: blur(20px) saturate(1.2)` | All glass surfaces |
| Phone glass blur | `blur(24px) saturate(1.15)` on the sheet; buttons `blur(18px) saturate(1.2)` | Mobile |
| Card top sheen (phone) | `linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.055) 60%)` + `inset 0 1px 0 rgba(255,255,255,.05)` | Phone cards |
| Phone top fade | `mask-image: linear-gradient(180deg, transparent 0 44px, #000 108px)` | Content scrolling under the status bar |

### 3.1 Shadows

| Token | Value | Use |
| --- | --- | --- |
| Pin shadow | `0 4px 14px rgba(0,0,0,.45)` | Map pins |
| Floating marker | `0 8px 24px rgba(0,0,0,.4)` | Unit marker, floating map card |
| Phone card | `0 14px 30px -12px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.05)` | Phone cards |
| Device | `0 0 0 2px #262A28, 0 40px 80px -20px rgba(0,0,0,.45)` | Phone mock frame only |
| Live dot halo | `0 0 0 4px rgba(123,216,143,.15)` | "Live" indicator |
| Knob ring | `0 0 0 3px rgba(0,0,0,.35)` | Timeline scrubber knob |
| Text on map | `0 2px 24px rgba(0,0,0,.5)` (titles) · `0 1px 6px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9)` (labels) | Any text placed directly on imagery |

Desktop rail cards have **no drop shadow**; depth comes from fill contrast and the 1px hairline.

---

## 4. Typography

**Family:** Outfit (Google Fonts, weights 200 / 300 / 400 / 500), fallback `system-ui, sans-serif`. Antialiased. Tabular figures (`font-variant-numeric: tabular-nums`) on every number that updates.

### 4.1 Type scale

| Role | Size / weight / line-height | Tracking | Colour | Example |
| --- | --- | --- | --- | --- |
| Display (map title) | 44 / 200 / 1.05 | −0.01em | ink + title shadow | "Wayanad Response" |
| Hero numeral | 46 / 200 / 0.95 | −0.02em | ink + ink-3 split | "168.4" |
| Phone numeral | 52 / 200 / 0.9 | −0.02em | ink + ink-3 split | "73.3" |
| Stat tile numeral | 34 / 200 / 1 | 0 | ink | "9" |
| Floating card numeral | 34 / 200 / 1 | 0 | ink | "87%" |
| Panel heading | 19 / 300 | 0 | ink | "Needs your decision" |
| Phone sheet title | 24 / 300 / 1.2 | 0 | ink | "Incident Report Details" |
| Phone card title | 21 / 300 | 0.003em | ink | "Details of the damage" |
| Card title (desktop) | 17 / 400 | 0 | ink | "Rainfall · Meppadi gauge" |
| Brand wordmark | 16 / 400 | 0.01em | ink | "ResilienceOps" |
| Unit after a numeral | 16 / 300 (phone 18 / 300) | 0 | ink-2 | "mm", "%" |
| Body / alert title | 14 / 400 / 1.35–1.4 | 0 | ink | Alert titles, nav, buttons |
| Secondary | 13 / 400 | 0 | ink or ink-2 | Card subtitle, affected list, table cells |
| Meta / caption | 12 / 400 | 0 | ink-2 | Timestamps, chip text, legends |
| Micro | 11 / 400 | 0 | ink-2 | Chart axes, scrubber times, badge numbers |
| Axis label (phone) | 13 / 400 italic | 0 | ink-2 | "Left" / "Right" |

### 4.2 Typography rules
- **Weight floor:** 200–300 only at ≥ 19px. Anything smaller is 400 (500 for badges and the primary button).
- **Split numerals:** the integer plus the decimal point in ink; the trailing digit(s) in ink-3; the unit in ink-2 at about a third of the size, baseline-aligned, 4–5px gap.
- **Separators:** use a middle dot " · " between metadata ("Critical · 6 min ago · Corroborated by 3 sources").
- **Sentence case** everywhere. No all-caps labels.
- Screen-reader numerals: visible split digits are `aria-hidden`; a `.sr-only` span carries the full value ("168.4 millimetres").

---

## 5. Layout and spacing

### 5.1 Spacing scale (px)
`2 · 4 · 6 · 8 · 10 · 12 · 14 · 16 · 18 · 20 · 22 · 24 · 28`
- **12** is the default gap between cards and between stacked blocks.
- **8** is the gap between chips, buttons and pills.
- **16 / 20** are rail and floating-panel inset gutters.

### 5.2 Desktop frame (designed at 1440 × 900)

```
┌──────────── top bar 72px (floats over everything) ───────────────────────┐
│ brand · phase nav                     search · live · help · bell · avatar│
├── rail 468px ──┬──────────────── map stage (fills) ──────────────────────┤
│ 84px top pad   │ map title block (left 28, top 92)   decision panel      │
│ filters        │                                     (right 20, top 84,  │
│ stat tiles     │                                      w 360)             │
│ KPI chart card │ map controls (left 24, bottom 284)                      │
│ 2×2 unit cards │ ┌ bottom cards (left/right/bottom 20, h 252) ────────┐  │
│ (scrolls)      │ │ 1.35fr                    │ 1fr                    │  │
└────────────────┴─┴───────────────────────────┴────────────────────────┴──┘
```

| Region | Size | Position / padding |
| --- | --- | --- |
| Top bar | height 72 | padding 0 20 0 22; transparent over the top scrim |
| Rail | width 468 | padding 84 16 20; vertical stack, gap 12; scrolls |
| Map stage | remaining width | z-index 1 (own stacking context) |
| Map title block | max-width 520 | left 28, top 92 |
| Decision panel | width 360 | right 20, top 84; max-height = 100% − 84 − 290; scrolls |
| Bottom cards | height 252 | left 20, right 20, bottom 20; columns 1.35fr / 1fr; gap 12 |
| Map controls | 44px circles | left 24, bottom 284; gap 8 |
| Toast | auto | centred, 290 from bottom |

**Below 1180px** the layout stacks: top bar wraps, rail then map (70vh, radius 24) then decision panel then bottom cards, all static. *(A proper tablet pass is still open in the checklist.)*

### 5.3 Card sizes and ratios

| Component | Size | Ratio / notes |
| --- | --- | --- |
| Filter pill | 4-up grid in 436px → ~103 × 46 | ≈ 2.2 : 1 |
| Stat tile | 2-up → ~212 × 96 min | ≈ 2.2 : 1; label top-left, numeral bottom-right |
| KPI chart card | full rail width × ~300 | Header, value row, chart 150 tall, legend |
| Unit card | 2-up → ~212 × ~330 | ≈ 2 : 3 portrait; vehicle art 74 tall, minimap 76 tall |
| Floating map card | 200 × ~110 | Anchored 18–22px from its pin |
| Decision alert | 332 wide (panel minus padding) | Collapsed ~72 tall |
| Bottom table card | 1.35fr × 252 | — |
| Bottom chart card | 1fr × 252 | Chart viewBox 384 × 170 |
| Phone | 390 × 844 frame, 12 bezel | Sheet gutter 12, card gap 12 |

### 5.4 Corner radius

| Token / use | Radius |
| --- | --- |
| Pills, buttons, chips, search, badges, nav items | `999px` (fully round) |
| Round icon buttons, pins, avatar | `50%` |
| `--r-lg` cards, decision panel, bottom cards | `26px` |
| Phone cards | `30px` · phone sheet top corners `36px` · phone address pill `999px` |
| `--r-md` stat tiles, alert cards, guide, floating map card | `20px` |
| Legend popover | `18px` |
| Filter pills | `16px` |
| Inner callouts (Why, state), minimap | `14px` / `12px` |
| Focus ring | `12px` |
| Keyboard hint (`kbd`) | `6px` |
| Phone device / screen | `56px` / `44px` |

**Nesting rule:** inner radius = outer radius − padding (e.g. 26 card − 14 padding ≈ 12–14 inner). Never put a card with the same radius inside another card.

### 5.5 Padding

| Component | Padding |
| --- | --- |
| KPI card | 18 20 14 |
| Bottom card | 18 20 |
| Unit card | 16 16 12 |
| Stat tile | 16 18 |
| Decision panel | 18 14 14; header 0 6 0 8 |
| Alert toggle | 14 14 12; body 0 14 14 46 (aligned under the title) |
| Guide card | 16 18 |
| Floating map card | 14 16 |
| Legend popover | 14 16 |
| Phone card body | 24 18 24 22 · address pill 0 8 0 22 |

---

## 6. Components

Every component below exists in the Respond view; reuse it as-is.

### 6.1 Navigation (updated 15 Oct 2026 — phases are not nav tabs)
- **Top nav** holds views only: Timeline · Reports · Audit. Prepare / Respond / Recover are **not** top-nav tabs.
- **No event chip** (removed 15 Oct 2026: one event, and its dropdown did nothing). The event ID leads the subline under the page title on every phase and view ("WYN-2026-001 · …").
- **Current phase** (16 Oct 2026; replaces the map's phase tag): an eyebrow line in `.map-head`, 8px above the page title and on its left edge (moved out of the top bar 16 Oct 2026): "Current phase" 13 ink-2 then the phase name 14 ink with an 8px dot (Prepare amber · Respond red with halo · Recover green). Text only, never a chip or control; not shown on Timeline/Reports/Audit.
- **Account menu and switchers** (18 Oct 2026, from Experimentation/phases; replaces the 340w profile menu): the avatar opens a small glass menu (280w, radius 22): who you are (name 14.5 · "role · org" 12.5 ink-2), then 44px rows **Switch phase** (current phase on the right, red dot when another phase needs attention) · **Switch role** (short role) · divider · **Open the field app (phone)**. Arrow keys, Home/End; Esc returns focus to the avatar.
  - Each switch opens a **centred dialog** over the app: scrim `rgba(11,11,11,.55)` + `blur(16px) saturate(.75)`, the app steps back to `scale(.985)` and is `inert`. Dialog 1080w max, radius 32, eyebrow 14 · title 40/300 · lede 16, three tiles (gap 22), footer with the other switch.
  - Tiles: isometric diorama (300:250, radius 24, tinted by the tile accent) · name 22/500 with a dot · a short purpose 14.5 ink-2 ("Before the storm" / "During the event" / "After the event") · **one status chip** (28h pill, 13): Done = quiet ring + green ✓ "Done · Day 0, 07:05"; Now = accent tint + ring, "**Now** · 5 to approve" (the count is `#nav-count`; the tail hides at 0); Next = dashed, "Next · not active yet". Current tile: accent ring + "You're here" / "You're signed in"; on Timeline/Reports/Audit "Current phase", still clickable. Nudges from other phases ("+1", red dot) sit on the tile corner (ids `nav-prepare/-respond/-recover`).
  - Role tiles: initials disc (accent-tinted) + name, role title, one capability chip in the accent ("Approves · all phases" / "Recommends · Prepare, Respond" / "Escalates · Recover"). Role accents: Commander **gold `#e3c27a`** (not green: green means done or verified) · Analyst blue `#8ab4f8` · Coordinator violet `#c3a6f2`.
  - Behaviour: focus starts on the current tile; arrows/Home/End move, Tab is trapped; Esc, ✕ or the backdrop closes and returns focus to the avatar. Choosing: the picked tile grows, the others step back, then the page changes (420 ms) and a toast confirms on arrival. Drawings animate only on hover/focus; reduced motion removes all of it. ≤820px: tiles stack as rows (150px picture left).
  - A role's locked approval toasts "Sent to Ananya Menon, Incident Commander, for approval · from …" and changes nothing.
- **Map header (all phases):** one row — event chip · "New here?". Map key lives with the map controls on every phase; the top-bar status reads "● Simulated · <time>" (amber dot) on every phase.
- **Top-bar tools (shared shell, every phase):**
  - **Search** (combobox + listbox, `Ctrl K`): searches the page's own left-panel cards (Place / Team / Community) and decision-panel items (Decision / Task / Need); up to 8 results with the match underlined in amber and a kind tag; ↑↓ Enter Esc; choosing one selects the card (map flies) or opens the panel item (expanding it and the panel if minimised) and outlines it briefly (`.ro-hit`). Our own clear button replaces the browser's blue ×.
  - **Helpline** (headset): glass list of district contacts (DEOC 1077 · KSDMA State EOC 1070 · Police 112 · Fire & Rescue 101 · Ambulance 108) and the DEOC radio net; actions are simulated and say so.
  - **Notifications** (bell; 16 Oct 2026, ref: notification panel): glass 440w. Header "Your notifications" + icon buttons (mark all read ✓✓ · settings). Segmented tabs View all n · Critical · Unread n. Feed rows split by dotted rules: 40px avatar (AI sparkle · agency · person) with a 12px severity dot; a sentence "**Actor** verb **object**"; time on the left and age on the right ("Done" when resolved); green unread dot; then, as relevant, a quote card, an attachment card (e.g. the drafted report) or inline actions (e.g. Why this? · Approve dispatch, which still respects role permissions). Opening a row marks it read and takes you to it; focus lands on the first notification.
  - One popover open at a time (role menu included); Esc returns focus to its button; click outside closes.
- Earlier phase-tab rules below are kept for reference only.
- **Phase nav pill:** 40 tall, padding 0 16, 14px. Default ink-2 on transparent; hover ink on white 5%; **current** `card-hi` fill + inset 1px `hair-2`, `aria-current="page"`.
- **Phase states:** done = green ✓ icon before the label (plus sr-only "4 of 5 readiness tasks done") · active with work = red count badge (20px) · idle = plain.
- **Separator:** 1 × 20, `hair-2`, margin 0 8, between phases and utility views.
- **Order:** Prepare · Respond · Recover | Timeline · Reports · Audit.

### 6.2 Buttons

| Type | Spec | Use |
| --- | --- | --- |
| Primary | 40h, pad 0 16, ink fill, `#141716` text 13/500, round | The single approving action per card ("Approve dispatch") |
| Secondary | 40h, white 6% fill, `hair-2` border, ink 13/400; hover white 12% | Edit, Why this?, Got it, Review |
| Glass pill | 40h, pad 0 14, glass, 13px, 16px icon | Map chips (event, map key, help) |
| Round icon | 44 × 44 glass circle, 20px icon | Map controls, top-bar tools |
| Open link ↗ | 36 × 36 transparent circle, 18px arrow; hover white 7% | Card header "open detail" |
| Help pill | Glass pill + border `rgba(255,255,255,.28)` | "New here? How to read this view" |

One primary button per decision. Destructive actions (Reject) use secondary style plus a confirmation step.

### 6.3 Chips / status pills
- 26h, pad 0 10, radius 999, 12px, **1px border in currentColor**, transparent fill, nowrap.
- Variants: `crit` (critical), `warn` (warning), `ok` (ok), `neutral` (ink-2 text, `hair-2` border).
- Optional 12px leading icon (▲ for warnings).
- Vocabulary: Standby · En route · On site · Delayed · Blocked · Very heavy · Near capacity.

### 6.4 Badges and severity dots
- **Count badge:** 18–24 round, critical fill, `#1B0F0E` 11–13/500 text.
- **Severity dot:** 22 round, critical or warning fill with "!" in on-colour.
- **Status dot (tables):** 7px circle + text label: awaiting = critical · moving / on site = ok · delayed = warning · neutral = ink-2.

### 6.5 Stat tile
Icon (20px, filled signal shape) + label stacked top-left (ink-2 14px, gap 8); numeral 34/200 bottom-right.

### 6.6 KPI card
Header (title 17/400 + subtitle 13 ink-2 + ↗) → value row (split numeral 46/200 + unit + status chip, gap 10) → chart → inline legend (12px; solid = observed, dashed ink-2 = forecast, dashed amber = threshold).

### 6.7 Unit (team / asset) card
1. Header: name 17/400 + agency·location 12 ink-2 + ↗.
2. **Line-art vehicle** (220 × 84 viewBox, stroke 1.1, ink at 85%), with a centred **unit tag** pill: 30h, `rgba(70,76,72,.92)`, 24px letter disc (agency code: F = Fire & Rescue, C = crew, M = medical, S = supply) + call sign.
3. Meta row: status chip · signals (GPS, Radio / LTE; weak signal turns warning).
4. **Minimap** 76 tall: 14px grid in white 7%, two 4% blocks, route in ink 1.6px, start dot r4.
5. **Scrubber:** "06:00" · tick bar (1px ticks every 4px at white 28%) with a knob at progress % · "Now".
- Selected: radial glow (§3) + `hair-2` border, `aria-pressed="true"`; selecting flies the map to the unit.
- Problem state: tint the affected part of the line art with warning or critical at 35% fill (e.g. the delayed truck's doors).

### 6.8 Decision panel and alert card (the human-in-the-loop component)
- Panel: glass, radius 26; heading 19/300 + count badge.
- **Group header:** 16px icon + label 14 + "(n)" in ink-2.
- **Alert card:** radius 20; fill by severity (critical / warning / neutral white 4%).
  - Toggle row: severity dot · title 14/400 + meta 12 ink-2 ("Critical · 6 min ago · Corroborated by 3 sources") · caret (rotates 180° when open). `aria-expanded` + `aria-controls`.
  - Body, in this order:
    1. **Affected** — label 12 ink-2, then items with a 1.5px white 50% left rule; title 13 + detail 12 ink-2.
    2. **AI recommendation** — sparkle icon + sentence 13 + detail 12 ink-2 + **confidence line** 12 in warning with a clock icon ("Medium confidence — Route C last checked 18 min ago").
    3. **Why this?** — collapsible list, 12 ink-2, on black 22%, radius 14; it lists reasons **and sources**.
    4. **Actions** — Primary · Edit · Why this?
    5. **State line** — replaces the actions after approval: ok ✓ + "Approved by Ananya Menon at 12:14. Waiting for Fire & Rescue to accept." `role="status"`.
- Lifecycle shown in copy: Recommended → Approved (who, when) → Accepted (agency, when) → En route / Done.

### 6.9 Data table
13px tabular; header 12 ink-2; rows 7px vertical padding with a top `hair` rule; a leading 22px letter disc for task type; status = dot + text; "vs plan" = clock icon + delta in warning (late) or ok (early), "—" when not started.

### 6.10 Charts (inline SVG)
- Lines: observed ink 1.4px · forecast ink-2 at 85%, 1.2px, dash 3 3 · threshold warning 1.2px, dash 5 4.
- Gridlines white 6%; axis text 11px ink-2; the y-axis sits on the **right**.
- Exceedance columns: white 5% vertical bands.
- **Now** marker: 1px white 35% vertical line + "Now" label.
- Peak marker: r 3.5 ink dot.
- Segmented value lines (camp chart): one horizontal line per item (ink 1.8px; warning 2.4px when over threshold); value 15/300 above, name and % 11px below; background "noise" bars white 8–9%.
- Every chart has `role="img"` and an `aria-label` that states the finding, not just the title.
- **Comparisons across different units** (teams, beds, hours…) use **aligned rows**: name · bar against a need tick · value · status · action. Never encode them as heights in columns; labels on different baselines read as broken layout.

### 6.11 Map elements

| Element | Spec |
| --- | --- |
| Category pin | 28 circle, category fill, 2px white 85% ring, 14px white glyph, pin shadow |
| Place dot | 18 circle `#D9DDD9`, 6px dark centre; **not interactive** |
| Critical incident | 30 core (critical, 2px white ring, 16px dark glyph) + pulsing ring (2.2s, scale .6→1.6; off under reduced motion) |
| Watch incident | Same, warning colour |
| Unit marker | 54 glass circle (`rgba(160,170,160,.45)` + blur 8, 1px white 35%), 20px heading arrow rotated to bearing; dashed 1.2px white reach circle (dash 4 5) |
| Assigned route | White 3.2px, round caps |
| Alternate (unverified) | White 2.6px, dash 7 7 → turns solid once accepted |
| Blocked segment | Critical 5px |
| Risk zone | Warning 1.2px dashed outline (4 4) + 40° hatch, 1.4px strokes every 7px at 70% |
| Map label | 12 ink with double text shadow; "blocked" variant `#FFD1CC` 500 |
| Floating map card | 200w glass, radius 20; title 14 + ↗; meta 12 ink-2; numeral 34/200 + status word in warning 14 |
| Attribution | Bottom-right, 11px ink-2 on page 75%; must stay visible (Esri, Leaflet) |

### 6.11b Map layers control (Prepare; to adopt in Respond)
- A 64×64 glass **Layers** thumbnail (mini map preview + "Layers" caption) sits first in the map-controls row, before + / locate / −.
- Hover, keyboard focus or tap opens a glass tray **above** it (12px gap, radius 22): "Show on map" + one 64px mini-map tile per layer, with label and count. On = 2px ink ring + ✓ badge; off = 45% opacity, no badge. Each tile is a toggle (`aria-pressed`); the thumbnail's accessible name reports "n of 4 shown".
- Closes 250ms after the pointer leaves, when focus leaves, or on Esc (focus returns to the thumbnail).
- State class is `is-open` — never `open`, which is the ↗ link class and carries negative margins.

### 6.11c Recover components
- **Coverage states** (map zones, rail, matrix): Unserved < 40% = critical solid 2.2px + 16% fill + ▲ · Partly served 40–84% = warning dashed 6 4 + ◐ · Served ≥ 85% = ok thin 1.4px + ✓ · **Not yet assessed** = ink-2 dotted + grey hatch + ? (never shown as "fine"). Glyph shapes carry the state, so colour is never the only cue.
- **Zone label**: glass pill (rgba(17,20,19,.82), 26px) with glyph + name + coverage %; each community has a fixed side (above / below / left / right) so labels never stack; "proj." suffix when the timeline previews a future day.
- **Community card** (option C, 14 Oct 2026; replaces the need-chip grid): name + place line → **coverage numeral** 34/200 (unit 15/300 ink-2; "—" when not assessed) with status glyph + word and "n in need" right-aligned → **line-art need grid**: 3 × 2 (row 1 water drop · food bowl · medicine cross, row 2 tent · bolt · road). The grid takes the card's spare height (`flex: 1`, `container-type: size`) and icons scale to it: `min(40px, (100cqh − 10px) / 2)` — about 27px at 1440×900, 40px on taller screens. Rows sit on the caption (`align-content: end`, 10px above the caption) so spare height never opens between icons and text. Columns `space-between`, 4px inset, row gap 10, stroke 1.3: met = ink at 32% (fades back), gap = critical stroke + 35% critical tint fill, partly = warning stroke + lower-half warning tint, unknown = ink-2 dotted → **caption** 10px below the icons and just above the source line, one line each, never listing met needs: "No water, food and power" (critical) · "Partly: medicine and road" (warning) · "Everything else met" / "All needs met" (ok) · "Unknown until a team assesses it" (may wrap) → source line at the bottom. Icons carry an SVG `<title>` for hover; the card button's `aria-label` states coverage and every need. Status is never colour-only (fill and dotted outline differ too).
- **Verified-impact card** (option C, 14 Oct 2026): `<dl>`, 2×2 tiles. Each tile = number (22px/300, unit in `small`) → mini visual (12px row, `aria-hidden`) → one line "Label · Source". Visual matches the number's scale: **case dots** for small human counts (hollow `--critical` ring = open, filled `--ok` = resolved; total in text "open of 5" + sr-only "2 resolved"); **progress bar** for large counts (fill on the same grey hatch as "not yet assessed" on the map; `--warning` fill only when the remainder needs action, `--ink-2` when it's context). Number goes `--critical` only when something is open. Tiles with nothing to act on (injuries) have no visual. No fatality figures. Card is 184px at 1440×900 so the rail doesn't scroll.
- **Relief pipeline stepper**: 5 dots (Requested · Committed · En route · Delivered · Verified); done = ink, current = 12px ring in warning (ok + filled when verified); status word on the right ("Promised only", "Needs check"…). Only Verified counts as covered.
- **Lesson ruler** (Learn → Prepare, 14 Oct 2026; base = Ron Design Lab tick-ruler reference): one lesson at a time.
  - Row 1: lesson title 15/300 + place 12 ink-2 · gap in warning 12 on the right ("34 h short of plan").
  - **Tick ruler** 0 → plan, drawn at the real width (redraw on resize): minor ticks 6px, major 14px; ticks inside what actually happened are ink 1.5px, the rest white 28% 1px.
  - **Dots above**: big grey 6r at the right end = the plan, amber 5r = the miss, with its label beside it (never above, so it can't meet the title). No unlabelled dots: a dot that doesn't say what it is gets removed.
  - **Pointer markers below**: house shapes at the start and end of what happened; the one under the miss is amber like its dot, the other ink.
  - **Numbers**: hero (34/200 ink + label 13 ink-2) left-aligned under the first pointer; plan (label + 26/200 ink-2) right-aligned to the ruler end.
  - Footer (26px, text level with the timeline card's day labels): sparkle + recommended task · compact secondary "+ Add" (28px) · borderless pager ‹ n/3 › on the right. Once added, "+ Add" becomes a green ✓ (24px target) with a glass tooltip "✓ Prepare task added" on hover or focus (Esc hides it); Prepare nav gets +n.
  - Amber, never red: lessons are learning, not blame. The ruler is `aria-hidden`; an sr-only sentence states plan, actual and gap; the lesson area is `aria-live="polite"`.
- ~~Layout switch~~ and ~~Needs matrix~~: removed 17 Oct 2026 — Recover ships the Timeline layout only.
- **Map header rule**: title · subline · **one row** of controls (event switcher · view switch · help), never wrapping. A status (e.g. simulated data) is never a pill: it lives in the top-bar status chip ("● Simulated · Day 2, 09:00 IST", amber dot). Map tools (key, layers, zoom) live with the map controls, not in the header.
- **Map key control**: 44px round glass button with a list-swatch icon, after Stack in the bottom-left controls; opens a 280w glass card (radius 18, padding 14 16, gap 9) **upwards**; closes on Esc (focus returns), outside click or toggle. Tooltip "Map key" on hover/focus.
- **Product tour** (15 Oct 2026; replaces the "New here?" guide panel on **Prepare, Respond and Recover**, one shared engine, steps per page): opens automatically on the first visit (remembered in `localStorage`, `rec.tour.seen`); "New here?" reopens it.
  - Everything outside the step's area is dimmed **and blurred** (`rgba(8,10,9,.62)` + `backdrop-filter: blur(6px)`), masked with a rounded hole (radius 26, 6px outset) so the real area stays sharp; a 2px ink ring at 55% outlines it and glides between areas (0.35s, none under reduced motion).
  - **Each step previews its own feature**, not a region of the page: a step can name `crop` (a selector, or `[selector, n]` for the first n matches) and the live copy is clipped to that feature (radius 16) and fitted to the preview, so no two steps show the same picture. Steps with no crop (welcome, map) show the whole page. Examples: Respond = teams carousel · first decision card · bottom cards · the Approve/Edit/Why row; Prepare = two places · two tasks · the 24-hour outlook · the Run demo button; Recover = the communities list · the missed-community card · the bottom cards · the Assign verification row.
  - Glass card 560w, radius 26, placed **off the lit area** (right of it, else left, else above, else below; centred only when there's no area). For an area that fills most of the screen (the map), the card sits on the left over the dimmed panel and narrows to fit (min 360px), gliding 0.35s between steps: **live crop** on top (230px; a scaled, inert copy of the page centred on the area, per-step zoom) → "n of 6" (12 ink-2) → title 19/300 → one or two lines 14 ink-2 → actions: Skip (secondary) · Back · Next (primary). Last step: "Explore on my own" · "▶ Watch the recovery loop", which closes the tour and starts the demo.
  - Same six-step shape on every phase: welcome · left panel · map · decision panel · bottom cards · next action. The last step's primary button is the phase's natural next move: Prepare "▶ Run demo to 12:02" · Respond "Go to the first decision" (focuses Approve dispatch) · Recover "▶ Watch the recovery loop". Seen-state keys: `prep.tour.seen`, `resp.tour.seen`, `rec.tour.seen`.
  - Accessibility: `role=dialog` + `aria-modal`, page behind is `inert`, focus starts on the primary button and Tab stays in the card, ← → move between steps, Esc closes and returns focus. The crop is `aria-hidden`.
- **Icon-only tooltip** (`[data-tip]`): glass, 12px, radius 10, 8px off the control, above for bottom controls and below for header controls; shown on hover and `:focus-visible`.
- Rule learned twice: don't reuse an existing class name for a new state or element (`.open`, `.need` both clashed). Prefix new ones (`is-open`, `ic-need`).

### 6.11d Views: Timeline · Reports · Audit (15 Oct 2026)
Event-wide reading pages in the top nav (links, `aria-current="page"`), same top bar, **no map**: rail (468) of summary + filters, and a scrolling reading column (`.vmain`, padding 92/32/40, faint radial wash) with title 44/200 + subline "WYN-2026-001 · … · Simulated". All three read one simulated event record (`RO_EVENT`, in `test-run/views-src.html`) that matches the phase pages; no death figures.
- **Filter chips** (`.fchip`): 32h toggles, `aria-pressed`, ✓ when on, count in ink-2; a `role="status"` line "Showing n of N" + Reset. Distinct from status chips.
- **Verification chip** (`.vchip`, 24h): Verified ✓ ok solid · Estimated ◐ warning dashed · Reported ○ ink-2. **Actor disc** (30px): AI = sparkle (brighter) · Person · Agency.
- **Filters live with the list, not the rail** (16 Oct): a toolbar above each list — "Showing n of N" + Reset (only when filtered) on the left, a 40h glass "Filter" pill (icon + count badge) on the right — opening the shared **filter card** (`RO_UI.filterCard`, Timeline + Audit; swapped 16 Oct 2026). Rails hold data, not controls.
- **Filter dropdown** (16 Oct 2026; ref: dark search list; used by **Reports** since the swap — groups Status · Sent to · Priority · Day · Order): 320w, radius 18, `#0d0f0e` (darker than the cards so it reads as a layer), `role=dialog`. A sticky search field on top (42h, radius 12, focus lands there; Enter picks the first match, Esc clears then closes). Groups (Phase · Who · Kind · Verification on Timeline; Human decision · Phase · Agent on Audit) of 38h icon rows: icon · label · count · ✓ at the right when picked (`role=radio`); hover/keyboard row = white 10% highlight. Phase rows use the phase dots (amber · red · green); Audit decision icons keep their meaning colours. Picks apply at once; sticky "Reset all" footer. Typing on a row jumps to search; arrows move through the visible rows. A link can preset a group (`?view=timeline&f=recover`).
- **Timeline:** rail = **Event status as a severity curve** (option B, 16 Oct; after the curve reference): title + "● Recovery" pill with "severity easing" beneath it; hero 46/200 "Moderate"; green ▼ "Down from critical at 12:02 Day 0 · 45 h ago"; then the curve of event severity over time at real width (dashed level gridlines, each marked with a 4-bar signal glyph filled to its level — 4 red, 3 amber, 1–2 ink — instead of words; Recovery period lightly shaded; stages labelled where they began; glowing amber Now dot with a dashed drop to the Day axis). Severity source (DDMA assessment, simulated) lives in the chart's `aria-label`, not a footnote. Then **How sure the record is** (hero "15 of 24 entries verified" + aligned rows per phase: segmented bar verified / estimated (hatched) / reported, count) and **Who acted** (AI · People · Agencies trio). Main = "At a glance" strip (one mark per entry in order; diamond AI · circle person · square agency; amber = awaiting decision; phase bands, day ticks, Now line; `aria-hidden`, click opens the row) + cards per day and phase with rows: time · actor · title + "kind · actor · source" · verification chip · caret. Expanded: detail + "Open the AI trace" / "Open in <phase>" / "Open the report". Deep link `?view=timeline#e7`.
- **Full timeline drawer** (16 Oct 2026; ref: activity feed): "Open full timeline" in the At a glance header, or a click on any mark, opens a glass drawer from the right (680w, radius 26, slides 24px + fades 260 ms `cubic-bezier(0.23, 1, 0.32, 1)`; fade only under reduced motion) over a dimmed, blurred page (inert). Day · phase headings; a vertical line with a 32px icon per entry (AI sparkle · person · agency; amber ring when awaiting); a sentence "**Actor** verb" with the time on the right; an item card (kind icon · title · verification chip); an optional note with a 2px green edge (amber when awaiting) labelled by its source; links to the AI trace / phase / report. Opens scrolled to the clicked entry with a brief highlight. Esc, × or the scrim closes; focus is trapped while open and returns to the opener.
- **Reports:** rail = one card that fills the rail: "Reports · n" + a 36px round **filter icon** (count badge when filters are on) that opens a **dropdown menu** (glass, 260w, radius 18): groups Day · Sent to · Priority · Status · Order, one choice each (`menuitemradio`, ✓ + count, first option = All), list updates live, "Reset all" at the bottom; arrows/Home/End move, Esc or outside click closes. No pill toggles here, then the scrolling list (name · "Day · time · to X · priority" with Urgent ▲ red / High ↑ amber / Routine grey · Draft / Sent) and "Showing n of N · Reset". Nine items: KSDMA situation reports, NDMA summary, partner requests/updates, media briefings. **Who it's for** lives with the draft, not the rail: segmented KSDMA · NDMA · Partners · Media under the title + one-line description, shown only while a draft is unsent; sections carry `data-for` and hide per audience (Partners: needs/gaps as totals, no personal data; Media: verified figures only). Main = AI-drafted banner (warning fill, sparkle), document card with numbered sections (summary lead 22/300 · severity and phase · affected areas table with state glyphs · verified impact figures · resources · gaps · decisions needed (numbered amber discs) · sources and freshness), every figure tagged. Primary "Approve and send to <audience>" (IC only; others "Recommend to IC" / "Send to IC"). On approval the banner, audience switch and button go, the subline reads "approved by Ananya Menon at 09:12 · sent to …", and a **success pop-up** appears bottom right (glass 360w, radius 20, green check disc, title + one line, ×, closes after 6 s, `role=status`) — never over the title or its actions. Sent reports are read-only. Rule: any component with its own `display` must still honour `[hidden]` (`.view-app [hidden] { display: none !important }`).
- **Audit:** rail = **"This event so far" decision dial** (16 Oct; after the position-card reference) + **Where people changed the AI** (the edits and the rejection, each opening its trace). Filters (decision · phase · agent) are in the list toolbar.
  - Dial (260px): a minutes ring on a **square-root scale** (labelled 0 · 1 · 5 · 10 · 20 · 30 · 45, clockwise from the top) so the many short waits get room; one marker per recommendation at the minutes it waited for a human decision — approved = filled green, edited = dashed green ring, rejected = hollow grey ring, escalated = white diamond; **waiting** ones sit on an outer amber orbit at minutes-so-far. A dashed tick marks the median.
  - Centre: a dark glass orb with soft glows sized by share of outcomes (green decided, amber waiting, grey rejected/escalated); default shows the median (36/200 "5.5 min · median wait").
  - Interactive: hover the ring (nearest marker by angle) or focus the dial and use ←/→ Home End; the orb shows that wait + outcome, its glow brightens, a dashed pin points at it, a line above the row names the agent and recommendation, and the row reads Waited · Day · Phase (default: Decided · Awaiting · Longest). Click / Enter opens the trace; Esc clears. Implemented as `role=listbox` with `aria-activedescendant` options; the row is `aria-live`.
  Main = trace cards: agent · day · time · phase / recommendation / outcome chip (Approved ✓ · Approved with edits dashed · Rejected ✕ grey · Awaiting decision clock amber · Escalated ↑). Expanded = vertical trace (Recommendation → Evidence with chips → Confidence + amber limitation → Human decision with `<del>/<ins>` edit diff or rejection reason → Task → Agency acceptance → Outcome); not-applicable steps are hollow dots. "See it on the timeline", and "Decide in <phase>" when awaiting. Deep link `?view=audit#tr4`.
- **Way back:** a quiet "← Back to <phase>" link above each view's title returns to the last phase you were in (session memory; else your role's home). The ResilienceOps logo does the same from anywhere.
- On views the bell lists the event's open items (`RO_ALERTS`); search covers rows, sections and traces (`data-sk-t`).

### 6.11e Recover rail cards (16 Oct 2026)
- **Verified impact** (ref: asset card): header = 40px icon chip (shield-check) · title + "● Updated 08:40" · 36px chevron button that hides/shows the table (`aria-expanded`). A progress line "Households assessed · Panchayats — 420 / 530" on a 2px track, amber fill to 79% with a ▾ marker. Then an inner panel table (Measure · Count · Source · Status), each row a coloured dot + measure, count with unit in ink-2, source, and a **filled status pill** (Open red · 89% full amber · Verified green, on-colour text).
- **Communities** — one card, two states:
  - **List** (ref: materials list): "Communities · worst first · coverage"; rows separated by hairlines: status dot + name, coverage % right; a 3px bar in the state colour (hatched when not assessed); "n in need · source · time" + status word right. Hint at the bottom: "Select a community to see its needs".
  - **Detail** (row click; map flies there): name with dot + place line, ⌃ back button (Esc too; focus returns to the row); coverage numeral + status; a 3×2 **labelled** need grid (32px icon · need · Met/Partly/Gap/Unknown in its colour); the "what's missing" lines; source.
  - Replaces the 2×2 community tiles. Search results for a community open its detail.

- **Teams carousel** (Respond, 16 Oct 2026): the four team cards are one card filling the rest of the rail (no rail scroll). Slides share one grid cell (constant height) and crossfade (220 ms, `cubic-bezier(0.23, 1, 0.32, 1)`); auto-advance every 3 s. Pagination: four 24px dot targets (active = 18px ink pill, `aria-current`) + a 28px pause/play button. Rotation pauses on hover or focus inside, with the button, and starts paused under reduced motion (WCAG 2.2.2). `aria-roledescription` carousel/slide; the slide region is `aria-live="off"` while rotating, `polite` when paused. Clicking the slide flies the map to that team; auto-advance never moves the map. Search results for a team show its slide.
  - **Trip panel** (17 Oct 2026; replaces the unlabelled route sketch and the empty 06:00→Now bar): a 16-radius inset box answering a dispatcher's questions in reading order — **from → to** with the ETA on the right (amber when late, green when arrived, grey "Awaiting dispatch"); a **route track** (driven part solid ink, rest dashed, named stops as ticks, a problem stop amber with "▲ name", the unit's letter disc in its status colour at its position, "n% of the way" / "Arrived" / "At base" + "via …" underneath); three **facts** (distance or time left, against plan in amber/green); and the **shift strip** 06:00 → 12:10 split by state (At base white 14% · Standby ink 45% · En route `--ok` · On site green 55% · Delayed `--warning`) with a key of the states used. Approving the Rescue Unit 2 dispatch updates its panel (En route, ETA 12:41, on plan). The vehicle drawing is 50px tall to make room. The card's `aria-label` reads the whole trip.
  - **No pill over the drawings** (17 Oct 2026): the unit pill is gone from the vehicle drawing; the call sign moves to the subline ("Fire & Rescue · Kalpetta · FR-02"). The status row now reads status chip · **registration plate** (white plate `#eef0ee`, black 11px/500 text, 4px radius, as on the road, e.g. KL 12 G 4471) on the left, GPS · network · **call button** on the right. Call = 30px round `tel:` link to the driver ("Call Suresh K."), amber when the network is weak, so comms can still reach a unit that drops off data. The slide is a `group`; a full-card stretched button shows the unit on the map and the call link sits above it; hidden slides are `inert`. Plates, drivers and numbers are simulated.
  - Prepare place cards: the rank-and-risk pill no longer covers the terrain drawing; the rank is a 20px number in the risk colour before the place name.

- **Minimised panel pill** (16 Oct 2026): the expand icon is now a **chevron-down** in the 32px disc, so the pill reads as a dropdown that opens the panel. Respond has it too: "Needs your decision n ⌄" in the critical fill; the map's incident and the tour reopen the panel. The Respond map frames the incident area (Kalpetta · Vythiri · Meppadi · Chooralmala) in the free map space: left of the panel when it's open, centred when it's minimised; toggling glides there in 0.7 s (`flyToBounds`, instant under reduced motion), and the ⊙ recentre control uses the same framing.
- **Full map** (16 Oct 2026): last button in the map controls (expand icon, tooltip "Full map"; `aria-pressed`). On: the rail collapses (grid column → 0, 360 ms `cubic-bezier(0.77, 0, 0.175, 1)`), and the map title, decision panel/pill, bottom cards and floating map cards fade out (240 ms `--ease-out`); the top bar and map controls stay, the controls drop to the bottom edge, the icon turns into the inward (minimise) arrows. Off: the button again or Esc. Leaflet re-measures after the move.
- **Filter card** (16 Oct 2026; ref: filter card; now `RO_UI.filterCard` on **Timeline** — Phase · Who · Kind, time range stacked by verification, "Verified only" switch — and **Audit** — Human decision · Phase · Agent, time range stacked by decision outcome; groups with more than 5 options wrap; the card fits the space below its button and scrolls inside). Original Reports spec: glass 372w, radius 24. "Filter" 19/300 + Reset filters. Segmented pill groups (pressed = raised `card-hi` + shadow): Status (All · Draft · Sent, with icons: Draft amber, Sent green), Sent to (Any · KSDMA · NDMA · Partners · Media), Priority (Any · Urgent · High · Routine, each with its 8px colour dot). **Time range**: histogram of reports per 2 h, each bar stacked by priority (Urgent `--critical` · High `--warning` · Routine ink 60%, with a key); bars outside the range dim to 28% + a two-thumb slider (thumbs never overlap: From covers start→midpoint, To midpoint→end) with ink value pills that stay inside the panel; "Most sent …" on the right. More options: an "Oldest first" switch. Footer: Cancel · **Show n results** (live count) — changes apply only on that button; Esc / outside click cancel.

- **Detail pages behind the cards' ↗** (16 Oct 2026): every card arrow opens a real page (not in the nav; "Back to <phase>" link), landing on the card's section, which scrolls in and flashes once (`ro-hit`).
  - **Forecast and risk** `?view=forecast` — `#rain` observed vs forecast mm/h chart (observed ink line, forecast dashed grey, landslide-watch 15 mm/h amber dashed, hours above the watch line shaded amber 7%, landslide marker red) · `#outlook` risk by place with peak window, exposure (estimated) and what happened · `#outcome` forecast versus outcome (lesson · planned · what happened · change for Prepare + owner). Rail: totals, sources, confidence, limitation note.
  - **Tasks and resources** `?view=tasks` — `#board` tasks grouped Needs a decision · Behind plan · Moving · Done in Prepare (fixed columns: task + why · team · status · against plan · action) · `#resources` confirmed / needed bars (amber when short). Each short resource has **Draft a request**: a centred dialog (560w, radius 26, same surface as the full-timeline drawer, page inert, focus trapped, Esc / ✕ / Cancel close without saving) with an AI-drafted, editable request — Send to · Priority · What is needed · How much · Needed by · Deliver to · Why · evidence. Empty fields are flagged on save (red border + "Fill in: …", focus to the first). **Save draft for the IC** never sends: the request appears in Reports as "Resource request #n" (Draft, no audience switch) for the IC to approve and send (other roles see "Send to IC"); the row then reads "Draft with the IC" or "Request sent" with an "Open in Reports" link. Drafts last for the visit (sessionStorage). Rail: time to dispatch + counts by status, capacity gaps.
  - **Relief and camps** `?view=relief` — `#requests` table with a 5-step progress bar (done ink 55% · current amber · verified green) · rail `#camps` occupancy bars (amber at ≥85%, "near capacity").
  - Links: Prepare Rainfall → `#rain`, 24-hour outlook → `#outlook`, Capacity → `tasks#resources`; Respond Rainfall → `#rain`, Time to dispatch → `tasks#board`, Camps → `relief#camps`; Recover Relief pipeline → `relief#requests`, Recovery timeline → Timeline filtered to Recover, Learn → Prepare → `forecast#outcome`. Status in tables is always icon + word; long outcome sentences stay ink with only the icon coloured.

- **Who acted** (Timeline rail, 17 Oct 2026): fills the rest of the rail (min 340px). The AI · People · Agencies counts are toggle buttons that filter the timeline (same state as the Filter card; pressed = raised `card-hi`). Below, **By actor**: every agent, person and agency, busiest first — kind icon, name, count, and a 4px bar (length = entries, split by phase in the phase colours, with a key); actors outside the active filter dim to 38%. A row opens the full-timeline drawer at that actor's first entry. **No scrolling anywhere in the Timeline rail** (17 Oct 2026): Who acted takes exactly the space left. Actor rows are single 28px lines (icon · name · phase bar · count) and only the rows that fit are shown; "All n ›" in the By-actor heading opens the full timeline. When the card is too short for one row (container query on the card), the By-actor section drops and only the counts remain. Short screens get slightly tighter rail spacing (≤880px: 76px top, 8px gaps, 12px card padding, 118px severity chart; ≤820px: 74 / 6 / 10 / 100px); 900px and up are unchanged.

- **Prepare priority places: tile → detail card** (17 Oct 2026, fitted to the grid the same day; ported from the `prepare/` component, app tokens, dark only, `pp-` classes). Tiles keep the 2×2 rail grid (rank · name · ↗ · terrain sketch with the hatched at-risk zone · risk · people · readiness bar). Clicking a tile morphs it into the detail card **in exactly the 2×2 grid's box**: the card's height is locked to the grid's, so the column never grows or scrolls (clip-path grows from the tile, the other tiles fade; 480 ms `--ease-out`; ✕ / Esc morph back; reduced motion = instant; a timed fallback finishes the morph if frames are paused). The map also flies to the place. Card, top to bottom: header (rank, name · Approve all n · ✕; then risk glyph + level · people · n/N ready, full width) → the terrain, which takes whatever height is left and is drawn at that real size so text stays 1:1; risk factors are pinned in two stacked rows, 22px pins (a lower-row pin rises to stay clear of the ground and rooftops; severe pins glow three times; light rain over the zone) → the next task awaiting approval on one line (title truncates, full title on hover; owner · due) with Approve; approving moves to the next. Dropped to fit: the runway (17 Oct — the plan panel already shows the same tasks and times; its height went to the landscape), the alert strip (the rain card above carries it), shortfall chips, unknowns, Risk detail / Review plan links. **One state:** Meppadi's tasks are the plan panel's five tasks — approving in the card approves in the panel and vice versa; tile readiness is derived from task status (Meppadi starts 0 of 5). Card approvals follow role permissions (analyst/coordinator see "Recommend to IC"). Page data wins (clock 06:20, heavy rain from each place's risk window, exposure, tasks).
- Rails fade out under the floating top bar (mask 56→76px) so scrolled content never runs into the logo.

### 6.12 Overlays
- **Toast:** glass pill, 14px, fades and rises 20px over 0.25s, auto-dismisses after 3.2s, `role="status"` / `aria-live="polite"`.
- **Legend popover:** glass, 280w, radius 18, grid gap 9, 22px swatch column; Esc closes and returns focus.
- **Guide (first run):** glass, 360w, radius 20; numbered 20px discs (white 12%); opt-in via the help pill; focus moves to "Got it"; Esc closes.

### 6.13 Phone-specific
- Device 390 × 844, status bar 15/500, Dynamic Island 120 × 34.
- Full-bleed bottom sheet (top corners 36) instead of a floating card, so there are no cards inside cards.
- Glass header buttons 48 tall; address pill 68 tall.
- Damage gauge: 6px track white 30%, segments critical / white / dark marker; 6px tick ruler every 6–7px; split numeral 52/200.
- `dl / dt / dd` for key–value telemetry.

---

## 7. Iconography and imagery

- **Icon style:** outline, 24 viewBox, stroke 1.5 (1.6–2.2 for small or emphasis), round caps and joins, `currentColor`. Filled glyphs only inside pins and severity shapes.
- **Sizes:** 20 (top bar, controls) · 18 (↗ open) · 16 (chips, groups, pills) · 14 (signals, pin glyphs) · 12–13 (deltas, chip icons).
- **Core set:** ↗ open · ✕ close · ⌄ caret · ✓ done · ▲ warning · ! severity · sparkle (AI) · clock (delay / confidence) · GPS waves · wifi / LTE · headset (helpline) · bell · search · layers (map key) · ? help · + / − / locate · landslide (mountain) · flood (waves) · camp (tent) · medical (+) · crew (cone) · copy.
- **AI marker:** the sparkle icon is reserved for AI-generated content; never use it decoratively.
- **Minimise / expand pair:** both on the top-right ↔ bottom-left diagonal. Minimise (on an open panel) = arrows pointing **inward** to the centre; expand (on the minimised pill) = arrows pointing **outward** to the corners. Never use the outward glyph to mean minimise.
- **Line-art vehicles:** side elevation, 220 × 84 viewBox, stroke 1.1, no fill, ink 85%. Set: fire tender, excavator, ambulance, relief truck (to add: boat, bus for evacuation, drone).
- **Brand mark:** three terrain contour lines plus a dot (placeholder; see checklist).
- **Avatar:** initials on the green-grey gradient; no stock photos of real people.
- **Imagery:** satellite + hillshade only, desaturated per §3. No photos in chrome.

---

## 8. Motion

| Interaction | Spec |
| --- | --- |
| Hover / colour | 0.2s ease |
| Selected-card glow | 0.3s ease |
| Caret rotate | 0.2s ease, 180° |
| Toast | 0.25s ease opacity + 20px translate |
| Map fly-to | 0.8s (`map.flyTo`); instant `setView` under reduced motion |
| Incident ping | 2.2s ease-out infinite |
| Approval sequence | Approved → (≈2.6s, simulated) → Accepted; each step announced in a toast and the state line |

**Motion and interaction layer** (16 Oct 2026; `test-run/motion.css` + `motion.js`, appended to every page by `build-app.py`). Rules from Emil Kowalski (motion only for feedback, spatial consistency, state or a jarring change; transform + opacity; under 300 ms; never `ease-in` or `scale(0)`) and Vercel's interface guidelines (keyboard parity, input-driven and interruptible, hover gated to fine pointers).

| Token | Value |
| --- | --- |
| `--ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` — entrances, popovers, feedback |
| `--ease-in-out` | `cubic-bezier(0.77, 0, 0.175, 1)` — things moving on screen (full map, truck) |
| `--ease-drawer` | `cubic-bezier(0.32, 0.72, 0, 1)` — reserved for sheets |

| Interaction | Spec |
| --- | --- |
| Press | buttons, pills, segments, chips `scale(.97)`; rail cards `scale(.985)`; 160 ms ease-out |
| Card ↗ | hover: 32px disc white 8% + arrow `translate(2px,-2px)` 200 ms; card border to `--hair-2` |
| Popovers (role/phase menu, notifications, filters) | from `scale(.97) translateY(-4px)` + opacity 0, origin top right, 180 ms (`@starting-style`); close is instant |
| Tooltips (`data-tip`) | first after 350 ms, then instant for neighbours (warm for 500 ms) |
| Decision panel ↔ pill | both grow from the top-right corner, `scale(.96)` + opacity, 220 / 200 ms |
| Things that appear (state lines, "Why", expanded rows, notes) | opacity + `translateY(-4px)`, 200 ms |
| Page entrance | rail, title, panel, controls and bottom cards rise 8px, 300 ms, 50 ms stagger (`fill: backwards`, never blocks input; off in tour previews) |
| Changing numbers (counts, KPIs, badges) | new value rises from 35% with 2px blur, 260 ms |
| Content swaps (report body, filtered lists) | cross-fade from 35% opacity with 2px blur, 200 ms |
| Interactive charts | hover, tap or ←/→ (Shift = 4 steps, Home/End) snap a guideline (bars: a highlight band) to the nearest point; dots on each series; tooltip with time, values and a warning note (e.g. above landslide watch) above the highest dot, kept inside the card, glides 120 ms between points; a polite live region reads the point. On: Prepare and Respond rainfall, Respond camps, Timeline severity, Forecast rainfall |
| Relief truck (Recover demo) | one continuous rAF glide along the route, 3.3 s ease-in-out (was 60 timed jumps) |

**Recover charts** (17 Oct 2026): the recovery timeline reads any day on hover / ←→ (coverage, recorded or projected, plus road, power and telecom state) and click or Enter moves the map preview there, like the slider. Community coverage bars and pipeline steps glide from the old value to the new one when they change (`RO_MOTION.grow`: scaleX, 400 ms ease-in-out); lessons cross-fade when paging. **Verified impact**: "Households assessed" is a segmented bar by panchayat (width = households, amber = assessed; Meppadi 205/240 · Vythiri 115/120 · Chooralmala 100/120 · Pozhuthana 0/50) with a hover/keyboard band showing each one's count, share and why it's behind. **Learn → Prepare ruler** reads any tick on hover/keyboard: what was true at that point against the plan (e.g. 20 h → Water ran out · 20 h of 48 planned). Chart tooltips sit above the point unless that would leave the window. Communities rows share the card height; a six-icon needs strip (gap red, partly amber, met faint, unknown dashed) shows when the card has room (container query: icons at ≥505px, with labels at ≥560px).

**Community detail = coverage ring** (17 Oct 2026; ref: `recover/ring.html`): selecting any community in the Communities card opens a ring instead of the icon grid — header (dot, name, subline, ↑ back to the list), status line (icon + word · "n in need"), then six segments around a ticked disc: Water top-right, Food right, Medicine bottom-right, Shelter bottom-left, Power left, Road top-left. Each segment fills by the % of that need met (gap = hatched `--critical` with a soft glow, partly `--warning`, met `--ok`, not assessed = dashed grey); badge icon on the segment, name + state word outside. Centre: thin inner ring + average coverage ("68 % covered"; "— not assessed" for Pozhuthana). Legend groups the needs by state; source line last. App tokens, Outfit, dark only. The ring scales to the card's height (it fills the space between the status line and the legend), so it never scrolls. Hover / tap / ←→ highlights one need (others dim to 35%) with a tooltip: state, % met, the figure (e.g. "Out · Day 3"); a live region reads it. On open: segments sweep in 60 ms apart (520 ms each, ease-out), the centre counts up (800 ms), the inner ring draws, gaps glow three times then stop; reduced motion shows the final ring; a 1.3 s fallback guarantees the final state even if animation frames don't run.

**Reduced motion** keeps the fades that explain a change and drops all movement: no press scale, no rise or slide, numbers and entrances fade only, truck jumps to the end, scrolling is instant. (Replaces the old rule that turned every transition off.)

**Deliberately not animated:** the command search (Ctrl K) and keyboard focus moves (used constantly); chart lines don't draw in (data people read shouldn't move for style); the 24-hour outlook and recovery timelines already have scrubbers, so they get no second hover layer.

---

## 9. Accessibility patterns (must ship with every view)

- Skip link "Skip to decisions" (first focusable element).
- Landmarks: `header` / `nav` (phase), `aside` (rail), `main` (stage), `section`s labelled by their headings; map `role="region"` with a descriptive label.
- Focus: 2px white outline, 3px offset, radius 12 on every interactive element.
- Targets ≥ 24 × 24 (most are 40–46). Non-interactive map decorations are `interactive:false`.
- Toggles use `aria-pressed` (filters, unit cards); disclosures use `aria-expanded` + `aria-controls` (alerts, legend, guide, Why).
- Live updates via `role="status"` regions (toast, approval state).
- Status = icon + word + colour, never colour alone.
- Keyboard: Ctrl/⌘ K → search; Esc closes popovers and returns focus.
- Automated check: axe-core 4.10 (wcag2a/aa, 21aa, 22aa) must report 0 violations.

---

## 10. Content and voice

- Plain language a non-expert understands in one read: "Landslide blocks the Meppadi–Chooralmala road", not "Incident INC-0112 class LS-3".
- Lead with the place and the problem; then impact; then time and source.
- Use ranges for people ("about 10–18 households"), never false precision; **no casualty predictions**.
- Name who decided and when ("Approved by Ananya Menon at 12:14").
- Times in 24h IST; distances in km; rainfall in mm and mm/h.
- Malayalam / English support is planned (checklist).

---

## 11. Token block (copy into every view)

```css
:root {
  --page:#111413; --rail:#161918; --card:#1e2221; --card-hi:#252a28;
  --glass:rgba(26,30,28,.78); --glass-hi:rgba(40,45,42,.82);
  --hair:rgba(255,255,255,.07); --hair-2:rgba(255,255,255,.12);
  --ink:#f2f4f2; --ink-2:#b9c0bb; --ink-3:#8a928d;
  --critical:#ff6b5f; --critical-bg:rgba(110,38,33,.55);
  --warning:#f0a04b; --warning-bg:rgba(110,72,30,.42); --ok:#7bd88f;
  --camp:#3b8bdd; --medical:#e07a9b; --crew:#c9d14a;
  --focus:#ffffff;
  --r-lg:26px; --r-md:20px; --r-sm:14px; --r-pill:999px;
  --rail-w:468px; --gap:12px;
  --blur:blur(20px) saturate(1.2);
  --font:"Outfit", system-ui, sans-serif;
}
```

## 12. Phase adaptations (same system, different emphasis)

| | Prepare | Respond | Recover |
| --- | --- | --- | --- |
| Map shows | Forecast + risk zones (hatched), exposure, pre-positioned assets | Live incidents, units, routes, camps | Damage and needs coverage, served vs unserved areas |
| Decision panel | "Plan to approve" — readiness tasks | "Needs your decision" — incidents | "Still unserved" — needs and gaps |
| Dominant colour signal | Warning (amber: risk, not yet harm) | Critical (red: harm now) | Warning → ok (closing gaps) |
| Hero KPI | Readiness % / hours to impact | Time to dispatch | People still in need |

## Event state and handovers (17 Oct 2026)
- **`test-run/state.js`** (built in before the views and phases): `RO_STATE` keeps what each phase hands on for this visit (sessionStorage `ro.state`): `handover.prepare`, `handover.respond`, `prep.cap`, `report.sr4`, and a `log` of actions taken on the pages. Everything still works without storage.
- **Review dialog** (`RO_REVIEW.open`, styles `.rv-*` in `app-shell.css`): 560px solid card (#1c201f, radius 26) over a 62% scrim · header (title 19/300 + one-line source/time, ✕) · AI banner ("… draft · review before sending") · fields as label/value rows · lists with ✓ Done / ▲ Carried over / • Assumptions · footer note + Not now | primary action. Focus moves to the primary button, Tab is trapped, Esc / ✕ / scrim cancel and return focus. **Role-aware:** only the IC approves (the coordinator too in Recover); others see "Recommend to IC" / "Send to IC" plus "Approval sits with Ananya Menon". Used by Prepare's requests and the Respond → Recover handover; tier 2 placeholders will reuse it.
- **Handover note** (`RO_HANDNOTE`, `.ro-ho`): first item under the next phase's panel header — "Handed over from Prepare · Day 0 · 12:06 · Ananya Menon · n done · n carried over", collapsed; opens to Carried over (amber diamond) then Done (green dot). Searchable.
- **Capacity rows** have three states: short (amber ▲ "2 short" + Fix →) → requested (dashed amber bar, clock "Requested" / "Stocking") → confirmed (white bar to the need tick, green ✓ "Confirmed"). The KSDMA draft row in the plan panel mirrors it (Sent · waiting → Confirmed).
- **Respond → Recover step:** "Next phase" group at the foot of the decisions panel, added once the dispatch is accepted; neutral "→" item "Recovery, once rescue is complete" → (demo skip) amber "Recovery mode recommended" with Review handover / Stay in Respond. Moving to Recover is the IC's call.
- **Timeline** merges the log entries into the record in time order (same row anatomy; source names the approval record).
- **Actions behind buttons** (`RO_ACT`, 18 Oct 2026): a button carries `data-act="key"`; the page declares what it opens. Requests and escalations open the review dialog (with editable fields where a person would adjust the draft); reminders and checks run directly. Approving swaps the button for a green state line ("Sent to … at …", `.ro-done`, role="status") or, in a draft row, a "Sent" chip; edits keep the button. Each action adds a Timeline entry. The dialog validates empty fields inline ("Owner can't be empty."). Notification settings use the same dialog without approval (saved in this browser).
- No toast-only placeholders remain; the top-bar bell and helpline are popovers.
- **Timeline · At a glance** (17–18 Oct 2026, from `timeline/index.html`): title + one quiet stats line on the left ("24 entries · busiest half-hour …", "n of 24 highlighted"), "Open full timeline" alone on the right. Chart: "Severity" caption above its Critical/Moderate/Watch scale; severity dot columns every 30 min; entry marks (shape = who acted, fill = how sure, red + halo = awaiting decision); phase bands; orange Now. Legend footer = three labelled groups split by hairlines: Who acted · How sure · Needs action, each a row of highlight toggles. **Tooltip** = the app's dark glass popover (rgba(26,30,28,.94) + blur, hairline, radius 16), the list's own status chips (vchip), a severity-bars glyph on column tooltips, "Click or press Enter to pin" hint; pinned adds "Open in full timeline" (secondary button). It never covers the title row.
- **Risk detail** (`?view=risk&place=meppadi|vythiri|mananthavady|kalpetta`, 18 Oct 2026): title "Why is Meppadi critical?" / "Why is Vythiri high risk?". Rail: score (44/200) + level chip + a 0–1 scale with the 0.30/0.50/0.70 thresholds and a marker; places ranked (40px links); **On this page** fills the rest of the rail — one row per section with its key value (0.89 · 4 h above · 3 severe · 2.0–3.5k · 2 events · 4 items · 5 tasks), rows share the remaining height (min 28px), the section in view is marked (inset bar + card-hi), click scrolls and focuses the section heading. Fits with no scroll from 900px tall. Main: In short (agent text + source badge) → How the score adds up (table: part · why · value bar · weight · adds; total vs the next threshold) → rain chart (expected mm/h scaled to the place's 24 h total, 15 mm/h watch line, risk window band) → factors (severity glyph+word, source, verified/estimated chip) → exposure (ranges, vulnerable groups, capacity rows) → history → unknowns (amber diamonds) → readiness tasks → comparison. Scores use the agent's formula on `RO_SCENARIO` (backend/data/wayanad.json embedded at build), rounded the same way.
- **As of** (Timeline · Reports · Audit, 18 Oct 2026): these event-wide pages show the event up to the moment of the phase you came from — Prepare = Day 0 06:20, Respond = Day 0 12:10, Recover = now (all). Under the subline: "Showing the event as of [Prepare · 06:20] [Respond · 12:10] [Recover · now]" (32px pills, current = card-hi); the top-bar clock follows it. Entries after the cut are left out; a recommendation made before the cut but decided after it shows as *Awaiting decision*; outcomes are hidden until "now". Charts keep the whole event's axis but draw nothing after "Now" (the label moves into the empty future). Reports before the first one: "No reports yet" with why. What you did on a phase page counts from that phase on. Bell on these pages: Day 2 items only at "now". (`RO_ASOF` in views-src.html; `?asof=` overrides the remembered phase.)

