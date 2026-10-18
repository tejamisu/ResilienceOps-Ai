# ResilienceOps AI — Design Checklist

Living list of design decisions, open questions and things left out. Updated as we iterate.
Context: Wayanad, Kerala · Ron Design Lab visual direction · WCAG 2.2 AA + Nielsen / Shneiderman / PAIR / HAX quality bar.

## Decided
- [x] **Demo opens on Respond** (Wayanad Response dashboard). Revisit once Prepare exists. *(12 Oct 2026)*
- [x] Use case location is **Wayanad** only (Kollam superseded, Idukki not involved).
- [x] Visual direction: Ron Design Lab dark terrain + frosted glass (refs in `references/rondesignlab/`).
- [x] First-run guide is **opt-in** ("New here? How to read this view") so it never covers the map.
- [x] Thin type only at ≥ 20px; small text at weight 400 for legibility.
- [x] Status never colour-only: always icon + text.
- [x] **Prepare layout = hybrid**: Respond's shell + 24 h countdown timeline + ranked priority places. *(12 Oct 2026)*
- [x] Prepare timeline is **animated**; expected risk shown as **bands** (likely / possible), never exact lines.
- [x] **Simulated data only** — no recorded Wayanad flood/landslide history (sensitive).
- [x] Build a **Prepare → Respond handover** demo flow.
- [x] Prepare is built as a **standalone mock-up** (`test-run/prepare-mockup.html`); integrate into the app only on the user's go-ahead.

## On hold — needs a decision
- [x] **Map engine: stay on flat Leaflet** (decided 17 Oct 2026). Background: current is Leaflet + Esri World Imagery / Hillshade (free, no key, flat 2D). The reference's 3D tilted terrain needs MapLibre GL or Cesium plus a terrain source (e.g. Mapbox/MapTiler terrain-RGB, Google 3D tiles — most need an API key). Teammate to decide before building the real app; prototype and codebase should use the same engine.

## To design next
- [x] **Prepare** screen: forecast → readiness plan → "Activate Response" handover.
- [x] **Recover** screen: verified impact, needs & relief gaps, partner deliveries, forecast vs outcome.
- [x] Prepare → Respond and Respond → Recover transition prompts (human-confirmed). *(17 Oct 2026)*
- [x] Field responder phone app (`test-run/field.html`): task inbox, task detail (what/where/route/why/calls), accept → on my way → on site → report outcome (people moved, road, notes, photo), "I can't do this"; English / മലയാളം; every step lands on the Timeline. Linked from the avatar menu. *(18 Oct 2026)*
- [x] Destinations behind the ↗ links: incident detail, full task board, rainfall/forecast detail, relief camps.
- [x] "Edit" dispatch form (route, note; arrival recalculated) and partner request review. *(18 Oct 2026)*
- [x] Timeline, Reports, Audit views.
- [x] Malayalam: field app has a full EN/മല switch; Respond shows the resident's Malayalam voice note with its English translation (Field Intelligence Agent). The command dashboard stays English (DEOC officers). Malayalam to be checked by the DEOC language officer. *(18 Oct 2026)*

