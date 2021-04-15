from flask import Flask, Response
from flask_restful import Api

from skillaborator.evaluator import Evaluator
from skillaborator.question import Question
from os import environ

# TODO: don't let errors out

app = Flask(__name__)
api = Api(app)

api.add_resource(Question, '/question/<one_time_code>')
api.add_resource(Evaluator, '/selectedAnswers/<one_time_code>')


@app.after_request
def add_cors_after_request(response: Response):
    allow_origin = environ.get("ALLOW_ORIGIN", "http://api.app.localhost:4200")
    response.headers['Access-Control-Allow-Origin'] = allow_origin
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


if __name__ == '__main__':
    # app.run(debug=True, host="api.app.localhost", port=5000, ssl_context=('cert.pem', 'key.pem'))
    host = environ.get("SERVER_HOST", "api.app.localhost")
    app.run(debug=True, host=host)
