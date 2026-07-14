import json

pals = json.load(open('pals_1.0.filled.json', encoding='utf-8'))
brd  = json.load(open('breeding_1.0.json', encoding='utf-8'))

tpl = open('_app_template.html', encoding='utf-8').read()

pals_js = "const PALS = " + json.dumps(pals, ensure_ascii=False, separators=(',',':')) + ";"
brd_js  = "const BRD = "  + json.dumps(brd,  ensure_ascii=False, separators=(',',':')) + ";"

assert tpl.count("/*__PALS__*/") == 1
assert tpl.count("/*__BRD__*/") == 1
out = tpl.replace("/*__PALS__*/", pals_js).replace("/*__BRD__*/", brd_js)

with open('index.html','w',encoding='utf-8') as f:
    f.write(out)

import os
print("index.html written:", round(os.path.getsize('index.html')/1024,1), "KB")
print("PALS records:", len(pals))
print("BRD combos children:", len(brd['combos']))
