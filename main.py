from telegram.botcommand import BotCommand
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.files.file import File

from functions import db_connect, invalid_qn_number, invalid_title, invalid_typing_in_answers, invalid_typing_in_questions, show_answers, start_command, creating_form, cancel_command, no_of_questions, questions_started, answering, title_of_form, view_forms

from telegram import Bot, Update

import sqlite3

import logging

logging.basicConfig(filename="logs.log",
    filemode="w", 
    format= '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
    level=logging.INFO)

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
            insert into bot_data values(0)
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
        user_id int references user_table(user_id),
        name text,
        form_id int references form_table(form_id),
        answers text not null
        );''')
        
    db.commit()
    db.close()

def main():
    db_intialize(db_connect())
    api_token = "1869792637:AAETw6wyWCNr68OMuUxgkhwMpp-m0dQMoSI"
    updater = Updater(api_token)
    
    d = updater.dispatcher

    d.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            1 : [MessageHandler(Filters.text, answering)]
        },
        fallbacks=[MessageHandler(Filters.all,invalid_typing_in_answers)]
    ))

    d.add_handler(CommandHandler("view_forms", view_forms))
    d.add_handler(ConversationHandler(
        entry_points=[(CommandHandler("create", creating_form))],
        states={
            1 : [MessageHandler(Filters.text & ~Filters.regex("Cancel"), title_of_form),MessageHandler(Filters.all & ~Filters.regex("Cancel"),invalid_title)],
            2: [MessageHandler(Filters.regex('[0-9]'), no_of_questions), MessageHandler(Filters.all &~Filters.regex("Cancel"),invalid_qn_number)],
            3 : [MessageHandler(Filters.text & ~Filters.regex("Cancel"), questions_started),MessageHandler(Filters.all & ~Filters.regex("Cancel"),invalid_typing_in_questions)]
        },
        fallbacks= [MessageHandler(Filters.regex("Cancel"),cancel_command)]
    ))

    d.add_handler(CommandHandler("answers",show_answers))
    updater.bot.set_my_commands(
        [
        BotCommand("start","Start Me"),
        BotCommand("create","Form Creation"),
        BotCommand("view_forms", "Your Forms"),
        BotCommand("answers", "Answers for your Forms"),
        ]
    )
    updater.start_polling()

    updater.idle()

    

if __name__ == '__main__':
    main()
