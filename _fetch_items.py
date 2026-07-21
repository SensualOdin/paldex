#!/usr/bin/env python3
"""Build _items.json: per-material info from paldb.cc item pages (1.0-current).

For every material in the app's item index (drop/ranch items from
_paldetails.json + partner skills) plus a curated list of core gatherables
(Wood, Stone, Paldium Fragment, ...), scrape the paldb item page for:
  - description, rarity, type, sell price
  - usedIn:      recipes that consume it  [{product, qty}]
  - craftedFrom: its own recipe           [{mat, qty}]
  - sources:     non-Pal obtain methods (treasure boxes, merchants,
                 fishing, salvage, ...) detected from page sections

Run: python3 _fetch_items.py
"""
import html as htmllib
import json
import re
import sys
import time
import urllib.parse
import urllib.request

PALDB_URL = "https://paldb.cc/en/{}"
UA = {"User-Agent": "Mozilla/5.0 (personal Paldex build script)"}

EXTRA_ITEMS = [
    "Wood", "Stone", "Paldium Fragment", "Pure Quartz", "Sulfur", "Cement",
    "Polymer", "Refined Ingot", "Pal Metal Ingot", "Cake", "Flour", "Wheat",
    "Charcoal", "Gunpowder", "Berry Seeds",
]
# composite phrases parsed out of partner-skill prose — no item page exists
SKIP = {"Assorted items", "various seeds", "Mushroom or Cavern Mushroom"}

SECTION_LABEL = {
    "Treasure Box": "🎁 treasure boxes & caches",
    "Merchant": "🛒 sold by merchants",
    "Black Marketeer": "🕶 black marketeer",
    "Fishing": "🎣 fishing",
    "Salvage": "🧲 salvage sites",
    "Eggs": "🥚 eggs",
    "Wandering Merchant": "🛒 wandering merchant",
    "Research": "🔬 lab research",
    "Farming": "🌾 farming",
    "Cooking": "🍳 cooking",
    "Logging Site": "🪓 logging site",
    "Stone Pit": "⛏️ stone pit",
    "Mining Site": "⛏️ mining site",
}
IGNORE_SECTIONS = {"Stats", "Others", "Dropped By", "Crafting Materials",
                   "Produced By", "Tribes", "Spawner"}

ANCHOR_QTY = re.compile(
    r'<a class="itemname"[^>]*>(?:<img[^>]*/?>)?\s*([^<]+?)\s*</a>\s*'
    r'<small class="itemQuantity">(\d+)</small>')


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def fetch_retry(url, attempts=4):
    for a in range(attempts):
        try:
            return fetch(url)
        except Exception:
            if a == attempts - 1:
                raise
            time.sleep(4 * (a + 1))


def sections(page):
    """Split page into {title: html_segment} using card-title h5 headers."""
    parts = re.split(r'<h5 class="card-title[^>]*>', page)
    out = {}
    for seg in parts[1:]:
        m = re.match(r"\s*(?:<span[^>]*>)?\s*([A-Za-z &]+?)\s*(?:</span>)?\s*(?::[^<]*)?</h5>(.*)",
                     seg, re.S)
        if m:
            out.setdefault(m.group(1).strip(), m.group(2))
    return out


def parse_recipes(seg, item_name):
    """Rows of the Crafting Materials table -> (usedIn, craftedFrom)."""
    used, crafted = [], None
    body = seg.split("<thead", 1)[-1]
    rows = re.split(r"<tr>", body)[1:]
    for row in rows:
        cells = re.split(r"<td>", row)
        if len(cells) < 3:
            continue
        mats = [(htmllib.unescape(n), int(q)) for n, q in ANCHOR_QTY.findall(cells[1])]
        prod = ANCHOR_QTY.findall(cells[2])
        if not prod:
            continue
        pname = htmllib.unescape(prod[0][0])
        if pname == item_name:
            if crafted is None and mats:
                crafted = [{"mat": n, "qty": q} for n, q in mats]
            continue
        qty = next((q for n, q in mats if n == item_name), None)
        if qty is not None and not any(u["product"] == pname for u in used):
            used.append({"product": pname, "qty": qty})
    return used, crafted


def parse_meta(page):
    t = re.sub(r"<script.*?</script>", "", page, flags=re.S)
    t = re.sub(r"<[^>]+>", "|", t)
    t = re.sub(r"[ \t\r\n]+", " ", t)
    meta = {}
    m = re.search(r"\|Rarity\| \|(\w+)\|", t)
    if m: meta["rarity"] = m.group(1)
    m = re.search(r"\|Type\|\s*\|+\s*([A-Za-z][A-Za-z ]*?)\s*\|", t)
    if m: meta["type"] = m.group(1).strip()
    m = re.search(r"Sell:\s*([\d,]+)", t)
    if m: meta["sell"] = int(m.group(1).replace(",", ""))
    # description: paldb puts the clean item text in og:description
    m = re.search(r'<meta property="og:description" content="([^"]*)"', page)
    if m:
        desc = htmllib.unescape(m.group(1)).replace("\n", " ").strip()
        if desc and "Database Wiki" not in desc:
            meta["desc"] = desc
    m = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    if m and "itemicon" in m.group(1).lower():
        meta["iconUrl"] = m.group(1)
    return meta


