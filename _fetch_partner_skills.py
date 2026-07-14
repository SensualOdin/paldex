#!/usr/bin/env python3
"""Build _partner_skills_fill.json: partner skill {name, desc} per Pal display name.

Sources (both already credited in README):
  1. palworld.wiki.gg "Partner Skills" page (raw wikitext) — bulk of entries.
  2. paldb.cc per-Pal pages — gap-fill for Pals the wiki page doesn't list yet.

Run: python3 _fetch_partner_skills.py
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

WIKI_URL = "https://palworld.wiki.gg/wiki/Partner_Skills?action=raw"
PALDB_URL = "https://paldb.cc/en/{}"
UA = {"User-Agent": "Mozilla/5.0 (personal Paldex build script)"}
MARK = "\x1f"  # tag-boundary marker after HTML stripping


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def clean_wiki(s):
    s = re.sub(r"\{\{[iI]\|([^}|]+)[^}]*\}\}", r"\1", s)       # {{i|Name}} -> Name
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", s)    # [[a|b]] -> b
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_wiki(raw):
    entries = {}
    for m in re.finditer(r"\{\|.*?\|\}", raw, re.S):
        rows = m.group(0).split("|-")
        for row in rows[1:]:
            cells = [c for c in re.split(r"\n\|", "\n" + row.strip())
                     if c.strip() and not c.strip().startswith("}")]
            if len(cells) < 5:
                continue
            skill, pals_cell, _num, typ, desc = cells[0], cells[1], cells[2], cells[3], cells[4]
            names = re.findall(r"\{\{[iI]\|([^}|]+)", pals_cell) or [clean_wiki(pals_cell)]
            for n in names:
                n = n.strip()
                if n:
                    entries[n] = {"name": clean_wiki(skill), "type": clean_wiki(typ),
                                  "desc": clean_wiki(desc), "source": "palworld.wiki.gg"}
    return entries


def parse_paldb(html):
    """Extract (skill name, description) from a paldb.cc pal page."""
    text = re.sub(r"<[^>]+>", MARK, html)
    text = re.sub(r"[ \t\r\n]+", " ", text)
    SEP = "(?:" + MARK + r"|\s)*"
    # Preferred: "Partner Skill  <name>  Lv.1  <desc...>  Technology"
    m = re.search("Partner Skill" + SEP + "([^" + MARK + "]{3,60}?)" + SEP + r"Lv\.1", text)
    if not m:
        # Fallback: "Partner Skill: <name>"
        m = re.search("Partner Skill" + SEP + ":" + SEP + "([^" + MARK + "]{3,60})", text)
    if not m:
        return None
    name = m.group(1).strip(" :|")
    if not name or name in ("Active Skills", "Passive Skills"):
        return None
    tail = text[m.end():m.end() + 1200]
    desc_parts = []
    for p in (s.strip() for s in tail.split(MARK)):
        if p in ("Technology", "Work Suitability", "Active Skills", "Passive Skills",
                 "Skill Fruit", "Food", "Stats"):
            break
        if not p or re.fullmatch(r"Lv\.\d", p):
            continue
        desc_parts.append(p)
        if sum(len(w) for w in desc_parts) > 380:
            break
    desc = re.sub(r"\s+", " ", " ".join(desc_parts)).strip()
    return {"name": name, "desc": desc, "source": "paldb.cc"}


def main():
    pals = json.load(open("pals_1.0.json"))
    app_names = sorted({p["name"] for p in pals})

    print("fetching wiki page…")
    entries = parse_wiki(fetch(WIKI_URL))
    # wiki placeholders ("(TBA)") count as missing -> gap-fill from paldb.cc
    entries = {n: e for n, e in entries.items() if "TBA" not in e["name"]}
    covered = [n for n in app_names if n in entries]
    missing = [n for n in app_names if n not in entries]
    print(f"wiki covered {len(covered)}/{len(app_names)}; gap-filling {len(missing)} from paldb.cc")

    failed = []
    for i, n in enumerate(missing, 1):
        slug = urllib.parse.quote(n.replace(" ", "_").replace("(", "").replace(")", ""))
        try:
            got = parse_paldb(fetch(PALDB_URL.format(slug)))
            if got and got["desc"]:
                entries[n] = got
            else:
                failed.append(n)
        except Exception:
            failed.append(n)
        if i % 10 == 0:
            print(f"  {i}/{len(missing)}")
        time.sleep(0.25)

    final_missing = [n for n in app_names if n not in entries]
    out = {n: entries[n] for n in app_names if n in entries}
    json.dump(out, open("_partner_skills_fill.json", "w"), ensure_ascii=False, indent=0)
    print(f"OK: {len(out)}/{len(app_names)} partner skills -> _partner_skills_fill.json")
    if final_missing:
        print("STILL MISSING:", final_missing)
        sys.exit(1)


if __name__ == "__main__":
    main()
