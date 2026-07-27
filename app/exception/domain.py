"""Domain and application exceptions inheriting from CustomException."""

import uuid

from fastapi import status

from app.exception.base import CustomException


class NotFoundException(CustomException):
    def __init__(
        self,
        entity: str,
        entity_id: uuid.UUID | int | str,
        message: str | None = None,
    ) -> None:
        msg = message or f"{entity} not found: {entity_id}"
        super().__init__(
            message=msg,
            error_code=f"{entity.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity, "entity_id": str(entity_id)},
        )


class DuplicateException(CustomException):
    def __init__(
        self,
        entity: str,
        field: str,
        value: object,
        message: str | None = None,
    ) -> None:
        msg = message or f"{entity} already exists with {field}='{value}'"
        super().__init__(
            message=msg,
            error_code=f"DUPLICATE_{entity.upper()}",
            status_code=status.HTTP_409_CONFLICT,
            details={"entity": entity, "field": field, "value": str(value)},
        )


class InvalidOptionIndexException(CustomException):
    def __init__(
        self,
        index: int,
        options_count: int,
        message: str | None = None,
    ) -> None:
        msg = (
            message
            or f"Option index {index} is out of range for question with {options_count} options"
        )
        super().__init__(
            message=msg,
            error_code="INVALID_OPTION_INDEX",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"index": index, "options_count": options_count},
        )


class BadRequestException(CustomException):
    def __init__(self, message: str, error_code: str = "BAD_REQUEST") -> None:
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InternalServerErrorException(CustomException):
    def __init__(self, message: str = "An internal server error occurred.") -> None:
        super().__init__(
            message=message,
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
