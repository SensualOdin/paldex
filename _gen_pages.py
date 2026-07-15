#!/usr/bin/env python3
"""Generate per-Pal static SEO pages (pal/<slug>.html), sitemap.xml, vercel.json.

Each page is a real content page (stats, lore, work, partner skill, drops,
breeding links) with unique title/description, canonical URL, and a CTA into
the app at /#pal=<slug>. Pages interlink through breeding parents/children
and prev/next dex order so crawlers can walk the whole set.

Run after _merge_elements.py and _fetch_paldetails.py:
    python3 _gen_pages.py
"""
import html
import json
import os
import re
from datetime import date

SITE = "https://www.palydex.com"
EL_COLOR = {"neutral": "#B4AC9C", "fire": "#E8552B", "water": "#2FA9E0", "grass": "#57B947",
            "electric": "#F2C21B", "ice": "#79CEDC", "ground": "#C0883E", "dark": "#6A4C93",
            "dragon": "#7B5FD6"}
EL_TEXT = {"dark": "#fff", "dragon": "#fff"}
WORK_FULL = {"GenerateElectricity": "Electricity", "MedicineProduction": "Medicine"}

pals = json.load(open("pals_1.0.filled.json", encoding="utf-8"))
details = json.load(open("_paldetails.json", encoding="utf-8"))
brd = json.load(open("breeding_1.0.json", encoding="utf-8"))
icons = json.load(open("_icons.json", encoding="utf-8"))
spawns = json.load(open("_spawns.json", encoding="utf-8"))

by_idx = {p["internalIndex"]: p for p in pals}


def slug(p):
    s = re.sub(r"[^a-z0-9]+", "-", p["name"].lower()).strip("-")
    if p["isVariant"] and p["name"] == "Gumoss":
        s += "-special"
    return s


SLUG = {p["internalIndex"]: slug(p) for p in pals}

# breeding indexes
parent_of = {}
for child, prs in brd["combos"].items():
    for a, b in prs:
        parent_of.setdefault(a, set()).add(int(child))
        parent_of.setdefault(b, set()).add(int(child))

