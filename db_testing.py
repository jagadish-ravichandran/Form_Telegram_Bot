import sqlite3
import csv

from tabulate import tabulate


def show_output(cur):
    print(cur.fetchall())

db = sqlite3.connect("form_bot_db")

#print(type(con))
#con.close()
#exit()
cur = db.cursor()
formid = 3
userid= 576048895

#cur = db.execute("select * from question_table")
#cur.execute("select * from dummy")
#cur.execute('select * from sqlite_master')
#cur = db.execute(f"select ft.question_count, qt.* from question_table qt,form_table ft where ft.user_id = {userid} and qt.form_id = ft.form_id")
#cur = db.execute(f"select * from form_table")

cur = db.execute(
            f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid} and ft.form_id = {formid}"
        )
flist = cur.fetchall()
'''
for i in flist:
    qcount = i[0]
    formid = i[1]
    ans_dict = {}
    cur = db.execute(f"select name,answers from answer_table where form_id={formid}")
    ans_list = cur.fetchall()
    if ans_list == []:
        continue
    #print(ans_list)
    tracker = 0
    for j in ans_list:
        if tracker == qcount:
            tracker = 0 
        if tracker == 0:
            ans_dict[j[0]] = []
        ans_dict[j[0]].append(j[1])
        tracker+=1
    
    cur = db.execute(f"select question_id, question_desc from question_table,user_table ft where form_id = {formid} and ft.user_id = {userid}")
    qn = cur.fetchall()
    
    f = open(f"csv_files/answers_{userid}:{formid}.csv",mode="w")

    csv_writer = csv.writer(f, delimiter=",")
    
    qlist = ["User"]
    for i in qn:
        qlist.append(f"{i[0]}. {i[1]}")
    

    total_tab = []
    total_tab.append(qlist)
    
    csv_writer.writerow (qlist)
    
    for k,v in ans_dict.items():    
        v.insert(0,k)
        csv_writer.writerow(v)
        total_tab.append(v)

    tb = tabulate(total_tab, tablefmt="grid")
    print(type(tb))
    f.close()



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
'''

cur = db.execute("select ")
db.close()






