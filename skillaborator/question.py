from flask import Response, make_response
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service
from skillaborator.db_collections.answer_analysis_service import answer_analysis_service
from skillaborator.db_collections.session_service import session_service
from skillaborator.score_service import ScoreService


class Question(Resource):

    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400))

    @staticmethod
    def __invalid_session():
        abort(Response('Invalid session', status=401))

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
                            action='append')

        return parser.parse_args(strict=True)

    # TODO add 'neither' answer dynamically
    @staticmethod
    def get(one_time_code):
        """
        Get a random question calculated by the last question's level
        """
        args = Question.__parse_args()
        answer_ids = args.get('answerIds')

        session = session_service.get(one_time_code)
        if not session:
            Question.__invalid_session()

        # answer received, calculate next score if can
        if answer_ids is not None and len(answer_ids) != 0:
            prev_question_count = len(session.previous_question_ids)
            if prev_question_count == 0:
                Question.__no_question_found()
            else:
                last_question_id = session.previous_question_ids[prev_question_count - 1]
                session.current_score = ScoreService.calculate_next_score(last_question_id, answer_ids,
                                                                          session.current_score)
                answer_analysis_service.save_answer(
                    last_question_id, answer_ids)
        elif len(session.previous_question_ids) > 0:
            # there are no answers but there has been questions already, illegal call
            abort(Response('Must give an answer', status=400))

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
