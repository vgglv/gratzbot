from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from os import getenv
import app.db
import app.utils
from app.user import GUser
import time

FARM_PRICE = 20
ONE_DAY_IN_SECONDS = 86400

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatId = update.effective_chat.id
    if (chatId != int(getenv("CHAT_ID"))):
        print("top returns from method, since chatId is restricted")
        return
    users = app.db.getAllUsers()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['amount'], users[x]['token']), reverse=True)
    response = app.utils.items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=chatId, text=response, parse_mode="HTML")

async def gratz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.effective_message.reply_to_message):
        print("returning from gz, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from gz, since chat is restricted")
        return
    sending_user_id = str(update.effective_user.id)
    receiving_user_id = str(update.effective_message.reply_to_message.from_user.id)
    if (sending_user_id == receiving_user_id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No.", reply_to_message_id=update.effective_message.id)
        return
    sending_user_name = update.effective_user.first_name
    receiving_user_name = update.effective_message.reply_to_message.from_user.first_name

    receiving_user = app.db.getUser(receiving_user_id, receiving_user_name)
    sending_user = app.db.getUser(sending_user_id, sending_user_name)
    if (sending_user.isTokensZero()):
        response = f"<b>{sending_user.getName()}</b>, к сожалению у вас закончились GZ и вы не можете грацевать."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    sending_user.decrementToken()
    receiving_user.incrementGratzAmount()
    app.db.updateUserInDatabase(sending_user)
    app.db.updateUserInDatabase(receiving_user)
    response = f"<b>{receiving_user.getName()}</b>, ты собрал {receiving_user.getGratzAmount()} {app.utils.declensed_gratz(receiving_user.getGratzAmount())}!\n<b>{sending_user.getName()}</b>, у вас {sending_user.getToken()} GZ."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def gratzstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from stats, since chat is restricted")
        return
    user = app.db.getUser(str(update.effective_user.id), update.effective_user.first_name)
    response = f"<b>{user.getName()}</b>, у вас: \n• {user.getGratzAmount()} {app.utils.declensed_gratz(user.getGratzAmount())}; \n• {user.getToken()} GZ; \n• {user.getFarm()} {app.utils.declensed_farm(user.getFarm())};"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def givetoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.effective_message.reply_to_message):
        print("returning from give, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from give, since chat is restricted")
        return
    sending_user_id = str(update.effective_user.id)
    sending_user_name = update.effective_user.first_name
    receiving_user_id = str(update.effective_message.reply_to_message.from_user.id)
    if sending_user_id == receiving_user_id:
        return
    receiving_user_name = update.effective_message.reply_to_message.from_user.first_name
    receiving_user = app.db.getUser(receiving_user_id, receiving_user_name)
    sending_user = app.db.getUser(sending_user_id, sending_user_name)
    
    if (sending_user.isTokensZero()):
        response = f"<b>{sending_user.getName()}</b>, к сожалению, у вас закончились GZ."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    
    sending_user.decrementToken()
    receiving_user.incrementToken()

    response = f"<b>{receiving_user.getName()}</b>, ты собрал {receiving_user.getToken()} GZ!\n<b>{sending_user.getName()}</b>, у вас {sending_user.getToken()} GZ."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def buy_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from buy_farm, since chat is restricted")
        return
    user = app.db.getUser(str(update.effective_user.id), update.effective_user.first_name)
    if (user.getToken() < FARM_PRICE):
        response = f'<b>{user.getName()}</b> у вас не хватает GZ. Требуется {FARM_PRICE} GZ для покупки фермы.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    user.setFarm(user.getFarm() + 1)
    user.setToken(user.getToken() - FARM_PRICE)
    app.db.updateUserInDatabase(user)
    response = f'<b>{user.getName()}</b> вы купили ферму. Итого у вас {user.getFarm()} {app.utils.declensed_farm(user.getFarm())}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def collect_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from buy_farm, since chat is restricted")
        return
    user = app.db.getUser(str(update.effective_user.id), update.effective_user.first_name)

    current_time = int(time.time())
    delta_time = current_time - user.getSavedDate()
    days = delta_time // ONE_DAY_IN_SECONDS
    leftover = delta_time - (days * ONE_DAY_IN_SECONDS)
    if days <= 0:
        next_time_str = time.strftime('%H:%M:%S', time.gmtime(ONE_DAY_IN_SECONDS - delta_time))
        response = f'<b>{user.getName()}</b> дохода пока нет.\nВы сможете собрать следующий урожай через: {next_time_str}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    income = days * user.getFarm()
    user.setToken(user.getToken() + income)
    user.setSavedDate(current_time - leftover)
    next_time = user.getSavedDate() + ONE_DAY_IN_SECONDS - current_time
    next_time_str = time.strftime('%H:%M:%S', time.gmtime(next_time))
    app.db.updateUserInDatabase(user)
    response = f'<b>{user.getName()}</b>, ваш доход {days} дн. X {user.getFarm()} {app.utils.declensed_farm(user.getFarm())} = {income} GZ. Итого: {user.getToken()} GZ.\nВы сможете собрать следующий урожай через: {next_time_str}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from buy_farm, since chat is restricted")
        return
    user = app.db.getUser(str(update.effective_user.id), update.effective_user.first_name)
    response = f'FAQ:\nУ каждого пользователя в начале выдается 5 GZ и 1 Ферма.\n1 Ферма плодит в день 1 GZ.\nЧтобы собрать урожай с фермы, используйте команду <b>collect_farm</b>.\nПри вызове команды <b>collect_farm</b> записывается текущее время по серверу, при истечении 1 дня с этого времени вы можете снова собрать урожай.\nИспользуйте команду <b>buy_farm</b> чтобы купить ферму, цена одной фермы: {FARM_PRICE} GZ.\nЧтобы грацануть кого-то, нужно выбрать его сообщение как <i>reply</i> и вызвать команду <b>gratz</b>.\nТакже, вы можете подарить кому-то GZ через команду <b>give</b> и выбрав его сообщение как <i>reply</i>.\n<b>top</b> - выведет доску лидеров, у кого больше всех грацей на данный момент.\n<b>stats</b> - узнать свои статы.\n\nЧемпионы прошлого сезона:\n<b>Emōknight</b>, \n<b>Ｗｈａｌｅｒｉｄｅｒ➑➍</b>, \n<b>Eeevan</b>. \nВ этом сезоне задача набрать 500 грацей. Победителю будет подарен телеграм премиум на 3 месяца.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def runTelegramApp():
    print('running telegram app...')
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    gratztop_handler = CommandHandler('top', top)
    gratz_handler = CommandHandler('gratz', gratz)
    gratzstats_handler = CommandHandler('stats', gratzstats)
    givetoken_handler = CommandHandler('give', givetoken)
    buy_farm_handler = CommandHandler('buy_farm', buy_farm)
    collect_farm_handler = CommandHandler('collect_farm', collect_farm)
    faq_handler = CommandHandler('faq', faq)
    application.add_handler(gratztop_handler)
    application.add_handler(gratz_handler)
    application.add_handler(gratzstats_handler)
    application.add_handler(givetoken_handler)
    application.add_handler(buy_farm_handler)
    application.add_handler(collect_farm_handler)
    application.add_handler(faq_handler)
    await application.initialize()
    return application

async def processInput(value):
    application = await runTelegramApp()
    update = Update.de_json(value, application.bot)
    await application.process_update(update)

if __name__ == '__main__':
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    gratztop_handler = CommandHandler('top', top)
    gratz_handler = CommandHandler('gratz', gratz)
    gratzstats_handler = CommandHandler('stats', gratzstats)
    givetoken_handler = CommandHandler('give', givetoken)
    buy_farm_handler = CommandHandler('buy_farm', buy_farm)
    collect_farm_handler = CommandHandler('collect_farm', collect_farm)
    faq_handler = CommandHandler('faq', faq)
    application.add_handler(gratztop_handler)
    application.add_handler(gratz_handler)
    application.add_handler(gratzstats_handler)
    application.add_handler(givetoken_handler)
    application.add_handler(buy_farm_handler)
    application.add_handler(collect_farm_handler)
    application.add_handler(faq_handler)
    application.run_polling()