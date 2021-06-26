import csv
import logging
from os import stat
import sqlite3
from variables import database

from telegram import user

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def show_table(db: sqlite3.Connection, name: str):
    print(db.execute(f"select * from {name}").fetchall())


def db_connect():
    db_con = sqlite3.connect("form_bot_db")
    return db_con

def db_intialize(db: sqlite3.Connection):
    cur = db.cursor()

    cur = db.execute(database.bot_data)

    cur = db.execute("select * from bot_data")

    if len(cur.fetchall()) == 0:
        cur = db.execute(
            """
            insert into bot_data values(0)
        """
        )
    tables = database.get_tables()
    for i in tables:
        db.execute(i)
    db.commit()
    db.close()



class User: ## Operations done in user_table

    ##adding user
    @staticmethod
    def add_user(userid):
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(f"select * from user_table where user_id={userid}")

        if len(cur.fetchall()) == 0:
            cur = db.execute(f"insert into user_table values({userid},0)")
            db.commit()
        
        db.close()


    ### checking whether the user already answered the form
    @staticmethod
    def is_answered(userid, formid):
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(
                f"select distinct form_id from answer_table where user_id={userid} and form_id = {formid}"
            )
        result = cur.fetchone()
        db.close()
        return result


    ### increasing user form count
    @staticmethod
    def increase_form_count(userid):
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(f"select form_count from user_table where user_id = {userid}")
        user_form_count = cur.fetchone()[0]
        user_form_count += 1

        cur = db.execute(
            f"update user_table set form_count = {user_form_count} where user_id = {userid}"
        )
        db.commit()
        db.close()
        return user_form_count

    ### retrieving all forms created by user (or specific form)
    @staticmethod
    def forms_created(formid, userid):
        db = db_connect()
        cur = db.cursor()
        if formid == None:
            cur = db.execute(
            f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid}"
        )
        else:
            cur = db.execute(
                f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid} and ft.form_id = {formid}"
            )

        form_list = cur.fetchall()
        db.close()
        return form_list



class Bot:  ## Operations done in bot_data table

    ## increasing total form count
    @staticmethod
    def increase_form_count():
        db = db_connect()
        cur = db.cursor()
        cur = db.execute("select total_forms from bot_data")
        total_forms = cur.fetchone()[0]
        total_forms += 1
        cur = db.execute(f"update bot_data set total_forms = {total_forms}")
        db.commit()
        db.close()
        return total_forms


class Form: ##Operations done in form_table

    @staticmethod
    def insert_values(ft_record):
        db = db_connect()
        db.execute("insert into form_table values (?,?,?,?)", ft_record)
        db.commit()
        db.close()

    ## get form id for forms created by specific user
    @staticmethod
    def get_formid(userid):
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(f"select form_id from form_table where user_id = {userid}")
        result = cur.fetchall()
        db.close()
        return result




class Questions:

    @staticmethod
    def insert_values(qt_record):
        db = db_connect()
        db.execute("insert into question_table values(?, ?, ?,?)", qt_record)
        db.commit()
        db.close()

    @staticmethod
    def get_questions(formid, userid):
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(
        f"select question_id, question_desc from question_table,user_table ft where form_id = {formid} and ft.user_id = {userid}"
        )
        qn = cur.fetchall()
        db.close()
        return qn


class Answers: ## Operations done in answer_table

    @staticmethod
    def storing_answers(at_record):
        db = db_connect()
        db.execute("insert into answer_table values(?,?,?,?)",at_record)
        db.commit()
        db.close()

    ##obtaining total users answered for specific form id
    @staticmethod
    def user_count(formid): 
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(
            f"select count(distinct user_id) from answer_table where form_id={formid}"
        ) 
        user_count = cur.fetchone()[0]
        db.close()
        return user_count

    ## obtaining names and answers for specific form id
    @staticmethod
    def get_answers(formid):
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(f"select name,answers from answer_table where form_id={formid}")
        ans_list = cur.fetchall()
        return ans_list


### checking repeated title for an user
def title_check_db(user_id, title):
    db = db_connect()
    cur = db.cursor()
    cur = db.execute(f"select form_id,form_title from form_table where user_id={user_id}")
    tl_list = cur.fetchall()
    for i in tl_list:
        if title == i[1]:
            return i
    return []


### retrieving titles of all forms along with form_id
def title_extraction(user_id):
    db = db_connect()
    cur = db.cursor()
    cur = db.execute(f"select form_id, form_title from form_table where user_id={user_id}")
    return cur.fetchall()


### extracting questions for a given user_id (and form_id if any)
def extract_form(formid, userid) -> list:
    db = db_connect()
    cur = db.cursor()
    if formid is None:
        cur = db.execute(
            f"select ft.question_count, qt.* from question_table qt,form_table ft where ft.user_id = {userid} and qt.form_id = ft.form_id"
        )

    else:
        cur = db.execute(
            f"select ft.question_count, qt.* from question_table qt, form_table ft where ft.user_id={userid} and ft.form_id = {formid} and qt.form_id = {formid}"
        )

    result = cur.fetchall()
    db.close()
    return result


### create csv for answer for a single form and return filename if any
def creating_csv_for_each_form(form_records, userid):

    qcount = form_records[0]
    formid = form_records[1]
    ans_dict = {}
    
    ans_list = Answers.get_answers(formid)
    if ans_list == []:
        return (None, None) ## indicating no answers for given id

    tracker = 0
    for j in ans_list:
        if tracker == qcount:
            tracker = 0
        if tracker == 0:
            ans_dict[j[0]] = []
        ans_dict[j[0]].append(j[1])
        tracker += 1

    filename = f"csv_files/answers_{userid}:{formid}.csv"

    qn = Questions.get_questions(formid, userid)

    ## creating unique csv file for answers
    with open(file=filename, mode="w") as f:

        csv_writer = csv.writer(f, delimiter=",")
        total_tab = []
        qlist = ["User"]
        for i in qn:
            qlist.append(f"{i[0]}. {i[1]}")
        csv_writer.writerow(qlist)

        total_tab.append(qlist[0:3])
        for k, v in ans_dict.items():
            v.insert(0, k)
            if len(total_tab) <= 4:
                total_tab.append(v)
            csv_writer.writerow(v)

    return (filename, total_tab) ## returning filename and preview text

