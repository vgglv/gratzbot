from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from os import getenv
import app.db
import app.utils
import datetime
import random

async def gratztop(update: Update, context):
    print("top was called")
    chatId = update.effective_chat.id
    print(chatId)
    if (chatId != int(getenv("CHAT_ID"))):
        print("top returns from method, since chatId is restricted")
        return
    users = app.db.getAllUsers()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['amount'], users[x]['token']), reverse=True)
    response = app.utils.items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=chatId, text=response, parse_mode="HTML")

async def chance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from chance, since chat is restricted")
        return
    userId = str(update.effective_user.id)
    user = app.db.getUser(userId, update.effective_user.first_name)
    if (user["token"] > 0):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Шанс можно использовать только при нуле.")
        return
    chanceWeekDay = app.db.getChanceDate(userId)
    currentWeek = datetime.datetime.today().isocalendar().week
    if (chanceWeekDay == currentWeek):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="NO CHANCE TODAY - вы уже использовали сектор шанс на этой неделе.")
        return
    roll = random.randint(1,2)
    if roll == 1:
        app.db.setChanceDate(userId, currentWeek)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="К сожалению, вы не получаете +5 GZ. Попробуйте на следующей неделе.")
        return
    else:
        app.db.setUserData(userId, user["name"], user["amount"], user["token"] + 5, user["unlimited"])
        userName = user["name"]
        chanceData = app.db.getChances()
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=str(chanceData["image"]), caption=f"Поздравляем {userName}! Ты получаешь +5 GZ!")

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
    if (sendingUserId == receivingUserId):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No.", reply_to_message_id=update.effective_message.id)
        return
    receivingUserName = update.effective_message.reply_to_message.from_user.first_name
    receivingUser = app.db.getUser(receivingUserId, receivingUserName)
    sendingUser = app.db.getUser(sendingUserId, sendingUserName)
    if not receivingUser:
        receivingUser = app.db.createUser(receivingUserId, receivingUserName)
    if not sendingUser:
        sendingUser = app.db.createUser(sendingUserId, sendingUserName)
    if (sendingUser["token"] <= 0):
        response = f"<b>{sendingUserName}</b>, к сожалению у вас закончились GZ и вы не можете грацевать."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    sendingUserTokens = sendingUser["token"]
    if (not sendingUser["unlimited"]):
        sendingUserTokens = sendingUserTokens - 1

    receivingUserGratz = receivingUser["amount"] + 1
    app.db.setUserData(sendingUserId, sendingUserName, sendingUser["amount"], sendingUserTokens, sendingUser["unlimited"])
    app.db.setUserData(receivingUserId, receivingUserName, receivingUserGratz, receivingUser["token"], receivingUser["unlimited"])
    response = f"<b>{receivingUserName}</b>, ты собрал {receivingUserGratz} {app.utils.declensed_gratz(receivingUserGratz)}!\n<b>{sendingUserName}</b>, у вас {sendingUserTokens} GZ."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

    output = app.db.getOutput(str(receivingUserGratz))
    if output:
        if (output["amount"] > 0):
            app.db.setUserData(receivingUserId, receivingUserName, receivingUserGratz, receivingUser["token"] + output["amount"], output["unlimitedFunny"])
        if ("image" in output):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=str(output["image"]), caption=str(output["funnyText"]))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=output["funnyText"])

async def gratzstats(update: Update, context):
    print("stats was called")
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from stats, since chat is restricted")
        return
    userId = str(update.effective_user.id)
    userName = update.effective_user.first_name
    myUser = app.db.getUser(userId, userName)
    if not myUser:
        myUser = app.db.createUser(userId, userName)
    tokenAmount = myUser["token"]
    gratzAmount = myUser["amount"]
    response = f"<b>{userName}</b>, сейчас у тебя {gratzAmount} {app.utils.declensed_gratz(gratzAmount)} и {tokenAmount} GZ!"
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
    if sendingUserId == receivingUserId:
        return
    receivingUserName = update.effective_message.reply_to_message.from_user.first_name
    receivingUser = app.db.getUser(receivingUserId, receivingUserName)
    sendingUser = app.db.getUser(sendingUserId, sendingUserName)
    if not receivingUser:
        receivingUser = app.db.createUser(receivingUserId, receivingUserName)
    if not sendingUser:
        sendingUser = app.db.createUser(sendingUserId, sendingUserName)

    if (sendingUser["token"] <= 0):
        response = f"<b>{sendingUserName}</b>, к сожалению, у вас закончились GZ."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    receivingUserToken = receivingUser["token"] + 1
    sendingUserToken = sendingUser["token"] - 1
    app.db.setUserData(sendingUserId, sendingUserName, sendingUser["amount"], sendingUserToken, sendingUser["unlimited"])
    app.db.setUserData(receivingUserId, receivingUserName, receivingUser["amount"], receivingUserToken, receivingUser["unlimited"])
    response = f"<b>{receivingUserName}</b>, ты собрал {receivingUserToken} GZ!\n<b>{sendingUserName}</b>, у вас {sendingUserToken} GZ."
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=app.db.getOneGZImage(), caption=response, parse_mode="HTML")

async def runTelegramApp():
    print('running telegram app...')
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    gratztop_handler = CommandHandler('top', gratztop)
    gratz_handler = CommandHandler('gratz', gratz)
    gratzstats_handler = CommandHandler('stats', gratzstats)
    givetoken_handler = CommandHandler('give', givetoken)
    chance_handler = CommandHandler('chance', chance)
    application.add_handler(gratztop_handler)
    application.add_handler(gratz_handler)
    application.add_handler(gratzstats_handler)
    application.add_handler(givetoken_handler)
    application.add_handler(chance_handler)
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
    chance_handler = CommandHandler('chance', chance)
    application.add_handler(gratztop_handler)
    application.add_handler(gratz_handler)
    application.add_handler(gratzstats_handler)
    application.add_handler(givetoken_handler)
    application.add_handler(chance_handler)
    application.run_polling()