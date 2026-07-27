"""Attempt repository — pure data access layer."""

import uuid
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.associations import QuestionTopic
from app.model.attempt import QuestionAttempt
from app.model.question import Question
from app.model.topic import Topic
from app.repository.base_repository import BaseRepository
from app.schema.attempt import (
    ATTEMPT_FILTER_MAP,
    ATTEMPT_SEARCH_COLUMNS,
    ATTEMPT_SORT_MAP,
)
from app.schema.filter import FilterParams
from app.utils.repository.query_builder import QueryBuilder


class AttemptRepository(BaseRepository[QuestionAttempt]):
    """Repository for QuestionAttempt persistence operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, attempt: QuestionAttempt) -> QuestionAttempt:
        self.db.add(attempt)
        await self.db.flush()
        return attempt

    async def get_by_id(self, attempt_id: uuid.UUID) -> QuestionAttempt | None:
        stmt = (
            select(QuestionAttempt)
            .options(selectinload(QuestionAttempt.question))
            .where(QuestionAttempt.id == attempt_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_attempts(
        self, user_id: int, filter_params: FilterParams[Any]
    ) -> tuple[list[QuestionAttempt], int]:
        def extra_builder(builder: QueryBuilder, filters: FilterParams[Any]) -> QueryBuilder:
            builder.query = builder.query.where(QuestionAttempt.user_id == user_id)
            return builder

        return await self.list_generic(
            filter_params=filter_params,
            filter_map=ATTEMPT_FILTER_MAP,
            search_columns=ATTEMPT_SEARCH_COLUMNS,
            sort_map=ATTEMPT_SORT_MAP,
            default_sort=QuestionAttempt.created_at,
            model=QuestionAttempt,
            extra_query_builder=extra_builder,
            options=[selectinload(QuestionAttempt.question)],
        )

    async def get_raw_user_performance(self, user_id: int) -> Any:  # noqa: ANN401
        """Returns raw database row aggregate: (total_attempts, correct_attempts, total_time)."""
        stmt = (
            select(
                func.count(QuestionAttempt.id).label("total_attempts"),
                func.sum(case((QuestionAttempt.is_correct.is_(True), 1), else_=0)).label(
                    "correct_attempts"
                ),
                func.sum(QuestionAttempt.time_taken_seconds).label("total_time_seconds"),
            )
            .where(QuestionAttempt.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.one()

    async def get_raw_topic_performance(self, user_id: int) -> Any:  # noqa: ANN401
        """Returns raw database rows: topic_id, topic_name, total, correct, last_attempted_at."""
        stmt = (
            select(
                Topic.id.label("topic_id"),
                Topic.name.label("topic_name"),
                func.count(QuestionAttempt.id).label("total_attempts"),
                func.sum(case((QuestionAttempt.is_correct.is_(True), 1), else_=0)).label(
                    "correct_attempts"
                ),
                func.max(QuestionAttempt.created_at).label("last_attempted_at"),
            )
            .join(QuestionTopic, QuestionTopic.topic_id == Topic.id)
            .join(Question, Question.id == QuestionTopic.question_id)
            .join(QuestionAttempt, QuestionAttempt.question_id == Question.id)
            .where(QuestionAttempt.user_id == user_id)
            .group_by(Topic.id, Topic.name)
            .order_by(Topic.name.asc())
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_unattempted_topics_for_user(self, user_id: int) -> Any:  # noqa: ANN401
        """Fetches topics that exist in the system but have 0 attempts recorded for this user."""
        attempted_topic_ids_subquery = (
            select(QuestionTopic.topic_id)
            .join(QuestionAttempt, QuestionAttempt.question_id == QuestionTopic.question_id)
            .where(QuestionAttempt.user_id == user_id)
            .scalar_subquery()
        )
        stmt = select(Topic).where(Topic.id.not_in(attempted_topic_ids_subquery))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_incorrect_attempts_by_user(
        self, user_id: int, limit: int = 10
    ) -> list[QuestionAttempt]:
        stmt = (
            select(QuestionAttempt)
            .options(
                selectinload(QuestionAttempt.question).selectinload(Question.topics)
            )
            .where(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.is_correct.is_(False),
            )
            .order_by(QuestionAttempt.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
