from skillaborator.data_service import data_service_instance


class AnswerAnalysisService:

    def __init__(self):
        self.collection = data_service_instance.answer_analysis_collection

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


answer_analysis_service_instance = AnswerAnalysisService()
