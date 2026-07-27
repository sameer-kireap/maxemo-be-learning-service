"""Attempt domain service."""

import uuid
from typing import Any

from app.exception import InvalidOptionIndexException, NotFoundException
from app.interface.attempt_service import IAttemptService
from app.model.attempt import QuestionAttempt
from app.model.question import Question
from app.repository.attempt_repository import AttemptRepository
from app.repository.question_repository import QuestionRepository
from app.schema.filter import FilterParams


class AttemptService(IAttemptService):
    """Business logic service for QuestionAttempt entities and performance analytics."""

    def __init__(
        self,
        attempt_repository: AttemptRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self._attempt_repo = attempt_repository
        self._question_repo = question_repository

    async def submit_attempt(
        self,
        user_id: int,
        question_id: uuid.UUID,
        selected_option_index: int | None,
        time_taken_seconds: int,
    ) -> QuestionAttempt:
        question = await self._question_repo.get_by_id(question_id)
        if question is None:
            raise NotFoundException(entity="Question", entity_id=question_id)

        if selected_option_index is not None and (
            selected_option_index < 0 or selected_option_index >= len(question.options)
        ):
            raise InvalidOptionIndexException(
                index=selected_option_index, options_count=len(question.options)
            )

        # SERVER-DERIVED BUSINESS INVARIANT: Never trust client-provided is_correct
        is_correct = (
            selected_option_index is not None
            and selected_option_index == question.correct_option_index
        )

        attempt = QuestionAttempt(
            user_id=user_id,
            question_id=question_id,
            selected_option_index=selected_option_index,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
        )
        return await self._attempt_repo.create(attempt)

    async def get_user_attempts(
        self, user_id: int, offset: int = 0, limit: int = 100
    ) -> list[QuestionAttempt]:
        filter_params = FilterParams(offset=offset, limit=limit)
        items, _ = await self._attempt_repo.list_attempts(user_id, filter_params)
        return items

    async def get_user_performance_summary(self, user_id: int) -> dict[str, Any]:
        """Calculates performance statistics from raw DB aggregates."""
        row = await self._attempt_repo.get_raw_user_performance(user_id)

        total = row.total_attempts or 0
        correct = row.correct_attempts or 0
        total_time = float(row.total_time_seconds) if row.total_time_seconds else 0.0

        accuracy = (correct / total * 100.0) if total > 0 else 0.0
        avg_time = (total_time / total) if total > 0 else 0.0

        topic_breakdown = await self.get_user_topic_performance(user_id)

        return {
            "user_id": user_id,
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy_percentage": round(accuracy, 2),
            "avg_time_taken_seconds": round(avg_time, 2),
            "topic_breakdown": topic_breakdown,
        }

    async def get_user_topic_performance(self, user_id: int) -> list[dict[str, Any]]:
        """Calculates topic breakdown performance stats from raw DB rows."""
        rows = await self._attempt_repo.get_raw_topic_performance(user_id)

        topic_stats: list[dict[str, Any]] = []
        for r in rows:
            t_total = r.total_attempts or 0
            t_correct = r.correct_attempts or 0
            t_acc = (t_correct / t_total * 100.0) if t_total > 0 else 0.0
            topic_stats.append(
                {
                    "topic_id": str(r.topic_id),
                    "topic_name": r.topic_name,
                    "total_attempts": t_total,
                    "correct_attempts": t_correct,
                    "accuracy_percentage": round(t_acc, 2),
                }
            )

        return topic_stats

    async def get_revision_recommendations(
        self, user_id: int, limit: int = 10
    ) -> list[Question]:
        """Recommends weakest questions for user based on past performance."""
        return await self._question_repo.get_questions_by_user_attempt_accuracy(
            user_id, limit=limit
        )
