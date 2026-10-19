import csv
import shutil
import sys

KEEP = {
    # Postmedia papers
    **{o: {"news", "opinion", "business", "health"} for o in
       ("saultstar", "theobserver", "simcoereformer", "stratfordbeaconherald", "thesudburystar", "windsorstar")},
    # Torstar papers
    **{o: {"news", "news-story", "politics", "opinion", "opinion-story", "community-story", "business"} for o in
       ("stcatharinesstandard", "wellandtribune")},
    # Southern Alberta papers
    **{o: {"news", "commentary", "federal-election", "municipal-election", "lethbridge-news"} for o in
       ("lethbridgeherald", "medicinehatnews")},
    # Chronicle-Journal and Kelowna Daily Courier
    **{o: {"news", "opinion"} for o in ("chroniclejournal", "kelownadailycourier")},
}
KEEP.update({
    "lapresse": {"actualites", "international", "affaires", "societe", "debats", "dialogue",
                 "covid-19", "elections-federales"},
    "ledevoir": {"actualites", "monde", "opinion", "societe", "politique", "economie", "environnement"},
})
KEEP_ALL = {"journaldequebec"}      # sections are just years, so no topic filtering is possible
KEEP_YEARS = {"jdm": {"actualite"}}  # sections are years (kept) plus a few named ones; sports etc. dropped


def main():
    apply = "--apply" in sys.argv
    with open("sections.csv", newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        fields = rd.fieldnames
        rows = list(rd)
    changed = {}
    for r in rows:
        o = r["outlet_id"]
        if o in KEEP_ALL:
            new = "1"
        elif o in KEEP_YEARS:
            s = r["section"].split("/")[0]
            new = "1" if s.isdigit() or s in KEEP_YEARS[o] else "0"
        elif o in KEEP:
            new = "1" if r["section"].split("/")[0] in KEEP[o] else "0"
        else:
            continue
        if r["keep"] != new:
            changed[o] = changed.get(o, 0) + 1
            r["keep"] = new
    seen = {r["outlet_id"] for r in rows}
    for o in sorted(set(KEEP) | KEEP_ALL | set(KEEP_YEARS)):
        print(f"{o:24s} rows in file: {'yes' if o in seen else 'NO - run make_section_config.py first'}; changed: {changed.get(o, 0)}")
    if apply:
        shutil.copy("sections.csv", "sections.csv.bak")
        with open("sections.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print("Saved sections.csv (backup: sections.csv.bak)")
    else:
        print("Dry run. Add --apply to save.")


if __name__ == "__main__":
    main()