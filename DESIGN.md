---
name: Palydex
description: Palworld 1.0 companion rendered as a nixie laboratory counting instrument — blackened steel plates, engraved placard caps, plasma-orange glass digits.
colors:
  chassis-black: "#0a0b0d"
  plate-steel: "#17191e"
  plate-steel-deep: "#121418"
  card-steel: "#16181d"
  well-black: "#0b0c0f"
  hint-plate: "#101216"
  steel-line: "#26292f"
  card-line: "#2a2d33"
  plate-edge: "#33373e"
  steel-line-bright: "#383d45"
  rivet-highlight: "#3f444d"
  text: "#dfe2e6"
  muted: "#a2a8b1"
  faint: "#818893"
  white: "#f2f3f5"
  placard-lilac: "#aab2bd"
  plasma-orange: "#ff9a1c"
  lit-amber: "#ffb054"
  lit-line: "rgba(255,154,28,.62)"
  filament-gold: "#ffc46b"
  ember-orange: "#ffa94d"
  lamp-green: "#6fe392"
  lamp-rose: "#ff8ca6"
  vfd-blue: "#5fe6ff"
  vfd-lit: "#8ceaff"
  el-neutral: "#c9cfe2"
  el-fire: "#ff6a3d"
  el-water: "#4d9bff"
  el-grass: "#54d96a"
  el-electric: "#ffd94d"
  el-ice: "#6ee4ff"
  el-ground: "#e0913f"
  el-dark: "#b06bff"
  el-dragon: "#8f92ff"
typography:
  display:
    fontFamily: "\"Barlow Condensed\", \"Barlow\", sans-serif"
    fontSize: "clamp(22px, 2.6vw, 30px)"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "6px"
  label:
    fontFamily: "\"Barlow Condensed\", \"Barlow\", sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "2px"
  body:
    fontFamily: "\"Barlow\", system-ui, -apple-system, sans-serif"
    fontSize: "15.5px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.1px"
  data:
    fontFamily: "\"Chivo Mono\", ui-monospace, SFMono-Regular, monospace"
    fontSize: "21px"
    fontWeight: 300
    lineHeight: 1
    fontVariation: "tabular-nums"
rounded:
  chip: "5px"
  control: "7px"
  key: "8px"
  card: "10px"
  plate: "12px"
  pill: "99px"
  lamp: "50%"
spacing:
  xs: "6px"
  sm: "10px"
  md: "13px"
  lg: "18px"
  xl: "22px"
components:
  tab:
    backgroundColor: "linear-gradient(180deg,#1d2026,#15171c)"
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    rounded: "{rounded.key}"
    padding: "10px 16px"
  tab-active:
    backgroundColor: "linear-gradient(180deg,#221a10,#181209)"
    textColor: "{colors.plasma-orange}"
    typography: "{typography.label}"
    rounded: "{rounded.key}"
    padding: "10px 16px"
  button-mini:
    backgroundColor: "linear-gradient(180deg,#20242b,#171a1f)"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  button-go:
    backgroundColor: "linear-gradient(180deg,#221a10,#181209)"
    textColor: "{colors.lit-amber}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  card:
    backgroundColor: "linear-gradient(180deg,#16181d,#13151a)"
    rounded: "{rounded.card}"
  input-search:
    backgroundColor: "{colors.well-black}"
    textColor: "{colors.white}"
    rounded: "{rounded.key}"
  hud-count:
    backgroundColor: "linear-gradient(180deg,#0a0b0e,#0e1013)"
    textColor: "{colors.lit-amber}"
    typography: "{typography.data}"
    rounded: "{rounded.key}"
    padding: "7px 12px 6px"
  badge-tier-s:
    backgroundColor: "#241503"
    textColor: "{colors.filament-gold}"
    rounded: "{rounded.chip}"
    padding: "3px 7px"
---

# Design System: Palydex

## Overview

**Creative North Star: "The Nixie Laboratory Counter"**

