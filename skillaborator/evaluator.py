from flask import Response
from flask.json import loads
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service
from skillaborator.score_service import ScoreService
from skillaborator.answer_analysis_service import answer_analysis_service


class Evaluator(Resource):

    @staticmethod
    def __need_proper_answers():
        abort(Response('Selected answers provided are not sufficient', status=400))

    @staticmethod
    def get():
        """
        Post the selected answers for the questions, and get the right answers back in the response
        """
        parser = reqparse.RequestParser()

        parser.add_argument('currentScore', type=int, help='Current score of the user', location='cookies',
                            required=True)
        parser.add_argument(
            'questionId', type=str, help='Last question`s id', location='cookies', required=True)
        parser.add_argument('previousQuestionIds', type=str,
                            help='All previously answered questions', location='cookies')
        parser.add_argument('answerId', dest='answerIds', type=str, help='Last question`s chosen answers',
                            action='append')

        args = parser.parse_args(strict=True)

        final_score = args.get('currentScore')
        last_question_id = args.get('questionId')
        previous_question_ids = loads(args.get('previousQuestionIds'))
        last_question_answers = args.get('answerIds')

        if last_question_answers is None or final_score is None or last_question_id is None:
            Evaluator.__need_proper_answers()

        final_score = ScoreService.calculate_next_score(
            last_question_id, last_question_answers, final_score)
        answer_analysis_service.save_answer(
            last_question_id, last_question_answers)

        right_answers_by_questions = data_service.get_questions_right_answers(
            previous_question_ids)
        return {"rightAnswersByQuestions": right_answers_by_questions, "score": final_score}, 200
