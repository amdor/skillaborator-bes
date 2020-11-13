from typing import Union

from pymongo import MongoClient

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'
ANSWER_COLLECTION = 'answer'


class DataService:

    def __init__(self):
        # TODO getting url from config
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]
        self.answer_collection = self.db[ANSWER_COLLECTION]

    @staticmethod
    def first_or_none(cursor):
        if cursor is None:
            return None
        c_list = list(cursor)
        if len(c_list) == 0:
            return None
        return c_list[0]

    def get_question_by_level(self, level: int):
        """
        Get 1 random question matching the level, exclude _id field
        Maps answer ids to answers
        Computes multi field (true if question has multiple right answers)
        """
        question_cursor = self.question_collection.aggregate([
            {"$match": {"level": level}},
            {"$sample": {"size": 1}},
            {"$addFields": {
                "multi": {
                    "$cond": {
                        "if": {"$gt": [{"$size": "$rightAnswers"}, 1]}, "then": True,
                        "else": False
                    }
                }
            }},
            {"$project": {
                "_id": False,
                "rightAnswers": False,
            }}
        ])
        random_question = DataService.first_or_none(question_cursor)
        if random_question is None:
            return None
        answers = self.answer_collection.find(
            {"id": {"$in": random_question.get("answers", list())}},
            {"_id": False}
        )
        if answers is None:
            return None
        random_question["answers"] = list(answers)
        return random_question

    def get_right_answers_for_question(self, question_id: str) -> Union[list, None]:
        question = self.question_collection.find_one(
            {"id": question_id},
            {"_id": 0, "rightAnswers": 1})
        if question is None or "rightAnswers" not in question:
            return None
        return question["rightAnswers"]


data_service = DataService()
