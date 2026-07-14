# Palworld 1.0 Paldex + Breeding Calculator — Build Spec

**Target:** a single, self-contained `.html` file you host locally (no server, no build step).
**Two features:** (1) a Paldex browser with full info on every Pal, (2) a breeding calculator (forward / reverse / chain).
**Game version this spec targets:** Palworld **1.0**, build `1.100.427`, released **July 10, 2026**.
**Ships with this spec:** `pals_1.0.json` (display + stats + breeding power) and `breeding_1.0.json` (authoritative parent↔child table). Both are ready to embed.

---

## 1. Game state you must build against (1.0)

Palworld left Early Access on **July 10, 2026**. The update is large enough that the roster and every breeding recipe changed, so **do not reuse any pre-1.0 data or spreadsheet.** The relevant facts:

- **Roster:** Pocketpair/press cite **287 Pals** (72 new). Datamined datasets enumerate **~299 records** because they count elemental/regional variant forms and the Terraria collab Pals as separate entries. Build the app off the dataset count (299) — the "287" is just the headline Paldeck number.
- **Level cap:** raised 65 → 80.
- **New regions:** Sunreach (floating sky islands) and the World Tree (endgame). New resources: Soralite, Paloxite, Radiant Gems.
- **Two new mechanics that touch breeding:**
  - **Mutation** — a small chance a bred egg comes out "mutated" with boosted stats/IVs and a unique passive. **It does not change which species hatches**, so it does not affect the calculator's species prediction (treat it as an optional probability note).
  - **Awakening** — *not breeding.* Uses Radiant Gems to strengthen a Pal you already own. No eggs, no combinations. **Out of scope** for the calculator; mention it in the Paldex if you want, but keep it separate.
- **Condensation** duplicate requirements were reduced (relevant only if you add a condensation tracker later).
- **Tower bosses now breed same-species-only:** Faleris, Shadowbeak, Grizzbolt, Orserk, Lyleen. They're in the "self-only" set below.
- **⚠️ "Genetic Recombination" is not a real system.** It appears only on content-farm/SEO pages, never in Pocketpair's patch notes. Any guide leaning on that term has invented data — ignore it.

---

## 2. Breeding rules (complete and precise)

In-game prerequisites (for the Paldex/help text, not the math): Breeding Farm unlocked at **Technology level 19**, one **male** + one **female** Pal in the pen, a **Cake** in the box, and an **Egg Incubator** to hatch.

### 2.1 The core algorithm

Every Pal has a hidden integer called **Breeding Power** (aka *Combi Rank* / *Breeding Score*). In the 1.0 dataset these range roughly **30 → 3100**; **lower = rarer/stronger**.

```
childTarget = floor( (BP_parentA + BP_parentB + 1) / 2 )
child       = the Pal in the GENERIC RESULT POOL whose Breeding Power is closest to childTarget
```

**Tie-break (this is where most third-party calculators are wrong):**
1. Closest Breeding Power wins.
2. If two Pals are exactly equidistant → the one with the **higher** Breeding Power wins.
3. If two share a Breeding Power → the **lower Paldex number** wins.

Consequences: a child's rarity always lands *between* its parents, and **you can never breed something rarer than your rarest parent** (special combos aside). "Two legendaries make a third, rarer legendary" is a myth.

### 2.2 The three rules that override / constrain the formula

Check in this order:

1. **Same species breeds true.** Anubis × Anubis = Anubis, always. (This is the standard way to reroll passives on a Pal you like.)
2. **Special combos override the formula.** ~136 fixed cross-species recipes always produce a specific child regardless of Breeding Power — almost all of them the elemental/regional **variant** forms (e.g. Mossanda + Grizzbolt → Mossanda Lux). Parent order and gender don't matter **except** the one case below.
3. **Formula** for everything else.

### 2.3 The generic result pool (critical, easy to get wrong)

The formula only ever picks from the **generic result pool**. Excluded from being a *formula result* (even though they can be *parents*, and have a Breeding Power):
- **All variant forms** (the "B" / elemental / regional entries). Obtainable only via their special combo or by pairing two of them.
- **Self-only Pals** (28 of them): legendaries (Jetragon, Frostallion, Necromus, Paladius, Blazamut, Blazamut Ryu…), the 1.0 tower bosses, several uniques (the Xeno line, Neptilius, Selyne, Bellanoir Libero, Mimog, etc.), and Terraria collab Pals (caught, not bred). These come only from same-species pairing (or a specific override).

**Do not hand-guess this pool.** While writing this spec I did, and got a real result wrong: I had **Mimog** in the pool, but it's self-only, so anything averaging near its Breeding Power (1740) was resolving to Mimog instead of the correct **Tarantriss** (1730). The shipped `pals_1.0.json` derives `selfOnly` directly from the datamined table, which is why it's trustworthy — see §5.

