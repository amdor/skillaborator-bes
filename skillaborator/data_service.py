from os import environ
from typing import Optional, Union, List, Dict

from pymongo import MongoClient

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'
ANSWER_COLLECTION = 'answer'
ANSWER_ANALYSIS_COLLECTION = 'answer_analysis'
SESSION_COLLECTION = 'session'


class DataService:

    def __init__(self):
        db_host = environ.get("DB_HOST", 'mongodb://localhost:27017/')
        self.client = MongoClient(db_host)
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]
        self.answer_collection = self.db[ANSWER_COLLECTION]
        self.answer_analysis_collection = self.db[ANSWER_ANALYSIS_COLLECTION]
        self.session_collection = self.db[SESSION_COLLECTION]

    def __get_partial_question(self, question_id: str, right_answers=0, level=0):
        return self.question_collection.find_one(
            {"id": question_id},
            {"_id": 0, "rightAnswers": right_answers, "level": level})

    def __replace_answers_in_question(self, question: Dict):
        """
        Finds answers in collection by ids and replaces the original id array in questions with answer dicts
        """
        answers = self.answer_collection.find(
            {"id": {"$in": question.get("answers", list())}},
            {"_id": 0}
        )
        if answers is None:
            return None
        question["answers"] = list(answers)

    @staticmethod
    def first_or_none(cursor):
        if cursor is None:
            return None
        c_list = list(cursor)
        if len(c_list) == 0:
            return None
        return c_list[0]

    def get_question_by_level(self, level: int, previous_question_ids: List[str], tags: Optional[List[str]]):
        """
        Gets 1 random question matching the level, not matching previous ids
        Computes multi field (true if question has multiple right answers)
        Excludes _id and rightAnswers fields
        Maps answer ids to answers
        """
        question_cursor = self.question_collection.aggregate([
            {"$match": {
                "level": level,
                "id": {"$nin": previous_question_ids},
                "tags": {"$in": tags}
            }},
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
        self.__replace_answers_in_question(random_question)
        return random_question

    def get_question_right_answers_and_level(self, question_id: str):
        return self.__get_partial_question(question_id, right_answers=1, level=1)

    def get_questions_right_answers(self, question_ids: List[str]) -> Union[Dict[str, List[str]], None]:
        questions = self.question_collection.find(
            {"id": {"$in": question_ids}},
            {"_id": 0, "rightAnswers": 1, "id": 1})
        if questions is None:
            return None
        questions = list(questions)
        if not questions:
            return None
        # return a dict of question id keys and all the non empty right answers, right answer might be None to create
        # fake multi choice
        return {question.get("id"): [rightAnswer for rightAnswer in question.get("rightAnswers") if rightAnswer] for
                question in questions}

    def get_questions(self, question_ids: List[str]):
        questions = self.question_collection.find(
            {"id": {"$in": question_ids}},
            {"_id": 0, "rightAnswers": 1, "id": 1, "value": 1, "answers": 1, "code": 1, })
        if questions is None:
            return None
        questions = list(questions)
        if not questions:
            return None
        for question in questions:
            self.__replace_answers_in_question(question)
            question["multi"] = len(question["rightAnswers"]) > 1
            question["rightAnswers"] = [rightAnswer for rightAnswer in question.get("rightAnswers") if rightAnswer]
        return questions


data_service = DataService()
