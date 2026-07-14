# Palworld 1.0 Paldex &amp; Breeding Calculator

A single, self-contained `index.html` — a Paldex browser plus a breeding calculator for **Palworld 1.0** (build `1.100.427`, released July 10 2026). No server, no build step, no telemetry: everything runs client-side against data embedded inline in the file. Double-click to open, or serve the folder with any static server.

## Features

**Paldex browser**
- Grid of all 299 Pal records (287 headline Paldeck + variant/collab forms) with **real in-game Pal art** (embedded, offline), element-tinted cards, rarity tiers (blue/purple/gold), work-suitability icons, and breeding power.
- Instant client-side search by name; keyboard navigation (arrow keys or the on-device **D-pad**).
- Filters: element (9, with real element icons), work suitability (12), base/variant, breedable-as-result, nocturnal.
- Sort by dex, name, breeding power, rarity, or any stat.
- Detail panel: element-tinted hero, **partner skill** (name + effect, all 299), a **habitat heat map** (day/night toggle, rendered from the game's own spawn-distribution table — 259 Pals with wild habitats; the rest honestly say so), **animated stat bars** (normalized to the dex max), work-level pips, a breeding-power rarity gauge, and cross-links — **Bred from** (every parent pair) and **Breeds into** (every child), all with art. The panel is sticky — it follows as you scroll the grid.
- **Night LCD mode** (amber button, bottom-right): the screens switch to a backlit palette; persists across sessions. The blue button jumps to a random Pal.

**Tier lists**
- **Combat** and **Base Work** boards curated from the most recent 1.0 community tier lists (NextTier Jul 14 2026, cross-checked vs PalMods and oslink; sources linked in-app). Every name is validated against the dex at build time.
- **Elements** (9 boards, ranked by base Attack) and **Jobs** (12 boards, grouped by work level — 1.0 specialists reach Lv 8) are computed from the embedded game data, so they're complete and objective.

**Breeding calculator**
- **Forward** — pick two parents → child, with a *special-combo* badge when the fixed recipe overrides the averaging formula, a *gender-locked* badge for Katress×Wixen, and a plain-language formula explainer.
- **Reverse** — pick a target → every parent pair that produces it, each clickable to pivot.
- **Chain** — pick Pals you own + a target → shortest breeding path (BFS).

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
python _fetch_partner_skills.py  # wiki.gg Partner Skills page + paldb.cc gap-fill -> _partner_skills_fill.json
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
| `_fetch_partner_skills.py` | Scrapes partner skills (palworld.wiki.gg + paldb.cc gap-fill). |
| `_partner_skills_fill.json` | Partner skill name + effect for all 298 names (source tagged per entry). |
| `_fetch_icons.py` | Downloads Pal + element icons from palcalc (pinned commit) as data-URIs. |
| `_fetch_spawns.py` | Builds habitat heat-map data from the game's DT_PaldexDistributionData (via paldb.cc) + world map image (wiki.gg), land-mask calibrated. |
| `_tiers.json` | Curated 1.0 Combat + Base Work tiers with sources; names validated at build. |
| `_spawns.json` | 259 Pals × day/night spawn cells (96×96 grid) + embedded 1024px world map. |
| `_icons.json` | 298 Pal + 9 element icons, base64 data-URIs (embedded at build). |
| `_app_template.html` | HTML/CSS/JS template (data injected at build). |
| `_assemble.py` | Injects the JSON datasets into the template. |
| `_merge_elements.py` | Merges + validates element data. |
| `_verify_logic.py` | Verification checklist. |
| `palworld-paldex-app-spec.md` | Original build spec: breeding rules, data schemas, pipeline. |

## Credits

Data: [tylercamp/palcalc](https://github.com/tylercamp/palcalc) (game-file extracted, v26) · elements from [paldb.cc](https://paldb.cc) · partner skills from [palworld.wiki.gg](https://palworld.wiki.gg/wiki/Partner_Skills) and [paldb.cc](https://paldb.cc) · habitat data from the game's `DT_PaldexDistributionData` table (via [paldb.cc](https://paldb.cc)) with the world map from [palworld.wiki.gg](https://palworld.wiki.gg) · pre-1.0 element schema from [mlg404/palworld-paldex-api](https://github.com/mlg404/palworld-paldex-api). Pal &amp; element icons are Palworld game assets © Pocketpair, redistributed via palcalc, embedded for personal offline use. Palworld © Pocketpair.
