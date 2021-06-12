from telegram.ext import ConversationHandler
import sqlite3
from telegram import Update, CallbackQuery

form_id=1

def db_connect():
    db_con = sqlite3.connect('form telegram bot')
    return db_con

def start_command(update : Update, context : CallbackQuery):
    if context.args == []:
        user = update.effective_user.id
        context.bot.send_message(chat_id=user, text="I m here for creating forms")
        context.bot.send_message(chat_id=user, text="Type /create to start creating")
        return 0

    else:
        '''
        with open("sample.json", "r") as f:
            data = json.load(f)

        if update.message.chat_id in data[context.args[0]]['answered']:
            context.bot.send_message(chat_id=update.message.chat_id, text="You have answered this form already !")
            return ConversationHandler.END

        else:
            data[context.args[0]]['answered'].append(update.message.chat_id)
        
            with open("sample.json", "w") as f1:
                json.dump(data,f1)

            context.bot.send_message(
                chat_id=update.message.chat_id, text=f"Title of the form : {data[context.args[0]]['title']}")
            
            context.bot.send_message(
                    chat_id=update.message.chat_id, text= "Answers questions one by one !")

            return 3
        '''


def creating_form(update : Update, context : CallbackQuery):
    user = update.effective_user.id
    context.bot.send_message(chat_id = user, text="Let's create a form for you !")
    context.bot.send_message(chat_id = user, text="Enter the title of the form : ")
    return 4

def title_of_form(update : Update, context : CallbackQuery):
    user = update.effective_user.id

    title = update.message.text

    context.bot.send_message(chat_id = user, text = "Enter no. of questions do you want to add")
    try:
        question_count = int(update.message.text)
    except Exception as e:
        print(e)
    
    return 1
    

def answering(update : Update, context : CallbackQuery):

    answered = update.message.text
    #context.user_data['question1_answer'] = answered
    context.bot.send_message(
        chat_id=update.message.chat_id, text= "Your answer is received")
    context.user_data['question1'] = True
    a = context.user_data['question1_id']
    form_owner = a[:a.find('_')]
    context.bot.send_message(
        chat_id=int(form_owner), text=f"Answer received\n{answered}")
    return ConversationHandler.END
    

def no_of_questions(update : Update, context : CallbackQuery):

    form_count = context.user_data['form count']
    form = context.user_data[form_count]
    context.user_data[form]['questions count'] = int(update.message.text)
    context.user_data[form]['question iterator'] = 0 #TODO change this value to 1 if necessary
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Enter your question")

    
    return 2


def questions_started(update : Update, context : CallbackQuery):
   
    form_count = context.user_data['form count']
    form = context.user_data[form_count]
    
    question_count = context.user_data[form]['questions count']
    
    context.user_data[form][context.user_data[form]
                            ['question iterator']] = update.message.text

    '''with open('forms.txt', 'a') as f:
        f.write(
            str(context.user_data[form]['question iterator']) + " : " + update.message.text)
        f.write('\n')'''


    #counter = context.user_data[form]['question iterator']
    
    if context.user_data[form]['question iterator'] == question_count-1:
        print(context.user_data)
        
        context.bot.send_message(chat_id = update.message.chat_id, text = "Your form is created !")
        context.bot.send_message(chat_id = update.message.chat_id, text = "Here's is the link !")
        context.bot.send_message(chat_id = update.message.chat_id, text = f"https://t.me/Dummy1sbot?start={form}")
        return ConversationHandler.END

    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Enter your question")
        context.user_data[form]['question iterator'] += 1
        return 2

def cancel_command(update : Update, context : CallbackQuery):
    context.bot.send_message(chat_id=update.message.chat_id, text="Your current operation is cancelled")
