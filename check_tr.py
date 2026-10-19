from db import connect
c = connect()
print("outlet, non-syndicated headlines, translated")
for r in c.execute("""select h.outlet_id, count(*), sum(t.headline_id is not null)
    from headlines_clean h left join translations t on t.headline_id = h.id
    where h.is_syndicated = 0 and h.outlet_id in ('lapresse','ledevoir','jdm','journaldequebec','acadienouvelle')
    group by 1"""):
    print(r)
print()
print("language column in the database:")
for r in c.execute("select outlet_id, language from outlets where outlet_id in ('lapresse','ledevoir','jdm','journaldequebec','acadienouvelle')"): print(r)
