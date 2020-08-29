from flask import Flask, Response
from flask_restful import Api
from skillaborator.question import Question

app = Flask(__name__)
api = Api(app)

api.add_resource(Question, '/question')


@app.after_request
def add_cors_after_request(response: Response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    return response


if __name__ == '__main__':
    app.run(debug=True)