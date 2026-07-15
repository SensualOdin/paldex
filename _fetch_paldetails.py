#!/usr/bin/env python3
"""Build _paldetails.json: per-Pal drops, movesets, lore, boss title, passives.

Sources:
  - paldb.cc per-Pal pages (1.0-current): "Possible Drops", "Active Skills",
    "Summary" (Paldeck lore), and the Tribes section's "Tribe Boss" title.
  - tylercamp/palcalc db.json (pinned commit, same verified upstream as the
    breeding data): guaranteed passive skills per Pal, resolved to English
    name + description via the PassiveSkills catalog.

Run: python3 _fetch_paldetails.py
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

PALDB_URL = "https://paldb.cc/en/{}"
PALCALC_SHA = "b822c7fda4f019bd7c57f45437f14a74061a29bc"
PALCALC_DB = f"https://raw.githubusercontent.com/tylercamp/palcalc/{PALCALC_SHA}/PalCalc.Model/db.json"
UA = {"User-Agent": "Mozilla/5.0 (personal Paldex build script)"}
ELEMENTS = {"Neutral", "Fire", "Water", "Grass", "Electric", "Ice", "Ground", "Dark", "Dragon"}
MARK = "\x1f"


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def strip(html):
    text = re.sub(r"<[^>]+>", MARK, html)
    return re.sub(r"[ \t\r\n]+", " ", text)


def parse_drops(html):
    m = re.search(r"Possible Drops(.{0,4000}?)(?:Tribes|Spawner|Active Skills)", strip(html), re.S)
    if not m:
        return []
    parts = [p.strip() for p in m.group(1).split(MARK) if p.strip()]
    drops, i = [], 0
    # stream: Item | Probability | <name> <qty> <prob%> ...
    while i < len(parts) - 2:
        name, qty, prob = parts[i], parts[i + 1], parts[i + 2]
        if re.fullmatch(r"\d+%", prob) and re.fullmatch(r"\d+(?:&ndash;|–|-)?\d*", qty.replace("–", "-")):
            drops.append({"item": name, "qty": qty.replace("&ndash;", "–"), "p": prob})
            i += 3
        else:
            i += 1
    return drops


def parse_skills(html):
    m = re.search(r'card-title[^>]*data-i18n="common_active_skill"[^>]*>Active Skills(.{0,30000}?)(?:card-title[^>]*>|$)', html, re.S)
    if not m:
        return []
    text = strip(m.group(1))
    skills = []
    # pattern: Lv. N | Name | ... Element ... : CT | Power: P
    for sm in re.finditer(r"Lv\.\s*(\d+)\s*" + MARK + r"([^" + MARK + r"]+)" + MARK + r"(.{0,240}?)Power:\s*" + MARK + r"(\d+)", text, re.S):
        lv, name, mid, power = int(sm.group(1)), sm.group(2).strip(), sm.group(3), int(sm.group(4))
        el = next((e for e in ELEMENTS if e in mid), None)
        ct = re.search(r":\s*" + MARK + r"(\d+)", mid)
        skills.append({"lv": lv, "name": name, "el": (el or "").lower(), "ct": int(ct.group(1)) if ct else None, "pow": power})
    return skills


def parse_lore(html):
    """Paldeck summary/flavor text."""
    m = re.search(r"card-title[^>]*>\s*Summary\s*</h5>\s*<div[^>]*>(.*?)</div>", html, re.S)
    if m:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    t = re.sub(r"<[^>]+>", MARK, html)
    t = re.sub(r"[ \t\r\n]+", " ", t)
    mm = re.search(r"Summary\s*(?:" + MARK + r"|\s)+([^" + MARK + r"]{40,600})", t)
    return mm.group(1).strip() if mm else None


def parse_boss_title(html, name):
    """Alpha 'Tribe Boss' title, e.g. 'Big Floof' for Lamball."""
    t = re.sub(r"<[^>]+>", MARK, html)
    t = re.sub(r"[ \t\r\n]+", " ", t)
    mm = re.search(r"([^" + MARK + r"]{3,60}?)\s+" + re.escape(name) + r"\s*(?:" + MARK + r"|\s)+Tribe Boss", t)
    if not mm:
        return None
    title = mm.group(1).strip()
    return title if 2 < len(title) < 50 and not title.lower().startswith("tribe") else None


def load_passives():
    """internalName-keyed guaranteed passives per display name, from palcalc."""
    db = json.loads(fetch(PALCALC_DB))
    cat = {}
    for sk in db["PassiveSkills"]:
        iid = sk.get("InternalName")
        if iid and sk.get("Name") and sk["Name"] not in ("en Text", "-"):
            cat[iid] = {"name": sk["Name"], "desc": (sk.get("Description") or "").strip()}
    out = {}
    for p in db["Pals"]:
        ids = p.get("GuaranteedPassivesInternalIds") or []
        resolved = [cat[i] for i in ids if i in cat]
        if resolved:
            out[p["Name"]] = resolved
    return out


def main():
    pals = json.load(open("pals_1.0.json"))
    names = sorted({p["name"] for p in pals})
    print("loading guaranteed passives from palcalc…")
    passives = load_passives()
    print(f"  {len(passives)} pals with guaranteed passives")
    out, failed = {}, []
    for i, n in enumerate(names, 1):
        slug = urllib.parse.quote(n.replace(" ", "_").replace("(", "").replace(")", ""))
        try:
            html = fetch(PALDB_URL.format(slug))
            d, s = parse_drops(html), parse_skills(html)
            entry = {"drops": d, "skills": s}
            lore = parse_lore(html)
            if lore:
                entry["lore"] = lore
            title = parse_boss_title(html, n)
            if title:
                entry["bossTitle"] = title
            if n in passives:
                entry["passives"] = passives[n]
            if d or s or lore:
                out[n] = entry
            else:
                failed.append(n)
        except Exception:
            failed.append(n)
        if i % 25 == 0:
            print(f"  {i}/{len(names)}")
        time.sleep(0.25)
    json.dump(out, open("_paldetails.json", "w"), ensure_ascii=False, separators=(",", ":"))
    lore_n = sum(1 for v in out.values() if v.get("lore"))
    title_n = sum(1 for v in out.values() if v.get("bossTitle"))
    print(f"OK: {len(out)}/{len(names)} pals -> _paldetails.json (lore {lore_n}, bossTitle {title_n})")
    if failed:
        print("NO DATA:", failed)
        if len(failed) > 15:
            sys.exit(1)


if __name__ == "__main__":
    main()
