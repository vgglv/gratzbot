import time

class GUser:
    def __init__(self, user_id: str, name: str, gratz_amount: int = 0, token: int = 5, farm: int = 1, saved_date: int = None) -> None:
        self.user_id = user_id
        self.name = name
        self.gratz_amount = gratz_amount
        self.token = token
        self.farm = farm
        if not saved_date:
            self.saved_date = int(time.time())
        else:
            self.saved_date = saved_date

    def isTokensZero(self) -> bool:
        return self.token <= 0

    def incrementGratzAmount(self):
        self.gratz_amount = self.gratz_amount + 1

    def incrementToken(self):
        self.token = self.token + 1

    def decrementToken(self):
        self.token = self.token - 1

    def setUserId(self, user_id: str):
        self.user_id = user_id

    def setName(self, name: str):
        self.name = name

    def setGratzAmount(self, gratz_amount:int):
        self.gratz_amount = gratz_amount

    def setToken(self, token:int):
        self.token = token

    def setFarm(self, farm:int):
        self.farm = farm

    def setSavedDate(self, saved_date: int):
        self.saved_date = saved_date

    def getUserId(self) -> str:
        return self.user_id
    
    def getName(self) -> str:
        return self.name
    
    def getGratzAmount(self) -> int:
        return self.gratz_amount
    
    def getToken(self) -> int:
        return self.token
    
    def getFarm(self) -> int:
        return self.farm
    
    def getSavedDate(self) -> int:
        return self.saved_date
