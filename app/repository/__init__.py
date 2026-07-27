"""Repositories — pure data access layer."""

from app.repository.attempt_repository import AttemptRepository
from app.repository.base_repository import BaseRepository
from app.repository.question_repository import QuestionRepository
from app.repository.topic_repository import TopicRepository

__all__ = [
    "AttemptRepository",
    "BaseRepository",
    "QuestionRepository",
    "TopicRepository",
]
