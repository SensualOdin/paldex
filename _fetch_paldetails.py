#!/usr/bin/env python3
"""Build _paldetails.json: per-Pal possible drops + active-skill learnsets.

Source: paldb.cc per-Pal pages (1.0-current, already credited in README).
Parsed sections: "Possible Drops" (item, quantity, probability) and
"Active Skills" (level learned, skill name, element, cooldown, power).

Run: python3 _fetch_paldetails.py
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

PALDB_URL = "https://paldb.cc/en/{}"
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


def main():
    pals = json.load(open("pals_1.0.json"))
    names = sorted({p["name"] for p in pals})
    out, failed = {}, []
    for i, n in enumerate(names, 1):
        slug = urllib.parse.quote(n.replace(" ", "_").replace("(", "").replace(")", ""))
        try:
            html = fetch(PALDB_URL.format(slug))
            d, s = parse_drops(html), parse_skills(html)
            if d or s:
                out[n] = {"drops": d, "skills": s}
            else:
                failed.append(n)
        except Exception:
            failed.append(n)
        if i % 25 == 0:
            print(f"  {i}/{len(names)}")
        time.sleep(0.25)
    json.dump(out, open("_paldetails.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"OK: {len(out)}/{len(names)} pals -> _paldetails.json")
    if failed:
        print("NO DATA:", failed)
        if len(failed) > 15:
            sys.exit(1)


if __name__ == "__main__":
    main()
