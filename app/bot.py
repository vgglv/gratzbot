import datetime
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from os import getenv
# from app.db_csv import CSVDatabase
from app.db_firebase import FirebaseDatabase
# from app.db_json import JsonDatabase
from app import utils
from app.user import GUser
import time
from app import artifacts

FARM_PRICE = 20
ATTACK_COST = 20
ATTACK_SUCCESS_RATE = 50
STEAL_COST = 1
STEAL_SUCCESS_RATE = 30
FARM_COOLDOWN = 86400
CASINO_SUCCESS_RATE = 33
LOTTERY_COST = 1
LOTTERY_SUCCESS_RATE = 3

DB = FirebaseDatabase()
# DB = CSVDatabase()
# DB = JsonDatabase()


def get_stats(user: GUser):
    artifact_str = ''
    if len(user.artifacts) > 0:
        artifact_str = artifact_str + '\n• Артефакты:'

    for artifact_id in user.artifacts:
        artifact = artifacts.find_artefact_by_name(DB.artifacts_json, artifact_id)
        artifact_str = artifact_str + f"\n\t{artifact.icon} {artifact.name}. {artifact.description}"
    return f"<b>{user.name}</b>, у вас: \n• {user.gold} {utils.declensed_gold(user.gold)}; \n• {user.farm} {utils.declensed_farm(user.farm)};{artifact_str}"


def is_correct_chat(update: Update):
    chat_id = int(getenv("CHAT_ID"))
    return update.effective_chat.id == chat_id


def is_reply_message(update: Update):
    if not is_correct_chat(update):
        return False
    if not update.effective_message.reply_to_message:
        print("returning from give, since message was not a reply")
        return False
    # return True
    return not update.effective_message.reply_to_message.from_user.is_bot


def extract_replying_user(update: Update):
    user_id = str(update.effective_message.reply_to_message.from_user.id)
    user_name = update.effective_message.reply_to_message.from_user.first_name
    receiving_user = DB.get_user(user_id, user_name)
    return receiving_user


def extract_user(update: Update):
    sending_user_id = str(update.effective_user.id)
    sending_user_name = update.effective_user.first_name
    sending_user = DB.get_user(sending_user_id, sending_user_name)
    return sending_user


def is_same_user(user_1: GUser, user_2: GUser):
    return user_1.user_id == user_2.user_id


def boost_roll(user: GUser, required_type: str) -> int:
    roll_boost = 0
    all_artifacts = DB.artifacts_json
    for artifact in user.artifacts:
        artifact_class = artifacts.find_artefact_by_name(all_artifacts, artifact)
        if artifact_class.type == required_type:
            roll_boost += artifact_class.value

    return roll_boost


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    users = DB.get_all_users()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['farm'], users[x]['gold']), reverse=True)
    response = utils.items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = DB.get_user(str(update.effective_user.id), update.effective_user.first_name)
    response = get_stats(user)
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
        response = f"<b>{sending_user.name}</b>, неправильно ввели команду, RTFM."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    if gold_am > sending_user.gold:
        response = f"<b>{sending_user.name}</b>, нужно больше золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.set_gold(sending_user.gold - gold_am)
    receiving_user.set_gold(receiving_user.gold + gold_am)
    DB.update_user(sending_user)
    DB.update_user(receiving_user)

    response = f"<b>{sending_user.name}</b> дарит <b>{receiving_user.name}</b> {gold_am} {utils.declensed_gold(gold_am)}!\n\n{get_stats(sending_user)}\n\n{get_stats(receiving_user)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def buy_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = DB.get_user(str(update.effective_user.id), update.effective_user.first_name)
    if user.gold < FARM_PRICE:
        response = f'<b>{user.name}</b> не хватает золота. Требуется {FARM_PRICE} золотых для покупки фермы.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    user.set_farm(user.farm + 1)
    user.set_gold(user.gold - FARM_PRICE)
    DB.update_user(user)
    response = f'<b>{user.name}</b> вы купили ферму. Итого у вас {user.farm} {utils.declensed_farm(user.farm)}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    response = f'''
