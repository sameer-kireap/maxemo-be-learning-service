"""Question domain service."""

import uuid
from typing import Any

from app.constant.difficulty import DifficultyLevel
from app.exception import (
    InvalidOptionIndexException,
    QuestionNotFoundException,
    TopicNotFoundException,
)
from app.interface.question_service import IQuestionService
from app.mapper.question_mapper import QuestionMapper
from app.repository.question_repository import QuestionRepository
from app.repository.topic_repository import TopicRepository
from app.schema.filter import FilterParams
from app.schema.question import (
    QuestionAdminResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.schema.response import PaginatedResponse


class QuestionService(IQuestionService):
    """Business logic service for Question entities."""

    def __init__(
        self,
        question_repository: QuestionRepository,
        topic_repository: TopicRepository,
    ) -> None:
        self._question_repo = question_repository
        self._topic_repo = topic_repository

    async def create_question(self, payload: QuestionCreate) -> QuestionAdminResponse:
        if payload.correct_option_index < 0 or payload.correct_option_index >= len(payload.options):
            raise InvalidOptionIndexException(
                index=payload.correct_option_index, options_count=len(payload.options)
            )

        topics = await self._topic_repo.get_by_ids(payload.topic_ids)
        if len(topics) != len(set(payload.topic_ids)):
            missing = set(payload.topic_ids) - {t.id for t in topics}
            raise TopicNotFoundException(topic_id=str(list(missing)[0]))

        question = QuestionMapper.to_entity(payload, topics)
        created = await self._question_repo.create(question)
        return QuestionMapper.to_admin_response(created)

    async def get_question_by_id(self, question_id: uuid.UUID) -> QuestionResponse:
        question = await self._question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundException(question_id=question_id)
        return QuestionMapper.to_response(question)

    async def list_questions_paginated(
        self,
        filter_params: FilterParams[Any],
        topic_id: uuid.UUID | None = None,
        difficulty: DifficultyLevel | None = None,
    ) -> PaginatedResponse[QuestionResponse]:
        if difficulty is not None:
            filter_params.difficulty = difficulty  # type: ignore[attr-defined]

        items, total = await self._question_repo.list_questions(
            filter_params, topic_id=topic_id
        )
        return PaginatedResponse(
            offset=filter_params.offset,
            limit=filter_params.limit,
            total_records=total,
            items=QuestionMapper.to_response_list(items),
        )

    async def get_practice_questions(
        self, topic_ids: list[uuid.UUID], limit: int = 10
    ) -> list[QuestionResponse]:
        questions = await self._question_repo.get_random_by_topics(topic_ids, limit=limit)
        return QuestionMapper.to_response_list(questions)

    async def update_question(
        self, question_id: uuid.UUID, payload: QuestionUpdate
    ) -> QuestionAdminResponse:
        question = await self._question_repo.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundException(question_id=question_id)

        opts = payload.options if payload.options is not None else question.options
        idx = (
            payload.correct_option_index
            if payload.correct_option_index is not None
            else question.correct_option_index
        )

        if idx < 0 or idx >= len(opts):
            raise InvalidOptionIndexException(index=idx, options_count=len(opts))

        if payload.text is not None:
            question.text = payload.text.strip()
        if payload.options is not None:
            question.options = payload.options
        if payload.correct_option_index is not None:
            question.correct_option_index = payload.correct_option_index
        if payload.difficulty is not None:
            question.difficulty = payload.difficulty
        if payload.topic_ids is not None:
            topics = await self._topic_repo.get_by_ids(payload.topic_ids)
            question.topics = topics

        updated = await self._question_repo.update(question)
        return QuestionMapper.to_admin_response(updated)

    async def delete_question(self, question_id: uuid.UUID) -> None:
        deleted = await self._question_repo.delete(question_id)
        if not deleted:
            raise QuestionNotFoundException(question_id=question_id)
