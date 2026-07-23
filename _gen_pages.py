#!/usr/bin/env python3
"""Generate the static SEO layer: pal/<slug>.html, item/<slug>.html, landing
pages (breeding-calculator, tier-list, interactive-map), exported icon files,
sitemap.xml and vercel.json.

Every page is a real content page with unique title/description, canonical
URL, breadcrumb JSON-LD, per-page og:image and a CTA into the app (deep links:
/#pal=<slug>, /#item=<slug>, /#tab=<view>). Pages interlink — pal pages link
their drops to item pages, item pages link dropped-by Pals back — so crawlers
can walk the whole set.

Run after _merge_elements.py, _fetch_paldetails.py and _fetch_items.py:
    python3 _gen_pages.py
"""
import base64
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
itemdb = json.load(open("_items.json", encoding="utf-8"))
tiers = json.load(open("_tiers.json", encoding="utf-8"))
mapdata = json.load(open("_map.json", encoding="utf-8"))

by_idx = {p["internalIndex"]: p for p in pals}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def slug(p):
    s = slugify(p["name"])
    if p["isVariant"] and p["name"] == "Gumoss":
        s += "-special"
    return s


SLUG = {p["internalIndex"]: slug(p) for p in pals}
ISLUG = {n: slugify(n) for n in itemdb}
assert len(set(ISLUG.values())) == len(ISLUG)

# breeding indexes
parent_of = {}
for child, prs in brd["combos"].items():
    for a, b in prs:
        parent_of.setdefault(a, set()).add(int(child))
        parent_of.setdefault(b, set()).add(int(child))

# item indexes: dropped-by + ranch producers (mirrors the app's buildItemIndex)
RANCH_ALIAS = {"Pal Fluids": "Aquatic Pal Fluids"}
RANCH_RE = re.compile(r"sometimes\s+(?:drops|produces|lays(?:\s+an)?|digs\s+up|makes)\s+(.+?)\s+"
                      r"(?:from its back\s+)?when assigned to (?:a\s+)?Ranch", re.I)
dropped_by, ranch_by = {}, {}
_seen = set()
for p in pals:
    if p["name"] in _seen:
        continue
    _seen.add(p["name"])
    d = details.get(p["name"], {})
    for dr in d.get("drops") or []:
        dropped_by.setdefault(dr["item"], []).append((p, dr["qty"], dr["p"]))
    desc = (p.get("partnerSkill") or {}).get("desc") or ""
    if re.search(r"assigned to (a )?Ranch", desc, re.I):
        m = RANCH_RE.search(desc)
        item = m.group(1).strip() if m else ""
        item = RANCH_ALIAS.get(item, item)
        if item in itemdb:
            ranch_by.setdefault(item, []).append(p)

esc = html.escape


def de_emoji(s):
    return re.sub(r"[\U0001F000-\U0001FAFF☀-➿️‍]", "", s).strip()


def prob(x):
    m = re.search(r"[\d.]+", str(x))
    return float(m.group()) if m else 0.0


# ---- exported icon files (crawlable, cacheable; also per-page og:image) ----
def export_icon(data_uri, path):
    m = re.match(r"data:image/(\w+);base64,(.+)", data_uri)
    if not m:
        return None
    ext = {"jpeg": "jpg"}.get(m.group(1), m.group(1))
    full = f"{path}.{ext}"
    with open(full, "wb") as f:
        f.write(base64.b64decode(m.group(2)))
    return "/" + full


os.makedirs("icon/pal", exist_ok=True)
os.makedirs("icon/item", exist_ok=True)
PAL_ICON = {}
for p in pals:
    uri = icons["pals"].get(p["name"])
    if uri and p["internalIndex"] in SLUG:
        PAL_ICON[p["internalIndex"]] = export_icon(uri, f"icon/pal/{SLUG[p['internalIndex']]}")
