"""Attempt domain service."""

from app.exception import (
    InvalidOptionIndexException,
    QuestionNotFoundException,
)
from app.interface.attempt_service import IAttemptService
from app.mapper.attempt_mapper import AttemptMapper
from app.mapper.question_mapper import QuestionMapper
from app.repository.attempt_repository import AttemptRepository
from app.repository.question_repository import QuestionRepository
from app.schema.attempt import (
    AttemptResponse,
    AttemptSubmit,
    UserPerformanceResponse,
)
from app.schema.filter import FilterParams
from app.schema.question import QuestionResponse
from app.schema.response import PaginatedResponse


class AttemptService(IAttemptService):
    """Business logic service for QuestionAttempt entities and performance analytics."""

    def __init__(
        self,
        attempt_repository: AttemptRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self._attempt_repo = attempt_repository
        self._question_repo = question_repository

    async def submit_attempt(self, payload: AttemptSubmit) -> AttemptResponse:
        question = await self._question_repo.get_by_id(payload.question_id)
        if question is None:
            raise QuestionNotFoundException(question_id=payload.question_id)

        if payload.selected_option_index is not None and (
            payload.selected_option_index < 0
            or payload.selected_option_index >= len(question.options)
        ):
            raise InvalidOptionIndexException(
                index=payload.selected_option_index, options_count=len(question.options)
            )

        # SERVER-DERIVED BUSINESS INVARIANT: Never trust client-provided is_correct
        is_correct = (
            payload.selected_option_index is not None
            and payload.selected_option_index == question.correct_option_index
        )

        attempt = AttemptMapper.to_entity(payload, is_correct)
        created = await self._attempt_repo.create(attempt)
        # Attach question relation for DTO response mapping
        created.question = question
        return AttemptMapper.to_response(created)

    async def list_user_attempts_paginated(
        self, user_id: int, filter_params: FilterParams
    ) -> PaginatedResponse[AttemptResponse]:
        items, total = await self._attempt_repo.list_attempts(user_id, filter_params)
        return PaginatedResponse(
            offset=filter_params.offset,
            limit=filter_params.limit,
            total_records=total,
            items=AttemptMapper.to_response_list(items),
        )

    async def get_user_performance_summary(self, user_id: int) -> UserPerformanceResponse:
        """Delegates performance DTO mapping to AttemptMapper."""
        user_row = await self._attempt_repo.get_raw_user_performance(user_id)
        topic_rows = await self._attempt_repo.get_raw_topic_performance(user_id)
        return AttemptMapper.to_user_performance(user_id, user_row, topic_rows)

    async def get_revision_recommendations(
        self, user_id: int, limit: int = 10
    ) -> list[QuestionResponse]:
        """Recommends weakest questions for user based on past performance."""
        questions = await self._question_repo.get_questions_by_user_attempt_accuracy(
            user_id, limit=limit
        )
        return QuestionMapper.to_response_list(questions)
