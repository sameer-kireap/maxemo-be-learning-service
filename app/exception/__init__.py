"""Application exceptions and global exception handlers."""

from app.exception.base import CustomException
from app.exception.domain import (
    BadRequestException,
    DuplicateException,
    InternalServerErrorException,
    InvalidOptionIndexException,
    NotFoundException,
)
from app.exception.handler import register_exception_handlers

__all__ = [
    "BadRequestException",
    "CustomException",
    "DuplicateException",
    "InternalServerErrorException",
    "InvalidOptionIndexException",
    "NotFoundException",
    "register_exception_handlers",
]
