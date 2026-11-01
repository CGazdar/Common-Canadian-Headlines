"""Fill in leanings found on Media Bias/Fact Check (MBFC) for outlets that had none.

    python apply_leanings.py          show what would change
    python apply_leanings.py --apply  write outlets.csv (backup: outlets.csv.bak)

Only fills blanks. A leaning you already entered is never overwritten.
"""
import csv
import shutil
import sys

CHECKED = "2026-10-19"
FOUND = {   # outlet_id: (leaning, MBFC label)
    "lapresse": ("lean_left", "MBFC Left-Center"),
    "simcoereformer": ("lean_right", "MBFC Right-Center"),
    "thesudburystar": ("lean_right", "MBFC Right-Center"),
    "wellandtribune": ("lean_left", "MBFC Left-Center"),
    "timescolonist": ("lean_left", "MBFC Left-Center"),
    "intelligencer": ("lean_right", "MBFC Right-Center"),
    "brantfordexpositor": ("lean_right", "MBFC Right-Center"),
    "recorder": ("lean_right", "MBFC Right-Center"),
    "chathamdailynews": ("lean_right", "MBFC Right-Center"),
    "reddeeradvocate": ("lean_left", "MBFC Left-Center"),
    "yukonnews": ("lean_left", "MBFC Left-Center"),
    "chronicleherald": ("lean_right", "MBFC Right-Center (Chronicle Herald)"),
}

with open("outlets.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))
head, body = rows[0], rows[1:]
ix = {c: i for i, c in enumerate(head)}
for r in body:
    if not r or r[0] not in FOUND:
        continue
    lean, why = FOUND[r[0]]
    if r[ix["leaning"]].strip():
        print(f"{r[0]:20s} already has {r[ix['leaning']]!r}, left alone")
        continue
    print(f"{r[0]:20s} -> {lean}  ({why})")
    r[ix["leaning"]], r[ix["leaning_checked_on"]], r[ix["notes"]] = lean, CHECKED, why
if "--apply" in sys.argv:
    shutil.copy("outlets.csv", "outlets.csv.bak")
    with open("outlets.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print("Saved outlets.csv (backup: outlets.csv.bak)")
else:
    print("Dry run. Add --apply to save.")