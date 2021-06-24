from constants import CreationState
from answer_functions import answer_ck, answer_query
from form_functions import view_forms_ck, view_query
from bot_functions import (
    answering,
    cancel_command,
    creating_form,
    help_command,
    invalid_qn_number,
    invalid_title,
    invalid_typing_in_answers,
    invalid_typing_in_questions,
    no_of_questions,
    questions_started,
    start_command,
    title_of_form,
    typing_commands_in_CH,
    unknown_commands,
    unknown_messages,
)
import logging
import sqlite3

from telegram import Bot, Update
from telegram.botcommand import BotCommand
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.ext.callbackcontext import CallbackContext
from telegram.files.file import File

from db_functions import db_connect
from variables import api_token, database

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

    logging.info("\n------LOGGING STARTED-----\n")

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
                CreationState.RECIEVING_ANSWERS: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(Filters.text, answering),
                    MessageHandler(Filters.all, invalid_typing_in_answers),
                ],
                CreationState.RECIEVING_TITLE: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(
                        Filters.text & ~Filters.regex("Cancel"), title_of_form
                    ),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"), invalid_title
                    ),
                ],
                CreationState.RECIEVING_QUESTION_COUNT: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(Filters.regex("[0-9]"), no_of_questions),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"), invalid_qn_number
                    ),
                ],
                CreationState.RECIEVING_QUESTIONS: [
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

    d.add_handler(CommandHandler("view_forms", view_forms_ck))
    d.add_handler(CallbackQueryHandler(pattern = "^view_*",callback = view_query))

    d.add_handler(CommandHandler("answers", answer_ck))
    d.add_handler(CallbackQueryHandler(pattern = "^answer_*",callback = answer_query))

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