Palydex is a laboratory counting instrument for Palworld: every answer arrives as a lit reading on blackened steel. The whole app is a bench of machined charcoal plates — corner rivets, top-light edges, recessed glass wells — read like a cockpit by a mid-session player: mode placards across the top, a nixie count bank at the right, one glance per answer. The world deliberately refuses both the neon gaming dashboard and the dead pixel-arcade look (its own predecessor); readability outranks spectacle everywhere.

The only warm thing in the room is the lit channel: plasma-orange nixie light carried by a small set of dedicated tokens, applied to active controls and to every count. All numeric data — HUD counters, stats, dex numbers, breeding power — is set in Chivo Mono glass digits with tabular numerals; the important ones glow with a tube halo. Two indicator lamps carry player state: green for caught, rose for favorite. Night mode swaps the nixie orange for cold-cathode VFD blue while every steel surface stays identical — same bench, different tubes.

**Key Characteristics:**
- Near-black steel ground (#0a0b0d) under machined plates (#17191e → #121418) with 1px borders, inset top-light, corner rivets, and soft drop shadows
- One lit channel (5 tokens: `--lit`, `--litline`, `--litbg`, `--tube`, `--glow-cyan`) owns every glow; night mode re-tubes it to VFD blue and touches nothing else
- Three embedded faces, no italics: Barlow prose, Barlow Condensed engraved caps, Chivo Mono digits (variable 100–900, used at 300–500)
- Radius ladder 5/7/8/10/12px; perfect circles only for lamps, rivets, screw heads, and bench hardware
- Motion is minimal and eased — a ~1s boot tube-ignition, a .18s view fade, a .7s count float — all gated behind `prefers-reduced-motion`; nothing loops, nothing flashes

## Colors

A charcoal-steel neutral ramp with a single warm plasma channel; legacy role tokens (`--screen`, `--card`, `--line`, `--accent`, even `--glow-cyan`) keep their old names but are mapped onto laboratory values, so components consume roles while the world owns the hues.

### Primary
- **Plasma Orange** (`--accent` #ff9a1c) with **Lit Amber** (`--lit` #ffb054): the nixie plasma. Active mode keys, the GO button, focused-input borders, selected cards, links, the power lens dot — always delivered through the lit-channel tokens: `--litline` (border, rgba(255,154,28,.62)), `--litbg` (ember-glass gradient #221a10 → #181209), `--tube` (three-layer digit glow), and `--glow-cyan` (legacy name; now the 1px orange ring + 12px halo on lit controls).
- **Filament Gold** (`--gold` #ffc46b) and **Ember Orange** (`--orange` #ffa94d): the hotter and cooler ends of the same plasma — S-tier and A-tier readings, stat-bar filament tops, hot work-suitability chips.

### Secondary
- **Lamp Green** (`--lamp-green` #6fe392): the caught/owned lamp — caught toggle, green dex number on caught cards, CAUGHT HUD digits, surgery-safe chips, B-tier. Always paired with `--lamp-green-glow`.
- **Lamp Rose** (`--lamp-rose` #ff8ca6): the favorite lamp — favorite toggle, favorite count float, self-only pills. Always paired with `--lamp-rose-glow`.

### Tertiary
- **VFD Blue** (#5fe6ff) / **VFD Lit** (#8ceaff): night mode's cold-cathode tube family. Never appears by day; exists only as the `body.night` remap of the lit channel.
- **Element data colors** (`--el-*`): nine saturated hues for Palworld element identity on card edges, chips, and rings — data, not decoration, and unchanged by night mode.

### Neutral
- **Chassis Black** (#0a0b0d): the page ground, washed with a faint top plasma haze (rgba(255,138,0,.05)) and an edge vignette.
- **Plate Steel** (#17191e → #121418) / **Card Steel** (#16181d → #13151a): the machined-plate and specimen-card gradients; every raised surface is a subtle vertical steel gradient, never flat.
- **Well Black** (`--lcd` #0b0c0f) and **Hint Plate** (`--lcd2` #101216): recessed glass wells (inputs, HUD counters, stat tracks) and quiet flat hint plates.
- **Steel Line** (#26292f), **Card Line** (#2a2d33), **Plate Edge** (#33373e), **Steel Line Bright** (#383d45): the 1px border ladder, dim to bright; hover brightens borders to #4a505a.
- **Text** (#dfe2e6), **Muted** (#a2a8b1), **Faint** (#818893), **White** (#f2f3f5), **Placard Lilac** (#aab2bd): the text ramp; lilac is the engraved section-label voice.

### Named Rules
**The Same-Bench Rule.** `body.night` remaps only the lit channel and its warm aliases (`--lit`, `--litline`, `--litbg`, `--tube`, the glow tokens, `--accent`, `--gold`, `--orange`, `--magenta`, the lens) to the VFD blue family. Every neutral — chassis, plates, lines, text — stays byte-identical, and the green/rose lamps and element colors keep their hues. Same bench, different tubes. Any new lit treatment must route through these tokens or night mode silently breaks it.

**The One-Warm-Channel Rule.** Plasma orange is the only warm light in the room, and it means "lit / active / an answer." Rest states are steel; hover is brighter steel (border #4a505a + white text), never orange. Green means caught, rose means favorite — nothing else may borrow any of the three.

**The Legacy-Name Rule.** Role tokens keep pre-redesign names (`--glow-cyan` is orange, `--cyan` is #ff9a1c, `--screen` is steel). Style through the role token, never through what its name suggests.

## Typography

**Display Font:** Barlow Condensed 500/600 (fallback Barlow, sans-serif)
**Body Font:** Barlow 400/500/600 (fallback system-ui, sans-serif)
**Data Font:** Chivo Mono, variable 100–900, used at 300–500 (fallback ui-monospace)

**Character:** An instrument-panel trio: Barlow Condensed at 600 is the engraving on placards and mode keys — uppercase, heavily letter-spaced, never prose; Barlow carries all reading; Chivo Mono is the glass digit tube for every number on the bench. In the app all three ship as data-URI WOFF2 (offline constraint); the static SEO pages load the same faces as `/fonts/*.woff2`. No italic faces exist anywhere.

### Hierarchy
- **Display** (Condensed 600, clamp(22px, 2.6vw, 30px), 1.0, 6px tracking, uppercase): the engraved PALYDEX brand — steel-colored (#d5d9de) with a top-light/undercut text-shadow, not lit.
- **Label / Placard caps** (Condensed 600, 9.5–15px, 1.4–2.2px tracking, uppercase): mode tabs (13.5px), segment keys (12px), section headers (12.5px, lilac, closed by a hairline rule), panel h2s, modal titles, HUD labels (9.5px, 1.8px tracking), toasts.
- **Body** (Barlow 400, 15.5px/1.5, .1px tracking): all reading; hints and subtexts at 12.5–14px; emphasized names at Barlow 600 14–14.5px.
- **Data** (Chivo Mono 300–500, `font-variant-numeric: tabular-nums`): HUD digits 21px at weight 300 with `--tube` glow; tier letters 19px/500; key-values 15px/500; stats 14px/500; badges 11px/500; dex numbers 11px/400; version line 10.5px/400.

### Named Rules
**The Engraved-Caps Rule.** Barlow Condensed is engraving, not prose: 600 weight, uppercase, letter-spaced ≥1.4px, ≤15px except the brand. Anything a player reads in sentences is Barlow.

**The Glass-Digit Rule.** Every count, stat, rank, and ID is Chivo Mono with tabular numerals. Counts that answer the player's question glow (`--tube`); incidental numbers don't.

**The No-Italic Rule.** No italic faces are embedded and `font-style: italic` is never used (`i` elements are reset to normal); bold stops at 600 (`b, strong { font-weight: 600 }`).

## Layout

An open bench: `.device` is a transparent frame (max-width 1560px, `padding: 10px 16px 26px`) directly on the chassis ground — no outer card. The header is a riveted control plate (`.dev-top`): flex row of power lens + unlit lamps, engraved brand, mode-selector tabs, and the nixie count bank pushed right, on a 12px-radius steel plate with corner rivets.

Working views use a two-column grid: `minmax(0,1fr)` content beside a fixed 412px detail plate (`.grid-2`, 22px gap), collapsing to one column below 1000px. The Pal wall is `repeat(auto-fill, minmax(184px,1fr))` with 13px gaps (148px/9px below 760px). Spacing runs 6/7/10/12/13/18/22px with 18px plate padding as the anchor; the header plate is `14px 18px`. Below 760px body drops to 15px, the brand to 20px/4px tracking, HUD digits to 17px; the bench deck (d-pad + hardware buttons) hides below 640px. Mobile inputs hold 16px to prevent iOS zoom.

## Elevation & Depth

Depth is machined, not floated: surfaces read as steel plates catching light from above. The plate recipe is a 1px steel border + an inset top-light (`inset 0 1px 0 rgba(255,255,255,.05–.06)`) + an offset soft drop shadow (`0 12px 30px rgba(0,0,0,.45)` for plates, `0 2px 5px rgba(0,0,0,.4)` for controls, `0 3px 10px rgba(0,0,0,.35)` for cards) + radial-gradient rivet dots in the corners of top-level plates. Recessed wells invert it: `inset 0 2px 6px rgba(0,0,0,.55–.6)` with a faint bottom edge-light. Glow is reserved for the lit channel (`--tube`, `--glow-cyan`, lamp glows) — light emitting from data, never ambience. Modals sit on a blurred scrim (`rgba(6,7,9,.8)` + 3px backdrop-blur) with a deep `0 24px 70px` halo.

### Shadow Vocabulary
- **Plate** (`inset 0 1px 0 rgba(255,255,255,.05), 0 12px 30px rgba(0,0,0,.45)`): top-level plates (header, screen/bpanel backdrops, detail).
- **Control** (`inset 0 1px 0 rgba(255,255,255,.06), 0 2px 5px rgba(0,0,0,.4)`): keys and placard buttons; `:active` collapses to `translateY(1px)` + inset press.
- **Well** (`inset 0 2px 6px rgba(0,0,0,.6)`): HUD counters, search, selects, stat tracks, tier-letter blocks.
- **Tube** (`--tube: 0 0 4px rgba(255,166,60,.85), 0 0 12px rgba(255,138,0,.5), 0 0 26px rgba(255,138,0,.22)`): text-shadow on glowing digits.
- **Lit ring** (`--glow-cyan: 0 0 0 1px rgba(255,138,0,.22), 0 0 12px rgba(255,138,0,.2)`): box glow on active keys, selected cards, focused wells.
- **Lamps** (`--lamp-green-glow`, `--lamp-rose-glow`): 6px + 14px caught/favorite halos.

### Named Rules
**The Backdrop-Plate Rule.** Panels that host dropdowns or popups (`.screen`, `.bpanel`) draw their plate on a `::before` layer at `z-index: -1` with `isolation: isolate`, keeping the element itself background-free so overlays escape the plate. New panels with floating children must use this structure, not a plain background.

**The Machined-Light Rule.** Every raised surface carries the top-light inset; every recessed surface carries the well inset. Hover never lifts, scales, or glows — it sharpens the steel (brighter border, whiter text). Glow belongs to lit data only.

## Shapes

A rounded-rectangle machine language on a strict radius ladder: 5px chips/badges, 7px controls, 8px keys/wells/avatars, 10px cards/inner panels, 12px top-level plates; stat tracks and gauges are 99px pill slots. Perfect circles are hardware only: the 10px power lens, 7px unlit lamps, 3.5px corner rivets, 4px screw-head ends, and the round bench buttons. Borders are uniformly 1px (1.5px on rarity chips).

Signature hardware details: corner rivets (radial-gradient dots, #3f444d highlight → #202329) on the header and top-level plates; screw-head ends (4px machined dots at left and right) on the primary lit controls (`.tab.active`, `.wgo`); HUD wells carry a glass-top diagonal highlight plus a 4px anode-mesh grid (repeating 1px lines both axes). Section headers are engraved caps closed by a 1px hairline rule (`::after` flex line, #2e323a at .8 opacity).

The icon language is a single round-cap stroke set (`currentColor` SVG, 2–3px strokes, round joins): the `PIX_CHECK` check and `PIX_STAR` star JS constants (12px, class `.pxi`, −2px baseline), the search magnifier, and the SFX note. Functional text glyphs survive as data: `×` close, `⇅` sort flip, `♀`/`♂` gender.

### Named Rules
**The Radius-Ladder Rule.** Radii come only from the ladder (5/7/8/10/12/99px); circles are reserved for physical hardware (lamps, rivets, screws, bench buttons).

**The Rivet Rule.** Corner rivets mark top-level plates only; nested cards, chips, and wells stay clean so the chassis stays legible.

## Components

### Tabs (mode selector keys)
- **Character:** machined instrument keys, not a nav bar.
- **Shape:** 8px radius, 1px #383d45 border, `padding: 10px 16px`, steel key gradient (#1d2026 → #15171c) with control shadow.
- **Type:** Condensed 600, 13.5px, 2px tracking, uppercase; muted at rest.
- **Hover:** white text + #4a505a border; no fill change, no movement.
- **Active:** the full lit treatment — plasma text on `--litbg`, `--litline` border, `--glow-cyan` ring, 8px text glow, and 4px screw-head ends; `.15s` ease on color/border/shadow.

### Buttons
- **Mini / Reset** (`.mini`, `.reset`): Barlow 600 12.5px uppercase placard buttons, 7px radius, key gradient, control shadow; hover sharpens steel; `:active` is a 1px press with inset shadow.
- **Primary action** (`.wgo`): the lit key — `--litbg` fill, `--litline` border, lit-amber text with glow, screw-head ends; hover moves text to filament gold.
- **Segment keys** (`.gseg`, `.stageseg`, `.bsub .t`): Condensed 600 12px keys, 7px radius; the on-state takes the full lit treatment.
- **Bench hardware** (`.dbtn`): round steel-lamp buttons (blue-steel and amber radial gradients); pressed-on state glows plasma (VFD blue at night). The amber button toggles night mode, persisted to localStorage.

### Cards (specimen cards)
- **Shape:** 10px radius, 1px #2a2d33 border, card-steel gradient, faint top-light + `0 3px 10px` shadow.
- **Anatomy:** 3px element-colored top edge (`.eledge`); recessed near-black portrait well (8px radius, deep inset, element ring via `--ring`); Chivo Mono 11px dex number; Barlow 600 14.5px name; muted 12.5px subline.
- **Hover:** border to #454b54 and a deeper shadow — no lift, no glow. **Selected:** `--litline` border + `--glow-cyan`.
- **States:** caught cards light the dex number in lamp green; corner toggles fill green/rose wells with lamp glows; the breeding-power line reserves 66px right padding to clear them.

### Inputs / Fields
- **Style:** recessed glass wells — `--lcd` background, 1px #33373e border, 8px radius, deep well inset; Barlow 15px text, plasma caret, faint placeholders. Selects and the depth stepper share the treatment at 7px radius.
- **Focus:** `--litline` border + a 10px plasma (or VFD) halo on top of the well inset.

### Badges (tier & rarity)
- **Tier badges** (`.tbadge`): Chivo Mono 500 11px chips, 5px radius, on the plasma-intensity ramp — S: filament gold on ember glass #241503 with glow ring and text glow; A: ember orange on #221a10; B: lamp green on #10231a; C: steel #c9ced6 on #171a1f; D: faint on #131519. Tier-board letter blocks (`.tierlabel`, Chivo Mono 19px in recessed wells) ride the same ramp; nothing flashes.
- **Rarity chips** (`.rar`): star icon + number; steel outline by default, blue/purple gradient fills at rarity 5+/8+, gold gradient with a 9px halo at 10+.
- **Rarity gauge** (`.gauge`): a 12px recessed pill track whose plasma fades left-to-right (rgba(255,138,0,.5) → .05) — an intensity reading, not a fill bar — with a steel marker (`.gmark`) at the value.

### Stat bars (filament tubes)
- **Track:** 10px-high 99px pill, near-black #0a0b0e, 1px border, well inset.
- **Fill** (`.sfill`): the lit filament — vertical gradient #ffc46b → #ff8a00 with an 8px plasma halo and a glass-top highlight (`inset 0 1px 0 rgba(255,255,255,.5)`); VFD blue at night.

### HUD count bank (signature)
- **`.counts`** renders nixie tubes: each span is a recessed well (8px radius, deep inset) with a glass-top diagonal highlight and 4px anode-mesh grid, stacking a Chivo Mono 300 21px lit-amber digit with `--tube` glow above an engraved 9.5px/1.8px caps label. The CAUGHT tube burns lamp green. Right-aligned on the header plate; digits drop to 17px on mobile.

### Night mode (signature)
- **`body.night`** re-tubes the bench per the Same-Bench Rule: the lit channel and warm aliases become the VFD blue family (#5fe6ff / #8ceaff, blue `--litbg` glass #0e1c22 → #0a151b, blue `--tube` and rings) and per-component warm accents (S/A badges, stat fills, hot chips, notes) get blue equivalents. Steel, text, lamps, and element colors do not move.

### Sound & count juice (signature)
- Opt-in WebAudio instrument sounds (off by default, note-icon toggle in the header, persisted): relay click on toggle, soft sine blips on keys, a two-tone chime on count. Catching or favoriting floats a Chivo Mono `+1` (`.oneup`) in lit amber or lamp rose from the click point (.7s eased rise, removed under reduced motion). Toasts are lit placard plates (Condensed caps on `--litline`/`--glow-cyan`).

## Do's and Don'ts

### Do:
- **Do** route every lit/active/selected/focused treatment through the five lit-channel tokens (`--lit`, `--litline`, `--litbg`, `--tube`, `--glow-cyan`) so night mode re-tubes it for free (the Same-Bench Rule).
- **Do** build new panels with the plate recipe — 1px steel border, `inset 0 1px 0 rgba(255,255,255,.05)` top-light, offset soft shadow, 10–12px radius, corner rivets at top level — and draw plates that host popups on a `::before` backdrop layer (`z-index:-1`, `isolation:isolate`).
- **Do** set every numeral in Chivo Mono with `font-variant-numeric: tabular-nums` (300 for big glowing digits, 400–500 for inline data), and glow only the numbers that are answers.
- **Do** label sections with engraved Condensed 600 caps (lilac, ≥1.4px tracking) closed by a 1px hairline rule, and keep radii on the ladder (5/7/8/10/12/99px).
- **Do** keep all motion minimal, eased, and gated behind `prefers-reduced-motion` — the ~1s boot ignition, .18s view fade, .7s count float, .15s control transitions are the entire vocabulary — and draw new icons in the round-cap 2–3px stroke set (`currentColor`), keeping the data glyphs `× ⇅ ♀ ♂`.

### Don't:
- **Don't** hardcode orange into component states — a raw `#ff9a1c` border or glow is a night-mode bug; use the tokens (and remember `--glow-cyan` is a legacy name for the orange ring).
- **Don't** let hover lift, scale, or glow — hover sharpens steel (border #4a505a, whiter text); glow means lit data, and green/rose mean caught/favorite only.
- **Don't** flash, pulse, or loop any animation, and don't play sound without the opt-in SFX toggle.
- **Don't** use italics anywhere or weights above 600; Condensed caps never carry prose and never exceed 15px outside the brand.
- **Don't** load external fonts or network assets in the app (all faces are data-URI WOFF2; static pages use local `/fonts/*.woff2`), and don't recolor or restyle Pal/element/item art — embedded game assets, no license to alter.
