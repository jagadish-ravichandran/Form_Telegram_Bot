from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

from functions import db_connect, start_command, creating_form, cancel_command, no_of_questions, questions_started, answering, title_of_form

from telegram import Bot

import sqlite3



def db_intialize(db : sqlite3.Connection):
    cur = db.cursor()
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
    api_token = "1869792637:AAHepJn192WKZdpTFC3vOcYZn86nZGsD6iw"
    updater = Updater(api_token, use_context=True)
    
    d = updater.dispatcher
    #d.add_handler(CommandHandler("start", start_command))
    d.add_handler(ConversationHandler(
        entry_points=[(CommandHandler("start", start_command))],
        states={
            0 : [(CommandHandler("create", creating_form))],
            4 : [MessageHandler(Filters.text, title_of_form)],
            1: [MessageHandler(Filters.regex('[0-9]'), no_of_questions)],
            2 : [MessageHandler(Filters.text, questions_started)],
            3 : [MessageHandler(Filters.text, answering)]
        },
        fallbacks= [CommandHandler("cancel",cancel_command)]   
    ))
    
    updater.start_polling()

    

if __name__ == '__main__':
    main()
