"""Topic domain service."""

import uuid
from typing import Any

from app.exception import TopicAlreadyExistsException, TopicNotFoundException
from app.interface.topic_service import ITopicService
from app.mapper.topic_mapper import TopicMapper
from app.repository.topic_repository import TopicRepository
from app.schema.filter import FilterParams
from app.schema.response import PaginatedResponse
from app.schema.topic import TopicCreate, TopicResponse


class TopicService(ITopicService):
    """Business logic service for Topic entities."""

    def __init__(self, topic_repository: TopicRepository) -> None:
        self._topic_repo = topic_repository

    async def create_topic(self, payload: TopicCreate) -> TopicResponse:
        name = payload.name.strip()
        existing = await self._topic_repo.get_by_name(name)
        if existing is not None:
            raise TopicAlreadyExistsException(name=name)

        topic = TopicMapper.to_entity(payload)
        created = await self._topic_repo.create(topic)
        return TopicMapper.to_response(created)

    async def get_topic_by_id(self, topic_id: uuid.UUID) -> TopicResponse:
        topic = await self._topic_repo.get_by_id(topic_id)
        if topic is None:
            raise TopicNotFoundException(topic_id=topic_id)
        return TopicMapper.to_response(topic)

    async def list_topics_paginated(
        self, filter_params: FilterParams[Any]
    ) -> PaginatedResponse[TopicResponse]:
        items, total = await self._topic_repo.list_topics(filter_params)
        return PaginatedResponse(
            offset=filter_params.offset,
            limit=filter_params.limit,
            total_records=total,
            items=TopicMapper.to_response_list(items),
        )
