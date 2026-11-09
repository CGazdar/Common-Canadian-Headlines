import re, sys
from google.cloud import bigquery

args = sys.argv[1:]
month = "2024-01"
if "--month" in args:
    i = args.index("--month"); month = args[i + 1]; del args[i:i + 2]
top = 12
if "--top" in args:
    i = args.index("--top"); top = int(args[i + 1]); del args[i:i + 2]
words = [a.lower() for a in args]
if not words:
    sys.exit("Give at least one word, e.g.  python probe2.py --month 2024-01 rebelnews thehub")
print("Searching for:", words, "in", month)
y, m = map(int, month.split("-"))
ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
lo, hi = f"{y}-{m:02d}-01", f"{ny}-{nm:02d}-01"
pat = "(" + "|".join(re.escape(w) for w in words) + ")"
sql = f"""
SELECT LOWER(SourceCommonName) AS d, COUNT(*) AS n
FROM `gdelt-bq.gdeltv2.gkg_partitioned`
WHERE _PARTITIONTIME >= TIMESTAMP('{lo}') AND _PARTITIONTIME < TIMESTAMP('{hi}')
  AND REGEXP_CONTAINS(LOWER(SourceCommonName), r'{pat}')
GROUP BY d ORDER BY n DESC
"""
c = bigquery.Client()
dry = c.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
print(f"This scan would read {dry.total_bytes_processed/1e9:.1f} GB.")
if input("Run it? [y/N] ").strip().lower() != "y":
    sys.exit("Cancelled.")
rows = list(c.query(sql).result())
for w in words:
    hits = [(r.d, r.n) for r in rows if w in r.d]
    print(f"\n== {w}" + ("" if hits else "   (no matches)"))
    for d, n in hits[:top]:
        print(f"   {d:40s} {n}")
