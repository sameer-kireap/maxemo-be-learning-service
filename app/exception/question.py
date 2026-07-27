"""Question domain exceptions."""

import uuid

from fastapi import status

from app.exception.base import CustomException


class QuestionNotFoundException(CustomException):
    """Raised when a requested Question is not found."""

    def __init__(self, question_id: uuid.UUID | str) -> None:
        super().__init__(
            message=f"Question with ID '{question_id}' was not found.",
            error_code="QUESTION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidOptionIndexException(CustomException):
    """Raised when selected_option_index or correct_option_index is out of range."""

    def __init__(self, index: int, options_count: int) -> None:
        valid_range = f"0..{options_count - 1}" if options_count > 0 else "none"
        super().__init__(
            message=(
                f"Option index {index} is invalid. "
                f"Question options count is {options_count} (valid indices: {valid_range})."
            ),
            error_code="INVALID_OPTION_INDEX",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
