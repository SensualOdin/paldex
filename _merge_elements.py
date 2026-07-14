import json, sys

VALID = {"neutral","fire","water","grass","electric","ice","ground","dark","dragon"}

pals = json.load(open('pals_1.0.json', encoding='utf-8'))
fill = json.load(open('_elements_fill.json', encoding='utf-8'))

# validate fill tokens
bad = []
for name, elems in fill.items():
    for e in elems:
        if e not in VALID:
            bad.append((name, e))
if bad:
    print("INVALID TOKENS:", bad); sys.exit(1)

missing_before = [x for x in pals if not x.get('elements')]
missing_names = {x['name'] for x in missing_before}

# every missing name must be in fill, and vice versa
fill_names = set(fill.keys())
not_in_fill = missing_names - fill_names
extra_in_fill = fill_names - missing_names
if not_in_fill:
    print("MISSING FROM FILL (no data supplied):", sorted(not_in_fill)); sys.exit(1)
if extra_in_fill:
    print("WARNING: fill has names not in missing set (ignored):", sorted(extra_in_fill))

# apply
filled = 0
for x in pals:
    if not x.get('elements'):
        x['elements'] = list(fill[x['name']])
        x['elementSource'] = 'paldb.cc'
        filled += 1

remaining = [x for x in pals if not x.get('elements')]
print("records before:", len(pals))
print("missing before:", len(missing_before))
print("filled:", filled)
print("remaining empty:", len(remaining))
if remaining:
    print("STILL EMPTY:", [x['name'] for x in remaining]); sys.exit(1)

# element distribution sanity
from collections import Counter
c = Counter()
for x in pals:
    for e in x['elements']:
        c[e]+=1
print("element distribution:", dict(sorted(c.items(), key=lambda kv:-kv[1])))

json.dump(pals, open('pals_1.0.filled.json','w',encoding='utf-8'), ensure_ascii=False)
print("\nWROTE pals_1.0.filled.json  OK")
