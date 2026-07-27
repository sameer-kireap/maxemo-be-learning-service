"""Application custom exceptions and global exception handler."""

from app.exception.base import CustomException
from app.exception.handler import register_exception_handlers
from app.exception.question import (
    InvalidOptionIndexException,
    QuestionNotFoundException,
)
from app.exception.topic import (
    TopicAlreadyExistsException,
    TopicNotFoundException,
)

__all__ = [
    "CustomException",
    "InvalidOptionIndexException",
    "QuestionNotFoundException",
    "TopicAlreadyExistsException",
    "TopicNotFoundException",
    "register_exception_handlers",
]
