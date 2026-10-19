import sys
from db import connect
c = connect()
rows = c.execute("select h.headline, t.text_en from translations t join headlines_clean h on h.id = t.headline_id where h.headline like ? limit 25", ("%" + sys.argv[1] + "%",))
for fr, en in rows:
    print(fr, "->", en)
