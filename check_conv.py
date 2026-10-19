from db import connect
c = connect()
print("month, french outlets, headlines with 'convoi de la libert' / 'convoi' in 2022")
for r in c.execute("""select substr(h.month,1,7), count(*), sum(h.is_syndicated), sum(t.headline_id is not null)
    from headlines_clean h left join translations t on t.headline_id = h.id
    where h.outlet_id in ('lapresse','ledevoir','jdm','journaldequebec','acadienouvelle')
    and h.month like '2022-0%' and (h.headline like '%convoi de la libert%' or h.headline like '%convoi%')
    group by 1 order by 1"""):
    print(r)
