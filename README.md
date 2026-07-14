# Palworld 1.0 Paldex &amp; Breeding Calculator

A single, self-contained `index.html` — a Paldex browser plus a breeding calculator for **Palworld 1.0** (build `1.100.427`, released July 10 2026). No server, no build step, no telemetry: everything runs client-side against data embedded inline in the file. Double-click to open, or serve the folder with any static server.

## Features

**Paldex browser**
- Grid of all 299 Pal records (287 headline Paldeck + variant/collab forms), with element chips, work-suitability icons, breeding power, and rarity.
- Instant client-side search by name.
- Filters: element (9), work suitability (12), base/variant, breedable-as-result, nocturnal.
- Sort by dex, name, breeding power, rarity, or any stat.
- Detail panel: full stat block, work levels, and cross-links — **Bred from** (every parent pair) and **Breeds into** (every child).

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
python _merge_elements.py   # pals_1.0.json + _elements_fill.json -> pals_1.0.filled.json
python _assemble.py          # pals_1.0.filled.json + breeding_1.0.json + _app_template.html -> index.html
python _verify_logic.py      # runs the spec §10 verification checklist
```

## Files

| File | Purpose |
|---|---|
| `index.html` | The self-contained app (data embedded inline). |
| `pals_1.0.json` | Original Paldex/stats data (299 records). |
| `pals_1.0.filled.json` | Same, with all 161 element gaps filled. |
| `breeding_1.0.json` | Authoritative breeding table (44,849 pairs). |
| `_elements_fill.json` | The 161 element values merged in. |
| `_app_template.html` | HTML/CSS/JS template (data injected at build). |
| `_assemble.py` | Injects the JSON datasets into the template. |
| `_merge_elements.py` | Merges + validates element data. |
| `_verify_logic.py` | Verification checklist. |
| `palworld-paldex-app-spec.md` | Original build spec: breeding rules, data schemas, pipeline. |

## Credits

Data: [tylercamp/palcalc](https://github.com/tylercamp/palcalc) (game-file extracted, v26) · elements from [paldb.cc](https://paldb.cc) · pre-1.0 element schema from [mlg404/palworld-paldex-api](https://github.com/mlg404/palworld-paldex-api). Palworld © Pocketpair.
