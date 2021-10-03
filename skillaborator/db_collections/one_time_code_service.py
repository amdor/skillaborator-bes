import random
from typing import Optional
from skillaborator import data_service
from skillaborator.db_collections import question_service
import string
from flask_restful import abort
from pymongo.cursor import Cursor
from werkzeug.wrappers import Response
from skillaborator.data_service import DataService, data_service


class OneTimeCodeService:
    def __init__(self):
        self.collection = data_service.one_time_code_collection

    @staticmethod
    def __generate_id():
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

    def create_one_time_code(self, email: str) -> Optional[str]:
        tags = question_service.get_all_tags()
        correct_id_generated = False
        global_i = 0
        while correct_id_generated is False and global_i < 10:
            global_i = global_i + 1
            generated_id = OneTimeCodeService.__generate_id()
            code_already_used = list(self.collection.find({"code": generated_id}))
            if code_already_used:
                continue
            correct_id_generated = True
            one_time_code = {
                "code": generated_id,
                "tags": tags,
                "used": False,
                "offeredTo": email if email is not None else "B2C"
            }
            self.collection.insert_one(one_time_code)
            return generated_id

   
    def create_demo_one_time_code(self):
        generated_id = OneTimeCodeService.__generate_id()
        code_already_used = list(self.collection.find({"code": generated_id}))
        if code_already_used:
            self.collection.delete_one({"code": generated_id})
        tags_to_use = ["demo"]
        one_time_code = {
            "code": generated_id,
            "tags": tags_to_use,
            "used": False
        }
        insert_result = self.collection.insert_one(one_time_code)
        if not insert_result.acknowledged:
            abort(Response('A server error occurred, could not create session id', status=500))
        return generated_id

    def find_one_time_code(self, session_id: str):
        return self.collection.find_one({"code": session_id})
    
    def find_unused_code(self, offered_to: str):
        return self.collection.find_one({"offeredTo": offered_to, "used": False})

    def set_one_time_code_used(self, session_id: str):
        return self.collection.update_one({"code": session_id}, {"$set": {"used": True}})

    def get_one_time_code(self):
        cursor: Cursor = self.collection.aggregate([
            {"$match": {
                "used": False,
            }},
            {"$sample": {"size": 1}},
             {"$project": {
                "_id": False,
                "code": True,
            }}
        ])
        
        one_time_code = DataService.first_or_none(cursor)
        return one_time_code


one_time_code_service = OneTimeCodeService()