from telegram import ReplyKeyboardMarkup, InlineKeyboardButton
from CONFIG import admin_link

cancel_button = [["❌ Cancel"]]


cancel_markup = ReplyKeyboardMarkup(
    cancel_button, one_time_keyboard=False, resize_keyboard=True
)

message_developer_button = [InlineKeyboardButton(text = "Contact Developer 👨‍💻 ", url=admin_link)]

menu_button = [['🧾 Menu']]

menu_markup = ReplyKeyboardMarkup(
    menu_button, one_time_keyboard=False, resize_keyboard=True
)

menu_elements = [['Create 📝','View 🔎','Answers ✍'],['Help ℹ','Bot Stats 📈']]

me_markup = ReplyKeyboardMarkup(
    menu_elements,one_time_keyboard=False, resize_keyboard=True,
)

help_message = """I am <b>Form Bot</b> developed by ADMIN_USERNAME ❤️\n
My available commands 🔰\n
  /start - To <b>start</b> the bot
  /create - To <b>create your own form</b>
  /view_forms - To <b>view your created forms</b>
  /answers - To <b>retrieve answers</b> for your created forms
  /help - To show this <b>help message</b>
  /stats - To show <b>bot statistics</b>
    """

class database:

    bot_data = """
    create table if not exists bot_data (
        total_forms int
    )
    """

    user_table = """
    create table if not exists user_table (
    user_id int primary key, 
    form_count int not null
    );
    """

    form_table = """
    create table if not exists form_table (
    form_id int primary key, 
    form_title text not null, 
    user_id int references user_table(user_id), 
    question_count int
    );
    """

    question_table = """
    create table if not exists question_table (
    form_id int references form_table(form_id) on delete cascade, 
    title text, 
    question_id int not null, 
    question_desc text not null
    );
    """

    answer_table = """
    create table if not exists answer_table (
    user_id int references user_table(user_id),
    name text,
    form_id int references form_table(form_id) on delete cascade,
    answers text not null   
    );
    """
    @staticmethod
    def get_tables():
        return [database.user_table, database.form_table, database.question_table, database.answer_table]