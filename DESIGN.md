---
name: Palydex
description: Palworld 1.0 companion rendered as a CRT arcade cabinet screen — phosphor black, 16-color sprite palette, scanlines and glow.
colors:
  phosphor-black: "#05070d"
  deep-blue-panel: "#0a1022"
  sprite-blue: "#1e6cff"
  live-cyan: "#3fe0ff"
  caught-green: "#3ee54c"
  coin-yellow: "#ffe63a"
  attention-orange: "#ff9427"
  cabinet-red: "#ff4b3e"
  rank-magenta: "#ff3fa4"
  special-violet: "#8a4bff"
  favorite-pink: "#ff6ec7"
  label-lilac: "#b9a0ff"
  marquee-gold: "#ffc21c"
  phosphor-white: "#f4f6ff"
  dim-steel: "#8b93a7"
  screen: "#0a1022"
  card: "#0b1226"
  lcd-well: "#061224"
  line: "#22346f"
  line-bright: "#33479c"
  panel-raised: "#12204a"
  text: "#cfd9ff"
  text-muted: "#8fa0d8"
  text-faint: "#7a89c2"
typography:
  display:
    fontFamily: "\"Press Start 2P\", \"VT323\", monospace"
    fontSize: "clamp(20px, 3.2vw, 34px)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "2px"
  body:
    fontFamily: "\"VT323\", \"Courier New\", monospace"
    fontSize: "20px"
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: "0.2px"
  label:
    fontFamily: "\"Press Start 2P\", \"VT323\", monospace"
    fontSize: "9px"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "1px"
rounded:
  none: "0px"
  cabinet-button: "50%"
spacing:
  hair: "6px"
  tight: "8px"
  grid: "13px"
  panel: "18px"
  section: "22px"
components:
  tab:
    backgroundColor: "{colors.deep-blue-panel}"
    textColor: "{colors.text-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "12px 14px 11px"
  tab-active:
    backgroundColor: "rgba(63,224,255,.08)"
    textColor: "{colors.live-cyan}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "12px 14px 11px"
  button-mini:
    backgroundColor: "{colors.panel-raised}"
    textColor: "{colors.text}"
    rounded: "{rounded.none}"
    padding: "8px 13px"
  card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.none}"
  input-search:
    backgroundColor: "{colors.lcd-well}"
    textColor: "{colors.phosphor-white}"
    rounded: "{rounded.none}"
    padding: "9px 15px"
  badge-tier-s:
    backgroundColor: "#241c00"
    textColor: "{colors.marquee-gold}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "3px 6px"
---

# Design System: Palydex

## Overview

**Creative North Star: "The Arcade Cabinet Screen"**

Palydex is not a website about a game — it is the reference tool rendered in the medium games themselves lived in. The whole app plays on a single CRT: a 16-color sprite palette over phosphor black, fixed scanline and bloom overlays, notched pixel plates for panels, stage-select tabs, and a 1UP/HI-SCORE HUD cluster. Every answer (a breeding pair, a tier board, a map route) reads like a high-score table on an attract screen. The world deliberately refuses both the category's dark-dashboard-with-neon default and the project's earlier Pokédex-homage device shell; the shell's chrome (screws, hinge, lens barrel) is stripped to a bare marquee-and-screen frame.

Density is high and unapologetic: a wall of sprite-tile Pal cards beside a fixed detail plate, terminal-style hint bars, segmented pixel stat meters. Color is law-governed rather than decorative — each hue in the 16-color palette owns exactly one meaning, and the rarest color (flashing gold) is reserved for the rarest things. Depth comes from inset borders and phosphor glow, never from drop shadows. Night mode is not a dimmer: it swaps the entire token set to a green-phosphor monochrome monitor.

