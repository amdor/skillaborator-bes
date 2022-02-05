from os import environ
from pymongo.cursor import Cursor
from skillaborator.db_collections.collection_consts import ANSWER_ANALYSIS_COLLECTION, ANSWER_COLLECTION, AUTH_COLLECTION, DB_NAME, ONE_TIME_CODE_COLLECTION, QUESTION_COLLECTION, SESSION_COLLECTION

from pymongo import MongoClient, collection

class DataService:

    def __init__(self):
        db_host = environ.get("DB_HOST", 'mongodb://localhost:27017/')
        self.client = MongoClient(db_host)
        self.db = self.client[DB_NAME]
        self.question_collection: collection.Collection = self.db[QUESTION_COLLECTION]
        self.answer_collection: collection.Collection = self.db[ANSWER_COLLECTION]
        self.answer_analysis_collection: collection.Collection = self.db[ANSWER_ANALYSIS_COLLECTION]
        self.session_collection: collection.Collection = self.db[SESSION_COLLECTION]
        self.one_time_code_collection: collection.Collection = self.db[ONE_TIME_CODE_COLLECTION]
        self.auth_collection: collection.Collection = self.db[AUTH_COLLECTION]

    @staticmethod
    def first_or_none(cursor: Cursor):
        if cursor is None:
            return None
        c_list = list(cursor)
        if len(c_list) == 0:
            return None
        return c_list[0]

data_service_instance = DataService()
