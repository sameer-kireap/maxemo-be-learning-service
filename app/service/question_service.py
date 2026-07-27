"""Question domain service."""

import uuid

from app.constant.difficulty import DifficultyLevel
from app.exception import InvalidOptionIndexException, NotFoundException
from app.interface.question_service import IQuestionService
from app.model.question import Question
from app.repository.question_repository import QuestionRepository
from app.repository.topic_repository import TopicRepository
from app.schema.filter import FilterParams


class QuestionService(IQuestionService):
    """Business logic service for Question entities."""

    def __init__(
        self,
        question_repository: QuestionRepository,
        topic_repository: TopicRepository,
    ) -> None:
        self._question_repo = question_repository
        self._topic_repo = topic_repository

    async def create_question(
        self,
        text: str,
        options: list[str],
        correct_option_index: int,
        difficulty: DifficultyLevel,
        topic_ids: list[uuid.UUID],
    ) -> Question:
        if correct_option_index < 0 or correct_option_index >= len(options):
            raise InvalidOptionIndexException(
                index=correct_option_index, options_count=len(options)
            )

        topics = await self._topic_repo.get_by_ids(topic_ids)
        if len(topics) != len(set(topic_ids)):
            missing = set(topic_ids) - {t.id for t in topics}
            raise NotFoundException(entity="Topic", entity_id=str(list(missing)[0]))

        question = Question(
            text=text.strip(),
            options=options,
            correct_option_index=correct_option_index,
            difficulty=difficulty,
            topics=topics,
        )
        return await self._question_repo.create(question)

    async def get_question_by_id(self, question_id: uuid.UUID) -> Question:
        question = await self._question_repo.get_by_id(question_id)
        if question is None:
            raise NotFoundException(entity="Question", entity_id=question_id)
        return question

    async def list_questions(
        self,
        topic_id: uuid.UUID | None = None,
        difficulty: DifficultyLevel | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Question]:
        filter_params = FilterParams(offset=offset, limit=limit, sort_by="created_at")
        filter_params.difficulty = difficulty  # type: ignore[attr-defined]
        items, _ = await self._question_repo.list_questions(
            filter_params, topic_id=topic_id
        )
        return items

    async def list_questions_paginated(
        self,
        filter_params: FilterParams,
        topic_id: uuid.UUID | None = None,
    ) -> tuple[list[Question], int]:
        return await self._question_repo.list_questions(
            filter_params, topic_id=topic_id
        )

    async def get_practice_questions(
        self, topic_ids: list[uuid.UUID], limit: int = 10
    ) -> list[Question]:
        return await self._question_repo.get_random_by_topics(topic_ids, limit=limit)

    async def update_question(
        self,
        question_id: uuid.UUID,
        text: str | None = None,
        options: list[str] | None = None,
        correct_option_index: int | None = None,
        difficulty: DifficultyLevel | None = None,
        topic_ids: list[uuid.UUID] | None = None,
    ) -> Question:
        question = await self.get_question_by_id(question_id)

        opts = options if options is not None else question.options
        idx = (
            correct_option_index
            if correct_option_index is not None
            else question.correct_option_index
        )

        if idx < 0 or idx >= len(opts):
            raise InvalidOptionIndexException(index=idx, options_count=len(opts))

        if text is not None:
            question.text = text.strip()
        if options is not None:
            question.options = options
        if correct_option_index is not None:
            question.correct_option_index = correct_option_index
        if difficulty is not None:
            question.difficulty = difficulty
        if topic_ids is not None:
            topics = await self._topic_repo.get_by_ids(topic_ids)
            question.topics = topics

        return await self._question_repo.update(question)

    async def delete_question(self, question_id: uuid.UUID) -> None:
        deleted = await self._question_repo.delete(question_id)
        if not deleted:
            raise NotFoundException(entity="Question", entity_id=question_id)
