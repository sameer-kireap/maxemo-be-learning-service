"""Topic repository — pure data access layer."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.topic import Topic
from app.repository.base_repository import BaseRepository
from app.schema.filter import FilterParams


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
        self, filter_params: FilterParams
    ) -> tuple[list[Topic], int]:
        filter_map: dict[str, Any] = {}
        search_columns: list[Any] = [Topic.name]
        sort_map: dict[str, Any] = {
            "name": Topic.name,
            "created_at": Topic.created_at,
        }
        default_sort: Any = Topic.created_at

        return await self.list_generic(
            filter_params=filter_params,
            filter_map=filter_map,
            search_columns=search_columns,
            sort_map=sort_map,
            default_sort=default_sort,
            model=Topic,
        )
