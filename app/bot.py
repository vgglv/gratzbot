
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
from os import getenv
from app.db import users, getUser, setUserData, createUser, getOutput

token = getenv("TELEGRAM_TOKEN")
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
    if (chatId != closedChatId):
       return
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['amount'], users[x]['token']), reverse=True)
    response = items_to_html(sorted_users)
    botApp = Bot(token)
    botApp.send_message(chat_id=chatId, text=response, parse_mode="HTML")

def gratz(update: Update, context):
    if (not update.effective_message.reply_to_message):
        return
    if (update.effective_chat.id != closedChatId):
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
    botApp = Bot(token)
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
    if (update.effective_chat.id != closedChatId):
        return
    userId = str(update.effective_user.id)
    userName = update.effective_user.first_name
    myUser = getUser(userId)
    if not myUser:
        myUser = createUser(userId, userName)
    tokenAmount = myUser["token"]
    gratzAmount = myUser["amount"]
    response = f"<b>{userName}</b>, сейчас у тебя {gratzAmount} {declensed_gratz(gratzAmount)} и {tokenAmount} GZ!"
    botApp = Bot(token)
    botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

def givetoken(update: Update, context):
    if (not update.effective_message.reply_to_message):
        return
    if (update.effective_chat.id != closedChatId):
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
    botApp = Bot(token)
    botApp.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

def processInput(value):
    print("processing value")
    botApp = Bot(token)
    update = Update.de_json(value, botApp)
    gratztop_handler = CommandHandler('top', gratztop)
    gratz_handler = CommandHandler('gratz', gratz)
    gratzstats_handler = CommandHandler('stats', gratzstats)
    givetoken_handler = CommandHandler('give', givetoken)
    dispatcher = Dispatcher(botApp, None)
    dispatcher.add_handler(gratztop_handler)
    dispatcher.add_handler(gratz_handler)
    dispatcher.add_handler(gratzstats_handler)
    dispatcher.add_handler(givetoken_handler)
    dispatcher.process_update(update)