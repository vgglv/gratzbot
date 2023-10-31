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
STEAL_SUCCESS_RATE = 30
ONE_DAY_IN_SECONDS = 86400


def is_correct_chat(update: Update):
    return update.effective_chat.id == int(getenv("CHAT_ID"))


def is_reply_message(update: Update):
    if not is_correct_chat(update):
        return False
    if not update.effective_message.reply_to_message:
        print("returning from give, since message was not a reply")
        return False
    return True
    # return not update.effective_message.reply_to_message.from_user.is_bot


def extract_replying_user(update: Update):
    user_id = str(update.effective_message.reply_to_message.from_user.id)
    user_name = update.effective_message.reply_to_message.from_user.first_name
    receiving_user = app.db.get_user(user_id, user_name)
    return receiving_user


def extract_user(update: Update):
    sending_user_id = str(update.effective_user.id)
    sending_user_name = update.effective_user.first_name
    sending_user = app.db.get_user(sending_user_id, sending_user_name)
    return sending_user


def is_same_user(user_1: GUser, user_2: GUser):
    return user_1.user_id == user_2.user_id


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    users = app.db.get_all_users()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['farm'], users[x]['gold']), reverse=True)
    response = app.utils.items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = app.db.get_user(str(update.effective_user.id), update.effective_user.first_name)
    response = f"<b>{user.name}</b>, у вас: \n• {user.gold} {app.utils.declensed_gold(user.gold)}; \n• {user.farm} {app.utils.declensed_farm(user.farm)};"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_reply_message(update):
        return
    receiving_user = extract_replying_user(update)
    sending_user = extract_user(update)
    if is_same_user(receiving_user, sending_user):
        return

    text = update.effective_message.text
    try:
        res = [int(i) for i in text.split() if i.isdigit()]
        gold_am = res[0]
        print(f"gold_am is {gold_am}")
    except:
        response = f"<b>{sending_user.name}</b>, не могу..."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    if gold_am > sending_user.gold:
        response = f"<b>{sending_user.name}</b>, нужно больше золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.set_gold(sending_user.gold - gold_am)
    receiving_user.set_gold(receiving_user.gold + gold_am)
    app.db.update_user(sending_user)
    app.db.update_user(receiving_user)

    response = f"<b>{receiving_user.name}</b>, у вас {receiving_user.gold} {app.utils.declensed_gold(receiving_user.gold)}!\n<b>{sending_user.name}</b>, у вас {sending_user.farm} {app.utils.declensed_gold(sending_user.farm)}."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def buy_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = app.db.get_user(str(update.effective_user.id), update.effective_user.first_name)
    if user.gold < FARM_PRICE:
        response = f'<b>{user.name}</b> не хватает золота. Требуется {FARM_PRICE} золотых для покупки фермы.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    user.set_farm(user.farm + 1)
    user.set_gold(user.gold - FARM_PRICE)
    app.db.update_user(user)
    response = f'<b>{user.name}</b> вы купили ферму. Итого у вас {user.farm} {app.utils.declensed_farm(user.farm)}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    response = f'''
FAQ:\n
* У каждого пользователя в начале выдается 5 золотых и 1 Ферма.

* 1 Ферма плодит в день 1 золото.

* <b>buy_farm</b> - СТОИМОСТЬ: {FARM_PRICE} зол. 

* <b>collect</b> - собрать накопленное золото со всех ферм.

* <b>gratz</b> - подарить кому-то 1 золото

* <b>give N</b> - подарить N кол-во золота тому, кого реплаим.

* <b>top</b> - выведет доску лидеров, у кого больше всех золота на данный момент.

* <b>stats</b> - узнать свои статы.

* <b>attack</b> - СТОИМОСТЬ: {ATTACK_COST}. ОПИСАНИЕ: совершить набег на того, кому реплаим. ШАНС успеха = {ATTACK_SUCCESS_RATE}%. При успешном набеге у оппонента сгорает 1 ферма. Нельзя использовать против тех, у кого только 1 ферма.

