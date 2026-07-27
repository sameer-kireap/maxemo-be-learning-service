"""Service interface contracts."""

from app.interface.attempt_service import AttemptServiceProtocol
from app.interface.question_service import QuestionServiceProtocol
from app.interface.topic_service import TopicServiceProtocol

__all__ = [
    "AttemptServiceProtocol",
    "QuestionServiceProtocol",
    "TopicServiceProtocol",
]
