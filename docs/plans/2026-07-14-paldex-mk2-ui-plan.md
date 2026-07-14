# Paldex Mk-II UI Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the Paldex UI as "Mk-II": real embedded Pal icons everywhere, richer detail panel, proper breeding stage, functional device hardware (D-pad/LEDs/night mode), and a11y fixes — keeping the single-file offline promise.

**Architecture:** A new `_fetch_icons.py` build step downloads 299 Pal + 9 element PNGs from the pinned palcalc repo (same verified data source) and emits `_icons.json` of data-URIs. `_assemble.py` injects it into `_app_template.html` as a third data block. All UI work happens in `_app_template.html` (CSS + vanilla JS); `index.html` is always regenerated, never hand-edited.

**Tech Stack:** Python 3 stdlib (urllib, base64, json), vanilla HTML/CSS/JS. No new runtime dependencies.

**Design doc:** `docs/plans/2026-07-14-paldex-mk2-ui-design.md`

---

## Ground rules

- `index.html` is a build artifact: edit `_app_template.html`, then run `python3 _assemble.py`.
- After every template task: rebuild + reload `http://localhost:8742/index.html` + screenshot-verify.
- `python3 _verify_logic.py` must stay green (no data/logic changes in this project).
- Respect `prefers-reduced-motion` for every animation added.

---

### Task 1: `_fetch_icons.py` — icon pipeline

