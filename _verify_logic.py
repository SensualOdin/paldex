import json
pals = json.load(open('pals_1.0.filled.json', encoding='utf-8'))
brd  = json.load(open('breeding_1.0.json', encoding='utf-8'))
byIndex = {p['internalIndex']:p for p in pals}
byName  = {p['name']:p for p in pals}

# forward map
FORWARD={}
for child,pairs in brd['combos'].items():
    for a,b in pairs:
        k=(a,b) if a<b else (b,a)
        FORWARD[k]=int(child)

def breed(aIdx,bIdx,ag=None,bg=None):
    for g in brd['genderLocked']:
        if (g['p1']==aIdx and g['p2']==bIdx and g['p1g']==ag and g['p2g']==bg) or \
           (g['p1']==bIdx and g['p2']==aIdx and g['p1g']==bg and g['p2g']==ag):
            return byIndex[g['child']]
    k=(aIdx,bIdx) if aIdx<bIdx else (bIdx,aIdx)
    c=FORWARD.get(k)
    return byIndex[c] if c is not None else None

fails=[]
def check(cond,msg):
    print(("  OK  " if cond else " FAIL ")+msg)
    if not cond: fails.append(msg)

print("=== §10 Verification checklist ===")
# counts
totalPairs=sum(len(v) for v in brd['combos'].values())
check(len(pals)==299, f"299 Pal records (got {len(pals)})")
check(totalPairs==44849, f"44,849 combo pairs (got {totalPairs})")
check(len(brd['genderLocked'])==2, f"2 gender-locked rows (got {len(brd['genderLocked'])})")

# same-species breeds true (sample several that are breedable-as-result and appear as own combo)
same_ok=0; same_tested=0
for p in pals:
    idx=p['internalIndex']
    k=(idx,idx)
    if k in FORWARD:
        same_tested+=1
        if FORWARD[k]==idx: same_ok+=1
check(same_tested>0 and same_ok==same_tested, f"same-species pairs breed true ({same_ok}/{same_tested} self-pairs present in table)")

# variant recipe: Mossanda + Grizzbolt -> Mossanda Lux, badged special
def idx_of(name):
    return byName[name]['internalIndex'] if name in byName else None
for (pa,pb,expected) in [("Mossanda","Grizzbolt","Mossanda Lux")]:
    a,b=idx_of(pa),idx_of(pb)
    if a and b:
        c=breed(a,b)
        check(c is not None and c['name']==expected, f"{pa}+{pb} -> {expected} (got {c['name'] if c else None})")
    else:
        check(False, f"{pa}/{pb} not found in dataset")

# formula-vs-table special detection for Mossanda Lux (should differ from generic-pool formula)
GENERIC=[p for p in pals if not p['selfOnly'] and not p['isVariant']]
def formula_predict(target):
    best=None;bd=1e9
    for p in GENERIC:
        d=abs(p['breedingPower']-target)
        if d<bd or (d==bd and (p['breedingPower']>best['breedingPower'] or (p['breedingPower']==best['breedingPower'] and p['dex']<best['dex']))):
            best=p;bd=d
    return best
a,b=idx_of("Mossanda"),idx_of("Grizzbolt")
t=(byIndex[a]['breedingPower']+byIndex[b]['breedingPower']+1)//2
pred=formula_predict(t)
tbl=breed(a,b)
check(pred is None or pred['internalIndex']!=tbl['internalIndex'], f"Mossanda Lux flagged special (formula would say {pred['name'] if pred else None}, table says {tbl['name']})")

# Katress/Wixen gender lock
K=idx_of("Katress"); W=idx_of("Wixen")
ki=idx_of("Katress Ignis"); wn=idx_of("Wixen Noct")
c1=breed(K,W,"FEMALE","MALE")   # female Katress + male Wixen -> Katress Ignis
c2=breed(K,W,"MALE","FEMALE")   # male Katress + female Wixen -> Wixen Noct
check(c1 and c1['name']=="Katress Ignis", f"female Katress + male Wixen -> Katress Ignis (got {c1['name'] if c1 else None})")
check(c2 and c2['name']=="Wixen Noct", f"male Katress + female Wixen -> Wixen Noct (got {c2['name'] if c2 else None})")

# Mimog/Tarantriss boundary — the spec's cited near-miss. Mimog is self-only; ensure no pair resolves to Mimog via formula pool
mimog=byName.get("Mimog"); tara=byName.get("Tarantriss")
if mimog and tara:
    check(mimog['selfOnly']==True, f"Mimog is selfOnly ({mimog['breedingPower']})")
    # nothing in generic pool should BE mimog
    check(all(p['internalIndex']!=mimog['internalIndex'] for p in GENERIC), "Mimog excluded from generic pool")

# self-only unreachable unless owned: Jetragon
jet=byName.get("Jetragon")
if jet:
    ji=jet['internalIndex']
    # is Jetragon ever a FORWARD result from a non-self pair?
    as_result=[k for k,v in FORWARD.items() if v==ji and k[0]!=k[1]]
    check(len(as_result)==0, f"Jetragon not produced by any cross-species pair (self-only) — {len(as_result)} cross pairs")
    check(jet['selfOnly']==True, "Jetragon is selfOnly")

# element coverage
missing=[p['name'] for p in pals if not p.get('elements')]
check(len(missing)==0, f"all 299 have elements (missing: {len(missing)})")

print()
print("RESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
