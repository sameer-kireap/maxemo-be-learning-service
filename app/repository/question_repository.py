"""Question repository — pure data access layer."""

import uuid

from sqlalchemy import Float, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constant.difficulty import DifficultyLevel
from app.model.associations import QuestionTopic
from app.model.attempt import QuestionAttempt
from app.model.question import Question


class QuestionRepository:
    """Repository for Question persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, question: Question) -> Question:
        self._session.add(question)
        await self._session.flush()
        return question

    async def get_by_id(self, question_id: uuid.UUID) -> Question | None:
        stmt = (
            select(Question)
            .options(selectinload(Question.topics))
            .where(Question.id == question_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        topic_id: uuid.UUID | None = None,
        difficulty: DifficultyLevel | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Question]:
        stmt = select(Question).options(selectinload(Question.topics))

        if topic_id is not None:
            stmt = stmt.join(QuestionTopic).where(QuestionTopic.topic_id == topic_id)

        if difficulty is not None:
            stmt = stmt.where(Question.difficulty == difficulty)

        stmt = stmt.order_by(Question.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

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
        result = await self._session.execute(stmt)
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
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

    async def update(self, question: Question) -> Question:
        merged = await self._session.merge(question)
        await self._session.flush()
        return merged

    async def delete(self, question_id: uuid.UUID) -> bool:
        question = await self._session.get(Question, question_id)
        if question is None:
            return False
        await self._session.delete(question)
        await self._session.flush()
        return True
