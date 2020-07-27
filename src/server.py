from flask import Flask
from flask_restful import Api
from question import Question

app = Flask(__name__)
api = Api(app)

api.add_resource(Question, '/question')


if __name__ == '__main__':
    app.run(debug=True)
