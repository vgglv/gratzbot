from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from os import getenv
import app.db
import app.utils
from app.user import GUser
import time

FARM_PRICE = 20
ATTACK_COST = 30
ATTACK_SUCCESS_RATE = 70
STEAL_COST = 1
STEAL_SUCCESS_RATE = 50
ONE_DAY_IN_SECONDS = 86400

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatId = update.effective_chat.id
    if (chatId != int(getenv("CHAT_ID"))):
        print("top returns from method, since chatId is restricted")
        return
    users = app.db.getAllUsers()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['gold']), reverse=True)
    response = app.utils.items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=chatId, text=response, parse_mode="HTML")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from stats, since chat is restricted")
        return
    user = app.db.getUser(str(update.effective_user.id), update.effective_user.first_name)
    response = f"<b>{user.getName()}</b>, у вас: \n• {user.getGold()} {app.utils.declensed_gold(user.getGold())}; \n• {user.getFarm()} {app.utils.declensed_farm(user.getFarm())};"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.effective_message.reply_to_message):
        print("returning from give, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from give, since chat is restricted")
        return
    if (update.effective_message.reply_to_message.from_user.is_bot):
        return
    sending_user_id = str(update.effective_user.id)
    sending_user_name = update.effective_user.first_name
    receiving_user_id = str(update.effective_message.reply_to_message.from_user.id)
    if sending_user_id == receiving_user_id:
        return
    receiving_user_name = update.effective_message.reply_to_message.from_user.first_name
    receiving_user = app.db.getUser(receiving_user_id, receiving_user_name)
    sending_user = app.db.getUser(sending_user_id, sending_user_name)

    text = update.effective_message.text
    gold_am:int = 1
    try:
        res = [int(i) for i in text.split() if i.isdigit()]
        gold_am = res[0]
        print(f"gold_am is {gold_am}")
    except:
        response = f"<b>{sending_user.getName()}</b>, не могу..."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    if (gold_am > sending_user.getGold()):
        response = f"<b>{sending_user.getName()}</b>, нужно больше золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    
    sending_user.setGold(sending_user.getGold() - gold_am)
    receiving_user.setGold(receiving_user.getGold() + gold_am)
    app.db.updateUserInDatabase(sending_user)
    app.db.updateUserInDatabase(receiving_user)

    response = f"<b>{receiving_user.getName()}</b>, у вас {receiving_user.getGold()} {app.utils.declensed_gold(receiving_user.getGold())}!\n<b>{sending_user.getName()}</b>, у вас {sending_user.getGold()} {app.utils.declensed_gold(sending_user.getGold())}."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def buy_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from buy_farm, since chat is restricted")
        return
    user = app.db.getUser(str(update.effective_user.id), update.effective_user.first_name)
    if (user.getGold() < FARM_PRICE):
        response = f'<b>{user.getName()}</b> не хватает золота. Требуется {FARM_PRICE} золотых для покупки фермы.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    user.setFarm(user.getFarm() + 1)
    user.setGold(user.getGold() - FARM_PRICE)
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
    user.setGold(user.getGold() + income)
    user.setSavedDate(current_time - leftover)
    next_time = user.getSavedDate() + ONE_DAY_IN_SECONDS - current_time
    next_time_str = time.strftime('%H:%M:%S', time.gmtime(next_time))
    app.db.updateUserInDatabase(user)
    response = f'<b>{user.getName()}</b>, ваш доход {days} дн. X {user.getFarm()} {app.utils.declensed_farm(user.getFarm())} = {income} {app.utils.declensed_gold(income)}. Итого: {user.getGold()} {app.utils.declensed_gold(user.getGold())}.\nВы сможете собрать следующий урожай через: {next_time_str}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from buy_farm, since chat is restricted")
        return
    response = f'''
FAQ:\n
* У каждого пользователя в начале выдается 5 золотых и 1 Ферма.

* 1 Ферма плодит в день 1 золото.

* <b>buy_farm</b> - СТОИМОСТЬ: {FARM_PRICE} зол. 

* <b>collect</b> - собрать накопленное золото со всех ферм.

* <b>give N</b> - подарить N кол-во золота тому, кого реплаим.

* <b>top</b> - выведет доску лидеров, у кого больше всех золота на данный момент.

* <b>stats</b> - узнать свои статы.

* <b>attack</b> - СТОИМОСТЬ: {ATTACK_COST}. ОПИСАНИЕ: совершить набег на того, кому реплаим. ШАНС успеха = {ATTACK_SUCCESS_RATE}%. При успешном набеге у оппонента сгорает 1 ферма. Нельзя использовать против тех, у кого только 1 ферма.

* <b>steal</b> - СТОИМОСТЬ: {STEAL_COST}, ОПИСАНИЕ: украсть золото у того, кому реплаим. ШАНС успеха = {STEAL_SUCCESS_RATE}%. При провале у вас отнимается золото и отдается тому, у кого вы пытались спиздить. При успешной краже, вы крадете 1 золото.
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.effective_message.reply_to_message):
        print("returning from steal, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from steal, since chat is restricted")
        return
    sending_user_id = str(update.effective_user.id)
    sending_user_name = update.effective_user.first_name
    if (update.effective_message.reply_to_message.from_user.is_bot):
        return
    receiving_user_id = str(update.effective_message.reply_to_message.from_user.id)
    if sending_user_id == receiving_user_id:
        return
    receiving_user_name = update.effective_message.reply_to_message.from_user.first_name
    receiving_user = app.db.getUser(receiving_user_id, receiving_user_name)
    sending_user = app.db.getUser(sending_user_id, sending_user_name)
    if (sending_user.getGold() < STEAL_COST):
        response = f'<b>{sending_user_name}</b>, нужно больше золота ({STEAL_COST}). У вас: {sending_user.getGold()}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    if (receiving_user.getGold() <=0):
        response = f'У <b>{receiving_user_name}</b> нету золота.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    
    sending_user.decrementGold()
    response = f'Готовится кража... \n{sending_user_name} попытается украсть у {receiving_user_name} золото (шанс {STEAL_SUCCESS_RATE}%). \n{sending_user_name} потратил {STEAL_COST} золото... \nИтого у него остается {sending_user.getGold()} {app.utils.declensed_gold(sending_user.getGold())}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    
    if app.utils.roll_for_success(STEAL_SUCCESS_RATE):
        sending_user.incrementGold()
        receiving_user.decrementGold()
        app.db.updateUserInDatabase(sending_user)
        app.db.updateUserInDatabase(receiving_user)
        response = f'<b>{sending_user_name}</b> успешная кража!\n<b>{sending_user_name}</b> получает 1 золото\n<b>{receiving_user_name}</b> теряет 1 золото.\nИтого:\n* <b>{sending_user_name}</b> - {sending_user.getGold()} {app.utils.declensed_gold(sending_user.getGold())}\n* <b>{receiving_user_name}</b> - {receiving_user.getGold()} {app.utils.declensed_gold(receiving_user.getGold())}\n'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    else:
        receiving_user.incrementGold()
        sending_user.decrementGold()
        app.db.updateUserInDatabase(sending_user)
        app.db.updateUserInDatabase(receiving_user)
        response = f'<b>{sending_user_name}</b> вас поймали на краже!\n<b>{receiving_user_name}</b> получает 1 золото, <b>{sending_user_name}</b> теряет 1 золото.\nИтого:\n* <b>{sending_user_name}</b> - {sending_user.getGold()} {app.utils.declensed_gold(sending_user.getGold())}\n* <b>{receiving_user_name}</b> - {receiving_user.getGold()} {app.utils.declensed_gold(receiving_user.getGold())}'
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
        response = f'<b>{user.getName()}</b> дохода пока нет.\nВы сможете собрать золото через: {next_time_str}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    income = days * user.getFarm()
    user.setGold(user.getGold() + income)
    user.setSavedDate(current_time - leftover)
    next_time = user.getSavedDate() + ONE_DAY_IN_SECONDS - current_time
    next_time_str = time.strftime('%H:%M:%S', time.gmtime(next_time))
    app.db.updateUserInDatabase(user)
    response = f'<b>{user.getName()}</b>, ваш доход {days} дн. X {user.getFarm()} {app.utils.declensed_farm(user.getFarm())} = {income} {app.utils.declensed_gold(income)}. Итого: {user.getGold()} {app.utils.declensed_gold(user.getGold())}.\nВы сможете собрать золото через: {next_time_str}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.effective_message.reply_to_message):
        print("returning from steal, since message was not a reply")
        return
    if (update.effective_chat.id != int(getenv("CHAT_ID"))):
        print("returning from steal, since chat is restricted")
        return
    if (update.effective_message.reply_to_message.from_user.is_bot):
        return
    sending_user_id = str(update.effective_user.id)
    sending_user_name = update.effective_user.first_name
    receiving_user_id = str(update.effective_message.reply_to_message.from_user.id)
    if sending_user_id == receiving_user_id:
        return
    receiving_user_name = update.effective_message.reply_to_message.from_user.first_name
    receiving_user = app.db.getUser(receiving_user_id, receiving_user_name)
    sending_user = app.db.getUser(sending_user_id, sending_user_name)
    if (sending_user.getGold() < ATTACK_COST):
        response = f'<b>{sending_user_name}</b>, нужно больше золота (30), у вас {sending_user.getGold()}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    if (receiving_user.getFarm() <= 1):
        response = f'У <b>{receiving_user_name}</b> и так всего 1 ферма!'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    
    sending_user.setGold(sending_user.getGold() - ATTACK_COST)
    response = f'Готовим набег...\n{sending_user_name} атакует {receiving_user_name}.\nШанс успеха {ATTACK_SUCCESS_RATE}%...\nНа подготовку набега у {sending_user_name} потратилось {ATTACK_COST} золота\nИтого у него осталось: {sending_user.getGold()} {app.utils.declensed_gold(sending_user.getGold())}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    
    if app.utils.roll_for_success(ATTACK_SUCCESS_RATE):
        receiving_user.setFarm(receiving_user.getFarm() - 1)
        app.db.updateUserInDatabase(sending_user)
        app.db.updateUserInDatabase(receiving_user)
        response = f'<b>{sending_user_name}</b> вы безжалостно сожгли ферму <b>{receiving_user_name}</b>.\nИтого, у <b>{receiving_user_name}</b> осталось {receiving_user.getFarm()} {app.utils.declensed_farm(receiving_user.getFarm())}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    else:
        app.db.updateUserInDatabase(sending_user)
        response = f'<b>{sending_user_name}</b> ваш набег полностью провален!\n<b>{receiving_user_name}</b> все фермы в целости и сохранности.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def runTelegramApp():
    print('running telegram app...')
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    top_handler = CommandHandler('top', top)
    stats_handler = CommandHandler('stats', stats)
    give_handler = CommandHandler('give', give)
    buy_farm_handler = CommandHandler('buy_farm', buy_farm)
    steal_handler = CommandHandler('steal', steal)
    collect_farm_handler = CommandHandler('collect', collect_farm)
    faq_handler = CommandHandler('faq', faq)
    attack_handler = CommandHandler('attack', attack)
    application.add_handler(top_handler)
    application.add_handler(stats_handler)
    application.add_handler(give_handler)
    application.add_handler(buy_farm_handler)
    application.add_handler(collect_farm_handler)
    application.add_handler(faq_handler)
    application.add_handler(steal_handler)
    application.add_handler(attack_handler)
    await application.initialize()
    return application

async def processInput(value):
    application = await runTelegramApp()
    update = Update.de_json(value, application.bot)
    await application.process_update(update)

if __name__ == '__main__':
    application = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    top_handler = CommandHandler('top', top)
    stats_handler = CommandHandler('stats', stats)
    give_handler = CommandHandler('give', give)
    buy_farm_handler = CommandHandler('buy_farm', buy_farm)
    steal_handler = CommandHandler('steal', steal)
    collect_farm_handler = CommandHandler('collect', collect_farm)
    faq_handler = CommandHandler('faq', faq)
    attack_handler = CommandHandler('attack', attack)
    application.add_handler(top_handler)
    application.add_handler(stats_handler)
    application.add_handler(give_handler)
    application.add_handler(buy_farm_handler)
    application.add_handler(collect_farm_handler)
    application.add_handler(faq_handler)
    application.add_handler(steal_handler)
    application.add_handler(attack_handler)
    application.run_polling()