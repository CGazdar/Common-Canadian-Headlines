from db import connect
ids = "standardfreeholder thespec thewhig lfpress niagarafallsreview nugget owensoundsuntimes peterboroughexaminer pentictonherald timescolonist brandonsun acadienouvelle intelligencer brantfordexpositor recorder reddeeradvocate chathamdailynews vocm yukonnews whitehorsestar".split()
c = connect()
years = [str(y) for y in range(2019, 2027)]
print(f"{'outlet':22s}" + "".join(f"{y:>8s}" for y in years))
for o in ids:
    got = dict(c.execute("select substr(published_at,1,4), count(*) from headlines where outlet_id=? group by 1", (o,)).fetchall())
    print(f"{o:22s}" + "".join(f"{got.get(y, 0):8d}" for y in years))
