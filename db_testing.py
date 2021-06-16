import sqlite3

db = sqlite3.connect("testing_db")

#print(type(con))
#con.close()
#exit()
cur = db.cursor()

cur = db.execute('''
        create table if not exists bot_data (
            total_forms int
        )
    ''')

cur = db.execute("select * from bot_data")

if len(cur.fetchall()) == 0:
    cur = db.execute('''
        insert into bot_data values(0)
    ''')

else:

    cur = db.execute("select total_forms from bot_data")

    total_forms = cur.fetchone()[0]

    total_forms += 1

    cur = db.execute(f"update bot_data set total_forms = {total_forms}")

#cur.execute("create table if not exists dummy (name text, id int) ")
#v = "hai1"
#cur.execute("insert into dummy values(?,?)",(v,2000))

#cur.execute("select * from dummy")
#cur.execute('select * from sqlite_master')
#print(cur.fetchall())

db.commit()

db.close()






