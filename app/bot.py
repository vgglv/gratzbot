
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from os import getenv
#from app.db import getUser, setUserData, createUser, getOutput, getAllUsers
from app.db import getUser, setUserData, createUser, getOutput, getAllUsers
from app.utils import items_to_html, declensed_gratz
from app.ai import generate

token = getenv("TELEGRAM_TOKEN")
closedChatId = int(getenv("CHAT_ID"))

def gratztop(update: Update, context):
    print("top was called")
    chatId = update.effective_chat.id
    if (chatId != closedChatId):
        print("top returns from method, since chatId is restricted")
        return
    users = getAllUsers()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['amount'], users[x]['token']), reverse=True)
    response = items_to_html(sorted_users, users)
    botApp.send_message(chat_id=chatId, text=response, parse_mode="HTML")

def gratz(update: Update, context):
    print("gz was called")
    if (not update.effective_message.reply_to_message):
        print("returning from gz, since message was not a reply")
        return
    if (update.effective_chat.id != closedChatId):
        print("returning from gz, since chat is restricted")
        return
    sendingUserId = str(update.effective_user.id)
    sendingUserName = update.effective_user.first_name
    receivingUserId = str(update.effective_message.reply_to_message.from_user.id)
    receivingUserName = update.effective_message.reply_to_message.from_user.first_name
    receivingUser = getUser(receivingUserId, receivingUserName)
    sendingUser = getUser(sendingUserId, sendingUserName)
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
    print("stats was called")
    if (update.effective_chat.id != closedChatId):
        print("returning from stats, since chat is restricted")
        return
    userId = str(update.effective_user.id)
    userName = update.effective_user.first_name
    myUser = getUser(userId, userName)
    if not myUser:
        myUser = createUser(userId, userName)
    tokenAmount = myUser["token"]
    gratzAmount = myUser["amount"]
    response = f"<b>{userName}</b>, сейчас у тебя {gratzAmount} {declensed_gratz(gratzAmount)} и {tokenAmount} GZ!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

def givetoken(update: Update, context: CallbackContext):
    print("give was called")
    if (not update.effective_message.reply_to_message):
        print("returning from give, since message was not a reply")
        return
    if (update.effective_chat.id != closedChatId):
        print("returning from give, since chat is restricted")
        return
    sendingUserId = str(update.effective_user.id)
    sendingUserName = update.effective_user.first_name
    receivingUserId = str(update.effective_message.reply_to_message.from_user.id)
    receivingUserName = update.effective_message.reply_to_message.from_user.first_name
    receivingUser = getUser(receivingUserId, receivingUserName)
    sendingUser = getUser(sendingUserId, sendingUserName)
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

def chat(update: Update, context: CallbackContext):
    print('received prompt command')
    prompt = "".join(context.args)
    if (not prompt):
        print('prompt was none, returning')
        return
    answer = generate(prompt)
    if not answer:
        print('prompt was bad, returning...')
        context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка, повторите через некоторое время.")
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text=answer, parse_mode='Markdown')

botApp = Bot(token)
gratztop_handler = CommandHandler('top', gratztop)
gratz_handler = CommandHandler('gratz', gratz)
gratzstats_handler = CommandHandler('stats', gratzstats)
givetoken_handler = CommandHandler('give', givetoken)
chat_handler = CommandHandler('chat', chat)
dispatcher = Dispatcher(botApp, None)
dispatcher.add_handler(gratztop_handler)
dispatcher.add_handler(gratz_handler)
dispatcher.add_handler(gratzstats_handler)
dispatcher.add_handler(givetoken_handler)
dispatcher.add_handler(chat_handler)

def processInput(value):
    update = Update.de_json(value, botApp)
    dispatcher.process_update(update)