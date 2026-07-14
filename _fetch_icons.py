#!/usr/bin/env python3
"""Fetch Pal + element icons from tylercamp/palcalc (pinned commit) and emit
_icons.json of base64 data-URIs, keyed by display name / element key.

Upstream names the PNGs by English display name (e.g. Lamball.png), not
internalName. The two Gumoss records share one icon. Same verified upstream
as the breeding/stats data (see VERIFICATION.md). Icons are Palworld game
assets (C) Pocketpair, redistributed via palcalc.
"""
import base64
import json
import sys
import urllib.parse
import urllib.request

PALCALC_SHA = "b822c7fda4f019bd7c57f45437f14a74061a29bc"  # palcalc main, 2026-07-14, data v26
RAW = f"https://raw.githubusercontent.com/tylercamp/palcalc/{PALCALC_SHA}/PalCalc.UI/Resources"

ELEMENT_FILES = {  # app element key -> upstream filename
    "neutral": "Normal.png", "fire": "Fire.png", "water": "Water.png",
    "grass": "Leaf.png", "electric": "Electricity.png", "ice": "Ice.png",
    "ground": "Earth.png", "dark": "Dark.png", "dragon": "Dragon.png",
}

NAME_OVERRIDES = {}  # display name -> upstream filename stem, if they ever diverge


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def to_uri(png_bytes):
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode()


def main():
    pals = json.load(open("pals_1.0.json"))
    names = sorted({p["name"] for p in pals})  # 298 unique (Gumoss x2 shares one icon)
    icons, missing = {}, []
    for i, n in enumerate(names, 1):
        stem = NAME_OVERRIDES.get(n, n)
        try:
            icons[n] = to_uri(fetch(f"{RAW}/Pals/{urllib.parse.quote(stem)}.png"))
        except Exception as e:  # noqa: BLE001 - report all failures at end
            missing.append((n, str(e)))
        if i % 25 == 0:
            print(f"  {i}/{len(names)}")
    elements = {k: to_uri(fetch(f"{RAW}/Elements/{f}")) for k, f in ELEMENT_FILES.items()}
    if missing:
        print("MISSING:", missing)
        sys.exit(1)
    assert len(icons) == len(names) == 298, (len(icons), len(names))
    assert len(elements) == 9
    with open("_icons.json", "w") as f:
        json.dump({"sha": PALCALC_SHA, "pals": icons, "elements": elements}, f)
    print(f"OK: {len(icons)} pal icons + {len(elements)} element icons -> _icons.json")


if __name__ == "__main__":
    main()