### 2.4 The one gender-locked recipe

Katress × Wixen is the only pairing where parent gender decides the child:
- **female Katress + male Wixen → Katress Ignis**
- **male Katress + female Wixen → Wixen Noct**

(In the dataset these use internal names: `CatMage`=Katress, `FoxMage`=Wixen, `CatMage_Fire`=Katress Ignis, `FoxMage_Dark`=Wixen Noct. They live in `breeding_1.0.json → genderLocked`, not in the main `combos` map.)

### 2.5 Passive inheritance (only if you build the "stack passives" feature)

Children can inherit passive skills from *both* parents probabilistically. This is independent of species selection. It only matters for a "shortest chain to stack 4 desired passives" feature; species prediction ignores it. Passive definitions are available but not required for the two core features.

---

## 3. Recommended architecture decision

**Use the lookup table (`breeding_1.0.json`) as the source of truth for species prediction — not a hand-rolled formula.**

Rationale, learned the hard way while building the data for this spec:
- The datamined table bakes in the exact pool membership, all ~136 special combos, the gender-locked case, and the boundary tie-breaks — all correctly.
- A re-implemented formula got ~94% of pairs right but broke on boundary cases (the Mimog/Tarantriss band) and required an 18-entry correction to the self-only list. Not worth the risk when the answer key is 434 KB.

So: **forward and reverse lookups are dictionary operations on the table.** Keep the §2.1 formula in the UI only as an *explainer* ("why this result: parents avg to ~X, closest breedable is Y") — it's great for teaching, bad as the engine.

For a true single file, **embed both JSONs** inline (they gzip to ~15 KB + ~131 KB; raw ~560 KB is fine for a local file). If you'd rather keep the HTML lean, `fetch('./breeding_1.0.json')` works when you open the folder over a local static server; note `fetch` of a sibling file fails under the `file://` protocol in some browsers, so embedding is the safer default for double-click-to-open.

---

## 4. Data files (shipped) — schemas

### 4.1 `pals_1.0.json` — one array, 299 records (Paldex + stats + breeding power)

```jsonc
{
  "dex": 143,               // Paldeck number (variants share a base number)
  "isVariant": false,       // elemental/regional variant form?
  "name": "Nyafia",
  "internalName": "BadCatgirl",
  "internalIndex": 1,       // UNIQUE 1..308 — the join key to breeding_1.0.json
  "breedingPower": 1250,    // Combi Rank; lower = rarer
  "elements": ["dark"],     // 0–2 of the 9 element names; [] if not yet filled (see §8 gap)
  "elementSource": "mlg404",// "mlg404" = base roster; "TODO" = needs supplement
  "rarity": 4,
  "size": "M",              // XS..XL
  "nocturnal": true,
  "partnerSkill": null,     // object or null
  "price": 2182,
  "wildLevel": [30, 60],    // [min, max]; may be [0,0] for non-wild
  "stats": { "hp":110,"attack":100,"defense":100,
             "runSpeed":600,"rideSprint":900,"transport":400,"stamina":100 },
  "work": { "Handiwork":4,"Gathering":4,"Lumbering":2,"Transporting":3 }, // only levels > 0
  "selfOnly": false         // true = never a formula result (legendary/tower-boss/unique/collab)
}
```

The 12 work-suitability keys: `Kindling, Watering, Planting, GenerateElectricity, Handiwork, Gathering, Lumbering, Mining, MedicineProduction, Cooling, Transporting, Farming`.

The 9 elements: `Neutral, Fire, Water, Grass, Electric, Ice, Ground, Dark, Dragon`.

### 4.2 `breeding_1.0.json` — the authoritative breeding table

```jsonc
{
  "version": "v26",
  "index": {                              // internalIndex -> minimal identity, to join with pals
    "1": { "dex":143, "name":"Nyafia", "variant":false },
    ...
  },
  "genderLocked": [                        // the 2 Katress/Wixen rows (see §2.4)
    { "p1":<idx>, "p1g":"FEMALE", "p2":<idx>, "p2g":"MALE", "child":<idx> },
    ...
  ],
  "combos": {                              // child internalIndex -> every parent pair that makes it
    "42": [ [1,17], [3,88], ... ],         // pairs are [parent1Index, parent2Index], sorted, gender-agnostic
    ...
  }
}
```

- **Reverse lookup** ("what makes X?") is just `combos[childIndex]`.
- **Forward lookup** ("what do A+B make?") = invert `combos` once at load into a `"a,b" -> child` map (code in §6).
- 299 children, **44,849** parent pairs total. Same-species pairs are present in the table. Gender-locked pairs are *only* in `genderLocked`, not in `combos`.

---

## 5. How the data was produced / how to refresh it after a patch

