from flask import Response
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service


class Evaluator(Resource):

    @staticmethod
    def __need_proper_answers():
        abort(Response('Selected answers provided are not sufficient', status=400))

    # TODO: save question and selected answer for analyzis
    @staticmethod
    def post():
        """
        Post the selected answers for the questions, and get the right answer back in the response
        """
        parser = reqparse.RequestParser()
        parser.add_argument('selectedAnswers', required=True, type=list, location="json")
        args = parser.parse_args(strict=True)
        selected_answers = args.get('selectedAnswers')
        if selected_answers is None:
            Evaluator.__need_proper_answers()
        for index, selectedAnswer in enumerate(selected_answers):
            right_answer_id = data_service.get_right_answer_for_question(selectedAnswer['questionId'])
            selected_answers[index]['rightAnswerId'] = right_answer_id
        return selected_answers, 200
