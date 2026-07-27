"""Topic request, response, and filter DTO schemas."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.constant.sort import SortOrder
from app.model.topic import Topic
from app.schema.filter import FilterParams


class TopicCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique name of the topic")


class TopicResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class TopicSortField(StrEnum):
    NAME = "name"
    CREATED_AT = "created_at"


TOPIC_SORT_MAP: dict[TopicSortField, Any] = {
    TopicSortField.NAME: Topic.name,
    TopicSortField.CREATED_AT: Topic.created_at,
}

TOPIC_FILTER_MAP: dict[str, Any] = {
    "name": Topic.name,
}

TOPIC_SEARCH_COLUMNS: list[Any] = [Topic.name]


class TopicListFilterParams(FilterParams[TopicSortField]):
    name: str | None = Field(default=None, description="Filter by topic name")
    sort_by: TopicSortField | None = Field(default=TopicSortField.CREATED_AT)
    sort_order: SortOrder = Field(default=SortOrder.DESC)
