from os import getenv
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

token = str(getenv("TELEGRAM_TOKEN"))
botApp = Bot(token)
chatId = str(getenv("CHAT_ID"))

def gratztop(update: Update, context):
    botApp.send_message(chat_id=update.effective_chat.id, text="gratz top")

def gratz(update: Update, context):
    botApp.send_message(chat_id=update.effective_chat.id, text="gratz")

def gratzstats(update: Update, context):
    botApp.send_message(chat_id=update.effective_chat.id, text="gratzstats")

def givetoken(update: Update, context):
    botApp.send_message(chat_id=update.effective_chat.id, text="givetoken")

gratztop_handler = CommandHandler('gratztop', gratztop)
gratz_handler = CommandHandler('gratz', gratz)
gratzstats_handler = CommandHandler('gratzstats', gratzstats)
givetoken_handler = CommandHandler('givetoken', givetoken)

dispatcher = Dispatcher(botApp, None)
dispatcher.add_handler(gratztop_handler)
dispatcher.add_handler(gratz_handler)
dispatcher.add_handler(gratzstats_handler)
dispatcher.add_handler(givetoken_handler)

def process(value):
    update = Update.de_json(value, botApp)
    dispatcher.process_update(update)