* <b>steal</b> - СТОИМОСТЬ: {STEAL_COST}, ОПИСАНИЕ: украсть золото у того, кому реплаим. ШАНС успеха = {STEAL_SUCCESS_RATE}%. При провале у вас отнимается золото и отдается тому, у кого вы пытались спиздить. При успешной краже, вы крадете 1 золото.
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_reply_message(update):
        return
    sending_user = extract_user(update)
    receiving_user = extract_replying_user(update)
    if is_same_user(sending_user, receiving_user):
        return
    if sending_user.gold < STEAL_COST:
        response = f'<b>{sending_user.name}</b>, нужно больше золота ({STEAL_COST}). У вас: {sending_user.gold}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    if receiving_user.gold <= 0:
        response = f'У <b>{receiving_user.name}</b> нету золота.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.decrement_gold()
    response = f'Готовится кража... \n{sending_user.name} попытается украсть у {receiving_user.name} золото (шанс успеха {STEAL_SUCCESS_RATE}%). \nНа подготовки {sending_user.name} потратил {STEAL_COST} золото (осталось: {sending_user.gold})...'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

    if app.utils.roll_for_success(STEAL_SUCCESS_RATE):
        sending_user.increment_gold()
        receiving_user.decrement_gold()
        app.db.update_user(sending_user)
        app.db.update_user(receiving_user)
        response = f'<b>{sending_user.name}</b> успешная кража!\n<b>{sending_user.name}</b> получает 1 золото (итого: {sending_user.gold})!\n<b>{receiving_user.name}</b> теряет 1 золото (итого: {receiving_user.gold}).'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    else:
        app.db.update_user(sending_user)
        response = f'<b>{sending_user.name}</b> кража провалилась!'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def collect_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = app.db.get_user(str(update.effective_user.id), update.effective_user.first_name)
    current_time = int(time.time())
    delta_time = current_time - user.saved_date
    days = delta_time // ONE_DAY_IN_SECONDS
    leftover = delta_time - (days * ONE_DAY_IN_SECONDS)
    if days <= 0:
        next_time_str = time.strftime('%H:%M:%S', time.gmtime(ONE_DAY_IN_SECONDS - delta_time))
        response = f'<b>{user.name}</b> дохода пока нет.\nВы сможете собрать золото через: {next_time_str}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    income = days * user.farm
    user.set_gold(user.gold + income)
    user.set_saved_date(current_time - leftover)
    next_time = user.saved_date + ONE_DAY_IN_SECONDS - current_time
    next_time_str = time.strftime('%H:%M:%S', time.gmtime(next_time))
    app.db.update_user(user)
    response = f'<b>{user.name}</b>, ваш доход {days} дн. X {user.farm} {app.utils.declensed_farm(user.farm)} = {income} {app.utils.declensed_gold(income)}. Итого: {user.gold} {app.utils.declensed_gold(user.gold)}.\nВы сможете собрать золото через: {next_time_str}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_reply_message(update):
        return
    sending_user = extract_user(update)
    receiving_user = extract_replying_user(update)
    if is_same_user(sending_user, receiving_user):
        return
    if sending_user.gold < ATTACK_COST:
        response = f'<b>{sending_user.name}</b>, нужно больше золота (30), у вас {sending_user.gold}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    if receiving_user.farm <= 1:
        response = f'У <b>{receiving_user.name}</b> и так всего 1 ферма!'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.set_gold(sending_user.gold - ATTACK_COST)
    response = f'Готовим набег...\n{sending_user.name} атакует {receiving_user.name}.\nШанс успеха {ATTACK_SUCCESS_RATE}%...\nНа подготовку набега у {sending_user.name} потратилось {ATTACK_COST} золота\nИтого у него осталось: {sending_user.gold} {app.utils.declensed_gold(sending_user.gold)}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

    if app.utils.roll_for_success(ATTACK_SUCCESS_RATE):
        receiving_user.set_farm(receiving_user.farm - 1)
        app.db.update_user(sending_user)
        app.db.update_user(receiving_user)
        response = f'<b>{sending_user.name}</b> вы безжалостно сожгли ферму <b>{receiving_user.name}</b>.\nИтого, у <b>{receiving_user.name}</b> {receiving_user.farm} {app.utils.declensed_farm(receiving_user.farm)}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    else:
        app.db.update_user(sending_user)
        response = f'<b>{sending_user.name}</b> ваш набег полностью провален!\n<b>{receiving_user.name}</b> все фермы в целости и сохранности.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def gratz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_reply_message(update):
        return
    receiving_user = extract_replying_user(update)
    sending_user = extract_user(update)
    if is_same_user(receiving_user, sending_user):
        return

    if sending_user.gold <= 0:
        response = f"<b>{sending_user.name}</b>, нужно больше золота (1)."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.decrement_gold()
    receiving_user.increment_gold()
    app.db.update_user(sending_user)
    app.db.update_user(receiving_user)

    response = f"<b>{receiving_user.name}</b> грац! Получите +1 зол. (всего: {receiving_user.gold} {app.utils.declensed_gold(receiving_user.gold)}) от <b>{sending_user.name}</b> (всего: {sending_user.gold} {app.utils.declensed_gold(sending_user.gold)})."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

def run_telegram_app():
    print('running telegram app...')
    _app = ApplicationBuilder().token(getenv("TELEGRAM_TOKEN")).build()
    top_handler = CommandHandler('top', top)
    stats_handler = CommandHandler('stats', stats)
    give_handler = CommandHandler('give', give)
    buy_farm_handler = CommandHandler('buy_farm', buy_farm)
    steal_handler = CommandHandler('steal', steal)
    collect_farm_handler = CommandHandler('collect', collect_farm)
    faq_handler = CommandHandler('faq', faq)
    attack_handler = CommandHandler('attack', attack)
    gratz_handler = CommandHandler('gratz', gratz)
    _app.add_handler(top_handler)
    _app.add_handler(stats_handler)
    _app.add_handler(give_handler)
    _app.add_handler(buy_farm_handler)
    _app.add_handler(collect_farm_handler)
    _app.add_handler(faq_handler)
    _app.add_handler(steal_handler)
    _app.add_handler(attack_handler)
    _app.add_handler(gratz_handler)
    return _app


async def process_input(value):
    _app = run_telegram_app()
    await _app.initialize()
    update = Update.de_json(value, _app.bot)
    await _app.process_update(update)


if __name__ == '__main__':
    application = run_telegram_app()
    application.run_polling()
