from flask import Response, make_response
from flask.json import loads, dumps
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service
from skillaborator.score_service import ScoreService
from skillaborator.answer_analysis_service import answer_analysis_service


class Question(Resource):

    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400))

    @staticmethod
    def __format_question_texts(question):
        question['value'] = question['value'].replace(
            '\\n', '\n').replace('\\t', '\t')
        if 'code' in question:
            question['code']['value'] = question['code']['value'].replace(
                '\\n', '\n').replace('\\t', '\t')

    # TODO add 'neither' answer dynamically
    @staticmethod
    def get():
        """
        Get a random question calculated by the last question's level
        """
        parser = reqparse.RequestParser()

        parser.add_argument('currentScore', type=int,
                            help='Current score of the user', location='cookies')
        parser.add_argument('questionId', type=str,
                            help='Last question`s id', location='cookies')

        parser.add_argument('answerId', dest='answerIds', type=str, help='Last question`s chosen answers',
                            action='append')
        parser.add_argument('previousQuestionIds', type=str,
                            help='All previously answered questions', location='cookies')

        args = parser.parse_args(strict=True)
        current_score = args.get('currentScore')
        last_question_id = args.get('questionId')
        last_question_answers = args.get('answerIds')
        previous_question_ids = loads(args.get('previousQuestionIds') or "[]")

        # answer received, calculate next score if can
        if last_question_answers is not None and len(last_question_answers) != 0:
            if last_question_id is None:
                Question.__no_question_found()
            else:
                current_score = ScoreService.calculate_next_score(last_question_id, last_question_answers,
                                                                  current_score)
                answer_analysis_service.save_answer(
                    last_question_id, last_question_answers)
        else:
            current_score = 0
            previous_question_ids = []

        next_level = ScoreService.calculate_next_question_level(current_score)
        # get random question on that level
        random_question = data_service.get_question_by_level(
            next_level, previous_question_ids)
        if random_question is None:
            Question.__no_question_found()
        Question.__format_question_texts(random_question)

        previous_question_ids.append(random_question.get("id"))

        response: Response = make_response(random_question, 200)
        # TODO setcookie domain only for dev
        response.set_cookie(key='currentScore', value=f'{current_score}', httponly=True,
                            domain="api.app.localhost")
        response.set_cookie(key='questionId', value=f'{random_question.get("id")}', httponly=True,
                            domain="api.app.localhost")
        response.set_cookie(key='previousQuestionIds',
                            value=f'{dumps(previous_question_ids, separators=(",", ":"))}',
                            httponly=True,
                            domain="api.app.localhost")

        return response
