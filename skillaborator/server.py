from flask import Flask, Response
from flask_restful import Api

from skillaborator.evaluator import Evaluator
from skillaborator.question import Question

app = Flask(__name__)
api = Api(app)

api.add_resource(Question, '/question')
api.add_resource(Evaluator, '/selectedAnswers')


@app.after_request
def add_cors_after_request(response: Response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response


if __name__ == '__main__':
    app.run(debug=True)
