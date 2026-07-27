"""Generic filter and pagination parameters."""

from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.constant.sort import SortOrder

SortFieldT = TypeVar("SortFieldT", bound=StrEnum)


class FilterParams(BaseModel, Generic[SortFieldT]):  # noqa: UP046
    """Generic query parameter schema for filtering, searching, sorting, and pagination."""

    offset: int = Field(default=0, ge=0, description="Offset start index for pagination")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum items per page")
    search: str | None = Field(default=None, description="Free-text search query")
    sort_by: SortFieldT | None = Field(default=None, description="Field key to sort results by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort direction: asc or desc")
