import sys

from db import connect, sync_outlets

PATTERN = "%/news/canada/north/%"
QUARTER = "substr(published_at,1,4) || '-Q' || ((cast(substr(published_at,6,2) as integer) + 2) / 3)"


def main():
    apply = "--apply" in sys.argv
    conn = connect()
    sync_outlets(conn)
    have = conn.execute("SELECT 1 FROM outlets WHERE outlet_id='cbcnorth'").fetchone()
    rows = conn.execute(
        f"SELECT {QUARTER} AS q, count(*) FROM headlines "
        "WHERE outlet_id='cbc' AND url LIKE ? GROUP BY q ORDER BY q", (PATTERN,)).fetchall()
    already = conn.execute("SELECT count(*) FROM headlines WHERE outlet_id='cbcnorth'").fetchone()[0]
    total_cbc = conn.execute("SELECT count(*) FROM headlines WHERE outlet_id='cbc'").fetchone()[0]
    n = sum(c for _, c in rows)
    print(f"CBC headlines in total: {total_cbc:,}.  With /news/canada/north/ in the address: {n:,}.  Already moved: {already:,}\n")
    print("quarter    North headlines")
    for q, c in rows:
        print(f"{q}   {c:6,d}   {'#' * min(60, c // 20)}")
    print("\nA few examples:")
    for h, u in conn.execute("SELECT headline, url FROM headlines WHERE outlet_id='cbc' AND url LIKE ? "
                             "ORDER BY random() LIMIT 6", (PATTERN,)):
        print(f"  {h}\n    {u}")
    if not apply:
        print("\nNothing was changed. Add the cbcnorth row to outlets.csv, then run: python split_cbc_north.py --apply")
        return
    if not have:
        sys.exit("\nThere is no cbcnorth row in outlets.csv yet. Add it, then run this again with --apply.")
    cur = conn.execute("UPDATE headlines SET outlet_id='cbcnorth' WHERE outlet_id='cbc' AND url LIKE ?", (PATTERN,))
    conn.commit()
    print(f"\nMoved {cur.rowcount:,} headlines to cbcnorth. Now rerun: python clean.py")


if __name__ == "__main__":
    main()