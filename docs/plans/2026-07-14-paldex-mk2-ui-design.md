# Paldex Mk-II — UI Redesign Design Doc

**Date:** 2026-07-14 · **Status:** Approved by George

## Goal

Evolve the existing retro Pokédex-device theme (keep the identity) into a visually
striking, functional "device": real Pal artwork everywhere, a richer detail panel,
a proper breeding stage, working device hardware (D-pad, LEDs, night mode), and
accessibility fixes — while preserving the single-file, offline, no-server promise.

## Decisions (user-confirmed)

1. **Direction:** Evolve the Pokédex device look — not a modern reskin.
2. **Images:** Embed all icons as base64 data-URIs in `index.html` (~6MB total). No
   external requests at runtime, no icons/ folder, no hotlinking.

## Image sourcing

- Source: `tylercamp/palcalc` GitHub repo — the **same verified source** as the
  breeding/stats data (see VERIFICATION.md). `PalCalc.UI/Resources/Pals/*.png`
  (299 files, one per record, keyed by InternalName) + `PalCalc.UI/Resources/Elements/*.png` (9).
- Pinned to a specific commit SHA for reproducibility.
- New build step `_fetch_icons.py`: download → validate count vs pals_1.0.json →
  emit `_icons.json` `{internalName: dataURI}` (+ `_element_icons` map).
- `_assemble.py` injects `_icons.json` as a third data block.
- Licensing: Palworld assets © Pocketpair, redistributed via palcalc; credited in
  README; personal local use.

## UI changes

### Grid cards
- Icon capsule (real art) with element-tinted ring; element gradient edge on card.
- Rarity badge tiers (1–4 plain, 5–7 blue, 8–9 purple, 10+ gold, matching game rarity color conventions).
- Nocturnal moon glyph; variant tag stays.
- Hover: lift + shine sweep. Entry: staggered fade-up (respect `prefers-reduced-motion`).
- A11y: `role="button"`, `tabindex="0"`, Enter/Space activate, visible focus ring.

### Detail panel
- Element-tinted hero banner with large icon.
- Animated stat bars normalized to dex-wide max per stat.
- Work suitability as icon + level pips (1–5).
- Breeding-power gauge across 20–3100 with "lower = rarer" annotation.
- Bred-from / breeds-into entries get icon chips.

### Breeding tab
- Searchable parent pickers with icon thumbnails in the dropdown list.
- Forward result: *Parent × Parent → Egg → Child* ceremony layout; special-combo
  and gender-locked badges kept.
- Reverse: parent-pair rows with icons.
- Chain: step-by-step icon path with arrows.
- Egg-motif empty state instead of bare text.

### Device shell
- D-pad becomes functional: arrow keys / D-pad clicks move grid selection.
- Status LEDs blink on selection & tab switch.
- Lens: subtle animated glint.
- One round button toggles **night LCD mode** (amber/green backlit palette via CSS vars).

### Fixes
- Dark element chip contrast (illegible today).
- Focus rings + aria labels throughout.

## Out of scope (YAGNI)

Sound effects, localization, PWA/manifest, mobile-specific layout work beyond
existing responsiveness, changing any data or breeding logic.

## Verification

- `python3 _verify_logic.py` still passes (no data/logic change).
- `_fetch_icons.py` asserts 299/299 icon coverage against pals_1.0.json.
- Browser pass: grid, detail, all three breeding modes, night mode, keyboard nav,
  reduced-motion — screenshot review at desktop + narrow width.
