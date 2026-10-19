import csv
import shutil
import sys

with open("outlets.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))
header, body = rows[0], rows[1:]
n = len(header)
fixed = 0
for r in body:
    if len(r) == n - 1:                       # one field short: owner is in the notes slot
        print(f"fixing {r[0]}: owner = {r[-1]!r}")
        r[8:] = ["", r[8], r[9]]              # rss_url blank, notes = old rss slot, owner = last field
        fixed += 1
    elif len(r) != n:
        print(f"WARNING {r[0]}: has {len(r)} fields (expected {n}), not touched")
print(f"{fixed} rows need fixing")
if "--apply" in sys.argv and fixed:
    shutil.copy("outlets.csv", "outlets.csv.bak")
    with open("outlets.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print("Saved outlets.csv (backup: outlets.csv.bak)")