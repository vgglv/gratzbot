import csv
import os
from pathlib import Path
import time
from typing import Callable
import pandas as pd
from app.db_abstract import AbstractDatabase
from app.user import GUser

# pip3 install pandas
# or
# pip.exe install pandas
class CSVDatabase(AbstractDatabase):
    def __init__(self):
        csv_dir = 'csv'
        self.users_csv_path = f'{csv_dir}/users.csv'
        self.bank_csv_path = f'{csv_dir}/bank.csv'
        self.lgbt_person_csv_path = f'{csv_dir}/lgbt_person.csv'
        self.lgbt_stats_csv_path = f'{csv_dir}/lgbt_stats.csv'

        if not Path(csv_dir).is_dir():
            os.mkdir(csv_dir)

        if not Path(f'{self.users_csv_path}').is_file():
            df = pd.DataFrame(columns = ['key', 'user_id', 'name', 'gold', 'farm', 'saved_date']).set_index('key')
            df.to_csv(self.users_csv_path, quoting=csv.QUOTE_NONNUMERIC)
        if not Path(f'{self.bank_csv_path}').is_file():
            self.__set_gold_in_bank(0)
        if not Path(f'{self.lgbt_person_csv_path}').is_file():
            dict = {0: {'name': 'unknown', 'epoch_days': 0}}
            self.__save_dict_as_csv(dict, self.lgbt_person_csv_path)
        if not Path(f'{self.lgbt_stats_csv_path}').is_file():
            df = pd.DataFrame(columns = ['key', 'user_id', 'name', 'count']).set_index('key')
            df.to_csv(self.lgbt_stats_csv_path, quoting=csv.QUOTE_NONNUMERIC)
    
    def get_user_or_none(self, user_id: str) -> dict[str, any]:
        _dict = self.__get_users_dict()
        return _dict.get(user_id, None)

    def update_user(self, user: GUser) -> None:
        _dict = self.__get_users_dict()
        existing_user = _dict.get(user.user_id, None)
        if existing_user:
            existing_user['user_id'] = user.user_id
            existing_user['name'] = user.name
            existing_user['gold'] = user.gold
            existing_user['farm'] = user.farm
            existing_user['saved_date'] = user.saved_date
            _dict[user.user_id] = existing_user
            self.__save_users_dict(_dict)

    def create_user(self, user_id: str, name: str) -> dict[str, any]:
        current_timestamp = int(time.time())
        user_data = {
            'user_id': user_id,
            'name': name,
            'gold': 5,
            'farm': 1,
            'saved_date': current_timestamp
        }
        _dict = self.__get_users_dict()
        _dict[user_id] = user_data.copy()
        self.__save_users_dict(_dict)
        return user_data

    def get_all_users(self) -> dict[str, dict[str, any]]:
        return self.__get_users_dict()

    def set_gold_in_bank(self, gold: int) -> None:
        self.__set_gold_in_bank(gold)

    def get_gold_from_bank(self) -> int:
        return self.__get_gold_from_bank()

    def get_saved_lgbt_person(self) -> dict:
        return self.__get_saved_lgbt_person()

    def set_lgbt_person(self, user_id: str, name: str, epoch_days: int) -> None:
        self.__set_lgbt_person(user_id, name, epoch_days)

    
    # private methods below


    def __get_csv_as_dict(self, path: str, keyConverter: Callable) -> dict[any, dict[str, any]]:
        # use str or int for keyConverter depending on key type
        return pd.read_csv(path,
                           quoting=csv.QUOTE_NONNUMERIC,
                           converters={'key': keyConverter}).convert_dtypes().set_index('key').to_dict(orient='index')

    def __save_dict_as_csv(self, d: dict, path: str) -> None:
        _dict = {}
        for key, value in d.items():
            _dict[key] = value
            _dict[key]['key'] = key
        df = pd.DataFrame().from_dict(_dict, orient='index').set_index('key')
        df.to_csv(path, quoting=csv.QUOTE_NONNUMERIC)

    def __get_users_dict(self) -> dict[str, dict[str, any]]:
        return self.__get_csv_as_dict(self.users_csv_path, str)

    def __save_users_dict(self, d: dict) -> None:
        self.__save_dict_as_csv(d, self.users_csv_path)
    
    def __get_gold_from_bank(self) -> int:
        _dict = self.__get_csv_as_dict(self.bank_csv_path, int)
        return int(_dict[0]['amount'])

    def __set_gold_in_bank(self, gold: int) -> None:
        _dict = {0: {'amount': gold}}
        self.__save_dict_as_csv(_dict, self.bank_csv_path)
    
    def __get_saved_lgbt_person(self) -> dict[str, any]:
        dict = self.__get_csv_as_dict(self.lgbt_person_csv_path, int)
        return dict[0]

    def __set_lgbt_person(self, user_id: str, name: str, epoch_days: int) -> None:
        lgbt_person_dict = {0: {'name': name, 'epoch_days': epoch_days}}
        self.__save_dict_as_csv(lgbt_person_dict, self.lgbt_person_csv_path)

        lgbt_stats_dict = self.__get_csv_as_dict(self.lgbt_stats_csv_path, str)
        record = lgbt_stats_dict.get(user_id, None)
        if not record:
            record = {'user_id': user_id, 'name': name, 'count': 1}
        else:
            record['name'] = name
            record['count'] += 1
        lgbt_stats_dict[user_id] = record
        self.__save_dict_as_csv(lgbt_stats_dict, self.lgbt_stats_csv_path)
