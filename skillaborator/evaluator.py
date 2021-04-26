from flask import Response
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service
from skillaborator.db_collections.answer_analysis_service import answer_analysis_service
from skillaborator.db_collections.session_service import session_service
from skillaborator.score_service import ScoreService


class Evaluator(Resource):

    @staticmethod
    def __need_proper_answers():
        abort(Response('Selected answers provided are not sufficient', status=400))

    @staticmethod
    def __parse_args():
        # TODO: reusable parser?
        parser = reqparse.RequestParser()

        parser.add_argument('answerId', dest='answerIds', type=str, help='Last question`s chosen answers',
                            action='append')
        return parser.parse_args(strict=True)

    @staticmethod
    def get(one_time_code):
        """
        Returns the evaluation results with selected answers, score, and right answers
        """
        session = session_service.get(one_time_code)
        final_score = session.current_score
        if session.ended:
            questions_with_right_answers = data_service.get_questions(session.previous_question_ids)
            selected_answers = list()
            for i in range(len(session.previous_question_ids)):
                selected_answers.append(
                    {"questionId": session.previous_question_ids[i], "answerIds": session.selected_answers[i]})
            return {
                       "questionsWithRightAnswers": questions_with_right_answers,
                       "score": final_score,
                       "selectedAnswers": selected_answers
                   }, 200

    @staticmethod
    def put(one_time_code):
        """
        Post the selected answers for the questions, and get only the right answers back in the response
        """

        args = Evaluator.__parse_args()

        session = session_service.get(one_time_code)

        if session.ended:
            abort(Response('This session has already ended', status=400))

        last_question_answers = args.get('answerIds')
        final_score = session.current_score

        prev_question_count = len(session.previous_question_ids)
        if last_question_answers is None or final_score is None or prev_question_count == 0:
            Evaluator.__need_proper_answers()

        last_question_id = session.previous_question_ids[prev_question_count - 1]
        final_score = ScoreService.calculate_next_score(
            last_question_id, last_question_answers, final_score)

        answer_analysis_service.save_answer(
            last_question_id, last_question_answers)

        session.current_score = final_score
        session.selected_answers.append(last_question_answers)
        session_service.end(session)

        right_answers_by_questions = data_service.get_questions_right_answers(
            session.previous_question_ids)
        return {"rightAnswersByQuestions": right_answers_by_questions, "score": final_score}, 200
