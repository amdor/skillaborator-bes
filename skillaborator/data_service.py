from pymongo import MongoClient

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'


class DataService:

    def __init__(self):
        # TODO getting url from config
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]

    def get_question_by_level(self, level:int):
        question = self.question_collection.aggregate([
            {"$match": {"level": level}},
            {"$sample": {"size": 1}},
            {"$project": {"_id": False}}
        ])
        question_list = list(question)
        if len(question_list) == 0:
            return None
        return question_list[0]
