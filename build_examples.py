import collections
import json
import random
import re
from urllib.parse import parse_qsl, urlencode, urlsplit

from build_terms import (MAX_PER_OUTLET_QUARTER, load_keep, load_outlet_languages, quarter_of,
                         section_key, terms_of)
from db import HERE, connect
from lean_terms import MIN_OUTLET_QUARTER_HEADLINES, min_headlines
from track_terms import load_watch

PER_OUTLET_QUARTER = 5
OUT = HERE / "docs" / "examples"
TRACKING = re.compile(r"^(utm_.*|cmp|fbclid|gclid|ref|source|ocid|mc_.*)$", re.I)


def slug(term):
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def tidy(url):
    """The link without tracking parameters, as https://..."""
    p = urlsplit(url.strip())
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not TRACKING.match(k)]
    return f"https://{p.netloc}{p.path}" + ("?" + urlencode(q) if q else "")


def main():
    watch = set(load_watch())
    keep, lang = load_keep(), load_outlet_languages()
    conn = connect()
    conn.execute("CREATE TABLE IF NOT EXISTS translations "
                 "(headline_id INTEGER PRIMARY KEY, text_en TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS link_status (url TEXT PRIMARY KEY, status INTEGER, checked_on TEXT)")
    dead = {u for (u,) in conn.execute("SELECT url FROM link_status WHERE status IN (404, 410)")}

    quarters = collections.OrderedDict()
    for (month,) in conn.execute("SELECT DISTINCT month FROM headlines_clean ORDER BY month").fetchall():
        quarters.setdefault(quarter_of(month), []).append(month)

    result = {t: collections.defaultdict(dict) for t in watch}
    for quarter, months in quarters.items():
        marks = ",".join("?" * len(months))
        rows = conn.execute(
            "SELECT c.outlet_id, c.headline, h.url, h.published_at, t.text_en FROM headlines_clean c "
            "JOIN headlines h ON h.id = c.id "
            "LEFT JOIN translations t ON t.headline_id = c.id "
            f"WHERE c.is_syndicated = 0 AND c.month IN ({marks}) ORDER BY c.id", months).fetchall()
        by_outlet = collections.defaultdict(list)
        for oid, headline, url, published, text_en in rows:
            lg = lang.get(oid)
            shown = headline                    # what visitors see: the original headline
            if lg == "fr":
                if not text_en:
                    continue                    # not translated yet
                headline = text_en              # what is matched against the watch terms
            elif lg != "en":
                continue
            if keep.get((oid, section_key(url))):
                by_outlet[oid].append((headline, url, published, shown))
        rng = random.Random(quarter)            # identical to build_terms.py, so the same headlines are used
        for oid, items in by_outlet.items():
            if len(items) > MAX_PER_OUTLET_QUARTER:
                items = rng.sample(items, MAX_PER_OUTLET_QUARTER)
            if len(items) < min_headlines(oid):
                continue                         # the site hides this outlet-quarter, so no examples either
            matches = collections.defaultdict(list)
            for headline, url, published, shown in items:
                for t in terms_of(headline) & watch:
                    matches[t].append((shown, tidy(url), (published or "")[:10]))
            pick = random.Random(f"{quarter}|{oid}")
            for t, lst in matches.items():
                lst = sorted({x[1]: x for x in lst}.values(), key=lambda x: x[1])   # one entry per link, stable order
                pick.shuffle(lst)
                good = [x for x in lst if x[1] not in dead][:PER_OUTLET_QUARTER]
                if good:
                    result[t][quarter][oid] = [[h, u.replace("https://", "", 1), d] for h, u, d in good]

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    n = 0
    for t, by_q in result.items():
        (OUT / f"{slug(t)}.json").write_text(
            json.dumps({"term": t, "quarters": by_q}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        n += sum(len(v) for q in by_q.values() for v in q.values())
    size = sum(p.stat().st_size for p in OUT.glob("*.json")) / 1e6
    print(f"wrote {len(result)} files to {OUT}: {n:,} example headlines, {size:.1f} MB in total "
          f"({len(dead):,} known dead links skipped)")


if __name__ == "__main__":
    main()