"""Topic domain exceptions."""

import uuid

from fastapi import status

from app.exception.base import CustomException


class TopicNotFoundException(CustomException):
    """Raised when a requested Topic is not found."""

    def __init__(self, topic_id: uuid.UUID | str) -> None:
        super().__init__(
            message=f"Topic with ID '{topic_id}' was not found.",
            error_code="TOPIC_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TopicAlreadyExistsException(CustomException):
    """Raised when creating a Topic that already exists."""

    def __init__(self, name: str) -> None:
        super().__init__(
            message=f"Topic with name '{name}' already exists.",
            error_code="TOPIC_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
        )