**Key Characteristics:**
- Phosphor-black ground (#05070d) with faint blue/violet CRT wash; fixed scanline + bloom overlays (off-switch: `body.nofx`)
- 16 named sprite colors, each with a single semantic job; cyan = live, gold = ranked glory, orange = attention, green = caught, pink = favorite, lilac = label
- Two embedded fonts only: Press Start 2P for tiny caps chrome, VT323 for everything readable
- Square corners everywhere; major plates carry a 10px-step notched clip-path
- Motion is frame-quantized with `steps()` and fully gated behind `prefers-reduced-motion`

## Colors

A fixed 16-color arcade sprite palette over phosphor black; semantic role tokens (`--screen`, `--card`, `--line`, `--text`, `--muted`…) keep their legacy names but are mapped onto arcade values, so components consume roles while the world owns the hues.

### Primary
- **Live Cyan** (`--cyan` / `--accent`): the single "this is alive right now" color — active tab, focused input border, hovered/selected card border, segmented stat-bar fill, map zoom controls, power-on lens dot. Always paired with its glow (`--glow-cyan: 0 0 6px rgba(63,224,255,.55), 0 0 18px rgba(63,224,255,.22)`).

### Secondary
- **Marquee Gold** (`--gold` / `--warn`): glory and rank. Static on the PALYDEX marquee (`text-shadow: 3px 3px 0 var(--red)` drop-print plus gold bloom) and on rarity-10+ chips; flashing only per the Gold Law below. Glow: `--glow-gold`.
- **Rank Magenta** (`--magenta` / `--accent2`): A-tier badges, breeding-target tags.
- **Special Violet** (`--special`): dark-element and special accents.

### Tertiary
- **Caught Green** (`--green`): surveyed/owned state — caught toggle, green dex number on caught cards, CAUGHT HUD counter, surgery-safe chips.
- **Favorite Pink** (`--pink`): favorites toggle, self-only breeding pills.
- **Attention Orange** (`--orange`): the static attention channel — warning notes (`.note`), hot work-suitability chips (`.wk.hot`), and the `»` prompt glyph on terminal hint bars. Orange never flashes and gold never warns.
- **Label Lilac** (`--lilac`): section-header caps, passive-rank chips, variant pills — the quiet metadata voice.

### Neutral
- **Phosphor Black** (`--ph` #05070d): the page ground, washed with faint radial blue/violet light.
- **Deep Blue Panel** (`--deep` #0a1022) / **Screen** (`--screen`) / **Card** (`--card` #0b1226) / **Panel Raised** (`--panel3` #12204a): the stepped panel ladder, dark to less-dark.
- **LCD Well** (`--lcd` #061224): recessed input/track wells.
- **Line** (`--line` #22346f) and **Line Bright** (`--line2` #33479c): the 2px border grammar; bright line for panels and controls, dim line for cards and chips.
- **Text** (`--text` #cfd9ff), **Muted** (`--muted` #8fa0d8), **Faint** (`--muted2` #7a89c2), **Phosphor White** (`--white` #f4f6ff): the four-step text ramp.

### Named Rules
**The Gold Law.** Static gold is marquee/rarity-ranked chrome — the PALYDEX marquee, S-tier badge fill, rarity-10+ chips. *Flashing* gold (`goldlaw` 1.6s `steps(2)` brightness pulse) is reserved for legendary/S-tier only. Nothing else on any screen may flash gold; the flash's rarity is its meaning.

**The Cyan Live Rule.** Cyan means "live, selected, or focused now," and it always glows (`--glow-cyan`). Hover states move borders toward cyan; rest states never wear it.

**The Orange Channel Rule.** Static attention (warnings, hot chips, terminal prompts) is orange, never gold and never red. Red belongs to the cabinet lights and element chips, not to messaging.

## Typography

**Display Font:** Press Start 2P (embedded WOFF2 data URI; fallback VT323, monospace)
**Body Font:** VT323 (embedded WOFF2 data URI; fallback Courier New, monospace)

**Character:** Authentic bitmap-era pairing — Press Start 2P is the cabinet's silk-screened chrome, used tiny and in caps; VT323 is the phosphor terminal voice that carries all reading and all data. Both fonts ship inline as data URIs; the app loads no external font (offline constraint).

### Hierarchy
- **Display / Marquee** (400, `clamp(20px, 3.2vw, 34px)`, 1.0, 2px tracking): the PALYDEX marquee only — gold with a hard red drop-print and gold bloom.
- **Headline** (Press Start 2P 400, 10–12px, 1px tracking, uppercase): panel `h2`s, modal titles, wheel-row names.
- **Label** (Press Start 2P 400, 7–10px, 1–1.5px tracking, uppercase): tabs (10px), segment buttons (9px), section headers (9px, lilac, dash-flanked), tier badges (9px), HUD count labels (7px). Press Start 2P never appears above 12px except the marquee.
- **Body** (VT323 400, 20px/1.35, .2px tracking): default reading size for the whole app; hint bars and subtexts drop to 15–18px.
- **Data** (VT323 400, 16–21px, `font-variant-numeric: tabular-nums` on counters): inputs (18–21px), selects (17px), HUD numbers (20px), dex numbers (16px).

### Named Rules
**The Caps-for-Chrome Rule.** Press Start 2P is chrome, not prose: tiny (7–12px), uppercase, letter-spaced. Anything a player actually reads — sentences, stats, tooltips — is VT323 at 16px or larger.

## Layout

A full-bleed cabinet: `.device` is a transparent frame (max-width 1560px, `padding: 10px 14px 26px`) on the phosphor ground — no card, no border, no shadow. The header row (`.dev-top`) is a flex marquee — power dot + lights, gold marquee, stage-select tabs, HUD counts pushed right — closed by a 2px dashed rule. Dashed 2px lines in `--line` are the app's only separators: header bottom, footer top, section-header flanks, hint-bar borders.

Working views use a two-column grid: `minmax(0,1fr)` content beside a fixed 412px detail plate (`.grid-2`, 22px gap), collapsing to one column below 1000px. The Pal wall is `repeat(auto-fill, minmax(184px,1fr))` with 13px gaps. Spacing runs on small pixel steps — 6/8/10/13/14/16/18/22 — with 18px panel padding as the anchor. Below 760px, body drops to 18px, tabs to 8px, and the cabinet control deck (d-pad + buttons) hides below 640px.

## Elevation & Depth

No drop shadows. Depth is conveyed three ways: (1) the stepped panel-color ladder (ground → deep → card → panel-raised); (2) inset strokes — every plate wears `border: 2px solid var(--line2)` plus `inset 0 0 0 2px rgba(5,7,13,.8)` and a faint interior wash `inset 0 0 44px rgba(30,108,255,.05)`; (3) phosphor glow as the hover/active/selected response. The only screen-space shadows are light emissions: `--glow-cyan`, `--glow-gold`, modal halos (`0 0 60px rgba(30,108,255,.25)`), and the map popup's blue bloom. Physical cabinet buttons alone keep a hard `0 3px 0 rgba(0,0,0,.6)` ledge that collapses on `:active` (translateY(2px)).

Two fixed capability overlays sit above everything: `body::before` scanlines (1px dark lines on a 3px rhythm, z-index 2000) and `body::after` phosphor bloom (edge vignette + faint cyan center glow, z-index 1999). Both are `pointer-events: none` and are removed wholesale by the `body.nofx` off-switch class.

### Named Rules
**The Glow-Not-Shadow Rule.** Nothing casts a shadow; things emit light. Any state change is expressed as border color plus glow, never as lift, scale, or drop shadow (the arcade layer explicitly sets `transform: none` on hover where the old theme lifted).

## Shapes

Square corners are the law: `--radius: 0px`, `border-radius: 0` restated on every component (cards, chips, pills, inputs, badges, popups, canvas). The single exception is physical hardware: `.dbtn` cabinet buttons are perfect circles (`border-radius: 50%` — "physical cabinet buttons stay round").

Major plates are notched pixel plates: `.screen`, `.bpanel`, and `.detail` carry a 12-point `clip-path` polygon that cuts a 10px square step from each corner — the signature silhouette of the world. Borders are uniformly 2px solid (1–1.5px on small chips); section punctuation is 2px dashed. Stat bars are segmented pixel meters: a repeating 8px-on / 2px-off cyan gradient in a 12px LCD track.

The icon language is dual: authored pixel-grid SVGs (the `PIX_CHECK` checkmark and `PIX_STAR` star constants — 11px `currentColor` rect-step paths, class `.pxi`, baseline-nudged −2px) sit beside kept text-mode glyph idioms — `▶` tab cursor, `»` terminal prompt, `×` close/multiply, `⇅` sort flip, `♀`/`♂` gender. Thin-stroke outline SVGs survive only for the search magnifier and moon badge.

### Named Rules
**The Square-Corner Law.** Everything drawn on the screen has 0 radius. Round is reserved for the two physical cabinet buttons on the control deck.

**The Ten-Pixel Notch Rule.** Top-level plates (`.screen`, `.bpanel`, `.detail`) get the 10px-step notched clip-path; nested cards and chips stay plain squares so the notch stays special.

## Components

### Tabs (stage select)
- **Character:** an arcade stage-select row, not a nav bar.
- **Shape:** square, `border: 2px solid var(--line)`, `padding: 12px 14px 11px`.
- **Type:** Press Start 2P 10px uppercase, 1px tracking; muted at rest.
- **Active:** cyan text + cyan border + `rgba(63,224,255,.08)` fill + cyan glow, with a blinking `▶` cursor at left (`curblink` 1.1s `steps(2)`).
- **Hover:** white text, bright-line border; no fill, no movement.

### Buttons
- **Mini / Reset** (`.mini`, `.reset`): VT323 16px uppercase on panel-raised, 2px bright-line border, `padding: 8px 13px`. Hover = cyan border + white text (no transform); active = `translateY(2px)` press.
- **Primary action** (`.wgo`): sprite-blue fill, cyan border, white text, cyan glow.
- **Segment groups** (`.gseg`, `.stageseg`): Press Start 2P 9px pills on deep panel; the on-state uses the full cyan live treatment.
- **Cabinet buttons** (`.dbtn`): the round exception — 26px physical circles with a hard black ledge shadow, glow when pressed-on (night toggle is the amber button, persisted to localStorage).

### Cards (sprite tiles)
- **Corner style:** square, `border: 2px solid var(--line)`, no shadow at rest.
- **Background:** `--card` (#0b1226); 4px element-colored top edge (`.eledge`); portrait wells are near-black (#01030a) with a faint cyan inset ring.
- **Hover/selected:** cyan border + cyan glow (selected adds a 2px inner cyan wash); no lift.
- **States:** caught cards turn their dex number green; the check/star toggles fill green/pink with matching 8px glows.

### Inputs / Fields
- **Style:** recessed LCD wells — `--lcd` background, 2px bright-line border, square, VT323 18–21px, cyan caret; placeholders in faint text.
- **Focus:** cyan border + cyan glow (`:focus-within` on the search shell); selects share the treatment.

### Badges (tier & rarity)
- **Tier badges:** Press Start 2P 9px, `3px 6px`, square; S = gold on #241c00 with gold glow (flashing per the Gold Law), A = magenta, B = green, C = cyan, D = steel — each as colored text + 1px matching border on a dark tint.
- **Rarity chips:** `PIX_STAR` + number; blue (rarity 5+), purple (8+), static gold gradient (10+).

### Hint bars (terminal messages)
- **Style:** near-black #060d1d, 2px dashed border, VT323 16px muted text, opened by an orange `»` prompt glyph.

### HUD score cluster (signature)
- **`.counts`** renders arcade counters: each `span` stacks a Press Start 2P 7px faint-lilac label (`i` — PALS / CAUGHT / PAIRS / SELF-ONLY) over a VT323 20px tabular-nums value (`b`); the CAUGHT value is green. Right-aligned in the marquee row like a HI-SCORE readout.

### Night mode (signature)
- **`body.night`** is a full green-phosphor token remap, not a dim filter: ground goes #020804, cyan→#54ff7e, gold→#e8ff54, magenta→#7dff9e, pink→#a9ff8e, lilac→#8fe8a4, with matching green glows — the whole palette collapses onto one green monitor while every law (live color, gold law, glow grammar) keeps working through the tokens.

## Do's and Don'ts

### Do:
- **Do** express every live/hover/selected state as cyan border + `--glow-cyan`, keeping `transform: none` (press feedback only: `translateY(2px)` on `:active`).
- **Do** quantize all animation with `steps()` (`curblink` steps(2), `goldlaw` steps(2), `eggWobble` steps(6)) and wrap it in `@media (prefers-reduced-motion: no-preference)` with an explicit `reduce` kill-switch.
- **Do** route new colors through the semantic role tokens (`--screen`, `--card`, `--line`, `--text`…) so night mode's green-phosphor remap covers them for free.
- **Do** give new top-level plates the 10px notched clip-path and `2px solid var(--line2)` border; use 2px dashed `--line` for any separator.
- **Do** draw new icons as pixel-grid `currentColor` SVG rect-paths (`.pxi`, ~11px, −2px baseline nudge), and keep the text-mode glyphs (`▶ » × ⇅ ♀ ♂`) where they already speak.

### Don't:
- **Don't** flash gold on anything except legendary rarity and S-tier; static gold stays confined to marquee and rarity-ranked chrome (the Gold Law).
- **Don't** add border-radius to anything on-screen; only the round cabinet `.dbtn` hardware is exempt (the Square-Corner Law).
- **Don't** use drop shadows, lifts, or scale-on-hover — depth is inset strokes and emitted glow only.
- **Don't** load external fonts, CDN assets, or any network resource; both fonts are embedded data-URI WOFF2 and the app must stay single-file offline.
- **Don't** recolor, filter, or restyle Pal/element/item art — they are embedded Palworld game assets with no license to alter.
- **Don't** set Press Start 2P above 12px anywhere but the marquee, and don't set body/data VT323 below 15px.