## Known gaps in the current dashboard
- [x] **Respond: minimise "Needs your decision"** into a floating pill (same behaviour as Prepare's "Plan to approve"): map re-centres when minimised, pill turns red if a new critical item arrives, starts open. Agreed 13 Oct 2026 — don't touch Respond until asked.
- [ ] **Design bugs on the Respond page** noted by the user — to be listed and fixed in a later pass. *(12 Oct 2026)*
- [x] Laptop/tablet pass (≤1180px): no empty band under the top bar, cards size to content, map capped at 640px and framed for the stacked layout. *(18 Oct 2026)*
- [x] Plain map labels sit on a 62% dark backing: ≥ 4.5:1 even over white imagery. *(18 Oct 2026)*
- [ ] Gauge track on the phone damage card ≈ 2.2:1 (decorative; meaning carried by text) — confirm acceptable.
- [ ] Road geometry and pin positions are approximate and simulated; replace with real GIS layers when available.
- [x] Offline map: if imagery can't load, the map turns plain dark with a note; zones, routes and teams still draw. *(18 Oct 2026)*
- [ ] Only the Respond view, approve flow, filters, guide, legend and accordions are interactive; other controls show a placeholder note.

## Prepare mock-up — open items
- [x] ~~Prepare rail still scrolls by 39px at 1440×900~~ — no longer scrolls (rechecked 17 Oct 2026). (14 Oct 2026): layer pills moved out of the status card into a map Layers control, status card 126 → 70px. Still needed: a small cut below (e.g. last two places as slim rows, or a shorter rain chart).
- [x] Respond: the four layer pills moved into the map's Stack control; the two team tiles merged into one status card like Recover (Teams deployed 9 / 13 · Teams unreachable 2). *(16 Oct 2026)*
- [x] "Current phase" moved from the top bar to just above the page title, left-aligned with it. Timeline's full-timeline drawer was showing (empty) on load and could not close: `.ftl { display:flex }` overrode `[hidden]`; fixed with `.ftl[hidden]{display:none}`. Detail notes are now neutral instead of green. *(16 Oct 2026)*
- [x] Respond decisions panel minimises to a pill like Prepare/Recover. All 9 card ↗ arrows now open real pages: new Forecast and risk, Tasks and resources, Relief and camps views (+ Timeline filtered to Recover). Reports filter: priority-stacked histogram, status and priority colours. Timeline + Audit filter rebuilt as a dark search list. axe 0 on all. *(16 Oct 2026)*
- [x] "Draft a request" (Tasks › Resources) works: AI-drafted request dialog → saved as a draft in Reports → IC approves and sends; the row shows "Draft with the IC" / "Request sent". Product tours stay on the three phase pages only (Prepare · Respond · Recover); the views have none by design. *(16 Oct 2026)*
- [x] Motion and interaction layer (`motion.css` / `motion.js`): press feedback, card-arrow hover, popovers from their trigger, warm tooltips, panel ↔ pill, appearing state lines and rows, page entrance stagger, number ticks, content-swap cross-fades, interactive charts (hover / tap / arrow keys + live region) on 5 charts, smooth relief truck, gentler reduced motion. axe 0 on all 9 pages. *(16 Oct 2026)*
- [x] Filters swapped: Reports uses the dark search list; Timeline and Audit use the filter card (segments, stacked time-range histogram, apply on "Show n results"). *(16 Oct 2026)*
- [x] UI fixes: camps card ↗ was stretched by `.camps svg` (scoped to `#camp-chart`); toast sits at the foot on view pages instead of over content; Reports **Edit** edits the draft in place (saved per report, Esc/Done); **Save as PDF** opens a clean print copy; **Export audit report** downloads a real CSV. *(16 Oct 2026)*
- [x] Respond team cards: the abstract route sketch (no axes, scale or labels) is replaced by a trip panel — from → to + ETA, route progress with stops and the unit's position, distance/time left and against plan, and the shift so far by status. *(17 Oct 2026)*
- [x] Pills removed from the Respond vehicle drawings and Prepare terrain drawings; team cards show the registration plate and a call-the-driver button (tel:). *(17 Oct 2026)*
- [ ] Replace simulated plates, driver names and numbers with the fleet register when the agents connect.
- [x] Rainfall cards: "mm/h" moved a line above the top tick (Respond, Prepare). Recover: communities card fills its height (+ needs strip when there's room); recovery timeline hover/keyboard/click; bars and pipeline glide on change; lessons cross-fade. *(17 Oct 2026)*
- [x] Timeline rail: "Who acted" fills the empty space — counts filter the timeline; by-actor list with phase bars opens each actor's first entry. *(17 Oct 2026)*
- [x] Recover communities: detail view replaced by the coverage ring (all four communities), scaled to the card, interactive, with entrance motion. *(17 Oct 2026)*
- [x] Prepare places: tiles morph into the detail card (terrain with risk-factor pins, runway to heavy rain, approvals shared with the plan panel) for all four places. The card is locked to the 2×2 grid's box — no column growth or scroll (436 × 388 at 1440 × 900). axe 0. *(17 Oct 2026)*
- [ ] Feel-check on a real screen: entrance stagger and tooltip glide at 10% speed in DevTools; reduced motion via the OS setting.
- [x] **Integrate Prepare into the app** (shared nav, shared event state) — waiting for the user's go-ahead.
- [x] Risk Detail screen built (see Decided 17 Oct 2026).
- [x] Task Edit (owner, due, resources), public advisory review (English editable), KSDMA request and Nudge owner all work. *(18 Oct 2026)*
- [x] Kalpetta label moved above-left of its pins; the Meppadi zone card moved off Vythiri. Mananthavady stays at the top edge by design (its card flies there). *(18 Oct 2026)*
- [x] Capacity check is live: each gap goes short → requested → confirmed. Fix opens a reviewed request (KSDMA 2 SDRF teams, PWD excavator, partner camp beds); water closes when the camp task is done. *(17 Oct 2026)*
- [x] Excavator and camp-bed gaps have request drafts. *(17 Oct 2026)*
- [x] Respond reads Prepare's handover: a "Handed over from Prepare" note in the panel; Rescue Unit 2 starts staged at Meppadi (11 min, ETA 12:26) when its task was done; SDRF backup in the Why list when confirmed. Without a handover Respond shows its default. *(17 Oct 2026)*

## Recover mock-up — open items
- [x] **Recover layout: Timeline.** Overview and Needs matrix removed, with the layout switch and the Relief pipeline card (it only showed in those two; the Relief and camps page carries the requests). *(17 Oct 2026)*
- [x] Community cards redesigned as option C (coverage numeral, line-art need row, one-line "what's missing" caption). Options board kept at `test-run/explore-community-cards.html`. *(14 Oct 2026)*
- [x] ~~On tall screens the community cards stretch~~ — rechecked at 1440×1100 (18 Oct 2026): the coverage ring and needs strip fill the card. Original note: Icons now grow to 40px to use the space, but from about 1080px tall a gap opens between the coverage % and the icons. Options: cap the card height, or add a 7-day mini trend in that space.
- [x] Recover actions work: water and meal-pack requests (review, editable quantity), telecom escalation, generator fuel check, hygiene-kit reminder. A sent request doesn't close a gap; only a verified delivery does. *(18 Oct 2026)*
- [x] Verified-impact card redesigned as option C (2×2 tiles + case dots / progress bars). Rail still doesn't scroll at 1440×900. *(14 Oct 2026)*
- [ ] Camp capacity (1,450 beds) is a simulated figure. Wording kept as "In relief camps" (17 Oct 2026; reply was ambiguous — confirm).
- [x] Learn → Prepare rebuilt as a one-lesson tick ruler (Ron Design Lab ruler reference) with a pager. *(14 Oct 2026)*
- [ ] Lesson figures (14 h of 48 h, Route C 9 h, Chooralmala 5% of reports vs 40% of need) are simulated.
- [x] Recover map header cleaned up: one row (event switcher · layout thumbnails · New here?); Map key moved to the map controls and fixed (it spilled out and was covered by other chips); "Simulated scenario" chip removed and the top bar now says "● Simulated · Day 2" instead of "Live"; Run demo moved into the New here? guide. *(14 Oct 2026)*
- [x] Prepare and Respond headers brought in line with Recover (15 Oct 2026).
- [x] Recover "New here?" guide panel replaced by a 6-step product tour (spotlight + live crop), auto-opening on first visit. *(15 Oct 2026)*
- [x] Prepare and Respond now have the same product tour (old guide panels removed). *(15 Oct 2026)*
- [x] Respond → Recover: after the dispatch is accepted, a Next phase item → "Skip ahead to Day 1, 07:50" → Recovery mode recommended → Review handover → Move to Recover (IC). Recover shows "Handed over from Respond". *(17 Oct 2026)*

## Navigation (15 Oct 2026)
- [x] **Decided: hybrid.** Prepare / Respond / Recover leave the top nav.
- [x] Built into the integrated app `test-run/resilienceops.html` (15 Oct 2026): phases out of the top nav, event-phase stepper, role switch (Ananya Menon · Dr. Rahul Nair · Sreeja Thomas) with approval permissions.
- [x] Stepper in the event chip dropped at the user's request: current phase is now a quiet tag in the map's bottom-right; switching phase moved into the profile menu (Role + Phase sections, dot on the avatar when another phase needs attention). *(15 Oct 2026)*
- [x] Phase and role switching moved to a small account menu + centred dialogs over the blurred app (your phases design): dioramas, keyboard (arrows, Tab trap, Esc), focus return, arrival toast; axe 0 on both dialogs; no errors on any phase or view. Tile text cut to name · purpose · one status chip; Commander moved from green to gold (green = done/verified). *(18 Oct 2026)*
- [x] Recover's header cleanup applied to Prepare and Respond (one-row header, Map key in the map controls, "● Simulated" in the top bar). *(15 Oct 2026)*
- [x] Top-bar search, helpline and alerts work in every phase (shared shell). *(15 Oct 2026)*
- [x] Map-only places (camps, roads, hospital, outages, towns) are searchable; picking one flies the map there. *(18 Oct 2026)*
- [x] Every review, edit and fix action is role-aware through the shared dialog (analyst: "Recommend to IC"; coordinator approves in Recover). *(18 Oct 2026)*
- [x] Persona names: Dr. Rahul Nair (Hazard Analyst, DEOC) and Sreeja Thomas (Relief & Recovery Coordinator).
- Background: User's view: they are separate categories, switched from the profile/persona menu. Brief: one event, three phase lenses; the Incident Commander owns all three; "Role switch or delegated role" is a global utility. Proposed hybrid: event-phase stepper in the event chip + role switch in the avatar menu (Incident Commander = all phases · Hazard Analyst = Prepare · Relief & Recovery Coordinator = Recover).

## Timeline · Reports · Audit (15 Oct 2026)
- [x] Built into the app as event-wide views (`?view=timeline|reports|audit`) on one simulated event record; event chip removed, ID now in each subline.
- [x] Report Edit, Save as PDF and audit CSV export work (16 Oct 2026).
- [x] Views have no product tour — by design (16 Oct 2026).
- [x] Report #4 stays sent after a reload; sending it, resource requests, Prepare requests and the Chooralmala loop add Timeline entries (shared state, this visit). *(17 Oct 2026)*
- [ ] Still per-page only: Prepare plan approvals, Respond dispatch and the Recover loop reset on reload (only their handovers and log entries persist).

## Decided 17 Oct 2026
- [x] Archive the unused Recover components (level tubes, show filters, isometric depot) → `recover/_archive/`. The coverage ring and `recover.mjs` stay.
- [x] Dark theme only for now; the components' light variants are not ported.
- [x] Risk Detail page (`?view=risk&place=…`, all four places): in short (Forecast & Impact Agent), how the score adds up (5 parts × weights vs thresholds), rain against the 15 mm/h watch level with the risk window, risk factors (severity, source, how sure), who is exposed + capacity, history, what could change it, readiness tasks, comparison. Reached from the place card ("Why critical?"), the Forecast outlook table and search. *(18 Oct 2026)*

## Roadmap (agreed order, 17 Oct 2026)
1. ✅ **Tier 1 — join the phases (done 17 Oct 2026):** Respond reads Prepare's handover · Respond → Recover handover · approving a report adds a Timeline entry and approvals persist · Prepare capacity check reacts to approved drafts (+ excavator / camp-bed drafts).
2. ✅ **Tier 2 — placeholders (done 18 Oct 2026):** one shared review-draft panel for the toast-only actions; make Edit / Review / Fix role-aware.
3. ✅ **Tier 4 and Tier 5 done (18 Oct 2026)**, except what needs the user: motion feel-check on a real screen, real data.

- [x] Timeline, Reports and Audit follow the phase you came from (as of Prepare 06:20 / Respond 12:10 / Recover now), with a switch on each page. *(18 Oct 2026)*

## Submission (18 Oct 2026)
- [x] Deck: `submission/ResilienceOps-AI-deck.pdf` (10 slides, from `deck.html`); demo script `submission/DEMO-SCRIPT.md`; root `README.md`.
- [ ] **User:** follow `submission/YOUR-CHECKLIST.md` (key, deploy, GitHub, links in the deck, video, submit).

## Agents backend (18 Oct 2026)
- [x] Teammate's backend (9 agents, Google ADK + Gemini) brought into `backend/`; original Metro version kept in `backend/legacy/metro/`.
- [x] Re-grounded in Wayanad: one scenario file `backend/data/wayanad.json` with the app's figures; 11 agents (added Relief Coverage, Forecast vs Ground Reality, Command Orchestrator; Triage merged into Field Intelligence).
- [x] Each agent returns code-computed facts + Gemini-written text (rule-written fallback); JSON API (FastAPI) also serves the app; offline tests pass.
- [x] App wired (`test-run/api-client.js`): Prepare plan text, Respond dispatch recommendation, Recover missed-community alert, Report #4 summary, advisory (with Malayalam), Vythiri and handover text; source badge with Regenerate; human decisions posted to the backend log. Without the backend the app keeps its built-in text.
- [ ] **Add the Google AI Studio key** to `backend/.env` (user), then `POST /api/warm` and check every agent's Gemini text in the app.
- [ ] Deploy to Cloud Run (needs gcloud + a GCP project with billing); see `backend/README.md`.
- [x] Bound: Forecast page (per-place why, Forecast & Impact; lessons, Reconciliation), Report #4 verified impact (Damage Assessment), Recover lessons' Prepare task text, Audit › Live agent runs (all 11, tools called), field app task reasons (Dispatch), voice-note translation (Field Intelligence). *(18 Oct 2026)*
- [x] Optional Firestore store (`STORE=firestore`); falls back to local files. *(18 Oct 2026)*

## Questions for the team
- [ ] Which hazards beyond landslide + flash flood should the demo show (if any)?
- [ ] Should the persona avatar stay as initials ("AM") or use an illustrated avatar?
- [ ] Final product name and logo mark (current terrain-contour mark is a placeholder).

## Files
- **`test-run/resilienceops.html` — the integrated app (the real file).** Built by `test-run/build-app.py` from the three phase pages plus `app-shell.css` / `app-shell.js`. To change a phase, edit its page and re-run `python3 build-app.py`; shell changes go in the two `app-shell` files. Open a phase with `?phase=prepare|respond|recover`.
- `test-run/recover-mockup.html` — Recover mock-up (3 switchable layouts, guided demo)
- `test-run/prepare-mockup.html` — Prepare mock-up (desktop) with Prepare → Respond handover
- `design-system.md` — full design system extracted from the Respond view
- `test-run/wayanad-dashboard.html` — Respond dashboard (desktop)
- `test-run/incident-report-v2.html` — phone incident sheet (style test)
- `test-run/dashboard-analysis.md`, `test-run/design-analysis.md` — image analyses and extracted design system
- [x] Security self-test (the 14 attacks, run locally keyless): fixed CORS `*`, sticky `?api=` backend repoint, credit-burn via `/warm`+`/run` (owner-gate + rate limit), oversized/garbage input (size + schema caps), bounded decision log. XSS and SSRF were already safe. Residuals by design (public demo, no login): open GET reads, role/author on the decision log. Re-runnable: `bash backend/tests/security/run_security_tests.sh`; full before/after in `backend/tests/security/REPORT.md`. *(18 Oct 2026)*
