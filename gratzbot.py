from dotenv import load_dotenv
from os import getenv
import requests

class Gratzbot():
    def __init__(self):
        load_dotenv()
        self.key: str = getenv("gratz_bot_api_key")
        self.channel_id: int = int(getenv("channel_id"))
        self.update_id: int = -1

    def greet(self):
        print(f"Hello, my key is: {self.key}, channel_id: {self.channel_id}.")

    def request_updates(self):
        url: str = "https://api.telegram.org/bot" + self.key + "/getUpdates"
        data = {
            "update_id": self.update_id,
            "timeout": 10,
            "allowed_updates": ["message"]
        }
        try:
            response = requests.post(url=url, data=data).json()
            return response['result']
        except Exception as e:
            return None

    def set_update_id(self, update_id):
        self.update_id = update_id
