import time
from app.artifacts import Artifact
from app.utils import get_today


class GUser:
    def __init__(self, user_id: str, name: str, gold: int = 5, farm: int = 1, saved_date: int = None,
                 artifacts: [Artifact] = None) -> None:
        self.user_id = user_id
        self.name = name
        self.gold = gold
        self.farm = farm
        if not saved_date:
            self.saved_date = get_today()
        else:
            self.saved_date = saved_date

        if not artifacts:
            self.artifacts = []
        else:
            self.artifacts = artifacts

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

    def have_this_artifact(self, artifact_id: str) -> bool:
        for artifact in self.artifacts:
            if artifact == artifact_id:
                return True
        return False

    def append_artifact(self, artifact: any):
        self.artifacts.append(artifact)
