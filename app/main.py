from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher, ContextTypes, CommandHandler
from os import getenv

def gratztop(update, bot):
    bot.send_message(chat_id=update.effective_chat.id, text="gratz top")

token = str(getenv("TELEGRAM_TOKEN"))
botApp = Bot(token)

gratztop_handler = CommandHandler('gratztop', gratztop)
dispatcher = Dispatcher(botApp, None)
dispatcher.add_handler(gratztop_handler)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    value = request.get_json()
    update = Update.de_json(value, botApp)
    dispatcher.process_update(update)
    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return "Hello, world!"

if __name__ == "__main__":
    app.run()