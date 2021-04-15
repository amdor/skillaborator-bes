import random
import string

from flask.json import dumps
from pymongo import MongoClient, DESCENDING, collation

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'
ANSWER_COLLECTION = 'answer'
ONE_TIME_CODES_COLLECTION = 'one_time_codes'


class DataService:

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]
        self.answer_collection = self.db[ANSWER_COLLECTION]
        self.one_time_codes_collection = self.db[ONE_TIME_CODES_COLLECTION]


one_time_codes_to_insert = {"code_count": 1, "tags_to_use": []}

insert_answer = 0

answer_values = ["First",
                 "Second",
                 "Third",
                 "Fourth"]

question_value = "Select acceptable targeting"
question_level = 2
question_answers = ["9", "10", "11", "12"]
right_answers = ["10", ""]
tags = ['css']
code = {
    "value": """
.error {
  color: red !important;
}

.some-dialog {
  .error {
    color: red;
  }
}

#specificError{
  color: red;
}

.parent {
  .some-dialog {
    .list-item {
      .error {
        color: red;
      }
    }
  }
}""",
    "language": "css"
}


def get_id_for_collection(collection):
    numeric_collation = collation.Collation(
        locale="en_US", numericOrdering=True)
    ids = list(collection.find({}, {"id": 1, "_id": 0}, sort=[
        ("id", DESCENDING)], limit=1, collation=numeric_collation))
    return 0 if not ids else int(ids[0]["id"])


def insert_answer_or_question(_data_service):
    question_id = get_id_for_collection(_data_service.question_collection)

    if insert_answer:
        answer_id = get_id_for_collection(_data_service.answer_collection)
        for answer_value in answer_values:
            answer_id = answer_id + 1
            _data_service.answer_collection.insert_one(
                {"id": f"{answer_id}", "value": answer_value})
            print(f"\"{answer_id}\",", end=" ")
    else:
        question = {"id": f"{question_id + 1}",
                    "level": question_level,
                    "value": question_value,
                    "answers": question_answers,
                    "rightAnswers": right_answers,
                    "tags": tags}
        if code is not None:
            question["code"] = code
        print(dumps(question))
        _data_service.question_collection.insert_one(question)
        print(f"question id {question_id + 1}")


def add_tags(_data_service):
    u_result = _data_service.question_collection.update_many(
        {"id": {"$in": ["6", "7", "8"]}},
        {"$push": {"tags": {
            "$each": ["browser"]}}})
    print(f"{u_result.raw_result}")


def get_tags(_data_service):
    _tags = _data_service.question_collection.distinct("tags")
    print(f'{_tags}')


def insert_one_time_codes(_data_service):
    global_i = 0
    i = 0
    while i < one_time_codes_to_insert['code_count'] and global_i < 200:
        global_i = global_i + 1
        generated_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        code_already_used = list(_data_service.one_time_codes_collection.find({"code": generated_id}))
        if code_already_used:
            continue
        tags_to_use = one_time_codes_to_insert["tags_to_use"] if len(
            one_time_codes_to_insert["tags_to_use"]) else get_tags(
            _data_service)
        print(f'generated id: {generated_id}')
        one_time_code = {
            "code": generated_id,
            "tags": tags_to_use,
            "used": False
        }
        _data_service.one_time_codes_collection.insert_one(one_time_code)
        i = i + 1


if __name__ == '__main__':
    data_service = DataService()
    # insert_answer_or_question(data_service)
    # add_tags(data_service)
    # get_tags(data_service)
    insert_one_time_codes(data_service)
