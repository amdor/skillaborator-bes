from datetime import datetime

from flask import Response, make_response
from flask_restful import Resource, reqparse, abort, inputs

from skillaborator.data_service import data_service
from skillaborator.db_collections.answer_analysis_service import answer_analysis_service
from skillaborator.db_collections.session_service import session_service
from skillaborator.score_service import ScoreService


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

    @staticmethod
    def __parse_args():
        parser = reqparse.RequestParser()

        parser.add_argument('answerId', dest='answerIds', type=str, help='Last question`s chosen answers',
                            action='append', required=False)
        parser.add_argument('timedOut', type=inputs.boolean, help='Question has timed out', required=False)

        return parser.parse_args(strict=True)

    # TODO add 'neither' answer dynamically
    @staticmethod
    def get(one_time_code):
        """
        Get a random question calculated by the last question's level
        """
        args = Question.__parse_args()
        answer_ids = args.get('answerIds')
        timed_out = args.get('timedOut')

        new_session = (answer_ids is None or len(answer_ids) == 0) and timed_out is None
        session = session_service.get(one_time_code, new_session)
        if session.ended:
            abort(Response('This session has already ended', status=400))

        timed_out = timed_out or session.next_timeout < datetime.now()
        # disregard any answer ids if timed out
        if timed_out:
            answer_ids = []

        # answer received, calculate next score if can
        # we either must have answers or the time must've run out
        if answer_ids is not None and (len(answer_ids) != 0 or timed_out):
            prev_question_count = len(session.previous_question_ids)
            if prev_question_count == 0:
                Question.__no_question_found()
            else:
                last_question_id = session.previous_question_ids[prev_question_count - 1]
                session.current_score = ScoreService.calculate_next_score(last_question_id, answer_ids,
                                                                          session.current_score)
                answer_analysis_service.save_answer(
                    last_question_id, answer_ids)

            session.selected_answers.append(answer_ids)

        next_level = ScoreService.calculate_next_question_level(session.current_score)
        # get random question on that level
        random_question = data_service.get_question_by_level(
            next_level, session.previous_question_ids)
        if random_question is None:
            Question.__no_question_found()
        Question.__format_question_texts(random_question)

        session.previous_question_ids.append(random_question.get("id"))

        response: Response = make_response(random_question, 200)

        session_service.save(session)
        return response
