from flask import Flask, request, jsonify
from app.bot import process_input
import asyncio

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main():
    value = request.get_json()
    asyncio.run(process_input(value))
    return jsonify({"status": "ok"})


@app.route("/")
def home():
    return "Hello world!"

# if __name__ == "__main__":
#     app.run()