**Files:**
- Create: `_fetch_icons.py`
- Output (gitignored or committed — committed, it's source data): `_icons.json`

**Step 1: Pin the upstream commit**

Run: `curl -s https://api.github.com/repos/tylercamp/palcalc/commits/main | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])"`
Record the SHA into `PALCALC_SHA` constant.

**Step 2: Write `_fetch_icons.py`**

```python
#!/usr/bin/env python3
"""Fetch Pal + element icons from palcalc (pinned) and emit _icons.json of data-URIs."""
import base64, json, sys, urllib.request

PALCALC_SHA = "<SHA from step 1>"
RAW = f"https://raw.githubusercontent.com/tylercamp/palcalc/{PALCALC_SHA}/PalCalc.UI/Resources"
ELEMENT_FILES = {  # app element key -> upstream filename
    "neutral": "Normal.png", "fire": "Fire.png", "water": "Water.png",
    "grass": "Leaf.png", "electric": "Electricity.png", "ice": "Ice.png",
    "ground": "Earth.png", "dark": "Dark.png", "dragon": "Dragon.png",
}

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def to_uri(png_bytes):
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode()

def main():
    pals = json.load(open("pals_1.0.json"))
    names = sorted({p["internalName"] for p in pals})
    icons, missing = {}, []
    for i, n in enumerate(names, 1):
        try:
            icons[n] = to_uri(fetch(f"{RAW}/Pals/{n}.png"))
        except Exception as e:
            missing.append((n, str(e)))
        if i % 25 == 0:
            print(f"  {i}/{len(names)}")
    elements = {k: to_uri(fetch(f"{RAW}/Elements/{f}")) for k, f in ELEMENT_FILES.items()}
    if missing:
        print("MISSING:", missing); sys.exit(1)
    assert len(icons) == len(names) == 299, (len(icons), len(names))
    assert len(elements) == 9
    json.dump({"sha": PALCALC_SHA, "pals": icons, "elements": elements},
              open("_icons.json", "w"))
    print(f"OK: {len(icons)} pal icons + {len(elements)} element icons -> _icons.json")

if __name__ == "__main__":
    main()
```

**Step 3: Run and verify**

Run: `python3 _fetch_icons.py`
Expected: `OK: 299 pal icons + 9 element icons -> _icons.json`; file ~5.8MB.

Failure mode: if any InternalName has no matching PNG (e.g. filename mismatch), the
script exits 1 listing them — resolve by checking the repo tree for the actual
filename and adding a `NAME_OVERRIDES = {}` map.

---

### Task 2: `_assemble.py` injects icons

**Files:**
- Modify: `_assemble.py`
- Modify: `_app_template.html` (add `/*__ICONS__*/` placeholder next to existing data placeholders)

**Step 1:** Read current `_assemble.py`; it injects pals + breeding JSON into template placeholders. Add a third injection: `_icons.json` → `const ICONS = {...};` at placeholder `/*__ICONS__*/`.

**Step 2:** In `_app_template.html`, next to the existing data `<script>` block, add:

```js
const ICONS = /*__ICONS__*/{pals:{},elements:{}};
```

(Fallback empty object keeps the template itself openable for development.)

**Step 3: Rebuild and verify**

Run: `python3 _assemble.py && python3 - <<'EOF'
import re
html = open('index.html').read()
assert 'data:image/png;base64,' in html
print('icons embedded, index.html', len(html)//1024, 'KB')
EOF`
Expected: `icons embedded, index.html ~6xxx KB`

---

### Task 3: Icon helpers + grid cards use real art

**Files:**
- Modify: `_app_template.html`

**Steps:**
1. JS helper: `const palIcon = p => (ICONS.pals[p.internalName]) || null;` and render `<img class="pal-ico" src="..." alt="">` inside the existing capsule circle; keep the two-letter fallback when icon missing.
2. Element chips (cards, filters, detail) get `<img class="el-ico">` from `ICONS.elements[el]`.
3. Card restyle: element-tinted ring on capsule + top-edge gradient using `--el-*` var of first element; rarity badge tiers (CSS classes `.r-blue` 5–7, `.r-purple` 8–9, `.r-gold` 10+); nocturnal moon glyph top-right.
4. A11y: cards become `role="button" tabindex="0"` with keydown Enter/Space → select; `:focus-visible` ring.
5. Animations: `.card { transition: transform .15s, box-shadow .15s }` hover lift; staggered entry via `animation-delay: calc(var(--i) * 12ms)` capped at 40 items; wrap all in `@media (prefers-reduced-motion: no-preference)`.

**Verify:** rebuild, reload, screenshot: real art in every card, tinted rings, rarity tiers visible on a gold-tier Pal (e.g. Jetragon breedingPower 20 rarity 10+), tab-focus ring visible, Enter opens detail.

---

### Task 4: Detail panel upgrade

**Files:**
- Modify: `_app_template.html`

**Steps:**
1. Hero header: large icon (96px) on element-tinted banner gradient; name, dex, tags as today.
2. Stat bars: for each of the 7 stats, `width = stat / DEX_MAX[stat] * 100%`, animated from 0 on open (CSS transition); numeric value kept.
   Compute `DEX_MAX` once in JS from the pals array.
3. Work suitability: rows with element-style chip + 1–5 filled pips (`●●●○○`).
4. Breeding-power gauge: horizontal track 20→3100, marker at pal's value, caption "lower = rarer".
5. Bred-from / breeds-into lists: each entry gets a 28px icon chip.

**Verify:** rebuild, reload; select Lamball and Jetragon; screenshot both; bars/gauge/pips render, icons in cross-links.

---

### Task 5: Breeding tab stage

**Files:**
- Modify: `_app_template.html`

**Steps:**
1. Parent pickers: dropdown result rows get 28px icons (keep existing search logic).
2. Forward result: ceremony layout `[Parent A card] × [Parent B card] → [egg glyph] → [Child card]` with big icons; keep special-combo / gender-locked badges.
3. Reverse: each parent-pair row gets both icons + child context; clickable pivot preserved.
4. Chain: steps rendered as icon → icon → icon with arrows and pair labels.
5. Empty state: egg SVG motif + current hint text.

**Verify:** rebuild, reload; Forward: Katress × Wixen (gender-locked badge), a special combo (e.g. Relaxaurus + Sparkit = Relaxaurus Lux), a formula pair; Reverse for Anubis; Chain Lamball→Anubis. Screenshot each.

---

### Task 6: Functional device hardware

**Files:**
- Modify: `_app_template.html`

**Steps:**
1. D-pad: clicking arms moves grid selection (up/down/left/right by computed column count); ArrowKeys do the same when grid focused; Enter opens.
2. LEDs: `.blink` class (brief keyframe) on selection + tab switch.
3. Lens glint: slow CSS rotation of a highlight pseudo-element (reduced-motion aware).
4. Night LCD mode: bottom-right round button toggles `body.night`; override screen/panel/text CSS vars to backlit amber-green palette; persist in `localStorage('paldex-night')`.

**Verify:** rebuild, reload; arrows move selection; toggle night mode and screenshot; reload page — night persists.

---

### Task 7: A11y + contrast fixes

**Files:**
- Modify: `_app_template.html`

**Steps:**
1. Dark element chip: white text on `--el-dark` (and audit all 9 chips for ≥4.5:1).
2. Aria: `aria-label` on icon-only controls (D-pad, LEDs region `aria-hidden`, night toggle), `aria-pressed` on filter chips, `role="tablist"/"tab"` on Paldex/Breeding.
3. Focus-visible rings on every interactive element.

**Verify:** rebuild; keyboard-only walkthrough: tab through filters → grid → detail → breeding; night-mode contrast spot check.

---

### Task 8: Final QA + docs

**Files:**
- Modify: `README.md` (icons build step, new file table rows, credits line for icons)
- Modify: `.gitignore` only if needed

**Steps:**
1. `python3 _verify_logic.py` → all checks pass (unchanged data).
2. Full browser pass at 1280px and 800px width; screenshot suite: grid, detail, 3 breeding modes, night mode.
3. README: add `python3 _fetch_icons.py` to build steps; add `_fetch_icons.py` + `_icons.json` to file table; credits: "Pal & element icons © Pocketpair, via palcalc".
4. Present before/after screenshots to George.
