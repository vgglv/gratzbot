import time
from app.db_abstract import AbstractDatabase
from app.user import GUser
import json
import datetime


class JsonDatabase(AbstractDatabase):
    def __init__(self):
        with open('dummy_db.json') as f:
            self.db = json.load(f)
            f.close()
        self.artifacts_json = self.db["artifact"]

    def get_user(self, user_id: str, user_name: str) -> GUser:
        if user_id not in self.db["Users"]:
            print("user not exist, creating user...")
            user = self.create_user(user_id, user_name)
            print(f"created user: {user}")
        else:
            user = self.db["Users"][user_id]

        if "gold" not in user:
            user["gold"] = 0

        artifacts = []
        if "artifacts" in user:
            artifacts = user["artifacts"]

        result = GUser(
            user_id=user_id,
            name=user_name,
            gold=user["gold"],
            farm=user["farm"],
            saved_date=user["saved_date"],
            artifacts=artifacts
        )
        return result

    def update_user(self, user: GUser) -> None:
        value = {
            "name": user.name,
            "gold": user.gold,
            "farm": user.farm,
            "saved_date": user.saved_date,
            "artifacts": user.artifacts
        }
        self.db["Users"][user.user_id] = value
        self.save_json()

    def create_user(self, user_id: str, name: str) -> dict[str, any]:
        current_timestamp = int(time.time())
        user_data = {
            "name": name,
            "gold": 5,
            "farm": 1,
            "saved_date": current_timestamp,
            "artifacts": []
        }
        self.db["Users"][user_id] = user_data
        self.save_json()
        return user_data

    def get_all_users(self) -> dict[str, dict[str, any]]:
        return self.db["Users"]

    def set_gold_in_bank(self, gold: int) -> None:
        self.db["bank"]["gold"]["amount"] = gold
        self.save_json()

    def get_gold_from_bank(self) -> int:
        return int(self.db["bank"]["gold"]["amount"])

    def get_saved_lgbt_person(self) -> dict:
        lgbt_person = self.db["lgbt"]["person"]
        if not lgbt_person:
            epoch_days_yesterday = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).days - 1
            return {'epoch_days': epoch_days_yesterday, 'name': 'unknown'}
        return lgbt_person

    def set_lgbt_person(self, user_id: str, name: str, epoch_days: int) -> None:
        self.db["lgbt"]["person"] = {
            "epoch_days": epoch_days,
            "name": name
        }
        prev_count = self.db["lgbt"]["stats"][user_id]["count"]
        if not prev_count:
            prev_count = 0
        self.db["lgbt"]["stats"][user_id] = {
            "count": prev_count + 1,
            "name": name
        }
        self.save_json()

    def save_json(self):
        with open('dummy_db.json', 'w') as f:
            json.dump(self.db, f)
            f.close()