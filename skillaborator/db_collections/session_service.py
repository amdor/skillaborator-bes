from datetime import datetime, timedelta

from flask import Response
from flask_restful import abort

from skillaborator.data_service import data_service

ONE_TIME_CODE_COLLECTION = "one_time_codes"


class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.current_score = 0
        self.previous_question_ids = []
        self.selected_answers = []
        self.ended = False
        self.next_timeout = datetime.now() + timedelta(minutes=1)

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

        session = Session(session_id)
        insert_result = self.collection.insert_one(session.__dict__)
        if insert_result.acknowledged:
            self.one_time_code_collection.update_one({"code": session_id}, {"$set": {"used": True}})
            return session
        return abort(Response('A server error occurred', status=500))

    def get(self, session_id: str, new_session=False) -> Session:
        session_dict = self.collection.find_one({"session_id": session_id})
        if session_dict:
            if new_session:
                SessionService.__already_used()
            session = Session(session_id)
            session.parse_dict(session_dict)
            return session
        # TODO check used in one time collection
        return self.__create_new_session(session_id)

    def save(self, session: Session):
        session.next_timeout = datetime.now() + timedelta(minutes=1)
        self.collection.replace_one({"session_id": session.session_id}, session.__dict__)

    def end(self, session: Session):
        session.ended = True
        self.save(session)


session_service = SessionService()
