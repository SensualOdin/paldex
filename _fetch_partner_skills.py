#!/usr/bin/env python3
"""Build _partner_skills_fill.json: partner skill name + effect for all Pals.

Source: paldb.cc per-Pal pages (1.0-current) — the "Partner Skill" card
(anchored on data-i18n="common_coop_action"). paldb tracks the live game
build; the palworld.wiki.gg "Partner Skills" list page used by the first
version of this script was still serving pre-1.0 text for many Pals
(discovered via Surfent Terra: wiki said "decreases the weight of ores",
the 1.0 skill is "the player's attacks inflict Muddy (2~6)").

Run: python3 _fetch_partner_skills.py
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
MARK = "\x1f"


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


def parse_partner(html):
    """Extract (name, desc) from the Partner Skill card.

    The card is: <h5 ...><span data-i18n="common_coop_action">Partner Skill</span>: NAME</h5>
    followed by a d-flex row (skill icon + prose). The prose sits in the
    flex-grow-1 div and contains only inline elements (<br>, <a>, <span>), so
    capturing to the first </div> is safe; per-level tables come after it.
    """
    m = re.search(
        r'data-i18n="common_coop_action">Partner Skill</span>:\s*([^<]+)</h5>'
        r'.{0,800}?<div class="flex-grow-1">(.*?)</div>',
        html, re.S)
    if not m:
        return None, None
    name = m.group(1).strip()
    body = re.sub(r"<[^>]+>", MARK, m.group(2))
    body = re.sub(r"[ \t\r\n]+", " ", body)
    parts = [p.strip() for p in body.split(MARK) if p.strip()]
    desc = " ".join(parts)
    desc = re.sub(r"\s+([.,!?%)])", r"\1", desc)
    desc = re.sub(r"\(\s+", "(", desc)
    desc = re.sub(r"\s{2,}", " ", desc).strip()
    desc = re.sub(r"\s*Technology\s+\d+\s*$", "", desc)   # trailing unlock-cost metadata
    return htmllib.unescape(name), htmllib.unescape(desc) or None


def main():
    pals = json.load(open("pals_1.0.json", encoding="utf-8"))
    names = []
    for p in pals:
        if p["name"] not in names:
            names.append(p["name"])
    out, failed = {}, []
    for i, n in enumerate(names):
        slug = urllib.parse.quote(n.replace(" ", "_").replace("(", "").replace(")", ""))
        try:
            html = fetch_retry(PALDB_URL.format(slug))
            nm, desc = parse_partner(html)
            if nm and desc:
                out[n] = {"name": nm, "desc": desc, "source": "paldb.cc"}
            else:
                failed.append(n)
        except Exception as e:
            print(f"  ERR {n}: {e}", file=sys.stderr)
            failed.append(n)
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(names)}")
        time.sleep(1.2)

    # retry failures once more with extra backoff (paldb rate-limits bursts)
    for n in list(failed):
        time.sleep(5)
        try:
            slug = urllib.parse.quote(n.replace(" ", "_").replace("(", "").replace(")", ""))
            nm, desc = parse_partner(fetch_retry(PALDB_URL.format(slug)))
            if nm and desc:
                out[n] = {"name": nm, "desc": desc, "source": "paldb.cc"}
                failed.remove(n)
        except Exception:
            pass

    json.dump(out, open("_partner_skills_fill.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"OK: {len(out)}/{len(names)} partner skills -> _partner_skills_fill.json")
    if failed:
        print("NO DATA:", failed)


if __name__ == "__main__":
    main()
