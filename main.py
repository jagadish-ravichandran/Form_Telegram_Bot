from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

from functions import db_connect, start_command, creating_form, cancel_command, no_of_questions, questions_started, answering, title_of_form

from telegram import Bot

import sqlite3

import logging

logging.basicConfig(filename="logs.log",
    filemode="w", 
    format= '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

def db_intialize(db : sqlite3.Connection):
    cur = db.cursor()
    
    cur = db.execute('''
        create table if not exists bot_data (
            total_forms int
        )
    ''')

    cur = db.execute("select * from bot_data")

    if len(cur.fetchall()) == 0:
        cur = db.execute('''
            insert into bot_data (0)
        ''')
    
    cur = db.execute('''create table if not exists user_table (
    user_id int primary key, 
    form_count int not null
    );''')

    cur = db.execute('''create table if not exists form_table (
        form_id int primary key, 
        form_title text not null, 
        user_id int references user_table(user_id), question_count int
        );''')

    cur = db.execute('''create table if not exists question_table (
        form_id int references form_table(form_id), 
        title text references form_table(form_title), 
        question_id int not null, 
        question_desc text not null
        );''')

    cur = db.execute('''create table if not exists answer_table (
        user_id int references form_table(user_id), 
        form_id int references form_table(form_id),
        answers text not null
        );''')
        
    db.commit()
    db.close()

def main():
    db_intialize(db_connect())
    api_token = "1869792637:AAETw6wyWCNr68OMuUxgkhwMpp-m0dQMoSI"
    updater = Updater(api_token, use_context=True)
    
    d = updater.dispatcher
    #d.add_handler(CommandHandler("start", start_command))
    d.add_handler(ConversationHandler(
        entry_points=[(CommandHandler("start", start_command))],
        states={
            0 : [(CommandHandler("create", creating_form))],
            1 : [MessageHandler(Filters.text, title_of_form)],
            2: [MessageHandler(Filters.regex('[0-9]'), no_of_questions)],
            3 : [MessageHandler(Filters.text, questions_started)],
            4 : [MessageHandler(Filters.text, answering)]
        },
        fallbacks= [MessageHandler(Filters.regex("Cancel"),cancel_command)]   
    ))
    
    updater.start_polling()

    updater.idle()

    

if __name__ == '__main__':
    main()
