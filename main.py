from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

from functions import start_command, creating_form, cancel_command, no_of_questions, questions_started, answering, title_of_form

from telegram import Bot



def main():
    api_token = "1869792637:AAHepJn192WKZdpTFC3vOcYZn86nZGsD6iw"
    updater = Updater(api_token, use_context=True)
    
    d = updater.dispatcher
    #d.add_handler(CommandHandler("start", start_command))
    d.add_handler(ConversationHandler(
        entry_points=[(CommandHandler("start", start_command))],
        states={
            0 : [(CommandHandler("create", creating_form))],
            4 : [MessageHandler(Filters.text, title_of_form)],
            1: [MessageHandler(Filters.regex('[0-9]'), no_of_questions)],
            2 : [MessageHandler(Filters.text, questions_started)],
            3 : [MessageHandler(Filters.text, answering)]
        },
        fallbacks= [CommandHandler("cancel",cancel_command)]   
    ))
    
    updater.start_polling()

if __name__ == '__main__':
    main()
