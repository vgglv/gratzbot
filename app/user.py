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

    def isGoldZero(self) -> bool:
        return self.gold <= 0

    def incrementGratzAmount(self):
        self.gratz_amount = self.gratz_amount + 1

    def incrementGold(self):
        self.gold = self.gold + 1

    def decrementGold(self):
        self.gold = self.gold - 1

    def setUserId(self, user_id: str):
        self.user_id = user_id

    def setName(self, name: str):
        self.name = name

    def setGold(self, gold: int):
        self.gold = gold

    def setFarm(self, farm:int):
        self.farm = farm

    def setSavedDate(self, saved_date: int):
        self.saved_date = saved_date

    def getUserId(self) -> str:
        return self.user_id
    
    def getName(self) -> str:
        return self.name
    
    def getGold(self) -> int:
        return self.gold
    
    def getFarm(self) -> int:
        return self.farm
    
    def getSavedDate(self) -> int:
        return self.saved_date