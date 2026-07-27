"""Question entity to DTO mapper."""

from app.mapper.topic_mapper import TopicMapper
from app.model.question import Question
from app.schema.question import QuestionAdminResponse, QuestionResponse


class QuestionMapper:
    """Maps Question ORM entities to learner and admin DTO responses."""

    @staticmethod
    def to_response(question: Question) -> QuestionResponse:
        topics = (
            TopicMapper.to_response_list(question.topics)
            if hasattr(question, "topics") and question.topics
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
        topics = (
            TopicMapper.to_response_list(question.topics)
            if hasattr(question, "topics") and question.topics
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
