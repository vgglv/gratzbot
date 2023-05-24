from flask import Flask, request, jsonify
import bot

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    value = request.get_json()
    bot.process(value)
    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return "Hello, world!"

if __name__ == "__main__":
    app.run()