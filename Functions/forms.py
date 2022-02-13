import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from Functions.database import Form, extract_form, title_extraction
from telegram import Update
from telegram.ext import CallbackContext
from variables import me_markup

logger = logging.getLogger(__name__)

def displaying_each_form(update: Update, context: CallbackContext, flist: list) -> str:
    tracker = 1
    userid = update.effective_user.id
    if context.user_data.get("last_form", None):
        tracker = context.user_data["last_form"]
        context.user_data.clear()

    else:
        formid = flist[0][1]
        
        form_list = Form.get_formid(userid)
        for i in form_list:
            if i[0] == formid:
                tracker = form_list.index(i) + 1
                break


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
            # print("question list : ",questions)
            complete_form_text = f"<b>Form {tracker}</b>\n"
            complete_form_text += f"<b>{title}</b>\n\n"
            # complete_form_text += f"Questions : \n"
            count = 1
            for j in questions:
                complete_form_text += f"➡️ {count}. {j}\n\n"
                count += 1
            complete_form_text += "🔗 Link: "
            form_link = f"https://t.me/{context.bot.username}?start={userid}_{id}"
            complete_form_text += form_link

            fl_inline_bt = [InlineKeyboardButton(text = "Share this form 🚀",url = f"https://t.me/share/?url={form_link}")]
            fl_inline_mk = InlineKeyboardMarkup([fl_inline_bt])

            if update.callback_query == None:
                update.effective_message.reply_html(complete_form_text,disable_web_page_preview=True,reply_markup=fl_inline_mk)
            else:
                update.callback_query.edit_message_text(complete_form_text,disable_web_page_preview=True, parse_mode='HTML',reply_markup=fl_inline_mk)
            
            title = ""
            questions = []
            tracker+=1


def view_query(update : Update,context : CallbackContext):
    query = update.callback_query
    data = query.data
    userid = update.effective_user.id
    formid = int(data.split("_")[1])
    flist = extract_form(formid, userid)
    displaying_each_form(update, context, flist)

def view_forms_ck(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    numbering = []
    title_list = title_extraction(userid)
    if title_list == []:
        update.effective_message.reply_html("You have <b>no forms</b> 😓\nTry creating forms !")
        return
    title_text = "<b>Your forms </b>🗒️\n\n"
    
    count = 1
    temp_list = []
    for form_id, title in title_list:
        title_text += f"📌 {count}. {title}\n"

        temp_list.append(InlineKeyboardButton(text=str(count), callback_data="view_" + str(form_id)))
        
        if len(temp_list) == 4 :
            numbering.append(temp_list)
            temp_list = []

        count += 1

    if temp_list:
        numbering.append(temp_list)

    # update.effective_message.reply_text(title_text)
    update.effective_message.reply_html(title_text,reply_markup=InlineKeyboardMarkup(numbering))

    return 0


