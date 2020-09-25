from abc import ABCMeta, abstractmethod

import toml
from pymongo import MongoClient


class Database(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def add_search_queue(cls):
        pass

    @classmethod
    @abstractmethod
    def get_search_queue(cls):
        pass

    @classmethod
    @abstractmethod
    def update_search_queue(cls):
        pass

    @classmethod
    @abstractmethod
    def delete_table(cls):
        pass


class Mongodb(Database):
    def __init__(self, database, conf):
        self.__db = database
        self.__config = conf

    def add_search_queue(self, search_id: str) -> None:
        self.__collection = self.__db.get_collection(self.__config['database']['mongodb']['search_queue'])

        post = {
            'hashid': search_id,
            'status': 0,
            'answer': None
        }

        self.__collection.insert_one(post)

    def get_search_queue(self, search_id: str):
        self.__collection = self.__db.get_collection(self.__config['database']['mongodb']['search_queue'])

        cur = self.__collection.find_one({"hashid": search_id})

        return cur

    def update_search_queue(self, search_id: str, answerid: int):
        self.__collection = self.__db.get_collection(self.__config['database']['mongodb']['search_queue'])

        post_origin = {
            'hashid': search_id,
            'status': 0,
            'answerid': None
        }

        post_edited = {
            'hashid': search_id,
            'status': 1,
            'answer': answerid
        }

        self.__collection.update_one(post_origin, post_edited)

    def delete_table(self):
        self.__db.drop_collection(str(self.__config['database']['mongodb']['search']))


class MongodbFactory():
    def __init__(self):
        self.__client = None
        self.__db = None

    def connect_database(self):
        self.__config = toml.load(open('audearch-config.toml'))

        self.__client = MongoClient(host=self.__config['database']['mongodb']['host'], port=int(self.__config['database']['mongodb']['port']))
        self.__db = self.__client[self.__config['database']['mongodb']['dbname']]

        self.__database = Mongodb(self.__db, self.__config)

        return self.__database
