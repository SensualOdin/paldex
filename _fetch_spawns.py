#!/usr/bin/env python3
"""Build _spawns.json: per-Pal habitat heat-map data + embedded world map image.

Sources:
  - Spawn coordinates: the game's own DT_PaldexDistributionData table
    (1.0-current copy served by paldb.cc) — the data behind the in-game
    Paldex habitat display. Day + night location lists per species.
  - World map image: palworld.wiki.gg File:World_Map.webp, downscaled to
    1024px JPEG and embedded as a data URI.

Coordinates are normalized to map-image space using the landscape bounds
from paldb's map config, plus a small affine correction fit empirically by
maximizing points-on-land against the map's land mask (score 0.78 vs 0.17
random; water Pals legitimately spawn at sea). Points are quantized to a
96x96 grid; cells are deduplicated per Pal per time-of-day.

Run: python3 _fetch_spawns.py   (requires Pillow)
"""
import base64
import io
import json
import sys
import urllib.request

DIST_URL = "https://paldb.cc/DataTable/UI/DT_PaldexDistributionData.json"
MAP_URL = "https://palworld.wiki.gg/images/World_Map.webp"
UA = {"User-Agent": "Mozilla/5.0 (personal Paldex build script)"}

# Landscape world bounds (from paldb map config)
MINX, MAXX = -1099400, 349400
MINY, MAXY = -724400, 724400
RX, RY = MAXX - MINX, MAXY - MINY

# Empirical affine correction (land-mask fit, see module docstring)
SX, SY, OX, OY = 0.995, 0.96, 0.07, 0.03

GRID = 96


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def map_pos(p):
    """World coords -> normalized map-image (x right, y down), calibrated."""
    nx = (p["X"] - MINX) / RX   # world +X = map north
    ny = (p["Y"] - MINY) / RY   # world +Y = map east
    return (ny * SY + OY), ((1 - nx) * SX + OX)


def cells(points):
    out = set()
    for p in points:
        mx, my = map_pos(p)
        gx = min(GRID - 1, max(0, int(mx * GRID)))
        gy = min(GRID - 1, max(0, int(my * GRID)))
        out.add(gy * GRID + gx)
    return sorted(out)


def main():
    pals = json.load(open("pals_1.0.json"))
    print("fetching distribution data…")
    rows = json.loads(fetch(DIST_URL))[0]["Rows"]
    rows = {k.lower(): v for k, v in rows.items()}

    spawn_map, with_data = {}, 0
    for p in pals:
        r = rows.get(p["internalName"].lower())
        if not r:
            continue
        d = cells((r.get("dayTimeLocations") or {}).get("Locations") or [])
        n = cells((r.get("nightTimeLocations") or {}).get("Locations") or [])
        if d or n:
            spawn_map[p["internalName"]] = {"d": d, "n": n}
            with_data += 1

    print(f"pals with habitat data: {with_data}/{len(pals)}")
    assert with_data >= 250, "unexpectedly low habitat coverage"

    print("fetching world map…")
    from PIL import Image
    im = Image.open(io.BytesIO(fetch(MAP_URL)))
    im = im.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=72, optimize=True)
    map_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    print(f"map image: {len(buf.getvalue()) // 1024}KB")

    out = {"grid": GRID, "map": map_uri, "pals": spawn_map,
           "source": "DT_PaldexDistributionData via paldb.cc; map via palworld.wiki.gg"}
    with open("_spawns.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))
    import os
    print(f"OK -> _spawns.json ({os.path.getsize('_spawns.json') // 1024}KB)")


if __name__ == "__main__":
    main()
