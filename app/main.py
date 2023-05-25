from flask import Flask, request, jsonify
from os import getenv
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import firebase_admin
from firebase_admin import db
import base64

private_key_encoded = getenv("FIREBASE_PRIVATE_KEY")
private_key_encoded_bytes = private_key_encoded.encode('ascii')
private_key_decoded_bytes = base64.b64decode(private_key_encoded_bytes)
private_key_string = private_key_decoded_bytes.decode('ascii')

cred = firebase_admin.credentials.Certificate({
    "type": "service_account",
    "project_id": getenv("FIREBASE_PROJECT_ID"),
    "client_email": getenv("FIREBASE_CLIENT_EMAIL"),
    "private_key": private_key_string,
    "token_uri": getenv("FIREBASE_TOKEN_URI")
})
default_app = firebase_admin.initialize_app(cred, {'databaseURL': getenv("db_url")})
users_ref = db.reference("/Users/")
outputs_ref = db.reference("/Outputs/")
users = users_ref.get()
outputs = outputs_ref.get()

def getUser(userId: str):
    if userId in users:
        return users[userId]
    else:
        return None

def setUserData(userId: str, name: str, gratzAmount: int, token: int, unlimited: bool):
    myUser = getUser(userId)
    value = {
        "amount": gratzAmount,
        "name": name,
        "token": token,
        "unlimited": unlimited
    }
    if not myUser:
        users_ref.child(userId).set(value)
        users[userId] = value
    else:
        users_ref.child(userId).update(value)

    return users[userId]

def createUser(userId: str, name: str):
    return setUserData(userId, name, 0, 11, False)

def getOutput(amount: str):
    if amount in outputs:
        return outputs[amount]
    else:
        return None

token = getenv("TELEGRAM_TOKEN")
botApp = Bot(token)
closedChatId = getenv("CHAT_ID")

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
        name = users[item].get("name", "[ДАННЫЕ СКРЫТЫ]")
        amount = users[item].get("amount", 0)
        token = users[item].get("token", 0)
        _list.append(f"{place}. <b>{name}</b> - {amount} {declensed_gratz(amount)}, {token} GZ!")
    return "\n".join(_list)

def gratztop(update: Update, context):
    chatId = update.effective_chat.id
    #if (chatId != closedChatId):
    #    return
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['amount'], users[x]['token']), reverse=True)
    response = items_to_html(sorted_users)
    botApp.send_message(chat_id=chatId, text=response, parse_mode="HTML")

def gratz(update: Update, context):
    if (not update.effective_message.reply_to_message):
        return
    sendingUserId = str(update.effective_user.id)
    sendingUserName = update.effective_user.first_name
    receivingUserId = str(update.effective_message.reply_to_message.from_user.id)
    receivingUserName = update.effective_message.reply_to_message.from_user.first_name
    receivingUser = getUser(receivingUserId)
    sendingUser = getUser(sendingUserId)
    if not receivingUser:
        receivingUser = createUser(receivingUserId, receivingUserName)
    if not sendingUser:
        sendingUser = createUser(sendingUserId, sendingUserName)
    
    if (sendingUser["token"] <= 0):
        response = f"<b>{sendingUserName}</b>, к сожалению у вас закончились GZ и вы не можете грацевать."
        botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    sendingUserTokens = sendingUser["token"]
    if (not sendingUser["unlimited"]):
        sendingUserTokens = sendingUserTokens - 1

    receivingUserGratz = receivingUser["amount"] + 1
    setUserData(sendingUserId, sendingUserName, sendingUser["amount"], sendingUserTokens, sendingUser["unlimited"])
    setUserData(receivingUserId, receivingUserName, receivingUserGratz, receivingUser["token"], receivingUser["unlimited"])
    response = f"<b>{receivingUserName}</b>, ты собрал {receivingUserGratz} {declensed_gratz(receivingUserGratz)}!\n<b>{sendingUserName}</b>, у вас {sendingUserTokens} GZ."
    botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

    output = getOutput(str(receivingUserGratz))
    if output:
        if (output["amount"] > 0):
            setUserData(receivingUserId, receivingUserName, receivingUserGratz, receivingUser["token"] + output["amount"], output["unlimitedFunny"])
        botApp.send_message(chat_id=update.effective_chat.id, text=output["funnyText"])


def gratzstats(update: Update, context):
    userId = str(update.effective_user.id)
    userName = update.effective_user.first_name
    myUser = getUser(userId)
    if not myUser:
        myUser = createUser(userId, userName)
    tokenAmount = myUser["token"]
    gratzAmount = myUser["amount"]
    response = f"<b>{userName}</b>, сейчас у тебя {gratzAmount} {declensed_gratz(gratzAmount)} и {tokenAmount} GZ!"
    botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

def givetoken(update: Update, context):
    if (not update.effective_message.reply_to_message):
        return
    sendingUserId = str(update.effective_user.id)
    sendingUserName = update.effective_user.first_name
    receivingUserId = str(update.effective_message.reply_to_message.from_user.id)
    receivingUserName = update.effective_message.reply_to_message.from_user.first_name
    receivingUser = getUser(receivingUserId)
    sendingUser = getUser(sendingUserId)
    if not receivingUser:
        receivingUser = createUser(receivingUserId, receivingUserName)
    if not sendingUser:
        sendingUser = createUser(sendingUserId, sendingUserName)

    if (sendingUser["token"] <= 0):
        response = f"<b>{sendingUserName}</b>, к сожалению, у вас закончились GZ."
        botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    receivingUserToken = receivingUser["token"] + 1
    sendingUserToken = sendingUser["token"] - 1
    setUserData(sendingUserId, sendingUserName, sendingUser["amount"], sendingUserToken, sendingUser["unlimited"])
    setUserData(receivingUserId, receivingUserName, receivingUser["amount"], receivingUserToken, receivingUser["unlimited"])
    response = f"<b>{receivingUserName}</b>, ты собрал {receivingUserToken} GZ!\n<b>{sendingUserName}</b>, у вас {sendingUserToken} GZ."
    botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

gratztop_handler = CommandHandler('top', gratztop)
gratz_handler = CommandHandler('gratz', gratz)
gratzstats_handler = CommandHandler('stats', gratzstats)
givetoken_handler = CommandHandler('give', givetoken)

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