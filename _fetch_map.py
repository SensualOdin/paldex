#!/usr/bin/env python3
"""Build _map.json: interactive world-map data for the Map tab.

Sources (paldb.cc, 1.0-current — same family as our spawn/item data):
  - /js/map_data_en.js      main map (Palpagos Islands): ~13.8k markers,
                            80 region labels, marker-type icon set, world bounds
  - /js/treemap_data_en.js  The World Tree / Sunreach sky map: ~400 markers,
                            its own bounds + extra marker types
  - image/map8 + image/treemap8 tile pyramids: stitched at z2 (16x512px tiles)
    into one 2048px JPEG per map, embedded as data URIs

Also fits world->in-game map coordinates by trimmed least squares over
uniquely-named locations present both as markers (world pos) and region
labels (in-game pos).

Run: python3 _fetch_map.py
"""
import base64
import io
import json
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (personal Paldex build script)"}
MAIN_JS = "https://paldb.cc/js/map_data_en.js"
TREE_JS = "https://paldb.cc/js/treemap_data_en.js"
TILE = "https://cdn.paldb.cc/image/{d}/z{z}x{x}y{y}.webp"

# marker types that make sense to track as "collected" in the app
COLLECTIBLES = {"Lifmunk Effigy", "Cattiva Effigy", "Treasure", "Treasure Element",
                "Journals", "Fruit Tree", "Skill Fruits", "Note", "Relic"}


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", errors="ignore")


def parse_vars(js):
    decls = [(m.group(1), m.start()) for m in re.finditer(r"var (\w+) ?= ?", js)]
    out = {}
    for i, (n, p) in enumerate(decls):
        end = decls[i + 1][1] if i + 1 < len(decls) else len(js)
        blob = js[p:end]
        blob = blob[blob.index("=") + 1:].strip().rstrip(";").strip()
        try:
            out[n] = json.loads(blob)
        except Exception:
            pass
    return out