FAQ:\n
* У каждого пользователя в начале выдается 5 золотых и 1 Ферма.
* 1 Ферма генерит 1 золото каждый день.
* <b>buy_farm</b> - СТОИМОСТЬ: {FARM_PRICE} зол.
* <b>collect</b> - собрать накопленное золото со всех ферм.
* <b>gratz</b> - подарить кому-то 1 золото
* <b>give N</b> - подарить N кол-во золота тому, кого реплаим.
* <b>top</b> - выведет доску лидеров, у кого больше всех золота на данный момент.
* <b>stats</b> - узнать свои статы.
* <b>attack</b> - СТОИМОСТЬ: {ATTACK_COST}. ОПИСАНИЕ: совершить набег на того, кому реплаим. ШАНС успеха = {ATTACK_SUCCESS_RATE}%. При успешном набеге у оппонента отжимается 1 ферма и передается вам, в противном случае, ваша ферма отдается оппоненту. Нельзя использовать против тех, у кого только 1 ферма.
* <b>steal</b> - СТОИМОСТЬ: 0, ОПИСАНИЕ: украсть золото у того, кому реплаим. ШАНС успеха = {STEAL_SUCCESS_RATE}%. При провале у вас отнимается золото и отдается тому, у кого вы пытались украсть. При успешной краже, вы крадете 1 золото.
* <b>casino N</b> - поставить N золотых на казино, шанс удвоить их равен {CASINO_SUCCESS_RATE}%, в противном случае ваше золото уходит в <b>призовой фонд лотереи</b>.
* <b>lottery</b> - СТОИМОСТЬ: {LOTTERY_COST}. ШАНС успеха: {LOTTERY_SUCCESS_RATE}%. При выигрыше вы получаете <b>призовой фонд лотереи</b>.
* <b>lottery_all</b> - играть в лотерею до победного конца (или пока не закончится золото)
* <b>prize</b> - СТОИМОСТЬ: 0, выводит текущий призовой фонд.
* <b>artifacts</b> - вывести список артефактов доступных к покупке.
* <b>buy_artifact N</b> - купить артефакт N, где N это айди артефакта.
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

    roll_rate = STEAL_SUCCESS_RATE + boost_roll(sending_user, "steal_boost")

    if utils.roll_for_success(roll_rate):
        sending_user.increment_gold()
        receiving_user.decrement_gold()
        response = f'<b>{sending_user.name}</b> успешная кража!\nВы получаете 1 золотой из кармана <b>{receiving_user.name}</b> (шанс был {roll_rate}%).\n\n{get_stats(sending_user)}\n\n{get_stats(receiving_user)}'
    else:
        sending_user.decrement_gold()
        receiving_user.increment_gold()
        response = f'<b>{sending_user.name}</b> кража провалилась!\n<b>{receiving_user.name}</b> получает 1 золотой из вашего кармана (шанс был {roll_rate}%).\n\n{get_stats(sending_user)}\n\n{get_stats(receiving_user)}'

    DB.update_user(sending_user)
    DB.update_user(receiving_user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def collect_farm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = extract_user(update)
    is_lgbt = DB.get_saved_lgbt_person()["name"] == user.name
    have_rainbow_charm = "rainbow_charm" in user.artifacts
    current_time = int(time.time())
    delta_time = current_time - user.saved_date
    days = delta_time // FARM_COOLDOWN
    leftover = delta_time - (days * FARM_COOLDOWN)
    if days <= 0:
        next_time_str = time.strftime('%H:%M:%S', time.gmtime(FARM_COOLDOWN - delta_time))
        response = f'<b>{user.name}</b> дохода пока нет.\nВы сможете собрать золото через: {next_time_str}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    income = days * user.farm
    charm_text = ''
    if is_lgbt and have_rainbow_charm:
        charm = artifacts.find_artefact_by_name(DB.artifacts_json, "rainbow_charm")
        income *= charm.value
        charm_text = f' X {charm.value} rainbow_charm'
    user.set_gold(user.gold + income)
    user.set_saved_date(current_time - leftover)
    next_time = user.saved_date + FARM_COOLDOWN - current_time
    next_time_str = time.strftime('%H:%M:%S', time.gmtime(next_time))
    DB.update_user(user)
    response = f'<b>{user.name}</b>, ваш доход {days} дн. X {user.farm} {utils.declensed_farm(user.farm)}{charm_text} = {income} {utils.declensed_gold(income)}. Итого: {user.gold} {utils.declensed_gold(user.gold)}.\nВы сможете собрать золото через: {next_time_str}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_reply_message(update):
        return
    sending_user = extract_user(update)
    receiving_user = extract_replying_user(update)
    if is_same_user(sending_user, receiving_user):
        return
    if sending_user.gold < ATTACK_COST:
        response = f'<b>{sending_user.name}</b>, нужно больше золота ({ATTACK_COST}), у вас {sending_user.gold}.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return
    if receiving_user.farm <= 1:
        response = f'У <b>{receiving_user.name}</b> и так всего 1 ферма!'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.set_gold(sending_user.gold - ATTACK_COST)
    response = f'Готовим набег...\n{sending_user.name} атакует {receiving_user.name}.\nШанс успеха {ATTACK_SUCCESS_RATE}%...\nНа подготовку набега у {sending_user.name} потратилось {ATTACK_COST} золота\nИтого у него осталось: {sending_user.gold} {utils.declensed_gold(sending_user.gold)}.'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

    if utils.roll_for_success(ATTACK_SUCCESS_RATE):
        receiving_user.set_farm(receiving_user.farm - 1)
        sending_user.set_farm(sending_user.farm + 1)
        DB.update_user(sending_user)
        DB.update_user(receiving_user)
        response = f'<b>{sending_user.name}</b> вы безжалостно отобрали ферму у <b>{receiving_user.name}</b>..\n\n{get_stats(sending_user)}\n\n{get_stats(receiving_user)}'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
    else:
        sending_user.set_farm(sending_user.farm - 1)
        receiving_user.set_farm(receiving_user.farm + 1)
        DB.update_user(sending_user)
        DB.update_user(receiving_user)
        response = f'<b>{sending_user.name}</b> ваш набег провален!\n<b>{receiving_user.name}</b> отжимает одну из ваших ферм себе..\n\n{get_stats(sending_user)}\n\n{get_stats(receiving_user)}'
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
    DB.update_user(sending_user)
    DB.update_user(receiving_user)

    response = f"<b>{receiving_user.name}</b> грац! Получите +1 зол.\n\n{get_stats(sending_user)}\n\n{get_stats(receiving_user)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    sending_user = extract_user(update)
    message = update.effective_message.text
    try:
        res = [int(i) for i in message.split() if i.isdigit()]
        gold_am = res[0]
        print(f"gold_am is {gold_am}")
    except:
        response = f"<b>{sending_user.name}</b>, неправильный ввод команды, RTFM."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    if gold_am > sending_user.gold:
        response = f"<b>{sending_user.name}</b>, нужно больше золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    roll_rate = CASINO_SUCCESS_RATE + boost_roll(sending_user, "casino_boost")

    if utils.roll_for_success(roll_rate):
        big_money = gold_am * 2
        sending_user.set_gold(sending_user.gold + big_money - gold_am)
        response = f"<b>{sending_user.name}</b> ВЫ СОРВАЛИ КУШ! Вы получаете {big_money}! (шанс был: {roll_rate}%)\n\n{get_stats(sending_user)}"
    else:
        sending_user.set_gold(sending_user.gold - gold_am)
        current_g = DB.get_gold_from_bank() + gold_am
        DB.set_gold_in_bank(current_g)
        response = f"<b>{sending_user.name}</b> вы безнадежно потратили {gold_am} {utils.declensed_gold(gold_am)}, в следующий раз повезет (шанс был: {roll_rate}%).\n\n{get_stats(sending_user)}\n\nПризовой фонд лотереи: {current_g} {utils.declensed_gold(current_g)}."

    DB.update_user(sending_user)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def lottery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    sending_user = extract_user(update)
    gold_in_bank = DB.get_gold_from_bank()

    if gold_in_bank <= 0:
        response = f"<b>{sending_user.name}</b> в <b>призовом фонде</b> нет золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    if sending_user.gold < LOTTERY_COST:
        response = f"<b>{sending_user.name}</b> у вас нет денег на покупку лотерейного билета."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    sending_user.decrement_gold(LOTTERY_COST)

    if utils.roll_for_success(LOTTERY_SUCCESS_RATE):
        sending_user.gold = sending_user.gold + gold_in_bank
        DB.set_gold_in_bank(0)
        response = f"<b>{sending_user.name}</b> ВЫ ВЫИГРАЛИ!!!!\n\n{get_stats(sending_user)}"
    else:
        gold_in_bank = gold_in_bank + LOTTERY_COST
        response = f"<b>{sending_user.name}</b> вы не выиграли.\n\n{get_stats(sending_user)}\n\nПризовой фонд: {gold_in_bank} {utils.declensed_gold(gold_in_bank)}!"
        DB.set_gold_in_bank(gold_in_bank)

    DB.update_user(sending_user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def lottery_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return

    sending_user = extract_user(update)
    gold_in_bank = DB.get_gold_from_bank()
    initial_gold = sending_user.gold

    if gold_in_bank <= 0:
        response = f"<b>{sending_user.name}</b> в <b>призовом фонде</b> нет золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    if initial_gold < LOTTERY_COST:
        response = f"<b>{sending_user.name}</b> у вас нет денег на покупку лотерейного билета."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    tries_count = 0
    lottery_won = False

    while not lottery_won and sending_user.gold >= LOTTERY_COST:
        sending_user.decrement_gold(LOTTERY_COST)

        if utils.roll_for_success(LOTTERY_SUCCESS_RATE):
            lottery_won = True
            tries_count += 1
            sending_user.gold = sending_user.gold + gold_in_bank
            DB.set_gold_in_bank(0)
            response = f"<b>{sending_user.name}</b> ВЫ ВЫИГРАЛИ!!!!\nКоличество попыток: {tries_count}\n\n{get_stats(sending_user)}"
        else:
            tries_count += 1
            gold_in_bank = gold_in_bank + LOTTERY_COST


    if sending_user.gold < LOTTERY_COST:
        DB.set_gold_in_bank(gold_in_bank)
        response = f"<b>{sending_user.name}</b> вы не выиграли и потратили {initial_gold - sending_user.gold}.\n\n{get_stats(sending_user)}\n\nПризовой фонд: {gold_in_bank} {utils.declensed_gold(gold_in_bank)}!"

    DB.update_user(sending_user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def prize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    gold_in_bank = DB.get_gold_from_bank()
    response = f"Призовой фонд: {gold_in_bank} {utils.declensed_gold(gold_in_bank)}!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def lgbt_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    saved_lgbt_person = DB.get_saved_lgbt_person()
    if not saved_lgbt_person:
        response = 'Функция еще не реализована для используемого типа БД'
    else:
        current_epoch_days = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).days
        if current_epoch_days > int(saved_lgbt_person['epoch_days']):
            users = DB.get_all_users()
            lgbt_person_id = random.choice(list(users.keys()))
            current_lgbt_person = users[lgbt_person_id]
            DB.set_lgbt_person(user_id=lgbt_person_id, name=current_lgbt_person['name'], epoch_days=current_epoch_days)
            response = f'Сегодня пидор дня - <b>{current_lgbt_person["name"]}</b>!'
        else:
            response = f'Пидор дня сегодня уже был выбран, это <b>{saved_lgbt_person["name"]}</b>!'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def buy_artifact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = extract_user(update)
    all_artifacts = DB.artifacts_json
    message = update.effective_message.text
    try:
        res = [i for i in message.split() if i.isascii()]
        artifact_id = res[1]
    except:
        response = f"<b>{user.name}</b>, неправильный ввод команды.\nНапишите `buy_artifact N` где N это айдишник артефакта.\n\nАртефакты:{artifacts.print_artifacts(all_artifacts)}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")
        return

    artifact = artifacts.find_artefact_by_name(all_artifacts, artifact_id)
    if artifact is None:
        response = f"Артефакт с айдишником {artifact_id} не найден."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return

    if user.have_this_artifact(artifact.name):
        response = f"У вас уже есть этот артефакт."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return

    if user.gold < artifact.price:
        response = f"Артефакт стоит {artifact.price}, у вас {user.gold}. Попробуйте снова когда у вас будет достаточно золота."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return

    user.decrement_gold(artifact.price)
    user.append_artifact(artifact.name)

    DB.update_user(user)

    response = f"<b>{user.name}</b>, поздравляю с покупкой!\n\n{get_stats(user)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

async def show_artifacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    all_artifacts = DB.artifacts_json
    response = f"{artifacts.print_artifacts(all_artifacts)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")

def run_telegram_app():
    print('running telegram app...')
    token = getenv("TELEGRAM_TOKEN")
    _app = ApplicationBuilder().token(token).build()
    handlers = [
        CommandHandler('top', top),
        CommandHandler('stats', stats),
        CommandHandler('give', give),
        CommandHandler('buy_farm', buy_farm),
        CommandHandler('steal', steal),
        CommandHandler('collect', collect_farm),
        CommandHandler('faq', faq),
        CommandHandler('attack', attack),
        CommandHandler('gratz', gratz),
        CommandHandler('casino', casino),
        CommandHandler('lottery', lottery),
        CommandHandler('lottery_all', lottery_all),
        CommandHandler('prize', prize),
        CommandHandler('pidor', lgbt_person),
        CommandHandler('buy_artifact', buy_artifact),
        CommandHandler('artifacts', show_artifacts)
    ]
    _app.add_handlers(handlers=handlers)
    return _app


async def process_input(value):
    _app = run_telegram_app()
    await _app.initialize()
    update = Update.de_json(value, _app.bot)
    await _app.process_update(update)


if __name__ == '__main__':
    application = run_telegram_app()
    application.run_polling()