Both files are derived from **palcalc** (`tylercamp/palcalc`, `PalCalc.Model/db.json` + `breeding.json`, currently `v26`), which extracts directly from Palworld's game files via CUE4Parse — the most reliable public 1.0 source. `db.json` gave breeding power, stats, work suitability, rarity, partner skill, gender ratios; `breeding.json` gave the full parent→child table (from which `selfOnly` and the compact `combos` map were derived).

**When Pocketpair patches breeding again:** pull the updated palcalc `db.json` and `breeding.json` (or re-run `PalCalc.GenDB` against your game install), then re-run the compaction: keep the display fields from `db.json`, rebuild `combos` as `childIndex → [[p1,p2]…]` from the WILDCARD rows, keep non-WILDCARD rows as `genderLocked`, and set `selfOnly = (a Pal's only recipe is [self,self] or it has none)`. That's the whole pipeline.

**Element gap:** `db.json` does **not** carry element/type, so elements were merged from the pre-1.0 `mlg404/palworld-paldex-api` (`pals.json`). That covers the base roster but leaves **161 of 299** records (all 72 new 1.0 Pals + several variants) with `elements: []` / `elementSource:"TODO"`. Fill these from **paldb.cc** or the Palworld Fandom wiki (see §8).

---

## 6. Reference algorithms (drop-in JavaScript)

```js
// --- load & index -------------------------------------------------
const PALS = /* pals_1.0.json */;
const BRD  = /* breeding_1.0.json */;

const byIndex = new Map(PALS.map(p => [p.internalIndex, p]));

// forward map: "minIdx,maxIdx" -> child index
const FORWARD = new Map();
for (const [child, pairs] of Object.entries(BRD.combos))
  for (const [a, b] of pairs) {
    const k = a < b ? `${a},${b}` : `${b},${a}`;
    FORWARD.set(k, +child);
  }

// --- forward: two parents -> child --------------------------------
function breed(aIdx, bIdx, aGender, bGender) {
  // gender-locked special case first
  for (const g of BRD.genderLocked) {
    const match =
      (g.p1 === aIdx && g.p2 === bIdx && g.p1g === aGender && g.p2g === bGender) ||
      (g.p1 === bIdx && g.p2 === aIdx && g.p1g === bGender && g.p2g === aGender);
    if (match) return byIndex.get(g.child);
  }
  const k = aIdx < bIdx ? `${aIdx},${bIdx}` : `${bIdx},${aIdx}`;
  const child = FORWARD.get(k);
  return child != null ? byIndex.get(child) : null;
}

// --- reverse: target child -> every parent pair -------------------
function parentsOf(childIdx) {
  return (BRD.combos[childIdx] || []).map(([a, b]) => [byIndex.get(a), byIndex.get(b)]);
}

// --- formula (EXPLAINER ONLY — do not use as the engine) ----------
function formulaExplain(a, b) {
  const t = Math.floor((a.breedingPower + b.breedingPower + 1) / 2);
  return `parents average to combi rank ~${t}; closest breedable Pal wins (ties -> higher rank).`;
}

// --- chain finder: from owned Pals, shortest path to target -------
// BFS over reachable species. Each step breeds two currently-reachable Pals.
function shortestChain(ownedIdxs, targetIdx, maxDepth = 6) {
  const reachable = new Set(ownedIdxs);
  const from = new Map();                 // childIdx -> [pAIdx, pBIdx]
  if (reachable.has(targetIdx)) return []; // already have it
  for (let depth = 0; depth < maxDepth; depth++) {
    const current = [...reachable];
    let grew = false;
    for (let i = 0; i < current.length; i++)
      for (let j = i; j < current.length; j++) {
        const c = breed(current[i], current[j]); // gender-agnostic for pathing
        if (c && !reachable.has(c.internalIndex)) {
          reachable.add(c.internalIndex);
          from.set(c.internalIndex, [current[i], current[j]]);
          grew = true;
          if (c.internalIndex === targetIdx) {
            // reconstruct
            const steps = [];
            const walk = idx => {
              const pr = from.get(idx);
              if (!pr) return;
              walk(pr[0]); walk(pr[1]);
              steps.push([pr[0], pr[1], idx]);
            };
            walk(targetIdx);
            return steps.map(([a, b, c]) =>
              `${byIndex.get(a).name} + ${byIndex.get(b).name} = ${byIndex.get(c).name}`);
          }
        }
      }
    if (!grew) break;
  }
  return null; // unreachable within maxDepth
}
```

Notes: the BFS uses gender-agnostic `breed()`, which is correct for path *existence* (you can always obtain the needed gender). Only surface the gender requirement in the final displayed step for the Katress/Wixen case. Self-only targets will only be reachable if the owned set already contains that species (expected).

---

## 7. Feature spec

