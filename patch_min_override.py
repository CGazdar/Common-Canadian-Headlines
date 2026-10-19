import re
import shutil
from pathlib import Path

NEW = '''
# Small outlets kept on purpose (e.g. the territories' only local papers): their quarters count
# once they reach this many headlines, instead of MIN_OUTLET_QUARTER_HEADLINES.
MIN_OVERRIDES = {"whitehorsestar": 100, "yukonnews": 100}


def min_headlines(outlet_id):
    return MIN_OVERRIDES.get(outlet_id, MIN_OUTLET_QUARTER_HEADLINES)
'''


def edit(name, fn):
    p = Path(name)
    text = p.read_text(encoding="utf-8")
    new = fn(text)
    if new == text:
        print(f"{name}: nothing to change")
        return
    shutil.copy(p, f"{name}.bak")
    p.write_text(new, encoding="utf-8")
    print(f"{name}: updated")


def lean(t):
    if "def min_headlines" not in t:
        m = re.search(r"^MIN_OUTLET_QUARTER_HEADLINES = .*$", t, re.M)
        assert m, "constant not found in lean_terms.py"
        t = t[:m.end()] + "\n" + NEW + t[m.end():]
    return re.sub(r"(if (o|oid) in \w+ and n >= )MIN_OUTLET_QUARTER_HEADLINES",
                  r"\1min_headlines(\2)", t)


def users(t):
    t = re.sub(r"(if (o|oid) in \w+ and n >= )MIN_OUTLET_QUARTER_HEADLINES",
               r"\1min_headlines(\2)", t)
    t = t.replace("if len(items) < MIN_OUTLET_QUARTER_HEADLINES:", "if len(items) < min_headlines(oid):")
    if "min_headlines" in t and "import" in t:
        t = re.sub(r"from lean_terms import ([^\n]*)MIN_OUTLET_QUARTER_HEADLINES",
                   r"from lean_terms import \1MIN_OUTLET_QUARTER_HEADLINES, min_headlines", t, count=1) \
            if "min_headlines," not in t and ", min_headlines" not in t else t
    return t


edit("lean_terms.py", lean)
for f in ("build_examples.py", "export_dataset.py", "export_site_data.py", "track_terms.py"):
    edit(f, users)