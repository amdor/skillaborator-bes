from datetime import datetime, timedelta
from .one_time_code_service import one_time_code_service_instance

from flask import Response
from flask_restful import abort

from skillaborator.data_service import data_service_instance

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
        self.collection = data_service_instance.session_collection

    @staticmethod
    def __already_used():
        abort(Response('Session already used', status=401))

    def __create_new_session(self, session_id) -> Session:
        code = one_time_code_service_instance.find_one_time_code(session_id)
        if not code:
            abort(Response('Invalid session', status=404))
        if code.used:
            # somehow not in session collection, but already used
            SessionService.__already_used()

        session = Session(session_id, code.tags)
        insert_result = self.collection.insert_one(session.__dict__)
        if not insert_result.acknowledged:
            abort(Response('A server error occurred', status=500))
        one_time_code_service_instance.set_one_time_code_used(session_id)
        return session
    
    def get(self, session_id: str, new_session=False) -> Session:
        session_dict = self.collection.find_one({"session_id": session_id})
        if session_dict:
            if new_session:
                SessionService.__already_used()
            session = Session(session_id)
            session.parse_dict(session_dict)
            return session
        return self.__create_new_session(session_id)

    def get_demo_session(self) -> Session:
        demo_sesseion_id = one_time_code_service_instance.create_demo_one_time_code()
        session_dict = self.collection.find_one({"session_id": demo_sesseion_id})
        if session_dict:
            self.collection.delete_one({"session_id": demo_sesseion_id})
        return self.__create_new_session(demo_sesseion_id)

    def save(self, session: Session):
        session.next_timeout = datetime.now() + timedelta(minutes=1)
        self.collection.replace_one({"session_id": session.session_id}, session.__dict__)

    def end(self, session: Session):
        session.ended = True
        self.save(session)


session_service_instance = SessionService()