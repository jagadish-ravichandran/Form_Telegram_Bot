import sqlite3

con = sqlite3.connect("testing_db")

#print(type(con))
#con.close()
#exit()
cur = con.cursor()

cur = con.execute('''create table if not exists user_table (
    user_id int primary key, 
    form_count int not null
    );''')

cur = con.execute('''create table if not exists form_table (
    form_id int primary key, 
    form_title text not null, 
    user_id int references user_table(user_id), question_count int
    );''')

cur = con.execute('''create table if not exists question_table (
    form_id int references form_table(form_id), 
    title text references form_table(form_title), 
    question_id int not null, 
    question_desc text not null
    );''')

cur = con.execute('''create table if not exists answer_table (
    user_id int references form_table(user_id), 
    form_id int references form_table(form_id),
    answers text not null
    );''')



#cur.execute("create table if not exists dummy (name text, id int) ")
#v = "hai1"
#cur.execute("insert into dummy values(?,?)",(v,2000))

#cur.execute("select * from dummy")
#cur.execute('select * from sqlite_master')
#print(cur.fetchall())

con.commit()

con.close()






