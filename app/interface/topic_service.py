"""Topic service interface contract."""

import uuid
from abc import ABC, abstractmethod

from app.model.topic import Topic


class ITopicService(ABC):
    """Interface contract for Topic business logic services."""

    @abstractmethod
    async def create_topic(self, name: str) -> Topic:
        ...

    @abstractmethod
    async def get_topic_by_id(self, topic_id: uuid.UUID) -> Topic:
        ...

    @abstractmethod
    async def list_topics(self, offset: int = 0, limit: int = 100) -> list[Topic]:
        ...
