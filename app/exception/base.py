"""Base exception for application and domain layer errors."""

from typing import Any

from fastapi import status


class CustomException(Exception):  # noqa: N818
    """Base exception class from which all application exceptions inherit."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
