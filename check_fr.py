from db import connect
c = connect()
print("translations so far:", c.execute("select count(*) from translations").fetchone()[0])
print("quarter_totals rows overall:", c.execute("select count(*) from quarter_totals").fetchone()[0])
print("outlets in quarter_totals:", c.execute("select count(distinct outlet_id) from quarter_totals").fetchone()[0])
print("French outlets in sections.csv with keep=1:")
import csv
n = {}
for r in csv.DictReader(open("sections.csv")):
    if r["outlet_id"] in ("lapresse","ledevoir","jdm","journaldequebec") and r["keep"] in ("1","1.0"):
        n[r["outlet_id"]] = n.get(r["outlet_id"], 0) + 1
print(n)
