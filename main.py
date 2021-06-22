from telegram.botcommand import BotCommand
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from telegram.ext.callbackcontext import CallbackContext
from telegram.files.file import File

from bot_functions import (
    help_command,
    invalid_qn_number,
    invalid_title,
    invalid_typing_in_answers,
    invalid_typing_in_questions,
    show_answers,
    start_command,
    creating_form,
    cancel_command,
    no_of_questions,
    questions_started,
    answering,
    title_of_form,
    typing_commands_in_CH,
    unknown_commands,
    unknown_messages,
    view_forms,
    answer_query,
    answer_ck,
)

from db_functions import db_connect

from telegram import Bot, Update

import sqlite3

import logging

from variables import database, api_token

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


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


def main():
    db_intialize(db_connect())

    updater = Updater(api_token)

    d = updater.dispatcher

    d.add_handler(
        ConversationHandler(
            entry_points=[
                (CommandHandler("create", creating_form)),
                CommandHandler("start", start_command),
            ],
            states={
                0: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(Filters.text, answering),
                    MessageHandler(Filters.all, invalid_typing_in_answers),
                ],
                1: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(
                        Filters.text & ~Filters.regex("Cancel"), title_of_form
                    ),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"), invalid_title
                    ),
                ],
                2: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(Filters.regex("[0-9]"), no_of_questions),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"), invalid_qn_number
                    ),
                ],
                3: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(
                        Filters.text & ~Filters.regex("Cancel"), questions_started
                    ),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"),
                        invalid_typing_in_questions,
                    ),
                ],
            },
            fallbacks=[MessageHandler(Filters.regex("Cancel"), cancel_command)],
        )
    )

    d.add_handler(CommandHandler("view_forms", view_forms))
    d.add_handler(CommandHandler("answers", answer_ck))
    d.add_handler(CallbackQueryHandler(answer_query))
    d.add_handler(CommandHandler("help", help_command))
    d.add_handler(MessageHandler(Filters.command, unknown_commands))
    d.add_handler(MessageHandler(Filters.all, unknown_messages))

    updater.bot.set_my_commands(
        [
            BotCommand("start", "Start Me"),
            BotCommand("create", "Form Creation"),
            BotCommand("view_forms", "Your Forms"),
            BotCommand("answers", "Answers for your Forms"),
            BotCommand("help", "Available commands"),
        ]
    )
    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
