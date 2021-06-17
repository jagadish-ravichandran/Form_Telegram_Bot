import sqlite3

db = sqlite3.connect("form_bot_db")

#print(type(con))
#con.close()
#exit()
cur = db.cursor()
form_id = 4
user_id= 576048895

#cur = db.execute("select * from question_table")
cur = db.execute(f"select qt.* from question_table qt, form_table ft where ft.user_id={user_id} and ft.form_id = {form_id} and qt.form_id = {form_id}")

#cur.execute("select * from dummy")
#cur.execute('select * from sqlite_master')
print(cur.fetchall())

#db.commit()

db.close()






