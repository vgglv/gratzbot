from flask import Flask, request, jsonify
from os import getenv
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import firebase_admin
from firebase_admin import db

cred = firebase_admin.credentials.Certificate({
    "client_email": getenv("FIREBASE_CLIENT_EMAIL"),
    "private_key": getenv("FIREBASE_PRIVATE_KEY"),
    "project_id": getenv("FIREBASE_PROJECT_ID")
})
print('sucess')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': str(getenv("db_url"))})
users_ref = db.reference("/Users/")
outputs_ref = db.reference("/Outputs/")
users = users_ref.get()
outputs = outputs_ref.get()

def getUser(userId: str):
    if userId in users:
        return users[userId]
    else:
        return None

def setUserData(userId: str, name: str, gratzAmount: int, firstTime: bool, token: int, unlimited: bool):
    myUser = getUser(userId)
    if not myUser:
        users_ref.child(userId).set({
            "amount": gratzAmount,
            "firstTime": firstTime,
            "name": name,
            "token": token,
            "unlimited": False
        })
    else:
        users_ref.child(userId).update({
            "amount": gratzAmount,
            "firstTime": firstTime,
            "name": name,
            "token": token,
            "unlimited": False
        })

def getOutput(amount: str):
    if amount in outputs:
        return outputs[amount]
    else:
        return None

token = str(getenv("TELEGRAM_TOKEN"))
botApp = Bot(token)
chatId = str(getenv("CHAT_ID"))

def numeral_noun_declension(number, nominative_singular, genetive_singular, nominative_plural):
    dig_last = number % 10
    return (
        (number in range(5, 20)) and nominative_plural or
        (1 in (number, dig_last)) and nominative_singular or
        ({number, dig_last} & {2, 3, 4}) and genetive_singular or nominative_plural
    )

def declensed_gratz(n: int) -> str:
    return numeral_noun_declension(n, 'грац', 'граца', 'грацей')

def items_to_html(items) -> str:
    _list = []
    item: dict
    for index, item in enumerate(items):
        place = index + 1
        name = item.get("name", "[ДАННЫЕ СКРЫТЫ]")
        amount = item.get("amount", 0)
        token = item.get("token", 0)
        _list.append(f"{place}. <b>{name}</b> - {amount} {declensed_gratz(amount)}, {token} {declensed_token(token)}")
    return "\n".join(_list)

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

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    value = request.get_json()
    process(value)
    return jsonify({"status": "ok"})

@app.route("/")
def home():
    output = getOutput("10")
    return str(output["funnyText"])

if __name__ == "__main__":
    app.run()