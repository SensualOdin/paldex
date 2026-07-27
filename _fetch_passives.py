#!/usr/bin/env python3
"""Build _passives.json: the full standard passive-skill table with numeric
effects, ranks and Pal Surgery costs.

Sources (both game-file extractions):
  - tylercamp/palcalc db.json (pinned commit): English names, rank,
    surgery cost, human description, IsStandardPassiveSkill filter.
  - CreativeTechGuy/PalworldDBIndex DT_PassiveSkill_Main.json (1.0 dump):
    exact EffectType/EffectValue/TargetType triples per passive.

Run: python3 _fetch_passives.py
"""
import json
import urllib.request

PALCALC_SHA = "b822c7fda4f019bd7c57f45437f14a74061a29bc"  # same pin as _fetch_icons.py
DB_URL = f"https://raw.githubusercontent.com/tylercamp/palcalc/{PALCALC_SHA}/PalCalc.Model/db.json"
RAW_URL = ("https://raw.githubusercontent.com/CreativeTechGuy/PalworldDBIndex/"
           "main/src/raw_data/Pal/Content/Pal/DataTable/PassiveSkill/DT_PassiveSkill_Main.json")
UA = {"User-Agent": "Mozilla/5.0 (personal Paldex build script)"}

# game effect-type suffix -> our element keys
EL_MAP = {"Fire": "fire", "Water": "water", "Aqua": "water", "Ice": "ice",
          "Electricity": "electric", "Thunder": "electric", "Leaf": "grass",
          "Dark": "dark", "Dragon": "dragon", "Earth": "ground", "Normal": "neutral"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main():
    db = fetch(DB_URL)
    raw = fetch(RAW_URL)[0]["Rows"]

    out = []
    for p in db["PassiveSkills"]:
        if not p.get("IsStandardPassiveSkill"):
            continue
        r = raw.get(p["InternalName"])
        if not r:
            print("no raw row:", p["InternalName"])
            continue
        effects = []
        for i in (1, 2, 3, 4):
            t = r[f"EffectType{i}"].split("::")[1]
            if t == "no":
                continue
            tgt = r[f"TargetType{i}"].split("::")[1]
            effects.append({"t": t, "v": r[f"EffectValue{i}"],
                            "who": "player" if "Trainer" in tgt else "pal"})
        out.append({
            "name": p["Name"],
            "iname": p["InternalName"],
            "rank": p["Rank"],
            "surg": p.get("SurgeryCost") or 0,          # 0 = not surgery-addable
            "nat": bool(r.get("AddPal")),               # in the natural lottery pool
            "desc": p.get("Description") or "",
            "fx": effects,
        })

    assert len(out) >= 110, len(out)
    # every damage-relevant field the app model reads must be present
    names = {p["name"] for p in out}
    for must in ("Legend", "Musclehead", "Ferocious", "Brave", "Demon God",
                 "Vanguard", "Lucky", "Serenity", "Flame Emperor"):
        assert must in names, must

    with open("_passives.json", "w", encoding="utf-8") as f:
        json.dump({"passives": out, "elmap": EL_MAP,
                   "source": "palcalc db.json (pinned) + DT_PassiveSkill_Main.json (1.0 dump)"},
                  f, separators=(",", ":"))
    surg = sum(1 for p in out if p["surg"])
    print(f"OK -> _passives.json: {len(out)} standard passives, {surg} surgery-addable")


if __name__ == "__main__":
    main()
