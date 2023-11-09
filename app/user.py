import time


class GUser:
    def __init__(self, user_id: str, name: str, gold: int = 5, farm: int = 1, saved_date: int = None) -> None:
        self.user_id = user_id
        self.name = name
        self.gold = gold
        self.farm = farm
        if not saved_date:
            self.saved_date = int(time.time())
        else:
            self.saved_date = saved_date

    def is_gold_zero(self) -> bool:
        return self.gold <= 0

    def increment_gold(self):
        self.gold = self.gold + 1

    def decrement_gold(self, amount: int = 1):
        self.gold = self.gold - amount

    def set_user_id(self, user_id: str):
        self.user_id = user_id

    def set_name(self, name: str):
        self.name = name

    def set_gold(self, gold: int):
        self.gold = gold

    def set_farm(self, farm: int):
        self.farm = farm

    def set_saved_date(self, saved_date: int):
        self.saved_date = saved_date
