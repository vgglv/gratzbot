import os
import logging

import flask
import telegram

app = flask.Flask(__name__)
api = flask.Blueprint("serverless_handler", __name__)
bot = telegram.Bot(os.environ["TELEGRAM_TOKEN"])
logger = logging.getLogger(__name__)

@api.route("/", methods=["POST"])
def main():
    value = flask.request.get_json()
    logger.info("post: %s", value)
    return flask.jsonify({"status": "ok"})

@api.route("/")
def home():
    return "Hello, world!"

app.register_blueprint(api, url_prefix="/api/main")