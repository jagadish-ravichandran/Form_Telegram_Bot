import sqlite3

db = sqlite3.connect("form_bot_db")

#print(type(con))
#con.close()
#exit()
cur = db.cursor()
#formid = 3
userid= 576048895

#cur = db.execute("select * from question_table")
#cur = db.execute(f"select ft.question_count, qt.* from question_table qt, form_table ft where ft.user_id={user_id} and qt.form_id = ft.form_id")

#cur.execute("select * from dummy")
#cur.execute('select * from sqlite_master')
#cur = db.execute(f"select ft.question_count, qt.* from question_table qt,form_table ft where ft.user_id = {userid} and qt.form_id = ft.form_id")
cur = db.execute(f"select distinct form_id from answer_table where user_id={userid}")

flist = cur.fetchall()[0][0]
print(flist)
db.close()
exit()

form_dict = {}
title = ""
questions = []
for i in flist:
    if title == "":
        title += i[2]
    
    if i[2] == title:
        questions.append(i[4])

    if len(questions) == i[0]:
        form_dict[title] = questions        
        title = ""
        questions = []
#db.commit()

print(form_dict)

db.close()






