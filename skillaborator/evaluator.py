from flask import Response
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service
from skillaborator.score_service import ScoreService


class Evaluator(Resource):

    @staticmethod
    def __need_proper_answers():
        abort(Response('Selected answers provided are not sufficient', status=400))

    # TODO: save question and selected answer for analyzis
    @staticmethod
    def post():
        """
        Post the selected answers for the questions, and get the right answers back in the response
        """
        parser = reqparse.RequestParser()

        parser.add_argument('currentScore', type=int, help='Current score of the user', location='cookies',
                            required=True)
        parser.add_argument('questionId', type=str, help='Last question`s id', location='cookies', required=True)

        parser.add_argument('selectedAnswers', required=True, type=list, location="json")
        args = parser.parse_args(strict=True)

        selected_answers = args.get('selectedAnswers')
        final_score = args.get('currentScore')
        last_question_id = args.get('questionId')

        answered_questions_ids = []
        if selected_answers is None or final_score is None or last_question_id is None:
            Evaluator.__need_proper_answers()

        for index, selected_answer in enumerate(selected_answers):
            question_id = selected_answer.get('questionId')
            if question_id is None:
                Evaluator.__need_proper_answers()
            # get final score
            if question_id == last_question_id:
                selected_answer_ids = selected_answer.get('answerIds')
                if selected_answer_ids is None:
                    Evaluator.__need_proper_answers()
                final_score = ScoreService.calculate_next_score(question_id, selected_answer_ids, final_score)
            answered_questions_ids.append(question_id)

        right_answers_by_question = data_service.get_questions_right_answers(answered_questions_ids)
        for index, selected_answer in enumerate(selected_answers):
            selected_answers[index]['rightAnswerIds'] = right_answers_by_question.get(selected_answer.get('questionId'))
        return {"selectedAndRightAnswers": selected_answers, "score": final_score}, 200
