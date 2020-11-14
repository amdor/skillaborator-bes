from typing import List

from flask import Response, make_response
from flask_restful import Resource, reqparse, abort

from skillaborator.data_service import data_service

SCORE_BASE = 10


class Question(Resource):

    @staticmethod
    def __no_question_found():
        abort(Response('No question found', status=400))

    @staticmethod
    def __calculate_next_question_level(score: int) -> int:
        # 5 answers perfect score 55
        if score < 50:
            return 1
        # 10 answers perfect score 115
        elif score < 115:
            return 2
        # 15 answers perfect score 180
        elif score < 180:
            return 3
        else:
            return 4

    @staticmethod
    def __calculate_next_score(question_id: str, answer_ids: List[str], previous_score: int = 0) -> int:
        """
        Calculates next score: score for right answers is increasing by level, whereas penalty for wrong answers decreases by level,
         any partial answer's score is proportionate to the max received when all answers are right.
        :param question_id: the question to modify the score by
        :param answer_ids: the answers provided for the question
        :param previous_score: the starting score to modify
        :return: new score
        """
        question = data_service.get_question_right_answers_and_level(question_id)
        next_score = previous_score
        level = question.get("level")
        right_answer_ids = question.get("rightAnswers")
        score_increment = (SCORE_BASE + level) / len(right_answer_ids)
        score_decrement = (SCORE_BASE - (level * 2 if level > 1 else SCORE_BASE)) / len(right_answer_ids)
        for answer_id in answer_ids:
            next_score += score_increment if answer_id in right_answer_ids \
                else -score_decrement
        return int(next_score)

    @staticmethod
    def get():
        """
        Get a random question calculated by the last question's level
        """
        parser = reqparse.RequestParser()
        parser.add_argument('currentScore', type=int, help='Current score of the user', location='cookies')
        parser.add_argument('questionId', type=str, help='Last question`s id', location='cookies')
        parser.add_argument('answerId', dest='answerIds', type=str, help='Last question`s chosen answers',
                            required=True, action='append')
        args = parser.parse_args(strict=True)
        current_score = args.get('currentScore')
        last_question_id = args.get('questionId')
        last_question_answers = args.get('answerIds')
        # required together
        if last_question_id is not None and (last_question_answers is None or len(
                last_question_answers) == 0):
            Question.__no_question_found()

        # first question?
        if current_score is None or last_question_id is None:
            current_score = 0
        else:
            current_score = Question.__calculate_next_score(last_question_id, last_question_answers, current_score)

        next_level = Question.__calculate_next_question_level(current_score)
        # get random question on that level
        random_question = data_service.get_question_by_level(next_level)
        if random_question is None:
            Question.__no_question_found()

        random_question['value'] = random_question['value'].replace('\\n', '\n').replace('\\t', '\t')
        if 'code' in random_question:
            random_question['code']['value'] = random_question['code']['value'].replace('\\n', '\n').replace('\\t',
                                                                                                             '\t')
        response: Response = make_response(random_question, 200)
        response.set_cookie(key='currentScore', value=f'{current_score}', httponly=True)
        response.set_cookie(key='questionId', value=f'{random_question.get("id")}', httponly=True)

        return response
