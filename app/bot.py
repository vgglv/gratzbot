from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from os import getenv
from app.db import getUser, setUserData, createUser, getOutput, getAllUsers
from app.utils import items_to_html, declensed_gratz
from app.ai import generate

async def gratztop(update: Update, context):
    print("top was called")
    chatId = update.effective_chat.id
    if (chatId != int(getenv("CHAT_ID"))):
        print("top returns from method, since chatId is restricted")
        return
    users = getAllUsers()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['amount'], users[x]['token']), reverse=True)
    response = items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=chatId, text=response, parse_mode="HTML")

async def gratz(update: Update, context):
    print("gz was called")
    if (not update.effective_message.reply_to_message):
        print("returning from gz, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    sendingUserTokens = sendingUser["token"]
    if (not sendingUser["unlimited"]):
        sendingUserTokens = sendingUserTokens - 1

    receivingUserGratz = receivingUser["amount"] + 1
    setUserData(sendingUserId, sendingUserName, sendingUser["amount"], sendingUserTokens, sendingUser["unlimited"])
    setUserData(receivingUserId, receivingUserName, receivingUserGratz, receivingUser["token"], receivingUser["unlimited"])
    response = f"<b>{receivingUserName}</b>, ты собрал {receivingUserGratz} {declensed_gratz(receivingUserGratz)}!\n<b>{sendingUserName}</b>, у вас {sendingUserTokens} GZ."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

    output = getOutput(str(receivingUserGratz))
    if output:
        if (output["amount"] > 0):
            setUserData(receivingUserId, receivingUserName, receivingUserGratz, receivingUser["token"] + output["amount"], output["unlimitedFunny"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=output["funnyText"])


async def gratzstats(update: Update, context):
    print("stats was called")
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def givetoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("give was called")
    if (not update.effective_message.reply_to_message):
        print("returning from give, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    receivingUserToken = receivingUser["token"] + 1
    sendingUserToken = sendingUser["token"] - 1
    setUserData(sendingUserId, sendingUserName, sendingUser["amount"], sendingUserToken, sendingUser["unlimited"])
    setUserData(receivingUserId, receivingUserName, receivingUser["amount"], receivingUserToken, receivingUser["unlimited"])
    response = f"<b>{receivingUserName}</b>, ты собрал {receivingUserToken} GZ!\n<b>{sendingUserName}</b>, у вас {sendingUserToken} GZ."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.to_json())
    print('received prompt command')
    prompt = "".join(context.args)
    if (not prompt):
        print('prompt was none, returning')
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы ничего не написали! Пожалуйста, повторите заново.", reply_to_message_id=update.effective_message.id)
        return
    answer = generate(prompt)
    if not answer:
        print('prompt was bad, returning...')
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Not telling", reply_to_message_id=update.effective_message.id)
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, parse_mode='Markdown', reply_to_message_id=update.effective_message.id)

async def runTelegramApp():
    print('running telegram app...')
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    gratztop_handler = CommandHandler('top', gratztop)
    gratz_handler = CommandHandler('gratz', gratz)
    gratzstats_handler = CommandHandler('stats', gratzstats)
    givetoken_handler = CommandHandler('give', givetoken)
    chat_handler = CommandHandler('chat', chat)
    application.add_handler(gratztop_handler)
    application.add_handler(gratz_handler)
    application.add_handler(gratzstats_handler)
    application.add_handler(givetoken_handler)
    application.add_handler(chat_handler)
    await application.initialize()
    return application

async def processInput(value):
    application = await runTelegramApp()
    update = Update.de_json(value, application.bot)
    await application.process_update(update)

if __name__ == '__main__':
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    gratztop_handler = CommandHandler('top', gratztop)
    gratz_handler = CommandHandler('gratz', gratz)
    gratzstats_handler = CommandHandler('stats', gratzstats)
    givetoken_handler = CommandHandler('give', givetoken)
    chat_handler = CommandHandler('chat', chat)
    application.add_handler(gratztop_handler)
    application.add_handler(gratz_handler)
    application.add_handler(gratzstats_handler)
    application.add_handler(givetoken_handler)
    application.add_handler(chat_handler)
    application.run_polling()