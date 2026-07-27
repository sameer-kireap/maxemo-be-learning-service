"""Dependency injection package."""

from app.dependencies.attempt import get_attempt_repository, get_attempt_service
from app.dependencies.database import get_db_session
from app.dependencies.question import get_question_repository, get_question_service
from app.dependencies.topic import get_topic_repository, get_topic_service

__all__ = [
    "get_attempt_repository",
    "get_attempt_service",
    "get_db_session",
    "get_question_repository",
    "get_question_service",
    "get_topic_repository",
    "get_topic_service",
]
