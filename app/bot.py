import random
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from os import getenv
# from app.db_csv import CSVDatabase
from app.db_firebase import FirebaseDatabase
# from app.db_json import JsonDatabase
from app import utils
from app.user import GUser

DB = FirebaseDatabase()


# DB = CSVDatabase()
# DB = JsonDatabase()


def get_stats(user: GUser):
    return f"<b>{user.name}</b>, у вас: \n• {user.gratz} {utils.declensed_gratz(user.gratz)}."


def is_correct_chat(update: Update):
    if not isinstance(update.message, Message):
        return False
    chat_id = int(getenv("CHAT_ID"))
    return update.effective_chat.id == chat_id


def is_reply_message(update: Update):
    if not is_correct_chat(update):
        return False
    if not update.effective_message.reply_to_message:
        print("returning from give, since message was not a reply")
        return False
    # greturn True
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


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    users = DB.get_all_users()
    sorted_users = sorted(users.keys(), key=lambda x: (users[x]['gratz']), reverse=True)
    response = utils.items_to_html(sorted_users, users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    user = DB.get_user(str(update.effective_user.id), update.effective_user.first_name)
    response = get_stats(user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def gratz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_reply_message(update):
        return
    receiving_user = extract_replying_user(update)
    sending_user = extract_user(update)
    if is_same_user(receiving_user, sending_user):
        return

    receiving_user.gratz = receiving_user.gratz + 1
    DB.update_user(receiving_user)

    response = f"<b>{receiving_user.name}</b> грац!\n{get_stats(receiving_user)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


async def lgbt_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_correct_chat(update):
        return
    saved_lgbt_person = DB.get_saved_lgbt_person()
    if not saved_lgbt_person:
        response = 'Функция еще не реализована для используемого типа БД'
    else:
        current_epoch_days = utils.get_today()
        if current_epoch_days > int(saved_lgbt_person['epoch_days']):
            users = DB.get_all_users()
            lgbt_person_id = random.choice(list(users.keys()))
            current_lgbt_person = users[lgbt_person_id]
            DB.set_lgbt_person(user_id=lgbt_person_id, name=current_lgbt_person['name'], epoch_days=current_epoch_days)
            response = f'Сегодня пидор дня - <b>{current_lgbt_person["name"]}</b>!'
        else:
            response = f'Пидор дня сегодня уже был выбран, это <b>{saved_lgbt_person["name"]}</b>!'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="HTML")


def run_telegram_app():
    print('running telegram app...')
    token = getenv("TELEGRAM_TOKEN")
    _app = ApplicationBuilder().token(token).build()
    handlers = [
        CommandHandler('top', top),
        CommandHandler('stats', stats),
        CommandHandler('gratz', gratz),
        CommandHandler('pidor', lgbt_person),
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
