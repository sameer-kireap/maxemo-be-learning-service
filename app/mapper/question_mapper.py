"""Question entity and DTO mapper."""

from sqlalchemy import inspect

from app.mapper.topic_mapper import TopicMapper
from app.model.question import Question
from app.model.topic import Topic
from app.schema.question import QuestionAdminResponse, QuestionCreate, QuestionResponse


class QuestionMapper:
    """Maps Question entities to DTO responses and payload DTOs to entities."""

    @staticmethod
    def to_entity(payload: QuestionCreate, topics: list[Topic]) -> Question:
        return Question(
            text=payload.text.strip(),
            options=payload.options,
            correct_option_index=payload.correct_option_index,
            difficulty=payload.difficulty,
            topics=topics,
        )

    @staticmethod
    def to_response(question: Question) -> QuestionResponse:
        state = inspect(question)
        topics = (
            TopicMapper.to_response_list(question.topics)
            if "topics" not in state.unloaded and question.topics
            else []
        )
        return QuestionResponse(
            id=question.id,
            text=question.text,
            options=question.options,
            difficulty=question.difficulty,
            topics=topics,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )

    @staticmethod
    def to_admin_response(question: Question) -> QuestionAdminResponse:
        state = inspect(question)
        topics = (
            TopicMapper.to_response_list(question.topics)
            if "topics" not in state.unloaded and question.topics
            else []
        )
        return QuestionAdminResponse(
            id=question.id,
            text=question.text,
            options=question.options,
            correct_option_index=question.correct_option_index,
            difficulty=question.difficulty,
            topics=topics,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )

    @staticmethod
    def to_response_list(questions: list[Question]) -> list[QuestionResponse]:
        return [QuestionMapper.to_response(q) for q in questions]
