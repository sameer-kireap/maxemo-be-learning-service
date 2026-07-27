"""Standardized API response wrapper schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.schema.error import ErrorDetail

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Generic envelope for all API responses."""

    success: bool = Field(default=True, description="Indicates if the operation succeeded")
    data: T | None = Field(default=None, description="Response payload")
    message: str = Field(default="", description="Human readable response summary")
    error: ErrorDetail | None = Field(default=None, description="Error detail if request failed")


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Standard pagination wrapper for list endpoints."""

    offset: int = Field(default=0, description="Record starting offset")
    limit: int = Field(default=100, description="Max items per page")
    total_records: int = Field(default=0, description="Total matching records count")
    items: list[T] = Field(default_factory=list, description="Page items")
