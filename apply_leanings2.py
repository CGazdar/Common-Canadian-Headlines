import csv, shutil, sys
DATE = "2026-11-01"
NEW = {
    # Media Bias/Fact Check: Left-Center (high factual), owner Black Press Media
    **{o: "lean_left" for o in ("vicnews", "nanaimobulletin", "comoxvalleyrecord", "campbellrivermirror",
                                "vernonmorningstar", "kelownacapnews", "peacearchnews", "mapleridgenews")},
    # MBFC: Cape Breton Post and Chronicle Herald (SaltWire papers) are Right-Center
    "saltwire": "lean_right",
}
rows = list(csv.reader(open("outlets.csv", encoding="utf-8", newline="")))
h = rows[0]; iid, il, id_ = h.index("outlet_id"), h.index("leaning"), h.index("leaning_checked_on")
n = 0
for r in rows[1:]:
    if r and r[iid] in NEW and not r[il].strip():
        print(f"{r[iid]:24s} -> {NEW[r[iid]]}"); n += 1
        r[il] = NEW[r[iid]]; r[id_] = DATE
print(n, "blank leanings filled")
if "--apply" in sys.argv:
    shutil.copy("outlets.csv", "outlets.csv.bak")
    csv.writer(open("outlets.csv", "w", encoding="utf-8", newline="")).writerows(rows)
    print("Saved (backup outlets.csv.bak)")
else:
    print("Dry run. Add --apply to save.")
