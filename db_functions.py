import csv
import logging
import sqlite3

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


def title_check_db(user_id, title):
    db = db_connect()
    cur = db.cursor()
    cur = db.execute(f"select form_id,form_title from form_table where user_id={user_id}")
    tl_list = cur.fetchall()
    for i in tl_list:
        if title == i[1]:
            return i
    return []

def answer_check_db(form_id):
    
    pass

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


def creating_csv_for_each_form(form_records, userid):
    db = db_connect()
    cur = db.cursor()
    qcount = form_records[0]
    formid = form_records[1]
    ans_dict = {}
    cur = db.execute(f"select name,answers from answer_table where form_id={formid}")
    ans_list = cur.fetchall()

    if ans_list == []:
        return (None, None)
    tracker = 0
    for j in ans_list:
        if tracker == qcount:
            tracker = 0
        if tracker == 0:
            ans_dict[j[0]] = []
        ans_dict[j[0]].append(j[1])
        tracker += 1

    filename = f"csv_files/answers_{userid}:{formid}.csv"

    cur = db.execute(
        f"select question_id, question_desc from question_table,user_table ft where form_id = {formid} and ft.user_id = {userid}"
    )
    qn = cur.fetchall()

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

    return (filename, total_tab)

