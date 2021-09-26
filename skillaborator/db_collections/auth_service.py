from skillaborator.data_service import data_service

class AuthService:

    def __init__(self):
        self.collection = data_service.answer_analysis_collection

    def save_answer(self, question_id, answer_ids):
        for answer_id in answer_ids:
            self.collection.update_one(
                {
                    "question_id": question_id
                },
                {
                    "$inc": {
                        f"{answer_id}": 1  # {"$add": [0, f"${answer_id}", 1]}
                    }
                },
                upsert=True
            )


auth_service = AuthService()