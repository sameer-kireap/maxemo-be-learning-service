"""Topic domain service."""

import uuid

from app.exception import DuplicateException, NotFoundException
from app.interface.topic_service import ITopicService
from app.model.topic import Topic
from app.repository.topic_repository import TopicRepository
from app.schema.filter import FilterParams


class TopicService(ITopicService):
    """Business logic service for Topic entities."""

    def __init__(self, topic_repository: TopicRepository) -> None:
        self._topic_repo = topic_repository

    async def create_topic(self, name: str) -> Topic:
        existing = await self._topic_repo.get_by_name(name.strip())
        if existing is not None:
            raise DuplicateException(entity="Topic", field="name", value=name)

        topic = Topic(name=name.strip())
        return await self._topic_repo.create(topic)

    async def get_topic_by_id(self, topic_id: uuid.UUID) -> Topic:
        topic = await self._topic_repo.get_by_id(topic_id)
        if topic is None:
            raise NotFoundException(entity="Topic", entity_id=topic_id)
        return topic

    async def list_topics(self, offset: int = 0, limit: int = 100) -> list[Topic]:
        filter_params = FilterParams(offset=offset, limit=limit)
        items, _ = await self._topic_repo.list_topics(filter_params)
        return items

    async def list_topics_paginated(
        self, filter_params: FilterParams
    ) -> tuple[list[Topic], int]:
        return await self._topic_repo.list_topics(filter_params)
