from telegram.ext import ConversationHandler
import os
import json


def start_command(update, context):
    if context.args == []:
        context.bot.send_message(chat_id=update.message.chat_id, text="I m here for creating forms")
        context.bot.send_message(chat_id=update.message.chat_id, text="Type /create to start creating")
       
        with open("userid.json", 'r') as f:
            data = json.load(f)

            if update.message.chat_id in data['userid']:
                pass
            else:
                data['userid'].append(update.message.chat_id)
                context.user_data['form count'] = 0

            with open("userid.json", 'w') as f1:
                json.dump(data, f1)

        return 0

    else:
       
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


def creating_form(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Let's create a form for you !")
    context.bot.send_message(chat_id=update.message.chat_id, text="Enter the title of the form : ")
    return 4

def title_of_form(update, context):
    print("success")
    form_count = context.user_data['form count']
    form_count += 1
    context.user_data['form count'] += 1
    form = f'{update.message.chat_id}_' + str(form_count)
    context.user_data[form_count] = form
    context.user_data[form] = {}
    context.user_data[form]['answered']=[]

    title = update.message.text
    context.user_data[form]['title'] = title
    
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Enter no. of questions do you want to add")

    
    '''with open('forms.txt', 'a') as f:
        f.write(form)
        f.write('\n')'''
    
    
    return 1
    

def answering(update, context):

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
    

def no_of_questions(update, context):

    form_count = context.user_data['form count']
    form = context.user_data[form_count]
    context.user_data[form]['questions count'] = int(update.message.text)
    context.user_data[form]['question iterator'] = 0 #TODO change this value to 1 if necessary
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Enter your question")

    
    return 2


def questions_started(update, context):
   
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

        #with open("sample.json", "r") as f:
            #data = json.load(f)
        os.system("sample.json")
        with open("sample.json", "w") as f1:
            #json.dump({}, f1)
            json.dump(context.user_data,f1)
        
        context.bot.send_message(chat_id = update.message.chat_id, text = "Your form is created !")
        context.bot.send_message(chat_id = update.message.chat_id, text = "Here's is the link !")
        context.bot.send_message(chat_id = update.message.chat_id, text = f"https://t.me/Dummy1sbot?start={form}")
        return ConversationHandler.END

    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Enter your question")
        context.user_data[form]['question iterator'] += 1
        return 2

def cancel_command(update,context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Your current operation is cancelled")
