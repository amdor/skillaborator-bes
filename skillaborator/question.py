from flask import request, Response
from random import randint
from flask_restful import Resource, reqparse, abort

QUESTIONS = [
    {'question': 'What is the difference between var and let?', 'level': 1},
    {'question': 'What is block scope?', 'level': 1},
    {'question': 'Is JavaScript object oriented?', 'level': 3},
    {'question': 'What is prototypical inheritance?', 'level': 2},
]


class Question(Resource):
    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400))

    @staticmethod
    def get():
        parser = reqparse.RequestParser()
        parser.add_argument('level', type=int, help='Level of the question')
        args = parser.parse_args(strict=True)
        level = args.get('level')
        if level is None:
            Question.__no_question_found()
        # get random question on that level
        filtered_questions = list(
            filter(lambda question: question['level'] == level, QUESTIONS))
        if len(filtered_questions) == 0:
            Question.__no_question_found()
        return filtered_questions[randint(1, len(filtered_questions))-1]['question']
