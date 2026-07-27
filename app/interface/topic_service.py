"""Topic service interface contract."""

import uuid
from abc import ABC, abstractmethod

from app.schema.filter import FilterParams
from app.schema.response import PaginatedResponse
from app.schema.topic import TopicCreate, TopicResponse


class ITopicService(ABC):
    """Interface contract for Topic business logic services."""

    @abstractmethod
    async def create_topic(self, payload: TopicCreate) -> TopicResponse:
        ...

    @abstractmethod
    async def get_topic_by_id(self, topic_id: uuid.UUID) -> TopicResponse:
        ...

    @abstractmethod
    async def list_topics_paginated(
        self, filter_params: FilterParams
    ) -> PaginatedResponse[TopicResponse]:
        ...
