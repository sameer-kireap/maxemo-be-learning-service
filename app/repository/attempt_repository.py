"""Attempt repository — pure data access layer."""

import uuid

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.associations import QuestionTopic
from app.model.attempt import QuestionAttempt
from app.model.question import Question
from app.model.topic import Topic


class AttemptRepository:
    """Repository for QuestionAttempt persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, attempt: QuestionAttempt) -> QuestionAttempt:
        self._session.add(attempt)
        await self._session.flush()
        return attempt

    async def get_by_id(self, attempt_id: uuid.UUID) -> QuestionAttempt | None:
        stmt = (
            select(QuestionAttempt)
            .options(selectinload(QuestionAttempt.question))
            .where(QuestionAttempt.id == attempt_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: int, offset: int = 0, limit: int = 100
    ) -> list[QuestionAttempt]:
        stmt = (
            select(QuestionAttempt)
            .options(selectinload(QuestionAttempt.question))
            .where(QuestionAttempt.user_id == user_id)
            .order_by(QuestionAttempt.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_raw_user_performance(self, user_id: int) -> tuple[int, int, float]:
        """Returns raw tuple: (total_attempts, correct_attempts, total_time_seconds)."""
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
        result = await self._session.execute(stmt)
        row = result.one()

        total = row.total_attempts or 0
        correct = row.correct_attempts or 0
        total_time = float(row.total_time_seconds) if row.total_time_seconds else 0.0

        return total, correct, total_time

    async def get_raw_topic_performance(
        self, user_id: int
    ) -> list[tuple[uuid.UUID, str, int, int]]:
        """Returns raw rows: list of (topic_id, topic_name, total_attempts, correct_attempts)."""
        stmt = (
            select(
                Topic.id.label("topic_id"),
                Topic.name.label("topic_name"),
                func.count(QuestionAttempt.id).label("total_attempts"),
                func.sum(case((QuestionAttempt.is_correct.is_(True), 1), else_=0)).label(
                    "correct_attempts"
                ),
            )
            .join(QuestionTopic, QuestionTopic.topic_id == Topic.id)
            .join(Question, Question.id == QuestionTopic.question_id)
            .join(QuestionAttempt, QuestionAttempt.question_id == Question.id)
            .where(QuestionAttempt.user_id == user_id)
            .group_by(Topic.id, Topic.name)
            .order_by(Topic.name.asc())
        )
        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            (
                row.topic_id,
                row.topic_name,
                row.total_attempts or 0,
                row.correct_attempts or 0,
            )
            for row in rows
        ]

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
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
