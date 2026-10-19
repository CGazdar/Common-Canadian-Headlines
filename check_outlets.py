import json, re
t = open("docs/data.js", encoding="utf-8").read().strip()
t = re.sub(r"^window\.DATA\s*=\s*", "", t).rstrip().rstrip(";")
d = json.loads(t)
o = d["outlets"]
print("type:", type(o).__name__, "| size:", len(o))
items = list(o.items())[:3] if isinstance(o, dict) else o[:3]
for x in items: print("  sample:", x)
if isinstance(o, dict):
    print("provinces:", sorted({v.get("province") for v in o.values()}))
    m = json.loads(re.sub(r"^window\.MAP\s*=\s*", "", open("docs/map.js", encoding="utf-8").read().strip()).rstrip().rstrip(";"))
    both = [k for k in o if k in m["dots"] and o[k].get("province") != "NAT"]
    print("outlets that should get a dot:", len(both))
