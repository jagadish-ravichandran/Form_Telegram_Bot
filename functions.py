from sqlite3.dbapi2 import Cursor
from telegram.ext import ConversationHandler, CallbackContext
import sqlite3
from telegram import Update, user
import logging
import csv
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

cancel_button = [["Cancel"]]
cancel_markup = ReplyKeyboardMarkup(cancel_button, one_time_keyboard= False)

def show_table(db : sqlite3.Connection, name : str):
    print(db.execute(f"select * from {name}").fetchall())

def db_connect():
    db_con = sqlite3.connect('form_bot_db')
    return db_con

def invalid_qn_number(update : Update,context : CallbackContext):
    update.effective_message.reply_text("Invalid entry !\nEnter number (1-10) : ")
    return 2

def invalid_typing_in_answers(update : Update,context: CallbackContext):
    update.effective_message.reply_text("Invalid answer! Please enter valid text")
    return 1

def invalid_typing_in_questions(update : Update,context: CallbackContext):
    update.effective_message.reply_text("Invalid question! Please enter valid text")
    return 3

def invalid_title(update : Update,context : CallbackContext):
    update.effective_message.reply_text("Invalid title! Please enter valid text")
    return 1

def beginning(update: Update, context : CallbackContext):
    update.effective_message.reply_text("I m here for creating forms")
    update.effective_message.reply_text("Type /create to start creating")
    return ConversationHandler.END

def start_command(update : Update, context : CallbackContext):
    db = db_connect()
    cur = db.cursor()
    userid = int(update.effective_user.id)
    
   
    cur = db.execute(f'select * from user_table where user_id={userid}')
    if len(cur.fetchall()) == 0:
        cur = db.execute(f'insert into user_table values({userid},0)')
        db.commit()
        db.close()

    if not context.args:
        return beginning(update, context)

    else:
        ownerid, formid = list(map(int, context.args[0].split("_")))
        current_form = extract_form(formid,ownerid)

        if current_form is None:
            db.close()
            return beginning(update, context)

        cur = db.execute(f"select distinct form_id from answer_table where user_id={userid} and form_id = {formid}")
        if cur.fetchone():
            update.effective_message.reply_text("You answered this form already !")
            db.close()
            return beginning(update, context)

        context.user_data['form'] = current_form
        context.user_data['answers'] = []
        context.user_data['qns_to_answer'] = current_form[0][0]
        update.effective_message.reply_text(f"Form title : {current_form[0][2]}")
        update.effective_message.reply_text("Answer one by one for the following questions : ")
        context.user_data["answer_count"] = 0
        update.effective_message.reply_text(f"1. {current_form[0][4]}")
        return 1

def creating_form(update : Update, context : CallbackContext):
    update.effective_message.reply_text("Lets create forms !")
    update.effective_message.reply_text("Enter the title for your form : ", reply_markup=cancel_markup)
    return 1


def title_of_form(update : Update, context : CallbackContext):
    title = update.message.text
    context.user_data['title'] = title
    update.effective_message.reply_text("Enter no. of questions do you want to add (limit 10)")
    return 2


def storing_answers(update : Update, context : CallbackContext):
    db = db_connect()
    cur = db.cursor()
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    form_id = context.user_data["form"][0][1]
    answers = context.user_data["answers"]
    count = context.user_data["answer_count"]
    for i in range(count):
        db.execute("insert into answer_table values(?,?,?,?)",(user_id,name,form_id,answers[i]))
    db.commit()
    db.close()


def answering(update : Update, context : CallbackContext):
    
    current_form = context.user_data["form"]
    qcount = context.user_data["qns_to_answer"]
    answers = context.user_data["answers"]
    ans_count = context.user_data["answer_count"]

    if qcount-1 == ans_count:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_text = "Your answers are : \n"
        for i in answers:
            ans_text = ans_text + f"{(answers.index(i)+1)}. {i}\n"
        update.effective_message.reply_text(ans_text)
        storing_answers(update, context)
        update.effective_message.reply_text("Your answeres are saved ! \nThank You! ")
        return beginning(update, context)

    else:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_count = context.user_data["answer_count"]
        next_question = current_form[ans_count][4]
        update.effective_message.reply_text(f"{ans_count+1}. {next_question}")
        return 1


def no_of_questions(update : Update, context : CallbackContext):
    question_count = int(update.message.text)
    
    if not 0 < question_count <= 10:
        update.effective_message.reply_text("Invalid entry !\nEnter number (0-10) : ")
        return 2
    context.user_data['question_count'] = question_count
    context.user_data['current_question'] = 1
    context.user_data['questions'] = []
    update.effective_message.reply_text("Enter questions line by line : ")
    update.effective_message.reply_text(f"Enter your question number {context.user_data['current_question']}")
    return 3


