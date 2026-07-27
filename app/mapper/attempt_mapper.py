"""QuestionAttempt entity to DTO mapper."""

from app.mapper.question_mapper import QuestionMapper
from app.model.attempt import QuestionAttempt
from app.schema.attempt import AttemptResponse


class AttemptMapper:
    """Maps QuestionAttempt ORM entities to DTO responses."""

    @staticmethod
    def to_response(attempt: QuestionAttempt) -> AttemptResponse:
        question_dto = (
            QuestionMapper.to_response(attempt.question)
            if hasattr(attempt, "question") and attempt.question
            else None
        )
        return AttemptResponse(
            id=attempt.id,
            user_id=attempt.user_id,
            question_id=attempt.question_id,
            selected_option_index=attempt.selected_option_index,
            is_correct=attempt.is_correct,
            time_taken_seconds=attempt.time_taken_seconds,
            created_at=attempt.created_at,
            question=question_dto,
        )

    @staticmethod
    def to_response_list(attempts: list[QuestionAttempt]) -> list[AttemptResponse]:
        return [AttemptMapper.to_response(a) for a in attempts]
