from datetime import datetime, timezone
from collections import defaultdict
from google.cloud import bigquery
client = bigquery.Client()
since = datetime(2026, 10, 1, tzinfo=timezone.utc)
by_day, rows = defaultdict(float), []
for j in client.list_jobs(min_creation_time=since, max_results=2000):
    if j.job_type != "query":
        continue
    gb = (j.total_bytes_billed or 0) / 1e9
    day = j.created.astimezone().strftime("%Y-%m-%d")
    by_day[day] += gb
    rows.append((j.created.astimezone(), gb, (j.query or "")[:70].replace("\n", " ")))
print("GB billed per day (your local time):")
for d in sorted(by_day):
    print(f"  {d}  {by_day[d]:9.1f} GB")
oct_ = sum(v for d, v in by_day.items() if d < "2026-11-01")
nov = sum(v for d, v in by_day.items() if d >= "2026-11-01")
print(f"October total: {oct_/1000:.2f} TB    November so far: {nov/1000:.2f} TB")
print("Biggest 8 jobs:")
for t, gb, q in sorted(rows, key=lambda r: -r[1])[:8]:
    print(f"  {t:%m-%d %H:%M}  {gb:8.1f} GB  {q}")
