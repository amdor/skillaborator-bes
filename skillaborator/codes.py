from flask_restful import Resource
from skillaborator.data_service import data_service

class Codes(Resource):
    def __init__(self):
        self.collection = data_service.db["one_time_codes"]

    def get(self):
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
        
        ret = list()
        for doc in cursor:
            ret.append(doc["code"])
        return ret[0]