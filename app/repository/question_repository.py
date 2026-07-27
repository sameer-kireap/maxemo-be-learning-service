"""Question repository — pure data access layer."""

import uuid
from typing import Any

from sqlalchemy import Float, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.associations import QuestionTopic
from app.model.attempt import QuestionAttempt
from app.model.question import Question
from app.repository.base_repository import BaseRepository
from app.schema.filter import FilterParams
from app.schema.question import (
    QUESTION_FILTER_MAP,
    QUESTION_SEARCH_COLUMNS,
    QUESTION_SORT_MAP,
)
from app.utils.repository.query_builder import QueryBuilder


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question persistence operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, question: Question) -> Question:
        self.db.add(question)
        await self.db.flush()
        return question

    async def get_by_id(self, question_id: uuid.UUID) -> Question | None:
        stmt = (
            select(Question)
            .options(selectinload(Question.topics))
            .where(Question.id == question_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_questions(
        self,
        filter_params: FilterParams[Any],
        topic_id: uuid.UUID | None = None,
    ) -> tuple[list[Question], int]:
        def extra_builder(builder: QueryBuilder, filters: FilterParams[Any]) -> QueryBuilder:
            if topic_id is not None:
                builder.query = builder.query.join(QuestionTopic).where(
                    QuestionTopic.topic_id == topic_id
                )
            return builder

        return await self.list_generic(
            filter_params=filter_params,
            filter_map=QUESTION_FILTER_MAP,
            search_columns=QUESTION_SEARCH_COLUMNS,
            sort_map=QUESTION_SORT_MAP,
            default_sort=Question.created_at,
            model=Question,
            extra_query_builder=extra_builder,
            options=[selectinload(Question.topics)],
        )

    async def get_random_by_topics(
        self, topic_ids: list[uuid.UUID], limit: int = 10
    ) -> list[Question]:
        if not topic_ids:
            return []

        stmt = (
            select(Question)
            .options(selectinload(Question.topics))
            .join(QuestionTopic)
            .where(QuestionTopic.topic_id.in_(topic_ids))
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_questions_by_user_attempt_accuracy(
        self, user_id: int, limit: int = 10
    ) -> list[Question]:
        accuracy_expr = func.avg(
            case((QuestionAttempt.is_correct.is_(True), 1.0), else_=0.0)
        ).cast(Float)

        stmt = (
            select(Question)
            .options(selectinload(Question.topics))
            .join(QuestionAttempt, QuestionAttempt.question_id == Question.id)
            .where(QuestionAttempt.user_id == user_id)
            .group_by(Question.id)
            .order_by(accuracy_expr.asc(), Question.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def update(self, question: Question) -> Question:
        merged = await self.db.merge(question)
        await self.db.flush()
        return merged

    async def delete(self, question_id: uuid.UUID) -> bool:
        question = await self.db.get(Question, question_id)
        if question is None:
            return False
        await self.db.delete(question)
        await self.db.flush()
        return True
