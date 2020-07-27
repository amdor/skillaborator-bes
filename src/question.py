from flask import Flask, request
from random import randint
from flask_restful import Resource

QUESTIONS = [
    {'question': 'What is the difference between var and let?', 'level': 1},
    {'question': 'What is block scope?', 'level': 1},
    {'question': 'Is JavaScript object oriented?', 'level': 3},
    {'question': 'What is prototypical inheritance?', 'level': 2},
]


class Question(Resource):
    def get(self):
        level = request.args.get('level')
        # get random question on that level
        filtered_questions = list(
            filter(lambda question: question.level == level, QUESTIONS))
        return filtered_questions[randint(1, len(filtered_questions))]
