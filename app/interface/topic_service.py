"""Topic service interface contract."""

import uuid
from typing import Protocol

from app.model.topic import Topic


class TopicServiceProtocol(Protocol):
    """Interface contract for Topic business logic services."""

    async def create_topic(self, name: str) -> Topic:
        ...

    async def get_topic_by_id(self, topic_id: uuid.UUID) -> Topic:
        ...

    async def list_topics(self, offset: int = 0, limit: int = 100) -> list[Topic]:
        ...