def fit_igc(fd, rd):
    """gameX = ax*worldY + bx ; gameY = ay*worldX + by (trimmed LSQ)."""
    names = {}
    for r in rd:
        names.setdefault(r["item"], []).append(r)
    pairs = [(x["pos"], names[x["item"]][0]["ipos"]) for x in fd
             if x.get("item") in names and len(names[x["item"]]) == 1
             and "pos" in x and "ipos" in names[x["item"]][0]]

    def lsq(ws, gs):
        n = len(ws); sw = sum(ws); sg = sum(gs)
        sww = sum(w * w for w in ws); swg = sum(w * g for w, g in zip(ws, gs))
        a = (n * swg - sw * sg) / (n * sww - sw * sw)
        return a, (sg - a * sw) / n

    for _ in range(3):  # trim worst half each round
        ax, bx = lsq([p[0]["Y"] for p in pairs], [p[1]["X"] for p in pairs])
        ay, by = lsq([p[0]["X"] for p in pairs], [p[1]["Y"] for p in pairs])
        pairs.sort(key=lambda p: abs(ax * p[0]["Y"] + bx - p[1]["X"]) +
                                 abs(ay * p[0]["X"] + by - p[1]["Y"]))
        if len(pairs) <= 8:
            break
        pairs = pairs[:max(8, len(pairs) // 2)]
    err = max(abs(ax * p[0]["Y"] + bx - p[1]["X"]) + abs(ay * p[0]["X"] + by - p[1]["Y"])
              for p in pairs)
    print(f"  igc fit: gameX={ax:.7f}*wY+{bx:.1f}  gameY={ay:.7f}*wX+{by:.1f}  (residual {err:.0f})")
    return {"ax": ax, "bx": bx, "ay": ay, "by": by}


def stitch(dirname):
    from PIL import Image
    BG = (12, 20, 32)  # matches the app's map backdrop for genuinely-empty tiles
    big = Image.new("RGB", (2048, 2048), BG)
    for x in range(4):
        for y in range(4):
            t = None
            for attempt in range(4):
                try:
                    raw = fetch(TILE.format(d=dirname, z=2, x=x, y=y), binary=True)
                    t = Image.open(io.BytesIO(raw))
                    break
                except Exception as e:
                    if "404" in str(e):
                        break          # tile genuinely absent (empty sky/ocean)
                    time.sleep(4 * (attempt + 1))
            if t is not None:
                tc = t.convert("RGBA").resize((512, 512))
                base = Image.new("RGBA", (512, 512), BG + (255,))
                base.alpha_composite(tc)
                big.paste(base.convert("RGB"), (x * 512, y * 512))
            time.sleep(0.6)
    buf = io.BytesIO()
    big.save(buf, "JPEG", quality=72, optimize=True)
    print(f"  {dirname}: stitched 2048px, {buf.tell() // 1024}KB")
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def slim(data, igc, tlist, tset):
    """markers -> [typeIdx, x, y, name-or-'', lv-or-0, collectibleId-or-0]"""
    inv_y = lambda gx: (gx - igc["bx"]) / igc["ax"]   # gameX -> worldY
    inv_x = lambda gy: (gy - igc["by"]) / igc["ay"]   # gameY -> worldX
    out, cid = [], 1
    rows = list(data.get("fixedDungeon", []))
    for e in data.get("extras", []):
        if "ipos" in e:
            e = dict(e, pos={"X": inv_x(e["ipos"]["Y"]), "Y": inv_y(e["ipos"]["X"])})
        rows.append(e)
    for e in data.get("extrasIngame", []):
        if "ipos" in e:
            e = dict(e, type="Base Spot",
                     pos={"X": inv_x(e["ipos"]["Y"]), "Y": inv_y(e["ipos"]["X"])},
                     item=e.get("comment") or "Community base spot")
        rows.append(e)
    for x in rows:
        t = x.get("type")
        if not t or "pos" not in x:
            continue
        if t not in tset:
            tset[t] = len(tlist)
            tlist.append(t)
        name = x.get("item", "")
        if name == t:
            name = ""
        lv = x.get("lv") or 0
        cc = 0
        if t in COLLECTIBLES:
            cc = cid; cid += 1
        out.append([tset[t], round(x["pos"]["X"]), round(x["pos"]["Y"]),
                    name, lv, cc])
    return out


def main():
    print("fetching marker data…")
    main_d = parse_vars(fetch(MAIN_JS))
    tree_d = parse_vars(fetch(TREE_JS))

    igc = fit_igc(main_d["fixedDungeon"], main_d["regionData"])

    tlist, tset = [], {}
    m_main = slim(main_d, igc, tlist, tset)
    m_tree = slim(tree_d, igc, tlist, tset)
    print(f"  markers: main {len(m_main)}, tree {len(m_tree)}, types {len(tlist)}")

    # type metadata: category + icon data-URI
    icons = {}
    for src in (main_d, tree_d):
        for t, v in src.get("iconLookup", {}).items():
            if t in icons or t not in tset:
                continue
            icons[t] = {"cat": v.get("category", "Other")}
            url = v.get("fixed_icon")
            if url:
                try:
                    data = fetch(url, binary=True)
                    ext = "png" if url.endswith(".png") else "webp"
                    icons[t]["icon"] = f"data:image/{ext};base64," + base64.b64encode(data).decode()
                    time.sleep(0.25)
                except Exception as e:
                    print(f"  icon ERR {t}: {e}", file=sys.stderr)
    for t in tlist:
        icons.setdefault(t, {"cat": "Other"})
    print(f"  type icons: {sum(1 for v in icons.values() if 'icon' in v)}/{len(tlist)}")

    regions = {}
    for key, src in (("main", main_d), ("tree", tree_d)):
        regions[key] = [{"n": r["item"], "gx": r["ipos"]["X"], "gy": r["ipos"]["Y"]}
                        for r in src.get("regionData", []) if "ipos" in r]

    b_main = main_d["config"]
    b_tree = tree_d["config"]
    bounds = lambda c: {"minX": c["landScapeRealPositionMin"]["X"],
                        "maxX": c["landScapeRealPositionMax"]["X"],
                        "minY": c["landScapeRealPositionMin"]["Y"],
                        "maxY": c["landScapeRealPositionMax"]["Y"]}

    print("stitching map tiles…")
    img_main = stitch("map8")
    img_tree = stitch("treemap8")

    out = {"igc": igc, "tlist": tlist, "types": icons,
           "maps": {"main": {"img": img_main, "bounds": bounds(b_main),
                             "label": "Palpagos Islands"},
                    "tree": {"img": img_tree, "bounds": bounds(b_tree),
                             "label": "The World Tree"}},
           "markers": {"main": m_main, "tree": m_tree},
           "regions": regions,
           "source": "paldb.cc map data (game DataTables), fetched " + time.strftime("%Y-%m-%d")}
    with open("_map.json", "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
    import os
    print(f"OK -> _map.json ({os.path.getsize('_map.json') // 1024}KB)")


if __name__ == "__main__":
    main()
