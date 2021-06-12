import sqlite3

con = sqlite3.connect("testing")

cur = con.cursor()

cur.execute("create table if not exists dummy (name text, id int) ")
#v = "hai1"
#cur.execute("insert into dummy values(?,?)",(v,2000))

#cur.execute("select * from dummy")
cur.execute('select * from sqlite_master')
print(cur.fetchall())

con.commit()

con.close()






