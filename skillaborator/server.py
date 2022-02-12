import traceback
from os import environ

from flask import Flask, Response
from flask_restful import Api
from pymongo.cursor import Cursor
from werkzeug.exceptions import HTTPException

from skillaborator.api.evaluator import Evaluator
from skillaborator.api.question import Question
from skillaborator.api.linkedin_auth import LinkedInAuth
from skillaborator.api.user_code import UserCode


# TODO: don't let errors out

app = Flask(__name__)
api = Api(app)

api.add_resource(Question, '/question/<one_time_code>', '/question')
api.add_resource(Evaluator, '/selectedAnswers/<one_time_code>')
api.add_resource(LinkedInAuth, '/linkedin-login')
api.add_resource(UserCode, '/new-code')
# api.add_resource(Codes, '/code')


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    if app.debug:
        track = traceback.format_exc()
        print(track)
    # now you're handling non-HTTP exceptions only
    return Response('Internal error occurred', status=500)


@app.after_request
def add_cors_after_request(response: Response):
    allow_origin = environ.get("ALLOW_ORIGIN", "http://localhost:4200")
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
