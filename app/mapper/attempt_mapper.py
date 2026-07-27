"""QuestionAttempt entity and DTO mapper."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import inspect

from app.mapper.question_mapper import QuestionMapper
from app.model.attempt import QuestionAttempt
from app.schema.attempt import (
    AttemptResponse,
    AttemptSubmit,
    TopicPerformanceResponse,
    UserPerformanceResponse,
)


class AttemptMapper:
    """Maps QuestionAttempt entities to DTO responses and payload DTOs to entities."""

    @staticmethod
    def to_entity(payload: AttemptSubmit, is_correct: bool) -> QuestionAttempt:
        return QuestionAttempt(
            user_id=payload.user_id,
            question_id=payload.question_id,
            selected_option_index=payload.selected_option_index,
            is_correct=is_correct,
            time_taken_seconds=payload.time_taken_seconds,
        )

    @staticmethod
    def to_response(attempt: QuestionAttempt) -> AttemptResponse:
        state = inspect(attempt)
        question_dto = (
            QuestionMapper.to_response(attempt.question)
            if "question" not in state.unloaded and attempt.question
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

    @staticmethod
    def to_user_performance(
        user_id: int, user_row: Any, topic_rows: Sequence[Any]  # noqa: ANN401
    ) -> UserPerformanceResponse:
        """Maps raw performance DB rows into UserPerformanceResponse DTO."""
        total = user_row.total_attempts or 0
        correct = user_row.correct_attempts or 0
        total_time = float(user_row.total_time_seconds) if user_row.total_time_seconds else 0.0

        accuracy = (correct / total * 100.0) if total > 0 else 0.0
        avg_time = (total_time / total) if total > 0 else 0.0

        topic_stats: list[TopicPerformanceResponse] = []
        for r in topic_rows:
            t_total = r.total_attempts or 0
            t_correct = r.correct_attempts or 0
            t_acc = (t_correct / t_total * 100.0) if t_total > 0 else 0.0
            topic_stats.append(
                TopicPerformanceResponse(
                    topic_id=r.topic_id,
                    topic_name=r.topic_name,
                    total_attempts=t_total,
                    correct_attempts=t_correct,
                    accuracy_percentage=round(t_acc, 2),
                )
            )

        return UserPerformanceResponse(
            user_id=user_id,
            total_attempts=total,
            correct_attempts=correct,
            accuracy_percentage=round(accuracy, 2),
            avg_time_taken_seconds=round(avg_time, 2),
            topic_breakdown=topic_stats,
        )