def scrape_one(n):
    slug = urllib.parse.quote(n.replace(" ", "_"))
    try:
        page = fetch_retry(PALDB_URL.format(slug), attempts=2)
    except Exception:
        # paldb drops apostrophes from some slugs (Elizabee's Staff)
        page = fetch_retry(PALDB_URL.format(
            urllib.parse.quote(n.replace("'", "").replace(" ", "_"))))
    secs = sections(page)
    entry = parse_meta(page)
    if "Crafting Materials" in secs:
        used, crafted = parse_recipes(secs["Crafting Materials"], n)
        if used: entry["usedIn"] = used
        if crafted: entry["craftedFrom"] = crafted
    if "Production" in secs:
        # the item's own recipe lives here, prefixed by its crafting station(s)
        head = re.split(r"<table|<thead", secs["Production"], 1)[0]
        st = re.sub(r"<[^>]+>", "|", head)
        stations = [s.strip() for s in st.split("|")
                    if re.fullmatch(r"[A-Za-z][A-Za-z' ]{2,30}", s.strip())]
        _, crafted = parse_recipes(secs["Production"], n)
        if crafted: entry["craftedFrom"] = crafted
        if stations: entry["station"] = stations[:3]
    src = [lbl for sec, lbl in SECTION_LABEL.items() if sec in secs]
    if src: entry["sources"] = src
    return entry, secs


def refs(entry):
    """Item names an entry links to (recipe products + ingredients)."""
    return {u["product"] for u in entry.get("usedIn", [])} | \
           {m["mat"] for m in entry.get("craftedFrom", [])}


def main():
    details = json.load(open("_paldetails.json", encoding="utf-8"))
    names = set(EXTRA_ITEMS)
    for e in details.values():
        for d in e.get("drops", []):
            names.add(d["item"])
    ps = json.load(open("_partner_skills_fill.json", encoding="utf-8"))
    rr = re.compile(r"sometimes\s+(?:drops|produces|lays(?:\s+an)?|digs\s+up|makes)\s+(.+?)\s+"
                    r"(?:from its back\s+)?when assigned to (?:a\s+)?Ranch", re.I)
    for e in ps.values():
        m = rr.search(e["desc"])
        if m:
            names.add({"Pal Fluids": "Aquatic Pal Fluids"}.get(m.group(1).strip(), m.group(1).strip()))
    names -= SKIP
    names = sorted(n for n in names if n and n[0].isupper())

    out, failed, unknown_secs = {}, [], set()
    for i, n in enumerate(names):
        try:
            entry, secs = scrape_one(n)
            unknown_secs |= set(secs) - set(SECTION_LABEL) - IGNORE_SECTIONS
            if entry:
                out[n] = entry
            else:
                failed.append(n)
        except Exception as e:
            print(f"  ERR {n}: {e}", file=sys.stderr)
            failed.append(n)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(names)}")
        time.sleep(1.2)

    # Closure pass: follow recipe references and pull in crafted MATERIALS
    # (Coralum Ingot, boards, cloth tiers, ...) so intermediates are
    # first-class items. Gear (weapons/armor/saddles) is left out to keep the
    # materials cloud focused — it still shows as end-of-chain recipe chips.
    seen_nonmat = set()
    for round_no in range(3):
        frontier = sorted({r for e in out.values() for r in refs(e)}
                          - set(out) - seen_nonmat - SKIP - set(failed))
        if not frontier:
            break
        print(f"closure round {round_no+1}: {len(frontier)} referenced items")
        for n in frontier:
            try:
                entry, secs = scrape_one(n)
                if entry.get("type") in ("Material", "Ingredient"):
                    out[n] = entry
                    unknown_secs |= set(secs) - set(SECTION_LABEL) - IGNORE_SECTIONS
                else:
                    seen_nonmat.add(n)
            except Exception as e:
                print(f"  ERR {n}: {e}", file=sys.stderr)
                seen_nonmat.add(n)
            time.sleep(1.2)
        print(f"  -> kept materials, total now {len(out)} (skipped gear: {len(seen_nonmat)})")

    # embed the inventory icons as data-URIs (offline app, like the Pal art)
    import base64
    for n, e in out.items():
        url = e.pop("iconUrl", None)
        if not url or e.get("icon"):
            continue
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            ext = "png" if url.endswith(".png") else "webp"
            e["icon"] = f"data:image/{ext};base64," + base64.b64encode(data).decode()
            time.sleep(0.4)
        except Exception as ex:
            print(f"  icon ERR {n}: {ex}", file=sys.stderr)

    json.dump(out, open("_items.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"OK: {len(out)} items -> _items.json")
    if failed:
        print("NO DATA:", failed)
    if unknown_secs:
        print("unmapped sections seen:", sorted(unknown_secs)[:20])


if __name__ == "__main__":
    main()
