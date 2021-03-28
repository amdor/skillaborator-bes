from pymongo import MongoClient, DESCENDING, collation

DB_NAME = 'skillaborator'
QUESTION_COLLECTION = 'question'
ANSWER_COLLECTION = 'answer'


class DataService:

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[DB_NAME]
        self.question_collection = self.db[QUESTION_COLLECTION]
        self.answer_collection = self.db[ANSWER_COLLECTION]


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
            data_service.answer_collection.insert_one(
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
