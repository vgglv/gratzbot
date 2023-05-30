from flask import Flask, request, jsonify
from app.bot import processInput
import asyncio

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    value = request.get_json()
    asyncio.run(processInput(value))
    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return "Hello world!"

# if __name__ == "__main__":
#     app.run()