from pymongo import MongoClient, DESCENDING, collation

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


insert_answer = 0

answer_values = ["Header Translating Transfer Protocol",
                 "HyperText Transfer Protocol",
                 "Host Tracing Transfer Protocol",
                 "High-level Text Transfer Protocol"]

question_value = "What does HTTP stand for?"
question_level = 1
question_answers = ["74", "75", "76", "77"]
right_answers = ["75"]
tags = ['http', 'browser']
code = None


def insert_answer_or_question(_data_service):
    numeric_collation = collation.Collation(locale="en_US", numericOrdering=True)
    question_id = int(
        list(
            _data_service.question_collection.find({}, {"id": 1, "_id": 0}, sort=[("id", DESCENDING)], limit=1,
                                                   collation=numeric_collation)
        )[0]["id"]
    )
    answer_id = int(
        list(
            _data_service.answer_collection.find({}, {"id": 1, "_id": 0}, sort=[("id", DESCENDING)], limit=1,
                                                 collation=numeric_collation)
        )[0]["id"]
    )

    if insert_answer:
        for answer_value in answer_values:
            answer_id = answer_id + 1
            data_service.answer_collection.insert_one({"id": f"{answer_id}", "value": answer_value})
            print(f"answer id {answer_id}")
    else:
        question = {"id": f"{question_id + 1}",
                    "level": question_level,
                    "value": question_value,
                    "answers": question_answers,
                    "rightAnswers": right_answers,
                    "tags": tags}
        if code is not None:
            question["code"] = code
        data_service.question_collection.insert_one(question)
        print(f"question id {question_id + 1}")


def add_tags(_data_service):
    u_result = _data_service.question_collection.update_many(
        {"id": {"$in": ["6", "7", "8"]}},
        {"$push": {"tags": {
            "$each": ["browser"]}}})
    print(f"{u_result.raw_result}")


def get_tags(_data_service):
    _tags = data_service.question_collection.distinct("tags")
    print(f'{_tags}')


if __name__ == '__main__':
    data_service = DataService()
    insert_answer_or_question(data_service)
    # add_tags(data_service)
    # get_tags(data_service)
