import unittest
from unittest.mock import Mock

from skillaborator.collections.session_service import ONE_TIME_CODE_COLLECTION, SessionService


class Any(object):
    pass


class TestSessionService(unittest.TestCase):

    def setUp(self):
        session_collection_mock = Any()
        insert_result = Any()
        insert_result.acknowledged = True
        session_collection_mock.insert_one = Mock(return_value=insert_result)
        session_collection_mock.find_one = Mock(return_value=None)
        one_time_collection_mock = Any()
        one_time_collection_mock.find_one = Mock(return_value=None)
        db = {ONE_TIME_CODE_COLLECTION: one_time_collection_mock}
        service = SessionService()
        service.collection = session_collection_mock
        service.db = db
        self.service = service

    def test_existing(self):
        self.service.collection.find_one.return_value = {"session_id": "JBAXKY08", "current_score": 5,
                                                         "previous_question_ids": ["11"]}
        session = self.service.get("JBAXKY08")
        self.assertEqual(session.session_id, "JBAXKY08")
        self.assertEqual(5, session.current_score)
        self.assertEqual(session.previous_question_ids, ["11"])
