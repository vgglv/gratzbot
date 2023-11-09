import base64
import datetime
from os import getenv
import time
from typing import Dict

from app.db_abstract import AbstractDatabase
import firebase_admin
from firebase_admin import db

from app.user import GUser


class FirebaseDatabase(AbstractDatabase):
    def __init__(self):
        private_key_encoded = getenv("FIREBASE_PRIVATE_KEY")
        private_key_encoded_bytes = private_key_encoded.encode('ascii')
        private_key_decoded_bytes = base64.b64decode(private_key_encoded_bytes)
        private_key_string = private_key_decoded_bytes.decode('ascii')

        cred = firebase_admin.credentials.Certificate({
            "type": "service_account",
            "project_id": getenv("FIREBASE_PROJECT_ID"),
            "client_email": getenv("FIREBASE_CLIENT_EMAIL"),
            "private_key": private_key_string,
            "token_uri": getenv("FIREBASE_TOKEN_URI")
        })
        self.default_app = firebase_admin.initialize_app(cred, {'databaseURL': getenv("db_url")})

    def get_user(self, user_id: str, user_name: str) -> GUser:
        user = db.reference(f"/Users/{user_id}").get()
        print(f"getting user {user_id}, value: {user}")
        if not user:
            print("user not exist, creating user...")
            user = self.create_user(user_id, user_name)
            print(f"created user: {user}")

        if "gold" not in user:
            user["gold"] = 0

        result = GUser(
            user_id=user_id,
            name=user_name,
            gold=user["gold"],
            farm=user["farm"],
            saved_date=user["saved_date"]
        )
        return result

    def update_user(self, user: GUser) -> None:
        value = {
            "name": user.name,
            "gold": user.gold,
            "farm": user.farm,
            "saved_date": user.saved_date
        }
        db.reference(f"/Users/{user.user_id}").update(value)

    def create_user(self, user_id: str, name: str) -> dict[str, any]:
        current_timestamp = int(time.time())
        user_data = {
            "name": name,
            "gold": 5,
            "farm": 1,
            "saved_date": current_timestamp
        }
        db.reference("/Users/").child(user_id).set(user_data)
        return user_data

    def set_user_data(self, user: GUser) -> None:
        value = {
            "name": user.name,
            "gold": user.gold,
            "farm": user.farm,
            "saved_date": user.saved_date
        }
        db.reference(f"/Users/{user.user_id}").set(value)

    def get_all_users(self) -> dict[str, dict[str, any]]:
        return db.reference("/Users/").get()

    def set_gold_in_bank(self, gold: int) -> None:
        db.reference("/bank/gold").child("amount").set(gold)

    def get_gold_from_bank(self) -> int:
        gold = db.reference("/bank/gold").get()
        if not gold:
            db.reference("/bank/gold").child("amount").set(0)
            return 0
        return int(gold["amount"])

    def get_saved_lgbt_person(self) -> dict:
        lgbt_person = db.reference("/lgbt/person").get()
        if not lgbt_person:
            epoch_days_yesterday = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).days - 1
            return {'epoch_days': epoch_days_yesterday, 'name': 'unknown'}
        return lgbt_person

    def set_lgbt_person(self, user_id: str, name: str, epoch_days: int) -> None:
        db.reference("/lgbt/person").set({
          "epoch_days": epoch_days,
          "name": name
        })
        prev_count = db.reference(f"lgbt/stats/{user_id}/count").get()
        if not prev_count:
            prev_count = 0
        db.reference(f"/lgbt/stats/{user_id}").set({
            "count": prev_count + 1,
            "name": name
        })