### 7.1 Paldex view
- **Grid** of all 299 Pals: sprite (or colored element chip if no sprite), dex #, name, element badge(s), small work-suitability icons.
- **Search** by name (instant, client-side).
- **Filters:** element (9), work suitability (12, with min level), rarity, size, nocturnal, "breedable as result" (`!selfOnly`), variant / base.
- **Sort:** dex, name, breeding power, rarity, any stat.
- **Detail panel** on select: full stat block (HP, Attack, Defense, run/ride/transport speeds, stamina), work suitabilities with levels, partner skill, rarity, size, nocturnal, wild-level range, price, breeding power, and two cross-links — **"Bred from"** (`parentsOf`) and **"Breeds into"** (scan `FORWARD` for pairs containing this Pal). Flag `selfOnly` Pals with a "same-species only" note.

### 7.2 Breeding calculator
- **Forward:** pick Parent A + Parent B → show the child card, its element/rarity, whether the result is a **special-combo override** (compare table result vs the §2.1 formula prediction; if they differ, badge it "special combo"), and the formula explainer line. Show the gender selector *only* when both parents are Katress/Wixen.
- **Reverse:** pick a target → list every parent pair from `parentsOf(target)`, each pair clickable to pivot (grandparent lookup).
- **Chain:** multi-select "Pals I own" + a target → `shortestChain` renders the step list. Expose `maxDepth` as an advanced control.
- **Optional advanced:** mutation-egg note (flat small chance of boosted stats + unique passive; species unchanged), and a passive-stacking planner (needs passive data — separate follow-on).

---

## 8. Sprites, element badges, and the known data gap

- **Element badges without images:** define the 9 elements as colored CSS chips so the app is fully functional with zero external images. Suggested tokens (adjust to taste):

| Element | Color | Element | Color |
|---|---|---|---|
| Neutral | `#B4AC9C` | Ice | `#79CEDC` |
| Fire | `#E8552B` | Ground | `#C0883E` |
| Water | `#2FA9E0` | Dark | `#6A4C93` |
| Grass | `#57B947` | Dragon | `#7B5FD6` |
| Electric | `#F2C21B` | | |

- **The gap to close:** 161 records have `elements: []`. Fill from **paldb.cc** (1.0-current, per-Pal pages) or the **Palworld Fandom wiki**. The 72 new 1.0 Pals are the priority. Match on `name`/`internalName`.
- **Sprites (optional):** base-roster menu icons resolve from the Fandom wiki (`static.wikia.nocookie.net/palworld/images/...`); 1.0 Pals' sprites live on paldb.cc. Or skip sprites entirely for v1 and rely on element chips + names — the app is complete without them.

---

## 9. Build & host

Single `index.html` with three `<script>` blocks: the two JSON datasets as `const PALS = […]` / `const BRD = {…}`, then your app logic (vanilla JS or a CDN React — your call; vanilla keeps it one file with no network deps). Double-click to open, or serve the folder with any static server for the cleanest experience. No backend, no API keys, no telemetry — everything runs client-side against the embedded data. For styling, a dark, search-first, card/bento layout fits this kind of reference tool well.

---

## 10. Verification checklist before you trust it end-to-end

- [ ] Confirm counts on load: 299 Pal records, 44,849 combo pairs, 2 gender-locked rows.
- [ ] `breed()` returns the same species for any same-species pair.
- [ ] Spot-check 3–4 known variant recipes (e.g. Mossanda + Grizzbolt → Mossanda Lux) resolve via the table, and are badged "special combo."
- [ ] Katress/Wixen gender selector flips between Katress Ignis and Wixen Noct correctly.
- [ ] A self-only target (e.g. Jetragon) only appears reachable in the chain finder if you already own one.
- [ ] Before any big cake investment, verify a couple of results in-game — datamined tables are reliable but 1.0 data is still fresh (revised ~July 13, 2026).
- [ ] Fill the 161 missing element badges (§8).
- [ ] Note: **Astralym** (World Tree boss) was reported unbreedable/uncatchable at launch — confirm its handling if it surfaces.

---

## 11. Sources
- Pocketpair Palworld 1.0 patch notes (via Game8, VGC, thepcenthusiast, minestrator, nexttier) — release date, roster, level cap, regions, Mutation/Awakening, tower-boss breeding change.
- Palworld Wiki breeding page + drawpie / gamesomg / xgamingserver breeding guides — formula, tie-break, pool exclusions, gender-locked case, "Genetic Recombination" debunk.
- **Data:** `tylercamp/palcalc` (`db.json` + `breeding.json`, v26, game-file extracted) — breeding power, stats, work, full breeding table. `mlg404/palworld-paldex-api` (pre-1.0) — element/type schema + base-roster elements. **paldb.cc** — recommended for filling 1.0 element/sprite gaps.
