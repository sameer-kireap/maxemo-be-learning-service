"""Topic entity to DTO mapper."""

from app.model.topic import Topic
from app.schema.topic import TopicResponse


class TopicMapper:
    """Maps Topic ORM entities to DTO responses."""

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
