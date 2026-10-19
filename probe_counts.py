from db import connect
ids = "nunatsiaq nnsl nunavutnews yukonnews whitehorsestar northernjournal cabinradio timestranscript dailygleaner vocm ntv theindependent halifaxexaminer thecoast".split()
c = connect()
have = dict(c.execute("select outlet_id, count(*) from headlines where outlet_id in (%s) group by 1" % ",".join("?" * len(ids)), ids).fetchall())
for i in ids:
    print(f"{i:18s} {have.get(i, 0):6d}")
