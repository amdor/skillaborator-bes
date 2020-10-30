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
        """
        Get 1 random question matching the level, exclude _id field
        """
        question = self.question_collection.aggregate([
            {"$match": {"level": level}},
            {"$sample": {"size": 1}},
            {"$project": {"_id": False}}
        ])
        return DataService.first_or_none(question)

    def get_right_answer_level(self, question_id: str, answer_id: str):
        """
        If the answer for `answer_id` to the question for `question_id` is correct return the question level.
        Otherwise `None`
        :param question_id: question's id field
        :param answer_id: answer's id field
        :return: question level or `None`
        """
        question = self.question_collection.find_one(
            {"id": question_id},
            {"_id": 0, "level": 1, "answers": 1})
        if question is None:
            return None
        for answer_iter in question["answers"]:
            if answer_iter["id"] is answer_id:
                answer = answer_iter
                break
        if "right" not in answer or answer["right"] is not True:
            return None
        return {"level": question["level"]}

    def get_right_answer_for_question(self, question_id: str):
        question = self.question_collection.find_one(
            {"id": question_id},
            {"_id": 0, "answers": 1})
        if question is None:
            return ''
        for answer in question["answers"]:
            if answer.get('right') is True:
                return answer['id']
        return ''


data_service = DataService()
