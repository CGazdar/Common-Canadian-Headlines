"""Check which example links still work, and remember the answer in the database.

Reads docs/examples/*.json, asks each publisher's website whether the article still exists,
and stores the result in the link_status table. Only 404 (not found) and 410 (gone) count as dead.
Paywalls and bot blocking (403, 429, timeouts) are NOT treated as dead, because a reader's browser
usually gets through. Links checked in the last 90 days are skipped, so reruns are quick.

Usage:  python check_links.py          (can be stopped with Ctrl+C and resumed later)
        python check_links.py 500      (check only 500 links, to try it out)
Then:   python build_examples.py       (replaces dead links with working ones)
"""
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from urllib.parse import urlsplit

from db import HERE, connect

UA = "headline-research-link-check/0.1 (personal research project; checks that article links still exist)"
WORKERS = 8
PAUSE_PER_SITE = 0.5        # seconds between requests to the same publisher
RECHECK_AFTER_DAYS = 90

_locks, _last, _guard = {}, {}, threading.Lock()


def polite(host):
    with _guard:
        lock = _locks.setdefault(host, threading.Lock())
    with lock:
        wait = _last.get(host, 0) + PAUSE_PER_SITE - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()


def status_of(url):
    host = urlsplit(url).netloc
    for method in ("HEAD", "GET"):
        polite(host)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 405, 501):
                continue                        # some sites refuse HEAD, so ask again with GET
            return e.code
        except Exception:
            return 0                            # network trouble: unknown, not dead
    return 0


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    urls = set()
    for p in (HERE / "docs" / "examples").glob("*.json"):
        for by_o in json.loads(p.read_text(encoding="utf-8"))["quarters"].values():
            for items in by_o.values():
                urls.update("https://" + u for _, u, _ in items)
    conn = connect()
    conn.execute("CREATE TABLE IF NOT EXISTS link_status (url TEXT PRIMARY KEY, status INTEGER, checked_on TEXT)")
    cutoff = (date.today() - timedelta(days=RECHECK_AFTER_DAYS)).isoformat()
    fresh = {u for (u,) in conn.execute("SELECT url FROM link_status WHERE checked_on >= ?", (cutoff,))}
    todo = sorted(urls - fresh)
    if limit:
        todo = todo[:limit]
    print(f"{len(urls):,} example links; {len(todo):,} still to check", flush=True)
    done = dead = 0
    today = date.today().isoformat()
    try:
        with ThreadPoolExecutor(WORKERS) as pool:
            for url, st in zip(todo, pool.map(status_of, todo)):
                conn.execute("INSERT OR REPLACE INTO link_status VALUES (?,?,?)", (url, st, today))
                done += 1
                dead += st in (404, 410)
                if done % 200 == 0:
                    conn.commit()
                    print(f"  {done:,}/{len(todo):,} checked, {dead:,} dead so far", flush=True)
    except KeyboardInterrupt:
        print("\nStopped. Progress so far is saved; run again to continue.")
    conn.commit()
    print(f"Done: {done:,} checked, {dead:,} dead. Now run: python build_examples.py")


if __name__ == "__main__":
    main()