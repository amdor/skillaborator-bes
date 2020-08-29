from flask import Response
from flask_restful import Resource, reqparse, abort
from skillaborator.data_service import DataService

data_service = DataService()


class Question(Resource):

    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400)) \
 \
        @ staticmethod

    def __need_an_answer():
        abort(Response('Need question id and answer id', status=400))

    @staticmethod
    def get():
        parser = reqparse.RequestParser()
        parser.add_argument('level', type=int, help='Level of the question', required=True)
        args = parser.parse_args(strict=True)
        level = args.get('level')
        if level is None:
            Question.__no_question_found()
        # get random question on that level
        filtered_question = data_service.get_question_by_level(level)
        if filtered_question is None:
            Question.__no_question_found()
        return filtered_question, 200

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('questionId', required=True)
        parser.add_argument('answerId', required=True)
        args = parser.parse_args(strict=True)
        question_id = args.get('questionId')
        answer_id = args.get('answerId')
        if question_id is None or answer_id is None:
            Question.__need_an_answer()
        # TODO: get right answer from db question - answer mapping
        answer = data_service.is_answer_right(question_id, answer_id)

        if answer is None:
            return "Wrong parameters", 400
        # TODO: not the right answer
        if answer is None:
            return "", 200
        # TODO: save answer for user session if there's any
        # TODO: set HTTPOnly cookie for session
        return answer, 200