def questions_started(update : Update, context : CallbackContext):
    question = update.effective_message.text
    context.user_data['questions'].append(question)
    #logging.info(context.user_data)


    if context.user_data['current_question'] == context.user_data['question_count']:
        update.effective_message.reply_text("Your questions are saved successfully")
    
    else:
        context.user_data['current_question'] += 1
        update.effective_message.reply_text(f"Enter your question number {context.user_data['current_question']}")
        return 3

    userid = update.effective_user.id
    db = db_connect()

    # increasing user form count
    cur = db.execute(f"select form_count from user_table where user_id = {userid}")
    
    user_form_count = cur.fetchone()[0]
    user_form_count += 1
    
    cur = db.execute(f"update user_table set form_count = {user_form_count} where user_id = {userid}")
    
    # increasing total form count
    cur = db.execute("select total_forms from bot_data")

    total_forms = cur.fetchone()[0]

    total_forms += 1

    cur = db.execute(f"update bot_data set total_forms = {total_forms}")

    #generating form id and inserting to form table
    
    title = context.user_data['title']
    qcount = context.user_data['question_count']
    ft_record = (total_forms,title,userid,qcount)
    cur = db.execute("insert into form_table values (?,?,?,?)",ft_record)

    #show_table(db, "form_table")

    #inserting questions to question table
    for i in range(1,qcount+1):
        question_desc = context.user_data['questions'][i-1]
        qt_record = (total_forms,title,i,question_desc)
        cur = db.execute('insert into question_table values(?, ?, ?,?)',qt_record)
    
    db.commit()
    
    # displaying the last generated form
    last_form = extract_form(total_forms, userid)
    context.user_data["last_form"] = user_form_count
    displaying_each_form(update, context, last_form)
    db.close()

    return ConversationHandler.END

def extract_form(formid, userid) -> list:
    db = db_connect()
    cur = db.cursor()
    if formid is None:
        cur = db.execute(f"select ft.question_count, qt.* from question_table qt,form_table ft where ft.user_id = {userid} and qt.form_id = ft.form_id")
    
    else:
        cur = db.execute(f"select ft.question_count, qt.* from question_table qt, form_table ft where ft.user_id={userid} and ft.form_id = {formid} and qt.form_id = {formid}")
    #cur = db.execute("select * from question table where form_")
    result = cur.fetchall()
    db.close()
    return result

def displaying_each_form(update : Update, context : CallbackContext, flist : list) -> str:
    tracker = 1 
    if (context.user_data.get("last_form",None)):
        tracker = context.user_data["last_form"]
    title = ""
    id = 0
    questions = []
    for i in flist:
        if title == "":
            title += i[2]
            id = i[1]
        
        if i[2] == title:
            questions.append(i[4])

        if len(questions) == i[0]:
            #form_dict[title] = questions
            complete_form_text = f"Form {tracker} : \n\n"
            complete_form_text += f"Title : {title}\n"
            complete_form_text += f"Questions : \n"
            for j in questions:
                complete_form_text += f"{questions.index(j)+1}. {j}\n"
            form_link = f"https://t.me/{context.bot.username}?start={update.effective_user.id}_{id}"
            complete_form_text +=  form_link
            update.effective_message.reply_text(complete_form_text)
            title = ""
            questions = []
            tracker +=1
    
def view_forms(update : Update, context : CallbackContext):
    userid = update.effective_user.id
    flist = extract_form(formid= None, userid= userid)
    displaying_each_form(update, context, flist)


def show_answers(update : Update, context : CallbackContext):
    userid = update.effective_user.id
    #flist = extract_form(formid= None, userid= userid)
    #displaying_each_form(update, context, flist)
    creating_csv_for_answers_for_all_forms(update, context, userid)


def creating_csv_for_each_form(form_records, userid):
    db = db_connect()
    cur = db.cursor()
    qcount = form_records[0]
    formid = form_records[1]
    ans_dict = {}
    cur = db.execute(f"select name,answers from answer_table where form_id={formid}")
    ans_list = cur.fetchall()
 
    if ans_list == []:
        return None
    tracker = 0
    for j in ans_list:
        if tracker == qcount:
            tracker = 0 
        if tracker == 0:
            ans_dict[j[0]] = []
        ans_dict[j[0]].append(j[1])
        tracker+=1
    
    filename = f"csv_files/answers_{userid}:{formid}.csv"
    
    cur = db.execute(f"select question_id, question_desc from question_table,user_table ft where form_id = {formid} and ft.user_id = {userid}")
    qn = cur.fetchall()

    with open(file=filename,mode="w") as f:

        csv_writer = csv.writer(f, delimiter=",")
        
        qlist = ["User"]
        for i in qn:
            qlist.append(f"{i[0]}. {i[1]}")
        csv_writer.writerow (qlist)
        
        for k,v in ans_dict.items():    
            v.insert(0,k)
            csv_writer.writerow(v)

    return filename

def creating_csv_for_answers_for_all_forms(update : Update, context : CallbackContext, userid):
    db = db_connect()
    cur = db.cursor()

    ## extracting the form id for a given user id
    cur = db.execute(f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid}")
    anslist = cur.fetchall()
    #db.close()
    for i in anslist:
        csv_file = creating_csv_for_each_form(i, userid)
        if csv_file is None:
            continue
        caption_text = f"Total questions : {i[0]}\n"
        cur = db.execute(f"select count(distinct user_id) from answer_table where form_id={i[1]}")
        user_count = cur.fetchone()[0]
        caption_text += f"Total users answered : {user_count}"
        update.effective_message.reply_document(document = open(file=csv_file,mode="r"), filename = f"{i[2]}-Answers", caption=caption_text)

        os.remove(csv_file)


def cancel_command(update : Update, context : CallbackContext):
   update.effective_message.reply_text("Your current operation is cancelled")
   return beginning(update, context)

