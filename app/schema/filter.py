"""Filter parameters schema for generic list endpoints."""

from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    """Generic list query parameters using limit and offset."""

    offset: int = Field(default=0, ge=0, description="Record offset")
    limit: int = Field(default=100, ge=1, le=500, description="Max records to return")
    search: str | None = Field(default=None, description="Search term across configured columns")
    sort_by: str | None = Field(default=None, description="Column name to sort by")
    sort_order: str | None = Field(default="desc", description="Sort direction: asc or desc")
