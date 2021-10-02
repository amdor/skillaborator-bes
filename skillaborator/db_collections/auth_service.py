from datetime import datetime, timedelta

from skillaborator.data_service import data_service

class AuthModel:
    def __init__(self):
        self.email = ""
        self.token = ""
        self.next_skillaboration: datetime = None

    def parse_dict(self, session_dict):
        for k, v in session_dict.items():
            self.__dict__[k] = v

class AuthService:

    def __init__(self):
        self.collection = data_service.auth_collection

    def save_login(self, email: str, access_token: str):
        self.collection.update_one(
            {
                "email": email
            },
            {
                "token": access_token
            },
            upsert=True
        )

    def save_skillaboration_start(self, email: str):
        self.collection.update_one(
            {
                "email": email
            },
            {
               "next_skillaboration": datetime.now() + timedelta(weeks=2) 
            }
        )

    
    def can_start_new_evaluation(self, email: str, token: str) -> bool:
        auth_dict = self.collection.find_one({"email": email, "token": token})
        if auth_dict is None:
            return False
        auth = AuthModel()
        auth.parse_dict(auth_dict)
        if auth.next_skillaboration is None:
            return False
        return datetime.now() > auth.next_skillaboration



auth_service: AuthService = AuthService()