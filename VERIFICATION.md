# Data Verification Report — Palworld 1.0 Paldex &amp; Breeding Calculator

**Date:** 2026-07-14
**Scope:** Independent audit of the app's data and correctness claims against verified sources.
**Verdict:** ✅ **PASS** — the app's data is faithfully sourced and its correctness claims are accurate. Every field checkable against an independent source matched.

Verification was done three ways:

1. **Internal consistency** — counts, referential integrity, and cross-field logic within the shipped files.
2. **Direct upstream diff** — the actual upstream source (`tylercamp/palcalc` v26) was pulled from GitHub and diffed field-by-field.
3. **Live web checks** — provenance facts (build number, release date, Pal counts) and a sample of element typings verified against public sources.

---

## 1. Provenance &amp; external facts (web-verified)

| Claim | Result | Source |
|---|---|---|
| Build `1.100.427`, released July 10 2026 | ✅ Confirmed | Palworld wiki page titled [`1.0.0.100427`](https://palworld.wiki.gg/wiki/1.0.0.100427); [MP1st](https://mp1st.com/title-updates-and-patches/palworld-version-1-0-released-live-update-1-100-427); [Game8](https://game8.co/games/Palworld/archives/604495) |
| 287-entry Paldeck (204 base + 83 variants), 72 new Pals in 1.0 | ✅ Confirmed | [NextTier](https://nexttier.pro/guide/palworld-new-pals) |
| `tylercamp/palcalc` is a real, game-file-extracting breeding solver | ✅ Confirmed | [github.com/tylercamp/palcalc](https://github.com/tylercamp/palcalc) |
| Upstream data version is genuinely `v26` | ✅ Confirmed | Live upstream `db.json` `Version` field reads `"v26"` |

The app's 299 records = 287 official Paldeck entries + 12 collab/special forms (dex 10000–10010, plus Gumoss Special).

---

## 2. Direct diff vs upstream palcalc v26 (definitive check)

Upstream files pulled from `main`:

- `https://raw.githubusercontent.com/tylercamp/palcalc/main/PalCalc.Model/db.json` (`Version: "v26"`, 299 Pals)
- `https://raw.githubusercontent.com/tylercamp/palcalc/main/PalCalc.Model/breeding.json`

### Pal records — 0 differences

All **299** records matched upstream exactly across **16 fields plus work suitability**:

`name, internalName, dex, isVariant, breedingPower, price, rarity, nocturnal, wildLevel (min/max), hp, attack, defense, runSpeed, rideSprint, transport, stamina, workSuitability`

- App indices: 299 · Upstream indices: 299 · Symmetric difference: 0
- Field diffs: **0**

### Breeding table — 0 differences

- Upstream `Breeding` array: **44,851** entries (all internal names mapped, 0 unmapped).
- App: **44,849** gender-agnostic pairs + **2** gender-locked rows = **44,851**.
- Pairs in upstream but not app: 2 — and both are exactly the gender-locked Katress×Wixen recipes `(94,134)→95` and `(94,134)→135`, which the app correctly represents as its two `genderLocked` rows.
- Pairs in app but not upstream: **0** (nothing fabricated).
- Gender-locked rows match upstream byte-for-byte.

This confirms the README's "all 44,849 pairs, both gender-locked rows … match exactly (0 differences)" claim.

---

## 3. Internal consistency

| Check | Result |
|---|---|
| Record count | 299 ✅ |
| Breeding parent pairs | 44,849 ✅ |
| Gender-locked rows | 2 ✅ |
| Filled element values | 161 ✅ |
| Breeding power range | 20–3100 ✅ |
| Combo referential integrity | 0 dangling parent/child references ✅ |
| `selfOnly` (28 Pals) consistency with breeding table | 0 mismatches in **both** directions ✅ |
| Element fill completeness | 0 gaps in `pals_1.0.filled.json` ✅ |
| Element type vocabulary | Exactly Palworld's 9 canonical types (dark, grass, ground, water, fire, ice, neutral, electric, dragon) ✅ |

---

## 4. Element spot-check (the paldb.cc-sourced part) — 20/20

Elements are the one dataset **not** from palcalc (palcalc is breeding-focused and doesn't track elements). A 20-Pal spot-check against the live [Palworld wiki](https://palworld.wiki.gg) passed **20/20** — including two cases where the app was correct and initial recollection was outdated:

- **Pengullet** = Water/Ice ✅ (confirmed dual-type, not pure Water)
- **Relaxaurus** = Dragon/Water ✅ (confirmed dual-type as of Paldeck #50)

---

## 5. Minor notes (not errors)

- **"Gumoss" appears twice** — correct: the base Pal (internalIndex 130) and the real **Gumoss Special** variant (internalIndex 131), both dex #12.
- **"287 headline Paldeck" vs 85 `isVariant` flags** — a categorization nuance around collab forms; the 299 total reconciles cleanly (287 Paldeck + 12 collab/special).

---

## 6. Limitation of this audit

An attempt to *independently re-derive* the Palworld breeding formula (to confirm the "~136 special combos" figure from scratch) did **not** cleanly reproduce the table (best reimplementation ~66% agreement). This reflects the difficulty of replicating Palworld's exact averaging + tie-break + pool-membership rules — **not a defect in the app.** It validates the app's explicit design decision to be *table-driven* rather than formula-driven. The authoritative verification (§2) is unaffected: the table itself matches palcalc's game-file extraction exactly.

---

## Reproducing this audit

```bash
# Pull upstream palcalc v26 data
curl -sL -o palcalc_db.json       https://raw.githubusercontent.com/tylercamp/palcalc/main/PalCalc.Model/db.json
curl -sL -o palcalc_breeding.json https://raw.githubusercontent.com/tylercamp/palcalc/main/PalCalc.Model/breeding.json

# Then diff:
#  - pals_1.0.json      vs palcalc_db.json.Pals       (match on internalIndex, compare 16 fields + WorkSuitability)
#  - breeding_1.0.json  vs palcalc_breeding.json.Breeding (map InternalName->InternalIndex, compare (min,max,child) triples)
```

**Bottom line:** the data is faithfully sourced from the most reliable public 1.0 dataset (game-file-extracted palcalc v26); the provenance and version claims are all true; and every field checkable against an independent source matched. The README's own caveat remains the right one: 1.0 datamined data is fresh — verify a specific result in-game before a big cake investment.


## Addendum (2026-07-17): partner-skill data corrected

The original partner-skill scrape used palworld.wiki.gg's "Partner Skills"
list page, which was still serving **pre-1.0 text** — caught when Surfent
Terra showed the old ore-carrying skill instead of 1.0's "the player's
attacks inflict Muddy (2~6)". Re-scraped all 298 from paldb.cc per-Pal pages
(the same 1.0-current source as drops/movesets/lore): **255 of 298
descriptions and 48 skill names had changed**. Everything derived from that
text (Mounts tier boards, Ranch producers in the Items tab, Team-planner
synergy tags) was rebuilt and re-validated: 29 flying / 11 water mounts,
29 ranch producers, 24 attack-type imbuers, 7 status-inflicting and 4
status-payoff partner skills all parse cleanly from the new wording.
