import json, re
def load(path, name):
    t = open(path, encoding="utf-8").read().strip()
    t = re.sub(r"^window\.%s\s*=\s*" % name, "", t).rstrip().rstrip(";")
    return json.loads(t)
m = load("docs/map.js", "MAP")
print("MAP keys:", list(m.keys()))
dots = m.get("dots")
print("dots:", type(dots).__name__, len(dots) if dots is not None else None)
if dots:
    items = list(dots.items())[:3] if isinstance(dots, dict) else dots[:3]
    for d in items: print("  sample:", d)
try:
    d = load("docs/data.js", "DATA")
    print("DATA keys:", list(d.keys()))
    outs = d.get("outlets")
    print("outlets in data.js:", len(outs) if outs is not None else None)
except Exception as e:
    print("could not read data.js:", e)
