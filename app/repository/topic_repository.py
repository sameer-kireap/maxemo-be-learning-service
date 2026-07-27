"""Topic repository — pure data access layer."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.topic import Topic
from app.repository.base_repository import BaseRepository
from app.schema.filter import FilterParams
from app.schema.topic import TOPIC_FILTER_MAP, TOPIC_SEARCH_COLUMNS, TOPIC_SORT_MAP


class TopicRepository(BaseRepository[Topic]):
    """Repository for Topic persistence operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, topic: Topic) -> Topic:
        self.db.add(topic)
        await self.db.flush()
        return topic

    async def get_by_id(self, topic_id: uuid.UUID) -> Topic | None:
        stmt = (
            select(Topic)
            .options(selectinload(Topic.questions))
            .where(Topic.id == topic_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Topic | None:
        stmt = select(Topic).where(Topic.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, topic_ids: list[uuid.UUID]) -> list[Topic]:
        if not topic_ids:
            return []
        stmt = select(Topic).where(Topic.id.in_(topic_ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_topics(
        self, filter_params: FilterParams[Any]
    ) -> tuple[list[Topic], int]:
        return await self.list_generic(
            filter_params=filter_params,
            filter_map=TOPIC_FILTER_MAP,
            search_columns=TOPIC_SEARCH_COLUMNS,
            sort_map=TOPIC_SORT_MAP,
            default_sort=Topic.created_at,
            model=Topic,
        )
