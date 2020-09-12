from flask import Response
from flask_restful import Resource, reqparse, abort
from skillaborator.data_service import DataService

data_service = DataService()


class Question(Resource):

    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400))

    @staticmethod
    def __need_an_answer():
        abort(Response('Need question id and answer id', status=400))

    # TODO: get next question with regards to previous answer(s)
    @staticmethod
    def get():
        """
        Get a random question on the level provided as url param
        """
        parser = reqparse.RequestParser()
        parser.add_argument('level', type=int, help='Level of the question', required=True)
        args = parser.parse_args(strict=True)
        level = args.get('level')
        if level is None:
            Question.__no_question_found()
        # get random question on that level
        random_question = data_service.get_question_by_level(level)
        if random_question is None:
            Question.__no_question_found()

        random_question['value'] = random_question['value'].replace('\\n', '\n').replace('\\t', '\t')
        if 'code' in random_question:
            random_question['code']['value'] = random_question['code']['value'].replace('\\n', '\n').replace('\\t', '\t')
        return random_question, 200

    @staticmethod
    def post():
        """
        Expects question ids and corresponding answer ids in request body, returns an array of correct answers' levels
        """
        parser = reqparse.RequestParser()
        parser.add_argument('questionIds', required=True, type=list, location="json")
        parser.add_argument('answerIds', required=True, type=list, location="json")
        args = parser.parse_args(strict=True)
        question_ids = args.get('questionIds')
        answer_ids = args.get('questionIds')
        if question_ids is None or answer_ids is None:
            Question.__need_an_answer()
        # get right answers from db question - answer mapping
        right_answer_levels = []
        for index, question_id in enumerate(question_ids):
            answer_id = answer_ids[index]
            answer = data_service.get_right_answer_level(question_id, answer_id)
            if answer is None:
                continue
            right_answer_levels.append(answer["level"])
        return right_answer_levels, 200
