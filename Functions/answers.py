
from Functions.bot_callbacks import beginning
import logging
import os
from tabulate import tabulate
from Functions.database import Answers, User, creating_csv_for_each_form, title_extraction
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import CallbackContext
# from variables import inline_markup



logger = logging.getLogger(__name__)


def creating_csv_for_answers_for_all_forms(update: Update, context: CallbackContext, userid, formid):

    ## extracting the form id,title, question count for a given user id
    anslist = User.forms_created(formid, userid)
    
    flag = 0
    for i in anslist:
        csv_file, total_tab = creating_csv_for_each_form(i, userid)
        if csv_file is None:
            continue

        flag = 1
        caption_text = f"Total questions : {i[0]}\n"
        
        user_count = Answers.user_count(i[1])
        caption_text += f"Total users answered : {user_count}"

        tb = tabulate(total_tab, headers="firstrow", tablefmt="simple")

        if update.callback_query:
            update.callback_query.edit_message_text("Preview and answer csv file will be uploaded !")
        
        update.effective_message.reply_html(f"<pre>Title : {i[2]}\n{tb}!</pre>")
        update.effective_message.reply_document(
            document=open(file=csv_file, mode="r"),
            filename=f"{i[2]}-Answers.csv",
            caption=caption_text,
        )

        os.remove(csv_file)

    return flag ##indicates no answers for specific form

def answer_query(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    userid = update.effective_user.id
    formid = int(data.split("_")[1])
    # print(formid)
    query.answer("Displaying answers")

    ans_ck = creating_csv_for_answers_for_all_forms(update, context, userid,formid)

    if ans_ck == 0:
        query.edit_message_text("There is no answers for this form!")

    beginning(update, context)

def answer_ck(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    numbering = []
    title_text = "Your forms :\n"
    title_list = title_extraction(userid)
    count = 1
    temp_list = []
    for form_id, title in title_list:
        title_text += f"{count}. {title}\n"
        
        temp_list.append(InlineKeyboardButton(text=str(count), callback_data="answer_" + str(form_id)))
        
        if len(temp_list) == 4 :
            numbering.append(temp_list)
            temp_list = []

        count += 1

    if temp_list:
        numbering.append(temp_list)
 
    update.effective_message.reply_text(title_text, reply_markup= InlineKeyboardMarkup(numbering))


