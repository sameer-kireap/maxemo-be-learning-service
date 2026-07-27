"""Topic entity and DTO mapper."""

from app.model.topic import Topic
from app.schema.topic import TopicCreate, TopicResponse


class TopicMapper:
    """Maps Topic entities to DTO responses and payload DTOs to entities."""

    @staticmethod
    def to_entity(payload: TopicCreate) -> Topic:
        return Topic(name=payload.name.strip())

    @staticmethod
    def to_response(topic: Topic) -> TopicResponse:
        return TopicResponse(
            id=topic.id,
            name=topic.name,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
        )

    @staticmethod
    def to_response_list(topics: list[Topic]) -> list[TopicResponse]:
        return [TopicMapper.to_response(t) for t in topics]
