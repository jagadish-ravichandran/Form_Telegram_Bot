from constants import CreationState
from Functions.forms import displaying_each_form
from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
from telegram import (
    ReplyKeyboardRemove,
)
from variables import cancel_markup, help_message, menu_markup, message_developer_button, me_markup
from Functions.database import (
    Answers,
    Bot,
    Form,
    Questions,
    User,
    title_check_db,
    extract_form,
)

logger = logging.getLogger(__name__)


## handling unexpected entries inside an Conversation Handler in questions and answers
def invalid_typing_in_answers(update: Update, context: CallbackContext):
    update.effective_message.reply_html("Invalid answer 🚫\nPlease enter <b>valid text</b>")
    return CreationState.RECIEVING_ANSWERS


def invalid_title(update: Update, context: CallbackContext):
    update.effective_message.reply_html("Invalid title 🚫\nPlease enter <b>valid text</b>")
    return CreationState.RECIEVING_TITLE


def invalid_qn_number(update: Update, context: CallbackContext):
    update.effective_message.reply_html("Invalid entry 🚫\nEnter <b>number (1-10)</b> ")
    return CreationState.RECIEVING_QUESTION_COUNT


def invalid_typing_in_questions(update: Update, context: CallbackContext):
    update.effective_message.reply_html("Invalid question 🚫\nPlease enter <b>valid question</b>")
    return CreationState.RECIEVING_QUESTIONS


def typing_commands_in_CH(update: Update, context: CallbackContext):
    #command = update.effective_message.text[: update.message.entities[0].length]
    update.effective_message.reply_text(
        f"Your current process is cancelled ❌",
        reply_markup=menu_markup,
    )
    return ConversationHandler.END

def unknown_messages(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "I m unable to recognise this 😔",reply_markup=me_markup 
    )

def unknown_commands(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Sorry, I didn't understand that command 😔", reply_markup=me_markup
    )
    return help_command(update, context)


## Reply Keyboard button = Cancel
def cancel_command(update: Update, context: CallbackContext):
    update.effective_message.reply_html("Your current operation is <b>cancelled</b> ❌",reply_markup=me_markup)
    return -1


def help_command(update: Update, context: CallbackContext):
    update.effective_message.reply_html(
        help_message, reply_markup=menu_markup)

    return ConversationHandler.END

def stats(update: Update, context :CallbackContext):
    user_list = User.get_all()
    total_forms = Bot.get_total_forms()
    stats_text = f"Total users : <b>{len(user_list)} 👥</b>\nTotal Forms Created : <b>{total_forms}</b> 📝"
    update.effective_message.reply_html(stats_text, reply_markup=menu_markup)
    return

def show_menu(update: Update, conext : CallbackContext):
    update.effective_message.reply_text("Menu 🔽 ", reply_markup=me_markup)


def beginning(update: Update, context: CallbackContext):
    fullname = update.effective_user.full_name
 
    update.effective_message.reply_html(
        f"Hai <b>{fullname}</b>😇\nI m here for <b>creating forms</b>", reply_markup=InlineKeyboardMarkup([message_developer_button]), 
    )
    update.effective_message.reply_html(
        "Press <b>Menu</b> to know my commands",reply_markup=menu_markup
    )
    return ConversationHandler.END


def start_command(update: Update, context: CallbackContext):
    userid = int(update.effective_user.id)

    User.add_user(userid)

    if not context.args:
        return beginning(update, context)

    else:
        ownerid, formid = list(map(int, context.args[0].split("_")))
        if userid==ownerid: 
            update.effective_message.reply_html("Sorry! You can't answer your <b>own form</b> 🛑")
            return beginning(update, context)
        current_form = extract_form(formid, ownerid)

        if current_form == []:
            update.effective_message.reply_html(
                "This form is <b>invalid!<b/>\nIt maybe deleted by creator"
            )
            return beginning(update, context)

        
        if User.is_answered(userid, formid):
            update.effective_message.reply_html("Sorry! You answered this form <b>already </b>! 🛑")
            return beginning(update, context)

        context.user_data["form"] = current_form
        context.user_data["answers"] = []
        context.user_data["qns_to_answer"] = current_form[0][0]
        update.effective_message.reply_html(
            f"Form title : <b>{current_form[0][2]}</b>\nTotal questions : <b>{current_form[0][0]}</b>\n\n<i>Type your answers below</i> 👇"
        )
        context.user_data["answer_count"] = 0
        update.effective_message.reply_html(
            f"<b>1. {current_form[0][4]}</b>", reply_markup=cancel_markup
        )
        return CreationState.RECIEVING_ANSWERS


