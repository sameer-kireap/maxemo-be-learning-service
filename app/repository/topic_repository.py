"""Topic repository — pure data access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.topic import Topic


class TopicRepository:
    """Repository for Topic persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, topic: Topic) -> Topic:
        self._session.add(topic)
        await self._session.flush()
        return topic

    async def get_by_id(self, topic_id: uuid.UUID) -> Topic | None:
        stmt = (
            select(Topic)
            .options(selectinload(Topic.questions))
            .where(Topic.id == topic_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Topic | None:
        stmt = select(Topic).where(Topic.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, topic_ids: list[uuid.UUID]) -> list[Topic]:
        if not topic_ids:
            return []
        stmt = select(Topic).where(Topic.id.in_(topic_ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self, offset: int = 0, limit: int = 100) -> list[Topic]:
        stmt = (
            select(Topic)
            .order_by(Topic.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
