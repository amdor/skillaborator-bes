from flask import Flask, Response
from flask_restful import Api

from skillaborator.evaluator import Evaluator
from skillaborator.question import Question

# TODO: don't let errors out

app = Flask(__name__)
api = Api(app)

api.add_resource(Question, '/question')
api.add_resource(Evaluator, '/selectedAnswers')


@app.after_request
def add_cors_after_request(response: Response):
    # TODO this should come from config
    response.headers['Access-Control-Allow-Origin'] = 'http://api.app.localhost:4200'
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


if __name__ == '__main__':
    # TODO set run attributes by environment
    # app.run(debug=True, host="api.app.localhost", port=5000, ssl_context=('cert.pem', 'key.pem'))
    app.run(debug=True, host="api.app.localhost", port=5000)
