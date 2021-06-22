from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update
import logging
import os
from tabulate import tabulate
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from db_functions import (
    db_connect,
    title_check_db,
    extract_form,
    creating_csv_for_each_form,
)

cancel_button = [["Cancel"]]
cancel_markup = ReplyKeyboardMarkup(
    cancel_button, one_time_keyboard=False, resize_keyboard=True
)

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def invalid_typing_in_answers(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid answer! Please enter valid text")
    return 0


def invalid_title(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid title! Please enter valid text")
    return 1


def invalid_qn_number(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid entry !\nEnter number (1-10) : ")
    return 2


def invalid_typing_in_questions(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid question! Please enter valid text")
    return 3


def typing_commands_in_CH(update: Update, context: CallbackContext):
    command = update.effective_message.text[: update.message.entities[0].length]
    update.effective_message.reply_text(
        f"Your current process is cancelled !\nPlease enter the command again {command}",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def beginning(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "I m here for creating forms", reply_markup=ReplyKeyboardRemove()
    )
    update.effective_message.reply_text("Type /create to start creating")
    return ConversationHandler.END


def start_command(update: Update, context: CallbackContext):
    db = db_connect()
    cur = db.cursor()
    userid = int(update.effective_user.id)

    cur = db.execute(f"select * from user_table where user_id={userid}")
    if len(cur.fetchall()) == 0:
        cur = db.execute(f"insert into user_table values({userid},0)")
        db.commit()
        db.close()

    if not context.args:
        return beginning(update, context)

    else:
        ownerid, formid = list(map(int, context.args[0].split("_")))
        current_form = extract_form(formid, ownerid)

        if current_form is None:
            db.close()
            return beginning(update, context)

        cur = db.execute(
            f"select distinct form_id from answer_table where user_id={userid} and form_id = {formid}"
        )
        if cur.fetchone():
            update.effective_message.reply_text("You answered this form already !")
            db.close()
            return beginning(update, context)

        context.user_data["form"] = current_form
        context.user_data["answers"] = []
        context.user_data["qns_to_answer"] = current_form[0][0]
        update.effective_message.reply_text(
            f"Form title : {current_form[0][2]}\nTotal questions : {current_form[0][0]}\n\nAnswer one by one for the following questions : "
        )
        context.user_data["answer_count"] = 0
        update.effective_message.reply_text(
            f"1. {current_form[0][4]}", reply_markup=cancel_markup
        )
        return 0


def creating_form(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Lets create forms !")
    update.effective_message.reply_text(
        "Enter the title for your form : ", reply_markup=cancel_markup
    )
    return 1


def title_of_form(update: Update, context: CallbackContext):
    title = update.message.text
    userid = int(update.effective_user.id)
    tl_ck = title_check_db(userid, title)

    if tl_ck:
        update.effective_message.reply_text(
            "The form title is already entered!\nPlease enter other title: "
        )
        return 1

    context.user_data["title"] = title
    update.effective_message.reply_text(
        "Enter no. of questions do you want to add (limit 10)"
    )
    return 2


def storing_answers(update: Update, context: CallbackContext):
    db = db_connect()
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    form_id = context.user_data["form"][0][1]
    answers = context.user_data["answers"]
    count = context.user_data["answer_count"]
    for i in range(count):
        db.execute(
            "insert into answer_table values(?,?,?,?)",
            (user_id, name, form_id, answers[i]),
        )
    db.commit()
    db.close()


def answering(update: Update, context: CallbackContext):
    if update.effective_message.text == "Cancel":
        return cancel_command(update, context)
    current_form = context.user_data["form"]
    qcount = context.user_data["qns_to_answer"]
    answers = context.user_data["answers"]
    ans_count = context.user_data["answer_count"]

    if qcount - 1 == ans_count:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_text = "Your answers are : \n"
        for i in answers:
            ans_text = ans_text + f"{(answers.index(i)+1)}. {i}\n"
        update.effective_message.reply_html(ans_text)
        storing_answers(update, context)
        update.effective_message.reply_text("Your answers are saved ! \nThank You! ")
        return beginning(update, context)

    else:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_count = context.user_data["answer_count"]
        next_question = current_form[ans_count][4]
        update.effective_message.reply_text(f"{ans_count+1}. {next_question}")
        return 0


def no_of_questions(update: Update, context: CallbackContext):
    question_count = int(update.message.text)

    if not 0 < question_count <= 10:
        update.effective_message.reply_text("Invalid entry !\nEnter number (1-10) : ")
        return 2
    context.user_data["question_count"] = question_count
    context.user_data["current_question"] = 1
    context.user_data["questions"] = []
    update.effective_message.reply_text("Enter questions line by line : ")
    update.effective_message.reply_text(
        f"Enter your question number {context.user_data['current_question']}"
    )
    return 3


def questions_started(update: Update, context: CallbackContext):
    question = update.effective_message.text
    context.user_data["questions"].append(question)
    # logging.info(context.user_data)

    if context.user_data["current_question"] == context.user_data["question_count"]:
        update.effective_message.reply_text(
            "Your questions are saved successfully", reply_markup=ReplyKeyboardRemove()
        )

    else:
        context.user_data["current_question"] += 1
        update.effective_message.reply_text(
            f"Enter your question number {context.user_data['current_question']}"
        )
        return 3

    userid = update.effective_user.id
    db = db_connect()

    # increasing user form count
    cur = db.execute(f"select form_count from user_table where user_id = {userid}")

    user_form_count = cur.fetchone()[0]
    user_form_count += 1

    cur = db.execute(
        f"update user_table set form_count = {user_form_count} where user_id = {userid}"
    )

    # increasing total form count
    cur = db.execute("select total_forms from bot_data")

    total_forms = cur.fetchone()[0]

    total_forms += 1

    cur = db.execute(f"update bot_data set total_forms = {total_forms}")

    # generating form id and inserting to form table

    title = context.user_data["title"]
    qcount = context.user_data["question_count"]
    ft_record = (total_forms, title, userid, qcount)
    cur = db.execute("insert into form_table values (?,?,?,?)", ft_record)

    # show_table(db, "form_table")

    # inserting questions to question table
    for i in range(1, qcount + 1):
        question_desc = context.user_data["questions"][i - 1]
        qt_record = (total_forms, title, i, question_desc)
        cur = db.execute("insert into question_table values(?, ?, ?,?)", qt_record)

    db.commit()

    # displaying the last generated form
    last_form = extract_form(total_forms, userid)
    context.user_data["last_form"] = user_form_count
    displaying_each_form(update, context, last_form)
    db.close()

    return ConversationHandler.END


def displaying_each_form(update: Update, context: CallbackContext, flist: list) -> str:
    tracker = 1
    if context.user_data.get("last_form", None):
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
            # form_dict[title] = questions
            complete_form_text = f"Form {tracker} : \n\n"
            complete_form_text += f"Title : {title}\n"
            complete_form_text += f"Questions : \n"
            for j in questions:
                complete_form_text += f"{questions.index(j)+1}. {j}\n"
            form_link = f"https://t.me/{context.bot.username}?start={update.effective_user.id}_{id}"
            complete_form_text += form_link
            update.effective_message.reply_text(complete_form_text)
            title = ""
            questions = []
            tracker += 1


def view_forms(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    flist = extract_form(formid=None, userid=userid)
    if flist == []:
        update.effective_message.reply_text(
            "No forms created !\nType /create to start creating forms"
        )
        return
    displaying_each_form(update, context, flist)


def show_answers(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    
    update.effective_message.reply_text("Preview and its csv file will be uploaded !")
    creating_csv_for_answers_for_all_forms(update, context, userid)


def creating_csv_for_answers_for_all_forms(
    update: Update, context: CallbackContext, userid
):
    db = db_connect()
    cur = db.cursor()

    ## extracting the form id for a given user id
    cur = db.execute(
        f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid}"
    )
    anslist = cur.fetchall()
    # db.close()
    for i in anslist:
        csv_file, total_tab = creating_csv_for_each_form(i, userid)
        if csv_file is None:
            continue
        caption_text = f"Total questions : {i[0]}\n"
        cur = db.execute(
            f"select count(distinct user_id) from answer_table where form_id={i[1]}"
        )
        user_count = cur.fetchone()[0]
        caption_text += f"Total users answered : {user_count}"

        tb = tabulate(total_tab, headers="firstrow", tablefmt="simple")
        update.effective_message.reply_html(f"<pre>Title : {i[2]}\n{tb}!</pre>")

        update.effective_message.reply_document(
            document=open(file=csv_file, mode="r"),
            filename=f"{i[2]}-Answers",
            caption=caption_text,
        )

        os.remove(csv_file)


def cancel_command(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Your current operation is cancelled")
    return beginning(update, context)


def unknown_commands(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Sorry, I didn't understand that command.", reply_markup=ReplyKeyboardRemove()
    )
    update.effective_message.reply_text(
        "Type /help to find my commands and their functions"
    )


def help_command(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        """My name is form bot\n
Available commands :\n
/start - To start the bot\n
/create - Helps to create your own form\n
/view_forms - Helps to show your created forms\n
/answers - Used for retrieving answers for your created forms\n
/help - To show this help message
    """,
        reply_markup=ReplyKeyboardRemove(),
    )


def unknown_messages(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Use commands only !\nPlease type /help to know my commands"
    )
