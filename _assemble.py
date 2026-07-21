import json

pals   = json.load(open('pals_1.0.filled.json', encoding='utf-8'))
brd    = json.load(open('breeding_1.0.json', encoding='utf-8'))
icons  = json.load(open('_icons.json', encoding='utf-8'))
spawns = json.load(open('_spawns.json', encoding='utf-8'))
tiers  = json.load(open('_tiers.json', encoding='utf-8'))
try:
    details = json.load(open('_paldetails.json', encoding='utf-8'))
except FileNotFoundError:
    details = {}
    print("NOTE: _paldetails.json not found — drops/movesets omitted")
try:
    itemdb = json.load(open('_items.json', encoding='utf-8'))
except FileNotFoundError:
    itemdb = {}
    print("NOTE: _items.json not found — item lookup limited to Pal drops")

# validate every curated tier name against the dex — fail loudly on typos
_names = {p['name'] for p in pals}
_bad = [n for board in ('combat', 'workers')
        for stage in tiers[board]['stages'].values()
        for t, lst in stage.items() if t != 'blurb'
        for n in lst if n not in _names]
assert not _bad, f"_tiers.json has unknown pal names: {_bad}"

tpl = open('_app_template.html', encoding='utf-8').read()

pals_js   = "const PALS = "   + json.dumps(pals,   ensure_ascii=False, separators=(',',':')) + ";"
brd_js    = "const BRD = "    + json.dumps(brd,    ensure_ascii=False, separators=(',',':')) + ";"
icons_js  = "const ICONS = "  + json.dumps(icons,  ensure_ascii=False, separators=(',',':')) + ";"
spawns_js = "const SPAWNS = " + json.dumps(spawns, ensure_ascii=False, separators=(',',':')) + ";"
tiers_js  = "const TIERS = "  + json.dumps(tiers,  ensure_ascii=False, separators=(',',':')) + ";"
details_js = "const DETAILS = " + json.dumps(details, ensure_ascii=False, separators=(',',':')) + ";"
itemdb_js = "const ITEMDB = " + json.dumps(itemdb, ensure_ascii=False, separators=(',',':')) + ";"

assert tpl.count("/*__PALS__*/") == 1
assert tpl.count("/*__BRD__*/") == 1
assert tpl.count("/*__ICONS__*/") == 1
assert tpl.count("/*__SPAWNS__*/") == 1
assert tpl.count("/*__TIERS__*/") == 1
assert tpl.count("/*__DETAILS__*/") == 1
assert tpl.count("/*__ITEMS__*/") == 1
out = (tpl.replace("/*__PALS__*/", pals_js)
          .replace("/*__BRD__*/", brd_js)
          .replace("/*__ICONS__*/", icons_js)
          .replace("/*__SPAWNS__*/", spawns_js)
          .replace("/*__TIERS__*/", tiers_js)
          .replace("/*__DETAILS__*/", details_js)
          .replace("/*__ITEMS__*/", itemdb_js))

with open('index.html','w',encoding='utf-8') as f:
    f.write(out)

import os
print("index.html written:", round(os.path.getsize('index.html')/1024,1), "KB")
print("PALS records:", len(pals))
print("BRD combos children:", len(brd['combos']))
print("ICONS:", len(icons['pals']), "pal +", len(icons['elements']), "element")
print("SPAWNS:", len(spawns['pals']), "pals with habitat data, grid", spawns['grid'])
print("DETAILS:", len(details), "pals with drops/movesets")
print("ITEMDB:", len(itemdb), "items with sources/recipes")
