# Palworld 1.0 Paldex &amp; Breeding Calculator

A single, self-contained `index.html` — a Paldex browser plus a breeding calculator for **Palworld 1.0** (build `1.100.427`, released July 10 2026). No server, no build step, no telemetry: everything runs client-side against data embedded inline in the file. Double-click to open, or serve the folder with any static server.

## Features

**Paldex browser**
- Grid of all 299 Pal records (287 headline Paldeck + variant/collab forms) with **real in-game Pal art** (embedded, offline), element-tinted cards, rarity tiers (blue/purple/gold), work-suitability icons, and breeding power.
- Instant client-side search by name; keyboard navigation (arrow keys or the on-device **D-pad**).
- Filters: element (9, with real element icons), work suitability (12), base/variant, breedable-as-result, nocturnal.
- Sort by dex, name, breeding power, rarity, any stat, or **any of the 12 work suitabilities** (Sort: Handiwork Lv …) with an **ascending/descending flip** — Pals without the job always sink to the end, and the sorted job is highlighted on each card.
- Detail panel: element-tinted hero, **partner skill** (name + effect, all 299), a **habitat heat map** (day/night toggle, rendered from the game's own spawn-distribution table — 259 Pals with wild habitats; the rest honestly say so), **animated stat bars** (normalized to the dex max), work-level pips, a breeding-power rarity gauge, and cross-links — **Bred from** (every parent pair) and **Breeds into** (every child), all with art. The panel is sticky — it follows as you scroll the grid.
- **Night LCD mode** (amber button, bottom-right): the screens switch to a backlit palette; persists across sessions. The blue button jumps to a random Pal.
- **Mobile friendly**: at phone widths the device compacts (full-width tabs, two-column grid) and the detail panel becomes a slide-up bottom sheet (tap the scrim, ×, or Esc to dismiss).
- **Caught & Favorites tracker**: ✓/★ toggles on every card and in the detail panel, persisted in localStorage, with a caught-progress pill in the header and Caught / Missing / Favorites filters.
- **Element matchups**: deals-2×/takes-2× chips on every Pal, plus an **interactive matchup wheel** under Tiers → Elements — the 9 element emblems in a circle with attacker→victim arrows; tap an element to isolate what it beats (solid) and what beats it (dashed). Text chart included as a fold-out.
- **Item lookup** (Items tab): pick any of ~190 materials — raw drops AND crafted intermediates (ingots, cloth tiers, cement, …) — to see **where to get it** — every Pal that drops it (quantity + drop chance), Ranch producers (29 Pals), and world sources (treasure caches, merchants, fishing, salvage, lab research) — plus **what it's used to craft** with per-recipe quantities and, for craftables, their own recipe **with the crafting station** (Coralum Ingot ← 2× Coralum Ore + 5× Coal at a Gigantic Furnace). Materials cross-link (Ore → Ingot → Refined Ingot…), and drop chips in the Pal detail panel link straight in.
- **Team synergy planner** (Team tab): build a party of 5 and the planner parses partner skills + guaranteed passives into effect tags (attack-type imbues, element damage boosts, team Attack buffs, resistances) and surfaces cross-Pal synergies — e.g. an imbuer that turns your attacks Ground paired with a Ground-damage booster — plus offensive type coverage, uncovered elements, and shared weaknesses. Persisted in localStorage.
- **Pal Compare**: ⚖ button opens A-vs-B — mirrored stat bars, work levels, partner skills, and what the pair breeds into.
- **Movesets & drops**: per-Pal active skills (level learned, element, power, cooldown) and possible drops with quantities/probabilities, from paldb.cc (1.0).
- **Lore & boss titles**: Paldeck flavor text and alpha titles ("Guardian of the Dark Sun") on every Pal, plus **guaranteed passives** (46 Pals) from the palcalc game-file data.
- **Mounts tier boards**: Flying / Ground / Water, detected from partner skills and ranked by Ride Sprint speed.
- **Per-Pal URLs**: `#pal=<slug>` deep links in the app, plus 299 static `/pal/<slug>` pages (real content + interlinks) for search engines.
- **Interactive world map** (Map tab): canvas pan/zoom over the game's own map tiles with **13,800+ markers** from the game's tables — fast travel, Alpha Pals (with level), dungeons, towers, effigies, eggs, chests, every ore/coal/quartz/sulfur/soralite node, fishing spots, merchants — across **two maps** (Palpagos Islands at 4096px + The World Tree). Markers cluster into category-colored count bubbles at low zoom, get pin badges + name labels up close, and popups show Alpha Pal mini-stats, the **nearest fast travel statue with distance/direction**, and a **shareable location link** (`#map=main/x/y`). Category filters with presets (Essentials / Farming run / Collector), marker search + coordinate jump ("337,360"), in-game coordinate readout, **unlimited free found-tracking** with per-type progress and hide-found, **custom pins with notes** (double-click), progress **export/import** (no account needed), up to **three color-coded Pal spawn layers** overlaid at once with a day/night toggle, plus **click any empty spot to see every Pal that spawns there** (day and night, straight from the game's distribution table), and popups that deep-link into the dex (Alpha Pals) and item pages (resource nodes). All offline, zero ads.

**Tier lists**
- **Combat** and **Base Work** boards curated from the most recent 1.0 community tier lists (NextTier Jul 17 2026, cross-checked vs PalMods, Game8, oslink, GameRant, mein-mmo, creator boards from DPJ, Moxsy, KhrazeGaming and The Pal Professor, plus palworld.gg's stat-formula ranking as an objective cross-check — sources linked in-app), with an **Early / Mid / End game-stage selector** so new players get day-one value. Every name is validated against the dex at build time.
- **Elements** (9 boards, ranked by base Attack), **Jobs** (12 boards, grouped by work level — 1.0 specialists reach Lv 8) and **Mounts** (Flying/Ground/Water by Ride Sprint) are computed from the embedded game data, so they're complete and objective. The game-stage selector works here too — it filters by in-game rarity (early ≤ 4, mid ≤ 7), so "best flying mount early game" honestly answers *Nitewing*.

**Breeding calculator**
- **Forward** — pick two parents → child, with a *special-combo* badge when the fixed recipe overrides the averaging formula, a *gender-locked* badge for Katress×Wixen, and a plain-language formula explainer.
- **Reverse** — pick a target → every parent pair that produces it, each clickable to pivot.
- **Chain** — just pick the Pal you want and its breeding **family tree** appears instantly: target on top, each bred Pal branching to its parents, bottoming out at Pals you can **catch in the wild** (🌿 leaves link to habitat maps), with step-order badges. If it also spawns wild, a banner links straight to its habitat. Advanced fold-out restricts the tree to Pals you own (✓ leaves) and sets max depth.

## Data &amp; correctness

Species prediction is **table-driven**, not a re-implemented formula. The breeding table is the source of truth because it bakes in the exact pool membership, ~136 special combos, the one gender-locked recipe, and the boundary tie-breaks.

- **`breeding_1.0.json`** — the authoritative parent↔child table: 299 children, **44,849** parent pairs, 2 gender-locked rows.
- **`pals_1.0.json`** — display + stats + breeding power (299 records). The originally-shipped file left 161 element fields empty.
- **`_elements_fill.json`** — the 161 element values added, sourced from [paldb.cc](https://paldb.cc).

Both `breeding_1.0.json` and the stats/breeding-power/self-only data derive from **[tylercamp/palcalc](https://github.com/tylercamp/palcalc)** `v26` (`db.json` + `breeding.json`), which extracts directly from Palworld's game files via CUE4Parse — the most reliable public 1.0 source.

### Verification

The shipped `breeding_1.0.json` was diffed byte-for-byte against upstream palcalc `v26`: **all 44,849 pairs, both gender-locked rows, and every `selfOnly`/`breedingPower`/stat field match exactly (0 differences).** Specific recipes, the self-only set (including the 1.0 tower-boss change), the formula, and the breeding-power range (20–3100, lower = rarer) were cross-checked against independent 1.0 sources (paldb.cc, drawpie). See `_verify_logic.py` for the §10 checklist.

> Datamined tables are reliable but 1.0 data is fresh — verify a couple of results in-game before any big cake investment.

## Rebuilding from source

```
python _fetch_partner_skills.py  # paldb.cc per-Pal pages (1.0-current) -> _partner_skills_fill.json
python _fetch_paldetails.py      # paldb.cc per-Pal pages: drops, movesets, lore, boss titles + palcalc passives -> _paldetails.json
python _fetch_items.py           # paldb.cc item pages: desc, sell, sources, used-in recipes -> _items.json
python _fetch_map.py             # paldb.cc map tables: 13.8k markers, 2 stitched maps, icons -> _map.json
python _gen_pages.py             # 299 static SEO pages (pal/<slug>.html) + sitemap.xml + vercel.json
python _merge_elements.py        # pals_1.0.json + element fill + partner skills -> pals_1.0.filled.json
python _fetch_icons.py           # downloads 298 Pal + 9 element icons from palcalc (pinned commit) -> _icons.json
python _fetch_spawns.py          # game spawn-distribution table (via paldb.cc) + world map (wiki.gg) -> _spawns.json
python _assemble.py              # pals + breeding + icons + spawns + _app_template.html -> index.html (~6.5 MB)
python _verify_logic.py          # runs the spec §10 verification checklist
```

## Files

| File | Purpose |
|---|---|
| `index.html` | The self-contained app (data embedded inline). |
| `pals_1.0.json` | Original Paldex/stats data (299 records). |
| `pals_1.0.filled.json` | Same, with all 161 element gaps filled. |
| `breeding_1.0.json` | Authoritative breeding table (44,849 pairs). |
| `_elements_fill.json` | The 161 element values merged in. |
| `_fetch_partner_skills.py` | Scrapes 1.0 partner skills from paldb.cc per-Pal pages. |
| `_partner_skills_fill.json` | Partner skill name + effect for all 298 names (source tagged per entry). |
| `_fetch_icons.py` | Downloads Pal + element icons from palcalc (pinned commit) as data-URIs. |
| `_fetch_spawns.py` | Builds habitat heat-map data from the game's DT_PaldexDistributionData (via paldb.cc) + world map image (wiki.gg), land-mask calibrated. |
| `_tiers.json` | Curated 1.0 Combat + Base Work tiers with sources; names validated at build. |
| `_fetch_paldetails.py` | Scrapes per-Pal possible drops + active-skill learnsets from paldb.cc. |
| `_paldetails.json` | Drops (item/qty/probability) + movesets (level/element/power/CT) for all 298 names. |
| `_fetch_items.py` | Scrapes per-item pages from paldb.cc: description, sell price, world sources, recipes. |
| `_items.json` | ~190 materials (raw + crafted intermediates) with sources, recipes and crafting stations. |
| `_fetch_map.py` | Builds the interactive-map dataset: markers, regions, type icons, stitched map images, world→in-game coordinate fit. |
| `_map.json` | 13.8k+ markers across Palpagos + World Tree, with embedded map images and icons. |
| `_spawns.json` | 259 Pals × day/night spawn cells (96×96 grid) + embedded 1024px world map. |
| `_icons.json` | 298 Pal + 9 element icons, base64 data-URIs (embedded at build). |
| `_app_template.html` | HTML/CSS/JS template (data injected at build). |
| `_assemble.py` | Injects the JSON datasets into the template. |
| `_merge_elements.py` | Merges + validates element data. |
| `_verify_logic.py` | Verification checklist. |
| `palworld-paldex-app-spec.md` | Original build spec: breeding rules, data schemas, pipeline. |

## Credits

Data: [tylercamp/palcalc](https://github.com/tylercamp/palcalc) (game-file extracted, v26) · elements from [paldb.cc](https://paldb.cc) · partner skills from [paldb.cc](https://paldb.cc) per-Pal pages (1.0-current) · habitat data from the game's `DT_PaldexDistributionData` table (via [paldb.cc](https://paldb.cc)) with the world map from [palworld.wiki.gg](https://palworld.wiki.gg) · pre-1.0 element schema from [mlg404/palworld-paldex-api](https://github.com/mlg404/palworld-paldex-api). Pal &amp; element icons are Palworld game assets © Pocketpair, redistributed via palcalc, embedded for personal offline use. Palworld © Pocketpair.
