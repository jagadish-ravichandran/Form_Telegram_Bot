from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

api_token = "1869792637:AAETw6wyWCNr68OMuUxgkhwMpp-m0dQMoSI"

cancel_button = [["Cancel"]]


cancel_markup = ReplyKeyboardMarkup(
    cancel_button, one_time_keyboard=False, resize_keyboard=True
)


# inline_kb = [
#     [
#         InlineKeyboardButton("All forms", callback_data="All forms"),
#         InlineKeyboardButton("Forms with Title", callback_data="Forms with Title"),
#     ]
# ]

# inline_markup = InlineKeyboardMarkup(inline_kb)

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





