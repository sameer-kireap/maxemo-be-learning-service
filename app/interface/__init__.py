"""Service abstract base class interfaces."""

from app.interface.attempt_service import IAttemptService
from app.interface.question_service import IQuestionService
from app.interface.topic_service import ITopicService

__all__ = [
    "IAttemptService",
    "IQuestionService",
    "ITopicService",
]
