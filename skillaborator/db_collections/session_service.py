from datetime import datetime, timedelta
import random
import string
from typing import Optional

from flask import Response
from flask_restful import abort

from skillaborator.data_service import data_service

ONE_TIME_CODE_COLLECTION = "one_time_codes"


class Session:
    def __init__(self, session_id, tags = []):
        self.session_id = session_id
        self.current_score = 0
        self.previous_question_ids = []
        self.selected_answers = []
        self.ended = False
        self.next_timeout = datetime.now() + timedelta(minutes=1)
        self.tags = tags

    def parse_dict(self, session_dict):
        for k, v in session_dict.items():
            self.__dict__[k] = v


class SessionService:
    def __init__(self):
        self.collection = data_service.session_collection
        self.one_time_code_collection = data_service.db[ONE_TIME_CODE_COLLECTION]

    @staticmethod
    def __already_used():
        abort(Response('Session already used', status=401))

    def __create_new_session(self, session_id) -> Session:
        code = self.one_time_code_collection.find_one({"code": session_id})
        if not code:
            abort(Response('Invalid session', status=404))
        if code["used"]:
            # somehow not in session collection, but already used
            SessionService.__already_used()

        session = Session(session_id, code["tags"])
        insert_result = self.collection.insert_one(session.__dict__)
        if insert_result.acknowledged:
            self.one_time_code_collection.update_one({"code": session_id}, {"$set": {"used": True}})
            return session
        return abort(Response('A server error occurred', status=500))

    def __insert_demo_one_time_code(self):
        generated_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        code_already_used = list(self.one_time_code_collection.find({"code": generated_id}))
        if code_already_used:
            self.one_time_code_collection.delete_one({"code": generated_id})
            self.collection.delete_one({"session_id": generated_id})
        tags_to_use = ["demo"]
        one_time_code = {
            "code": generated_id,
            "tags": tags_to_use,
            "used": False
        }
        insert_result = self.one_time_code_collection.insert_one(one_time_code)
        if insert_result.acknowledged:
            return generated_id
        return abort(Response('A server error occurred, could not create session id', status=500))

    def get(self, session_id: Optional[str], new_session=False) -> Session:
        if(session_id is None):
            demo_sesseion_id = self.__insert_demo_one_time_code()
            return self.__create_new_session(demo_sesseion_id)

        session_dict = self.collection.find_one({"session_id": session_id})
        if session_dict:
            if new_session:
                SessionService.__already_used()
            session = Session(session_id)
            session.parse_dict(session_dict)
            return session
        return self.__create_new_session(session_id)

    def save(self, session: Session):
        session.next_timeout = datetime.now() + timedelta(minutes=1)
        self.collection.replace_one({"session_id": session.session_id}, session.__dict__)

    def end(self, session: Session):
        session.ended = True
        self.save(session)


session_service = SessionService()
