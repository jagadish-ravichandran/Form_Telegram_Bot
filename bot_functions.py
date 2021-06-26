from constants import CreationState
from form_functions import displaying_each_form
from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update
import logging
from tabulate import tabulate
from telegram import (
    ReplyKeyboardRemove,
 
)
from variables import cancel_markup
from db_functions import (
    Answers,
    Bot,
    Form,
    Questions,
    User,
    title_check_db,
    extract_form,
)

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


## handling unexpected entries inside an Conversation Handler in questions and answers
def invalid_typing_in_answers(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid answer! Please enter valid text")
    return CreationState.RECIEVING_ANSWERS


def invalid_title(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid title! Please enter valid text")
    return CreationState.RECIEVING_TITLE


def invalid_qn_number(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid entry !\nEnter number (1-10) : ")
    return CreationState.RECIEVING_QUESTION_COUNT


def invalid_typing_in_questions(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Invalid question! Please enter valid text")
    return CreationState.RECIEVING_QUESTIONS


def typing_commands_in_CH(update: Update, context: CallbackContext):
    command = update.effective_message.text[: update.message.entities[0].length]
    update.effective_message.reply_text(
        f"Your current process is cancelled !\nPlease enter the command again {command}",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def unknown_messages(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Use commands only !\nPlease type /help to know my commands"
    )

def unknown_commands(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Sorry, I didn't understand that command.", reply_markup=ReplyKeyboardRemove()
    )
    return help_command(update, context)


## Reply Keyboard button = Cancel
def cancel_command(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Your current operation is cancelled")
    return help_command(update, context)


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
    return ConversationHandler.END


def beginning(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "I m here for creating forms", reply_markup=ReplyKeyboardRemove()
    )
    update.effective_message.reply_text("Type /create to start creating forms or /help to know my commands")
    return ConversationHandler.END


def start_command(update: Update, context: CallbackContext):
    userid = int(update.effective_user.id)

    User.add_user(userid)

    if not context.args:
        return beginning(update, context)

    else:
        ownerid, formid = list(map(int, context.args[0].split("_")))
        current_form = extract_form(formid, ownerid)

        if current_form == []:
            update.effective_message.reply_text(
                "This form is invalid!\nIt maybe deleted by creator"
            )
            return beginning(update, context)

        
        if User.is_answered(userid, formid):
            update.effective_message.reply_text("You answered this form already !")
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
        return CreationState.RECIEVING_ANSWERS


def creating_form(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Lets create forms !")
    update.effective_message.reply_text(
        "Enter the title for your form : ", reply_markup=cancel_markup
    )
    return CreationState.RECIEVING_TITLE


def title_of_form(update: Update, context: CallbackContext):
    title = update.message.text
    userid = int(update.effective_user.id)

    ## checking already existing form title and inform if any
    tl_ck = title_check_db(userid, title)

    if tl_ck:
        update.effective_message.reply_text(
            "The form title is already entered!\nPlease enter other title: "
        )
        return CreationState.RECIEVING_TITLE

    context.user_data["title"] = title
    update.effective_message.reply_text(
        "Enter no. of questions do you want to add (limit 10)"
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
        counter = 1
        for i in answers:
            ans_text = ans_text + f"{counter}. {i}\n"
            counter += 1
        update.effective_message.reply_html(ans_text)
        storing_answers(update, context)
        update.effective_message.reply_text("Your answers are saved ! \nThank You! ")
        context.user_data.clear()
        return beginning(update, context)

    else:
        answers.append(update.effective_message.text)
        context.user_data["answer_count"] += 1
        ans_count = context.user_data["answer_count"]
        next_question = current_form[ans_count][4]
        update.effective_message.reply_text(f"{ans_count+1}. {next_question}")
        return CreationState.RECIEVING_ANSWERS


def no_of_questions(update: Update, context: CallbackContext):
    question_count = int(update.message.text)

    if not 0 < question_count <= 10:
        update.effective_message.reply_text("Invalid entry !\nEnter number (1-10) : ")
        return CreationState.RECIEVING_QUESTION_COUNT
    context.user_data["question_count"] = question_count
    context.user_data["current_question"] = 1
    context.user_data["questions"] = []
    update.effective_message.reply_text("Enter questions line by line : ")
    update.effective_message.reply_text(
        f"Enter your question number {context.user_data['current_question']}"
    )
    return CreationState.RECIEVING_QUESTIONS


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
