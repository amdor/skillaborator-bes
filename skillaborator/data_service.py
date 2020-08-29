from pymongo import MongoClient

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'


class DataService:

    def __init__(self):
        # TODO getting url from config
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]

    @staticmethod
    def first_or_none(cursor):
        if cursor is None:
            return None
        c_list = list(cursor)
        if len(c_list) == 0:
            return None
        return c_list[0]

    def get_question_by_level(self, level: int):
        # get 1 random question matching the level, exclude _id field
        question = self.question_collection.aggregate([
            {"$match": {"level": level}},
            {"$sample": {"size": 1}},
            {"$project": {"_id": False}}
        ])
        return DataService.first_or_none(question)

    def is_answer_right(self, question_id: str, answer_id: str):
        # find question with id and answer with id answer_id, exclude _id field, set right to False by default
        answer_right = self.question_collection.find_one(
            {"id": question_id, "answers": {"$elemMatch": {"id": answer_id, "right": {"$eq": True}}}},
            {"_id": 0})
        return answer_right is not None
