from flask import Response
from random import randint
from flask_restful import Resource, reqparse, abort

QUESTIONS = [
    {'id': '0', 'value': 'What is the difference between var and let?', 'level': 1, 'answers': [
        {'id': "0", 'value': "Answer1"},
        {'id': "1", 'value': "Answer2"},
        {'id': "2", 'value': "Answer2"},
        {
            'id': "3", 'value': """Answer
4 long multiline answer"""
        }
    ]},
    {'value': 'What is block scope?', 'level': 1},
    {'value': 'Is JavaScript object oriented?', 'level': 3},
    {'value': 'What is prototypical inheritance?', 'level': 2},
]


class Question(Resource):
    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400)) \

    @staticmethod
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
        filtered_questions = list(
            filter(lambda question: question['level'] == level, QUESTIONS))
        if len(filtered_questions) == 0:
            Question.__no_question_found()
        return filtered_questions[randint(1, len(filtered_questions)) - 1], 200

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('questionId', required=True)
        parser.add_argument('answerId', required=True)
        args = parser.parse_args(strict=True)
        questionId = args.get('questionId')
        answerId = args.get('questionId')
        if questionId is None or answerId is None:
            Question.__need_an_answer()
        # TODO: get right answer from db question - answer mapping
        # TODO: save answer for user session if there's any
        # TODO: set HTTPOnly cookie for session
        return '', 200


