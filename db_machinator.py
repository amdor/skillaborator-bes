import random
import string

from flask.json import dumps
from pymongo import MongoClient, DESCENDING, collation
from ssl import CERT_NONE

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'
ANSWER_COLLECTION = 'answer'
ONE_TIME_CODES_COLLECTION = 'one_time_codes'
SESSION_COLLECTION = 'session'


class DataService:

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]
        self.answer_collection = self.db[ANSWER_COLLECTION]
        self.one_time_codes_collection = self.db[ONE_TIME_CODES_COLLECTION]
        self.session_collection = self.db[SESSION_COLLECTION]


one_time_codes_to_insert = {"code_count": 20, "tags_to_use": [], "offered_to": "violet consulting"}

insert_answer = 0

answer_values = ["The script will be fetched in parallel to document parsing",
"The script will be evalutated as soon as available",
"The script will be evaluated after document parsing",
"The script will be fetched blocking document parsing"]

question_value = "List all true for this HTML snippet."
question_level = 3
question_answers = ["91", "92", "93", "94"]
right_answers = ["91", "93"]
tags = ['html']

# code = None


code = {
    "value": """<head>
    <script type="text/javascript" src="es5-javascript.js" defer>
    </script>
</head>""",
    "language": "html"
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
    return _tags


def insert_one_time_codes(_data_service: DataService):
    global_i = 0
    i = 0
    while i < one_time_codes_to_insert['code_count'] and global_i < 200:
        global_i = global_i + 1
        generated_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        code_already_used = list(_data_service.one_time_codes_collection.find({"code": generated_id}))
        if code_already_used:
            continue
        tags_to_use = one_time_codes_to_insert["tags_to_use"] if len(
            one_time_codes_to_insert["tags_to_use"]) > 0 else get_tags(
            _data_service)
        print(f'generated id: {generated_id}')
        one_time_code = {
            "code": generated_id,
            "tags": tags_to_use,
            "used": False
        }
        offered_to = one_time_codes_to_insert["offered_to"]
        if offered_to is not None:
            one_time_code["offeredTo"] = offered_to
        _data_service.one_time_codes_collection.insert_one(one_time_code)
        i = i + 1


def remove_sessions(_data_service: DataService):
    _data_service.session_collection.delete_many({})

def remove_used_one_time_codes(_data_service: DataService):
    _data_service.one_time_codes_collection.delete_many({})

def remove_demo_sessions_and_one_time_codes(_data_service: DataService):
    demo_query = {"tags": {"$in": ["demo"]}}
    _data_service.one_time_codes_collection.delete_many(demo_query)
    _data_service.session_collection.delete_many(demo_query)


if __name__ == '__main__':
    data_service = DataService()
    # insert_answer_or_question(data_service)
    # add_tags(data_service)
    # get_tags(data_service)
    # insert_one_time_codes(data_service)
    # remove_sessions(data_service)
    # remove_demo_sessions_and_one_time_codes(data_service)
    # remove_used_one_time_codes(data_service)
    

    ids = data_service.one_time_codes_collection.find({"offeredTo": "grafton"}).distinct("code")
    for id in ids:
        print(id)