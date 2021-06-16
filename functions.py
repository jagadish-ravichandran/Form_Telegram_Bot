from telegram.ext import ConversationHandler, CallbackContext
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, ReplyMarkup
import logging
from logging import FileHandler
import random

form_id = 1

def show_table(db : sqlite3.Connection, name : str):
    print(db.execute(f"select * from {name}").fetchall())

def db_connect():
    db_con = sqlite3.connect('form_bot_db')
    return db_con

def start_command(update : Update, context : CallbackContext):
    db = db_connect()
    cur = db.cursor()
    userid = int(update.effective_user.id)
    

    if not context.args:
        cur = db.execute(f'select * from user_table where user_id={userid}')
        if len(cur.fetchall()) == 0:
            cur = db.execute(f'insert into user_table values({userid},0)')
            db.commit()
            db.close()
        update.effective_message.reply_text("I m here for creating forms")
        update.effective_message.reply_text("Type /create to start creating")
        return 0

    else:
        '''
        with open("sample.json", "r") as f:
            data = json.load(f)

        if update.message.chat_id in data[context.args[0]]['answered']:
            context.bot.send_message(chat_id=update.message.chat_id, text="You have answered this form already !")
            return ConversationHandler.END

        else:
            data[context.args[0]]['answered'].append(update.message.chat_id)
        
            with open("sample.json", "w") as f1:
                json.dump(data,f1)

            context.bot.send_message(
                chat_id=update.message.chat_id, text=f"Title of the form : {data[context.args[0]]['title']}")
            
            context.bot.send_message(
                    chat_id=update.message.chat_id, text= "Answers questions one by one !")

            return 3
        '''


def creating_form(update : Update, context : CallbackContext):
    update.effective_message.reply_text("Lets create forms !")
    update.effective_message.reply_text("Enter the title for your form : ")
    return 1


def title_of_form(update : Update, context : CallbackContext):
    title = update.message.text
    context.user_data['title'] = title
    update.effective_message.reply_text("Enter no. of questions do you want to add")
    return 2


def answering(update : Update, context : CallbackContext):

    answered = update.message.text
    #context.user_data['question1_answer'] = answered
    context.bot.send_message(
        chat_id=update.message.chat_id, text= "Your answer is received")
    context.user_data['question1'] = True
    a = context.user_data['question1_id']
    form_owner = a[:a.find('_')]
    context.bot.send_message(
        chat_id=int(form_owner), text=f"Answer received\n{answered}")
    return ConversationHandler.END
    

def no_of_questions(update : Update, context : CallbackContext):
   
    question_count = int(update.message.text)

    context.user_data['question_count'] = question_count
    context.user_data['current_question'] = 1
    context.user_data['questions'] = []
    update.effective_message.reply_text("Enter questions line by line : ")
    update.effective_message.reply_text(f"Enter your question number {context.user_data['current_question']}")
    
    return 3


def questions_started(update : Update, context : CallbackContext):
    question = update.effective_message.text
    context.user_data['questions'].append(question)
    logging.info(context.user_data)


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
    
    cur = db.execute(f"update user_table set form_count = {user_form_count+1} where user_id = {userid}")
    
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

    #show_table(db, "question_table")
    db.commit()
    db.close()


    return ConversationHandler.END

def display_form(formid, userid) -> list:
    db = db_connect()
    cur = db.execute("select ")
    


def cancel_command(update : Update, context : CallbackContext):
   update.effective_message.reply_text("Your current operation is cancelled")