def creating_form(update: Update, context: CallbackContext):
    User.add_user(update.effective_user.id)
    update.effective_message.reply_html("<i>Lets create forms 📝</i>")
    update.effective_message.reply_html(
        "Enter the <b>title</b> for your form : ", reply_markup=cancel_markup
    )
    return CreationState.RECIEVING_TITLE


def title_of_form(update: Update, context: CallbackContext):
    title = update.message.text
    userid = int(update.effective_user.id)

    ## checking already existing form title and inform if any
    tl_ck = title_check_db(userid, title)

    if tl_ck:
        update.effective_message.reply_html(
            "The form title is <b>already entered! 🛑</b>\nPlease enter other title: "
        )
        return CreationState.RECIEVING_TITLE

    context.user_data["title"] = title
    update.effective_message.reply_html(
        "Enter <b>number of questions</b> for the form (limit 10): "
    )
    return CreationState.RECIEVING_QUESTION_COUNT


def storing_answers(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    form_id = context.user_data["form"][0][1]
    answers = context.user_data["answers"]
    count = context.user_data["answer_count"]
    for i in range(count):
        at_record = (user_id, name, form_id, answers[i])
        Answers.storing_answers(at_record)
        

def answering(update: Update, context: CallbackContext):
    if update.effective_message.text == "❌ Cancel":
        return cancel_command(update, context)

    current_form = context.user_data["form"]
    qcount = context.user_data["qns_to_answer"]
    answers = context.user_data["answers"]
    ans_count = context.user_data["answer_count"]

    if qcount - 1 == ans_count:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_text = "Your answers 🔻"                
        counter = 1
        for i in answers:
            ans_text = ans_text + f"{counter}. {i}\n"
            counter += 1
        update.effective_message.reply_html(ans_text)
        storing_answers(update, context)
        update.effective_message.reply_text("Your answers are saved 🗒")
        context.user_data.clear()
        return beginning(update, context)

    else:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_count = context.user_data["answer_count"]
        next_question = current_form[ans_count][4]
        update.effective_message.reply_html(f"<b>{ans_count+1}. {next_question}</b>")
        return CreationState.RECIEVING_ANSWERS


def no_of_questions(update: Update, context: CallbackContext):
    question_count = int(update.message.text)

    if not 0 < question_count <= 10:
        update.effective_message.reply_html("Invalid entry 🚫\nEnter <b>number (1-10)</b>")
        return CreationState.RECIEVING_QUESTION_COUNT
    context.user_data["question_count"] = question_count
    context.user_data["current_question"] = 1
    context.user_data["questions"] = []
    update.effective_message.reply_text("Enter questions line by line : ")
    update.effective_message.reply_html(
        f"<b>Question {context.user_data['current_question']}</b>❓"
    )
    return CreationState.RECIEVING_QUESTIONS


def questions_started(update: Update, context: CallbackContext):
    question = update.effective_message.text
    context.user_data["questions"].append(question)
    # logging.info(context.user_data)

    if context.user_data["current_question"] == context.user_data["question_count"]:
        update.effective_message.reply_text(
            "Your questions are saved successfully ✅",reply_markup=me_markup
        )

    else:
        context.user_data["current_question"] += 1
        update.effective_message.reply_html(
        f"<b>Question {context.user_data['current_question']}</b>❓"
        )
        return CreationState.RECIEVING_QUESTIONS

    userid = update.effective_user.id
    
    # increasing user form count
    user_form_count = User.increase_form_count(userid)

    # increasing total form count
    total_forms = Bot.increase_form_count()


    # inserting to form table
    title = context.user_data["title"]
    qcount = context.user_data["question_count"]
    ft_record = (total_forms, title, userid, qcount)
    Form.insert_values(ft_record)

    # inserting questions to question table
    for i in range(1, qcount + 1):
        question_desc = context.user_data["questions"][i - 1]
        qt_record = (total_forms, title, i, question_desc)
        Questions.insert_values(qt_record)


    # displaying the last generated form
    last_form = extract_form(total_forms, userid)
    context.user_data["last_form"] = user_form_count
    displaying_each_form(update, context, last_form)
    return ConversationHandler.END
