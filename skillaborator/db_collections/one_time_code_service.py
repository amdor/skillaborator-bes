from ast import Str
from curses import raw
import random
from typing import Optional
import string
from flask_restful import abort
from pymongo.cursor import Cursor
from werkzeug.wrappers import Response
from skillaborator.data_service import DataService, data_service_instance

class OneTimeCode:
    def __init__(self, code='', tags=[], used=False, offeredTo=None):
        self.code:str = code
        self.tags: list[str] = tags
        self.used: bool = used
        self.offeredTo: str = offeredTo

    def parse_dict(self, code_dict: dict):
        for k, v in code_dict.items():
            self.__dict__[k] = v


class OneTimeCodeService:
    def __init__(self):
        self.collection = data_service_instance.one_time_code_collection

    @staticmethod
    def __generate_id():
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

    def create_one_time_code(self, email: str) -> str   :
        tags = self.get_all_tags()
        correct_id_generated = False
        global_i = 0
        while correct_id_generated is False and global_i < 10:
            global_i = global_i + 1
            generated_id = OneTimeCodeService.__generate_id()
            code_already_used = list(self.collection.find({"code": generated_id}))
            if code_already_used:
                continue
            correct_id_generated = True
            one_time_code = OneTimeCode(generated_id, tags, False, offeredTo=email if email is not None else "B2C")
            self.collection.insert_one(one_time_code.__dict__)
            return one_time_code

   
    def create_demo_one_time_code(self) -> Str:
        generated_id = OneTimeCodeService.__generate_id()
        code_already_used = list(self.collection.find({"code": generated_id}))
        if code_already_used:
            self.collection.delete_one({"code": generated_id})
        tags_to_use = ["demo"]
        one_time_code = OneTimeCode(code=generated_id, tags=tags_to_use, used=False, offeredTo="demo")
        insert_result = self.collection.insert_one(one_time_code.__dict__)
        if not insert_result.acknowledged:
            abort(Response('A server error occurred, could not create session id', status=500))
        return generated_id

    def find_one_time_code(self, session_id: str) -> Optional[OneTimeCode]:
        raw_code = self.collection.find_one({"code": session_id})
        return self.parse_raw_code(raw_code)

    
    def find_unused_code(self, offered_to: str) -> Optional[OneTimeCode]:
        raw_code = self.collection.find_one({"offeredTo": offered_to, "used": False})
        return self.parse_raw_code(raw_code)

    def set_one_time_code_used(self, session_id: str):
        return self.collection.update_one({"code": session_id}, {"$set": {"used": True}})

    def get_one_time_code(self) -> Optional[OneTimeCode]:
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
        return self.parse_raw_code(one_time_code)
    
    def get_all_tags(self):
        return data_service_instance.question_collection.distinct("tags")

    def parse_raw_code(self, raw_code) -> Optional[OneTimeCode]:
        if not raw_code:
            return None
        one_time_code = OneTimeCode()
        one_time_code.parse_dict(raw_code)
        return one_time_code


one_time_code_service_instance = OneTimeCodeService()