from google.cloud import bigquery
TABLE = "`gdelt-bq.gdeltv2.gkg_partitioned`"
WORDS = ["gleaner", "transcript", "telegraph", "brunswick", "nnsl", "nunavut", "norj", "northernjournal",
         "cabin", "examiner", "ntv", "nunatsiaq", "whitehorse", "yukon", "independent"]
like = " OR ".join(f"LOWER(SourceCommonName) LIKE '%{w}%'" for w in WORDS)
sql = f"""SELECT SourceCommonName AS domain, COUNT(*) AS n FROM {TABLE}
WHERE _PARTITIONTIME >= TIMESTAMP('2023-01-01') AND _PARTITIONTIME < TIMESTAMP('2023-02-01')
AND ({like}) GROUP BY 1 HAVING n >= 20 ORDER BY n DESC"""
client = bigquery.Client()
dry = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True))
print(f"This will scan about {dry.total_bytes_processed / 1e9:.1f} GB")
if input("Run it? (y/n) ").strip().lower() == "y":
    for r in client.query(sql).result():
        print(f"{r.domain:40s} {r.n}")
