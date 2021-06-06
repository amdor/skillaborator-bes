from typing import List

from skillaborator.data_service import data_service

SCORE_BASE = 10
LEVEL_TWO_THRESHOLD = 5 * SCORE_BASE
LEVEL_THREE_THRESHOLD = LEVEL_TWO_THRESHOLD + 5 * (SCORE_BASE + 2)
LEVEL_FOUR_THRESHOLD = LEVEL_THREE_THRESHOLD + 5 * (SCORE_BASE + 3)


class ScoreService:

    @staticmethod
    def calculate_next_question_level(score: int) -> int:
        # 5 answers perfect score 55
        if score < LEVEL_TWO_THRESHOLD:
            return 1
        # 10 answers perfect score 115
        elif score < LEVEL_THREE_THRESHOLD:
            return 2
        # 15 answers perfect score 180
        elif score < LEVEL_FOUR_THRESHOLD:
            return 3
        else:
            return 4

    @staticmethod
    def calculate_next_score(question_id: str, answer_ids: List[str], previous_score: int = 0) -> int:
        """
        Calculates next score: score for right answers is increasing by level, whereas penalty for wrong answers
        decreases by level, any partial answer's score is proportionate to the max received when all answers are
        right.
        :param question_id: the question to modify the score by
        :param answer_ids: chosen answers to check against right answers
        :param previous_score: the starting score to modify
        :return: new score
        """
        question = data_service.get_question_right_answers_and_level(question_id)
        next_score = previous_score
        if len(answer_ids) == 0:
            return int(next_score)
        level = question.get("level")
        right_answer_ids = question.get("rightAnswers")
        score_increment = (SCORE_BASE + level) / len(right_answer_ids)
        score_decrement = (SCORE_BASE - (level * 2 if 1 < level < SCORE_BASE / 2 else SCORE_BASE))
        for answer_id in answer_ids:
            next_score += score_increment if answer_id in right_answer_ids \
                else -score_decrement
        return max(int(next_score), 0)