ITEM_ICON = {}
for n, it in itemdb.items():
    if it.get("icon"):
        ITEM_ICON[n] = export_icon(it["icon"], f"icon/item/{ISLUG[n]}")

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
a{color:#1f665d}.links a,.links span{display:inline-block;background:#fff;border:1.5px solid #cdd1b8;border-radius:999px;
padding:3px 11px;margin:3px 4px 3px 0;font-size:12.5px;text-decoration:none;font-weight:700}
.links img{width:16px;height:16px;vertical-align:-3px;margin-right:3px}
td img{width:18px;height:18px;vertical-align:-4px;margin-right:4px}
.footer{color:#ffdad6;font-size:11px;text-align:center;margin-top:12px;line-height:1.7}
.footer a{color:#fff}
.pn{display:flex;justify-content:space-between;margin-top:14px;font-size:13px}
.crumbs{font-size:12px;color:#5a5f4d;margin-bottom:8px}.crumbs a{color:#1f665d}
"""


def chip(el):
    return (f'<span class="chip" style="background:{EL_COLOR[el]};'
            f'color:{EL_TEXT.get(el, "#0b0d12")}">{el}</span>')


def head(title, desc, path, og_image=None, extra_ld=None):
    """Shared <head>: canonical, OG, twitter, breadcrumb JSON-LD."""
    og = og_image or f"{SITE}/og-image.png"
    card = "summary" if og_image else "summary_large_image"
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Palydex", "item": SITE + "/"}]
    parts = [x for x in path.split("/") if x]
    for i, part in enumerate(parts):
        crumbs.append({"@type": "ListItem", "position": i + 2,
                       "name": part.replace("-", " ").title(),
                       "item": f"{SITE}/{'/'.join(parts[:i + 1])}"})
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs}]
    if extra_ld:
        ld.append(extra_ld)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
    return f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/{path}">
<meta name="robots" content="index, follow">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Palydex">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/{path}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="{card}">
{ld_html}
<style>{CSS}</style>"""


def shell(head_html, crumbs_html, body, foot_links=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head>{head_html}</head><body><div class="wrap"><div class="device"><div class="screen">
<div class="crumbs">{crumbs_html}</div>
{body}
</div>
<div class="footer">Data: tylercamp/palcalc (game-file extracted, v26) &middot; paldb.cc &middot; palworld.wiki.gg &middot; Palworld &copy; Pocketpair<br>
<a href="/">Palydex home</a> &middot; <a href="/breeding-calculator">breeding calculator</a> &middot; <a href="/tier-list">tier list</a> &middot; <a href="/interactive-map">interactive map</a>{foot_links} &middot; free &middot; no ads</div>
</div></div></body></html>"""


def item_link(name, qty=None, pre=False):
    label = (f"{qty}× {esc(name)}" if pre else esc(name) + (f" ×{qty}" if qty else ""))
    ic = ITEM_ICON.get(name)
    img = f'<img src="{ic}" alt="" loading="lazy">' if ic else ""
    if name in itemdb:
        return f'<a href="/item/{ISLUG[name]}">{img}{label}</a>'
    return f"<span>{img}{label}</span>"


# ============================== PAL PAGES ==============================
def pal_page(p, prev_p, next_p):
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
        f"<tr><td>{item_link(x['item'])}</td><td>{esc(x['qty'])}</td><td>{esc(x['p'])}</td></tr>"
        for x in drops) + "</table>") if drops else ""
    skills_html = ("<h2>Active skills</h2><table><tr><th>Lv</th><th>Skill</th><th>El.</th><th>Power</th><th>CT</th></tr>" +
                   "".join(f"<tr><td>{x['lv']}</td><td>{esc(x['name'])}</td><td>{x.get('el') or ''}</td>"
                           f"<td>{x.get('pow') or ''}</td><td>{x.get('ct') or ''}</td></tr>"
                           for x in skills) + "</table>") if skills else ""

    pn = '<div class="pn">'
    pn += (f'<a href="/pal/{SLUG[prev_p["internalIndex"]]}">&larr; {esc(prev_p["name"])}</a>'
           if prev_p else "<span></span>")
    if next_p:
        pn += f'<a href="/pal/{SLUG[next_p["internalIndex"]]}">{esc(next_p["name"])} &rarr;</a>'
    pn += "</div>"

    icon = PAL_ICON.get(p["internalIndex"]) or ""
    hd = head(title, desc, f"pal/{s}", og_image=(SITE + icon) if icon else None)
    body = f"""<div class="hd"><img src="{icon}" alt="{name}, a {'/'.join(els) or 'Palworld'} Pal" width="84" height="84">
<div><h1>{name}</h1><div class="sub">Paldeck #{p['dex']} · Palworld 1.0{' · self-only' if p['selfOnly'] else ''}{' · nocturnal' if p['nocturnal'] else ''}</div>{boss}</div></div>
<div class="chips">{''.join(chip(e) for e in els)}</div>
{lore_html}
<a class="cta" href="/#pal={s}">Open {name} in the Palydex app &rarr;</a>
<div class="sub" style="text-align:center">breeding family tree &middot; habitat heat map &middot; interactive world map &middot; tier lists &middot; works offline</div>
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
<p>See the full <a href="/breeding-calculator">breeding calculator</a> for every pair and an instant breeding family tree.</p>
{'<p><b>Habitat:</b> wild spawn heat map (day/night) available in the app — also on the <a href="/interactive-map">interactive map</a> as a spawn layer.</p>' if habitat else '<p><b>Habitat:</b> no wild spawns — obtain via breeding, dungeons, raids, or the World Tree.</p>'}
{pn}"""
    crumbs = f'<a href="/">Palydex</a> › <a href="/#tab=paldex">Paldex</a> › {name}'
    return shell(hd, crumbs, body)


# ============================== ITEM PAGES ==============================
def item_desc(n, it, drops, ranch):
    bits = []
    if it.get("craftedFrom"):
        mats = " + ".join(f"{m['qty']}× {m['mat']}" for m in it["craftedFrom"])
        st = f" at {it['station'][0]}" if it.get("station") else ""
        bits.append(f"crafted from {mats}{st}")
    if drops:
        best = drops[0][0]["name"]
        bits.append(f"dropped by {len(drops)} Pal{'s' if len(drops) != 1 else ''} (e.g. {best})")
    if ranch:
        bits.append(f"ranch-produced by {', '.join(p['name'] for p in ranch[:3])}")
    if it.get("usedIn"):
        bits.append(f"used in {len(it['usedIn'])} recipe{'s' if len(it['usedIn']) != 1 else ''}")
    how = "; ".join(bits) if bits else "a gatherable material"
    return esc(f"How to get {n} in Palworld 1.0: {how}. Full sources and every recipe on Palydex."[:250])


def item_page(n, prev_n, next_n):
    it = itemdb[n]
    s = ISLUG[n]
    name = esc(n)
    drops = sorted(dropped_by.get(n, []), key=lambda x: (-prob(x[2]), -prob(x[1])))
    ranch = ranch_by.get(n, [])
    title = f"{name} — How to Get & Uses in Palworld 1.0 | Palydex"
    desc = item_desc(n, it, drops, ranch)
    icon = ITEM_ICON.get(n) or ""

    meta = " · ".join(x for x in [it.get("type"), it.get("rarity"),
                                  f"sells for {it['sell']} gold" if it.get("sell") is not None else None] if x)
    pal_row = lambda p, qty, pr: (f'<tr><td><a href="/pal/{SLUG[p["internalIndex"]]}">{esc(p["name"])}</a></td>'
                                  f"<td>{esc(str(qty))}</td><td>{esc(str(pr))}</td></tr>")
    drops_html = ("<h2>Dropped by</h2><table><tr><th>Pal</th><th>Qty</th><th>Rate</th></tr>" +
                  "".join(pal_row(p, q, pr) for p, q, pr in drops) + "</table>") if drops else ""
    ranch_html = ("<h2>Ranch production</h2><p class=\"links\">" +
                  "".join(f'<a href="/pal/{SLUG[p["internalIndex"]]}">{esc(p["name"])}</a>' for p in ranch) +
                  f"</p><p class=\"sub\">Assign these Pals to a Ranch — their partner skill produces {name} automatically.</p>") if ranch else ""
    src_html = ("<h2>Also found via</h2><p class=\"links\">" +
                "".join(f"<span>{esc(de_emoji(x))}</span>" for x in it.get("sources") or []) + "</p>") if it.get("sources") else ""
    craft_html = ""
    if it.get("craftedFrom"):
        st = f" — at {esc(' / '.join(it['station']))}" if it.get("station") else ""
        craft_html = (f"<h2>Crafted from{st}</h2><p class=\"links\">" +
                      "".join(item_link(m["mat"], m["qty"], pre=True) for m in it["craftedFrom"]) + "</p>")
    used_html = ""
    if it.get("usedIn"):
        used_html = ("<h2>Used to craft (needs ×N of this)</h2><p class=\"links\">" +
                     "".join(item_link(u["product"], u["qty"]) for u in it["usedIn"]) + "</p>")

    pn = '<div class="pn">'
    pn += f'<a href="/item/{ISLUG[prev_n]}">&larr; {esc(prev_n)}</a>' if prev_n else "<span></span>"
    if next_n:
        pn += f'<a href="/item/{ISLUG[next_n]}">{esc(next_n)} &rarr;</a>'
    pn += "</div>"

    hd = head(title, desc, f"item/{s}", og_image=(SITE + icon) if icon else None)
    body = f"""<div class="hd"><img src="{icon}" alt="{name} item icon in Palworld" width="84" height="84">
<div><h1>{name}</h1><div class="sub">{esc(meta)} · Palworld 1.0</div></div></div>
{f'<div class="lore">{esc(de_emoji(it.get("desc") or ""))}</div>' if it.get("desc") else ''}
<a class="cta" href="/#item={s}">Open {name} in the Palydex item finder &rarr;</a>
<div class="sub" style="text-align:center">every drop source &middot; ranch producers &middot; full recipe tree &middot; works offline</div>
{drops_html}
{ranch_html}
{src_html}
{craft_html}
{used_html}
{pn}"""
    crumbs = f'<a href="/">Palydex</a> › <a href="/#tab=items">Items</a> › {name}'
    return shell(hd, crumbs, body)


# ============================== LANDING PAGES ==============================
def pal_chip_links(names):
    out = []
    name_to_idx = {}
    for p in pals:
        name_to_idx.setdefault(p["name"], p["internalIndex"])
    for n in names:
        i = name_to_idx.get(n)
        if i is not None:
            out.append(f'<a href="/pal/{SLUG[i]}">{esc(n)}</a>')
    return "".join(out)


def breeding_landing():
    n_pairs = sum(len(v) for v in brd["combos"].values())
    self_only = sum(1 for p in pals if p.get("selfOnly"))
    popular = ["Anubis", "Jetragon", "Frostallion", "Necromus", "Paladius", "Shadowbeak",
               "Faleris", "Grizzbolt", "Lyleen", "Orserk", "Bellanoir Libero", "Selyne"]
    title = "Palworld Breeding Calculator (1.0) — All 44,849 Pairs & Family Trees | Palydex"
    desc = esc(f"Free Palworld 1.0 breeding calculator: forward (parents → child), reverse (child → every pair) "
               f"and instant breeding family trees for all 299 Pals, from the game's own table — {n_pairs:,} verified pairs, "
               "every special combo and the gender-locked recipe. No ads, works offline.")
    hd = head(title, desc, "breeding-calculator")
    body = f"""<div class="hd"><img src="/icon-192.png" alt="Palydex" width="84" height="84">
<div><h1>Palworld Breeding Calculator (1.0)</h1><div class="sub">table-driven · {n_pairs:,} verified pairs · 299 children</div></div></div>
<a class="cta" href="/#tab=breeding">Open the breeding calculator &rarr;</a>
<div class="sub" style="text-align:center">forward &middot; reverse &middot; instant family trees &middot; works offline</div>
<h2>What it does</h2>
<p><b>Forward:</b> pick two parents and see the exact child, with a special-combo badge when a fixed recipe
overrides the averaging formula and a gender-locked badge for the one gender-locked pair.</p>
<p><b>Reverse:</b> pick a target Pal and see every parent pair that produces it — all of them, not a sample.</p>
<p><b>Family tree:</b> pick the Pal you want (say Anubis) and the full breeding chain appears instantly —
target on top, each bred Pal branching into its parents, bottoming out at Pals you can catch in the wild,
with step-order badges and links to habitat maps.</p>
<h2>Why it's accurate</h2>
<p>Species prediction is <b>table-driven</b>, not a re-implemented formula: the app embeds the game's own
breeding table ({n_pairs:,} parent pairs, {self_only} self-only Pals, every special combo), extracted from
Palworld's 1.0 game files and diffed byte-for-byte against upstream. If the game produces it, the calculator shows it.</p>
<h2>Popular breeding targets</h2>
<p class="links">{pal_chip_links(popular)}</p>
<p>Or browse the full <a href="/#tab=paldex">Paldex</a> — every Pal page lists its parent pairs and what it breeds into.</p>"""
    crumbs = '<a href="/">Palydex</a> › Breeding Calculator'
    return shell(hd, crumbs, body)


def tier_landing():
    cur = tiers.get("curatedDate", "")
    title = f"Palworld 1.0 Tier List — Best Combat & Base Pals ({cur}) | Palydex"
    desc = esc("Palworld 1.0 tier list for combat and base work, curated from the newest community and creator "
               "rankings with an Early / Mid / End game-stage selector — plus objective element, job and mount "
               "boards computed from game-file stats. Sources linked. Free, no ads.")
    stages = [("early", "Early game"), ("mid", "Mid game"), ("end", "End game")]
    boards = []
    for key, label in [("combat", "Combat"), ("workers", "Base Work")]:
        b = tiers[key]["stages"]
        sec = [f"<h2>{label} tier list</h2>"]
        for sk, sl in stages:
            st = b.get(sk) or {}
            if not st:
                continue
            sec.append(f"<p><b>{sl}</b>{' — ' + esc(st.get('blurb','')) if st.get('blurb') else ''}</p>")
            for t in ("S", "A"):
                if st.get(t):
                    sec.append(f'<p><b>{t} tier:</b></p><p class="links">{pal_chip_links(st[t])}</p>')
        boards.append("".join(sec))
    srcs = "".join(f'<li><a href="{esc(s["url"])}" rel="nofollow">{esc(s["name"])}</a>'
                   f'{" — " + esc(s.get("updated","")) if s.get("updated") else ""}</li>'
                   for s in tiers.get("sources") or [])
    hd = head(title, desc, "tier-list")
    body = f"""<div class="hd"><img src="/icon-192.png" alt="Palydex" width="84" height="84">
<div><h1>Palworld 1.0 Tier List</h1><div class="sub">curated {esc(cur)} · Early / Mid / End game stages · sources linked</div></div></div>
<a class="cta" href="/#tab=tiers">Open the full tier boards &rarr;</a>
<div class="sub" style="text-align:center">combat &middot; base work &middot; elements &middot; jobs &middot; mounts &middot; works offline</div>
{boards[0]}
{boards[1]}
<h2>Objective boards</h2>
<p>The app also computes <b>Elements</b> (9 boards ranked by base Attack), <b>Jobs</b> (12 boards grouped by
work level — 1.0 specialists reach Lv 8) and <b>Mounts</b> (Flying / Ground / Water by Ride Sprint speed)
straight from the embedded game data, with the same game-stage selector.</p>
<h2>Sources</h2>
<ul>{srcs}</ul>
<p class="sub">Every name above is validated against the dex at build time. Tap any Pal for its full 1.0 stats page.</p>"""
    crumbs = '<a href="/">Palydex</a> › Tier List'
    return shell(hd, crumbs, body)


def map_landing():
    mk = mapdata["markers"]
    tlist = mapdata["tlist"]
    n_main, n_tree = len(mk["main"]), len(mk["tree"])
    from collections import Counter
    counts = Counter(tlist[m[0]] for m in mk["main"] + mk["tree"])
    alpha = counts.get("Alpha Pal", 0)
    notable = [("Alpha Pals (with levels)", alpha),
               ("ore / coal / quartz / sulfur nodes",
                sum(v for k, v in counts.items() if re.search(r"ore|coal|quartz|sulfur|soralite|paloxite|hexolite|chromite", k, re.I))),
               ("treasure chests & caches", sum(v for k, v in counts.items() if re.search(r"treasure|supply|junk|salvage", k, re.I))),
               ("dungeons, towers & bosses", sum(v for k, v in counts.items() if re.search(r"dungeon|tower|awakened|bounty", k, re.I))),
               ("eggs", sum(v for k, v in counts.items() if "egg" in k.lower())),
               ("effigies & journals", sum(v for k, v in counts.items() if re.search(r"effig|journal|note", k, re.I))),
               ("fast travel statues", counts.get("Fast Travel", 0)),
               ("fishing spots", counts.get("Fishing Spot", 0)),
               ("merchants & NPCs", sum(v for k, v in counts.items() if re.search(r"merchant|npc|city", k, re.I)))]
    rows = "".join(f"<tr><td>{esc(k)}</td><td><b>{v:,}</b></td></tr>" for k, v in notable if v)
    title = f"Palworld Interactive Map (1.0) — {n_main + n_tree:,} Markers, Free Tracking | Palydex"
    desc = esc(f"Free Palworld 1.0 interactive map: {n_main + n_tree:,} markers from the game's own tables across the "
               f"Palpagos Islands and the World Tree — {alpha} Alpha Pals, every ore node, chest, egg, effigy and dungeon. "
               "Unlimited found-tracking, custom pins, Pal spawn heat layers, shareable links. No account, no paywall, no ads.")
    hd = head(title, desc, "interactive-map")
    body = f"""<div class="hd"><img src="/icon-192.png" alt="Palydex" width="84" height="84">
<div><h1>Palworld Interactive Map (1.0)</h1><div class="sub">{n_main:,} markers on Palpagos · {n_tree:,} on the World Tree · from the game's tables</div></div></div>
<a class="cta" href="/#tab=map">Open the interactive map &rarr;</a>
<div class="sub" style="text-align:center">unlimited free tracking &middot; custom pins &middot; spawn layers &middot; works offline</div>
<h2>What's on it</h2>
<table><tr><th>Marker type</th><th>Count</th></tr>{rows}</table>
<h2>Features other maps charge for</h2>
<p><b>Unlimited found-tracking</b> — check off chests, effigies and eggs with per-type progress, no account and no
marker cap. <b>Custom pins with notes</b> (double-click anywhere). <b>Export / import</b> your progress as a file.</p>
<p><b>Pal spawn layers</b> — overlay up to three color-coded habitat heat maps at once with a day/night toggle,
or click any empty spot to see exactly which Pals spawn there, straight from the game's spawn-distribution table.</p>
<p><b>Shareable location links</b> — every marker popup gives a link (like <code>#map=main/337/360</code>) that
opens the map at that exact spot; popups show Alpha Pal mini-stats and the nearest fast travel statue with distance.</p>
<p>Alpha Pal popups deep-link to their <a href="/#tab=paldex">Paldex pages</a>; resource nodes link to the
<a href="/#tab=items">item database</a> so you can see what each material crafts into.</p>"""
    crumbs = '<a href="/">Palydex</a> › Interactive Map'
    return shell(hd, crumbs, body)


# ============================== MAIN ==============================
def main():
    os.makedirs("pal", exist_ok=True)
    os.makedirs("item", exist_ok=True)

    ordered = sorted(pals, key=lambda p: (p["dex"], p["internalIndex"]))
    n = 0
    for i, p in enumerate(ordered):
        prev_p = ordered[i - 1] if i > 0 else None
        next_p = ordered[i + 1] if i < len(ordered) - 1 else None
        with open(f"pal/{SLUG[p['internalIndex']]}.html", "w", encoding="utf-8") as f:
            f.write(pal_page(p, prev_p, next_p))
        n += 1
    assert n == len(pals) == len(set(SLUG.values())), (n, len(set(SLUG.values())))

    inames = sorted(itemdb, key=str.lower)
    ni = 0
    for i, name in enumerate(inames):
        prev_n = inames[i - 1] if i > 0 else None
        next_n = inames[i + 1] if i < len(inames) - 1 else None
        with open(f"item/{ISLUG[name]}.html", "w", encoding="utf-8") as f:
            f.write(item_page(name, prev_n, next_n))
        ni += 1

    landings = {"breeding-calculator": breeding_landing(),
                "tier-list": tier_landing(),
                "interactive-map": map_landing()}
    for path, content in landings.items():
        with open(f"{path}.html", "w", encoding="utf-8") as f:
            f.write(content)

    today = date.today().isoformat()
    url = lambda loc, freq, pr: (f"  <url><loc>{SITE}{loc}</loc><lastmod>{today}</lastmod>"
                                 f"<changefreq>{freq}</changefreq><priority>{pr}</priority></url>")
    urls = [url("/", "weekly", "1.0")]
    urls += [url(f"/{p}", "weekly", "0.9") for p in landings]
    urls += [url(f"/pal/{SLUG[p['internalIndex']]}", "monthly", "0.7") for p in ordered]
    urls += [url(f"/item/{ISLUG[nm]}", "monthly", "0.6") for nm in inames]
    with open("sitemap.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(urls) + "\n</urlset>\n")

    if not os.path.exists("vercel.json"):
        json.dump({"cleanUrls": True, "trailingSlash": False}, open("vercel.json", "w"), indent=2)
    print(f"OK: {n} pal pages, {ni} item pages, {len(landings)} landing pages, "
          f"{len(PAL_ICON)} pal icons, {len(ITEM_ICON)} item icons, sitemap.xml ({len(urls)} URLs)")


if __name__ == "__main__":
    main()
