from typing import Optional

from skillaborator.data_service import data_service

ONE_TIME_CODE_COLLECTION = "one_time_codes"


class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.current_score = 0
        self.previous_question_ids = []

    def parse_dict(self, session_dict):
        for k, v in session_dict.items():
            self.__dict__[k] = v


class SessionService:
    def __init__(self):
        self.collection = data_service.session_collection
        self.one_time_code_collection = data_service.db[ONE_TIME_CODE_COLLECTION]

    def __create_new_session(self, session_id) -> Optional[Session]:
        code = self.one_time_code_collection.find_one({"code": session_id})
        if not code:
            return None
        session = Session(session_id)
        insert_result = self.collection.insert_one(session.__dict__)
        if insert_result.acknowledged:
            return session
        return None

    def get(self, session_id) -> Optional[Session]:
        session_dict = self.collection.find_one({"session_id": session_id})
        if session_dict:
            session = Session(session_id)
            session.parse_dict(session_dict)
            return session
        return self.__create_new_session(session_id)

    def save(self, session: Session):
        self.collection.replace_one({"session_id": session.session_id}, session.__dict__)


session_service = SessionService()