esc = html.escape

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.55 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
background:#2f342a;color:#1e231a}
.wrap{max-width:760px;margin:0 auto;padding:18px 14px 40px}
.device{background:linear-gradient(158deg,#e0362c,#a51e17);border-radius:18px;padding:14px;border:2px solid #6f120d}
.screen{background:#eef1e2;border-radius:12px;border:3px solid #2c3128;padding:18px}
.hd{display:flex;gap:14px;align-items:center;margin-bottom:6px}
.hd img{width:84px;height:84px;border-radius:22%;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.2)}
h1{font-size:26px;margin:0}
.sub{color:#5a5f4d;font-size:13px}.bt{color:#a05a00;font-style:italic;font-weight:700;font-size:13px}
.chips{margin:8px 0}.chip{display:inline-block;padding:3px 11px;border-radius:999px;font-size:12px;
font-weight:800;margin-right:5px;text-transform:capitalize}
.lore{border-left:4px solid #c77d00;background:#fff;border-radius:8px;padding:9px 12px;font-style:italic;
color:#5a5f4d;font-size:13.5px;margin:12px 0}
h2{font-size:15px;margin:18px 0 8px;color:#1f665d;text-transform:uppercase;letter-spacing:.6px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
td,th{padding:5px 9px;border:1px solid #cdd1b8;text-align:left;background:#fff}
th{background:#e3e7d2;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.cta{display:block;text-align:center;background:#2b8a7e;color:#fff;font-weight:800;text-decoration:none;
padding:13px;border-radius:12px;font-size:16px;margin:18px 0 6px}
.cta:hover{background:#1f665d}
a{color:#1f665d}.links a{display:inline-block;background:#fff;border:1.5px solid #cdd1b8;border-radius:999px;
padding:3px 11px;margin:3px 4px 3px 0;font-size:12.5px;text-decoration:none;font-weight:700}
.footer{color:#ffdad6;font-size:11px;text-align:center;margin-top:12px;line-height:1.7}
.footer a{color:#fff}
.pn{display:flex;justify-content:space-between;margin-top:14px;font-size:13px}
"""


def chip(el):
    return (f'<span class="chip" style="background:{EL_COLOR[el]};'
            f'color:{EL_TEXT.get(el, "#0b0d12")}">{el}</span>')


def page(p, prev_p, next_p):
    d = details.get(p["name"], {})
    s = SLUG[p["internalIndex"]]
    name = esc(p["name"])
    els = p.get("elements") or []
    lore = d.get("lore", "")
    desc = (lore[:150] + "…" if len(lore) > 150 else lore) if lore else ""
    desc = (f"{name} (#{p['dex']}) — {'/'.join(els)} Pal in Palworld 1.0. " + desc).strip()
    desc = esc(desc[:250])
    title = f"{name} — Palworld 1.0 Stats, Breeding & Habitat | Palydex"

    st = p["stats"]
    stats_rows = "".join(f"<tr><td>{k}</td><td><b>{v}</b></td></tr>" for k, v in [
        ("HP", st["hp"]), ("Attack", st["attack"]), ("Defense", st["defense"]),
        ("Run Speed", st["runSpeed"]), ("Ride Sprint", st["rideSprint"]),
        ("Transport", st["transport"]), ("Stamina", st["stamina"]),
        ("Breeding Power", p["breedingPower"]), ("Rarity", p["rarity"]),
        ("Price", p["price"])])
    work = ", ".join(f"{WORK_FULL.get(k, k)} Lv {v}" for k, v in (p.get("work") or {}).items() if v > 0) or "None"
    ps = p.get("partnerSkill") or {}
    passives = d.get("passives") or []
    drops = d.get("drops") or []
    skills = (d.get("skills") or [])[:8]

    pairs = brd["combos"].get(str(p["internalIndex"]), [])
    pair_links = "".join(
        f'<a href="/pal/{SLUG[a]}">{esc(by_idx[a]["name"])}</a> + '
        f'<a href="/pal/{SLUG[b]}">{esc(by_idx[b]["name"])}</a><br>'
        for a, b in pairs[:6])
    children = sorted(parent_of.get(p["internalIndex"], []))[:12]
    child_links = "".join(f'<a href="/pal/{SLUG[c]}">{esc(by_idx[c]["name"])}</a>' for c in children)
    habitat = p["internalName"] in spawns["pals"]

    boss = f'<div class="bt">&ldquo;{esc(d["bossTitle"])}&rdquo;</div>' if d.get("bossTitle") else ""
    lore_html = f'<div class="lore">{esc(lore)}</div>' if lore else ""
    pass_html = ("<h2>Guaranteed passives</h2>" + "".join(
        f"<p><b>{esc(x['name'])}</b> — {esc(x.get('desc', ''))}</p>" for x in passives)) if passives else ""
    drops_html = ("<h2>Possible drops</h2><table><tr><th>Item</th><th>Qty</th><th>Rate</th></tr>" + "".join(
        f"<tr><td>{esc(x['item'])}</td><td>{esc(x['qty'])}</td><td>{esc(x['p'])}</td></tr>"
        for x in drops) + "</table>") if drops else ""
    skills_html = ("<h2>Active skills</h2><table><tr><th>Lv</th><th>Skill</th><th>El.</th><th>Power</th><th>CT</th></tr>" +
                   "".join(f"<tr><td>{x['lv']}</td><td>{esc(x['name'])}</td><td>{x.get('el') or ''}</td>"
                           f"<td>{x.get('pow') or ''}</td><td>{x.get('ct') or ''}</td></tr>"
                           for x in skills) + "</table>") if skills else ""

    pn = '<div class="pn">'
    if prev_p:
        pn += f'<a href="/pal/{SLUG[prev_p["internalIndex"]]}">&larr; {esc(prev_p["name"])}</a>'
    else:
        pn += "<span></span>"
    if next_p:
        pn += f'<a href="/pal/{SLUG[next_p["internalIndex"]]}">{esc(next_p["name"])} &rarr;</a>'
    pn += "</div>"

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/pal/{s}">
<meta name="robots" content="index, follow">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Palydex">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/pal/{s}"><meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
</head><body><div class="wrap"><div class="device"><div class="screen">
<div class="hd"><img src="{icons['pals'].get(p['name'], '')}" alt="{name} icon">
<div><h1>{name}</h1><div class="sub">Paldeck #{p['dex']} · Palworld 1.0{' · self-only' if p['selfOnly'] else ''}{' · nocturnal' if p['nocturnal'] else ''}</div>{boss}</div></div>
<div class="chips">{''.join(chip(e) for e in els)}</div>
{lore_html}
<a class="cta" href="/#pal={s}">Open {name} in the Palydex app &rarr;</a>
<div class="sub" style="text-align:center">breeding calculator &middot; habitat heat map &middot; tier lists &middot; works offline</div>
<h2>Stats (1.0, game-file data)</h2><table>{stats_rows}</table>
<h2>Work suitability</h2><p>{esc(work)}</p>
{'<h2>Partner skill</h2><p><b>' + esc(ps.get('name', '')) + '</b> — ' + esc(ps.get('desc', '')) + '</p>' if ps else ''}
{pass_html}
{skills_html}
{drops_html}
<h2>Breeding</h2>
<p>{name} is produced by <b>{len(pairs):,}</b> parent pair{'s' if len(pairs) != 1 else ''}{' (self-only: breed two ' + name + ')' if p['selfOnly'] else ''}. Sample pairs:</p>
<p class="links">{pair_links or '—'}</p>
{'<p>Breeds into:</p><p class="links">' + child_links + '</p>' if child_links else ''}
{'<p><b>Habitat:</b> wild spawn heat map (day/night) available in the app.</p>' if habitat else '<p><b>Habitat:</b> no wild spawns — obtain via breeding, dungeons, raids, or the World Tree.</p>'}
{pn}
</div>
<div class="footer">Data: tylercamp/palcalc (game-file extracted, v26) &middot; paldb.cc &middot; palworld.wiki.gg &middot; Palworld &copy; Pocketpair<br>
<a href="/">Palydex home</a> &middot; free &middot; no ads &middot; works offline</div>
</div></div></body></html>"""


def main():
    os.makedirs("pal", exist_ok=True)
    ordered = sorted(pals, key=lambda p: (p["dex"], p["internalIndex"]))
    n = 0
    for i, p in enumerate(ordered):
        prev_p = ordered[i - 1] if i > 0 else None
        next_p = ordered[i + 1] if i < len(ordered) - 1 else None
        with open(f"pal/{SLUG[p['internalIndex']]}.html", "w", encoding="utf-8") as f:
            f.write(page(p, prev_p, next_p))
        n += 1
    assert n == len(pals) == len(set(SLUG.values())), (n, len(set(SLUG.values())))

    today = date.today().isoformat()
    urls = [f"  <url><loc>{SITE}/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>"]
    urls += [f"  <url><loc>{SITE}/pal/{SLUG[p['internalIndex']]}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>"
             for p in ordered]
    with open("sitemap.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(urls) + "\n</urlset>\n")

    if not os.path.exists("vercel.json"):
        json.dump({"cleanUrls": True, "trailingSlash": False}, open("vercel.json", "w"), indent=2)
    print(f"OK: {n} pal pages, sitemap.xml ({len(urls)} URLs), vercel.json")


if __name__ == "__main__":
    main()
