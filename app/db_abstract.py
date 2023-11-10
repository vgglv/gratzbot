from abc import ABC, abstractmethod

from app.user import GUser


class AbstractDatabase(ABC):
    def get_user(self, user_id: str, user_name: str) -> GUser:
        user = self.get_user_or_none(user_id)
        print(f"getting user {user_id}, value: {user}")
        if not user:
            print("user not exist, creating user...")
            user = self.create_user(user_id, user_name)
            print(f"created user: {user}")

        if "gold" not in user:
            user["gold"] = 0

        return GUser(
            user_id=user_id,
            name=user_name,
            gold=user["gold"],
            farm=user["farm"],
            saved_date=user["saved_date"]
        )

    @abstractmethod
    def get_user_or_none(self, user_id: str) -> dict[str, any]:
        pass

    @abstractmethod
    def update_user(self, user: GUser) -> None:
        pass

    @abstractmethod
    def create_user(self, user_id: str, name: str) -> dict[str, any]:
        pass

    @abstractmethod
    def get_all_users(self) -> dict[str, dict[str, any]]:
        pass

    @abstractmethod
    def set_gold_in_bank(self, gold: int) -> None:
        pass

    @abstractmethod
    def get_gold_from_bank(self) -> int:
        pass

    @abstractmethod
    def get_saved_lgbt_person(self) -> dict:
        pass

    @abstractmethod
    def set_lgbt_person(self, user_id: str, name: str, epoch_days: int) -> None:
        pass
