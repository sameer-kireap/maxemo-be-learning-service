"""Attempt request, response, and filter DTO schemas."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.constant.sort import SortOrder
from app.model.attempt import QuestionAttempt
from app.schema.filter import FilterParams
from app.schema.question import QuestionResponse


class AttemptSubmit(BaseModel):
    user_id: int = Field(..., description="External user identifier")
    question_id: uuid.UUID = Field(..., description="ID of question attempted")
    selected_option_index: int | None = Field(
        default=None, ge=0, description="0-based index selected by learner, or null if skipped"
    )
    time_taken_seconds: int = Field(..., ge=0, description="Time spent on question in seconds")


class AttemptResponse(BaseModel):
    id: uuid.UUID
    user_id: int
    question_id: uuid.UUID
    selected_option_index: int | None
    is_correct: bool
    time_taken_seconds: int
    created_at: datetime
    question: QuestionResponse | None = None


class TopicPerformanceResponse(BaseModel):
    topic_id: uuid.UUID
    topic_name: str
    total_attempts: int
    correct_attempts: int
    accuracy_percentage: float = Field(
        ..., description="Accuracy % rounded to 2 decimal places"
    )


class UserPerformanceResponse(BaseModel):
    user_id: int
    total_attempts: int
    correct_attempts: int
    accuracy_percentage: float = Field(
        ..., description="Overall accuracy % rounded to 2 decimal places"
    )
    avg_time_taken_seconds: float = Field(..., description="Average response time in seconds")
    topic_breakdown: list[TopicPerformanceResponse] = Field(default_factory=list)


class AttemptSortField(StrEnum):
    CREATED_AT = "created_at"


ATTEMPT_SORT_MAP: dict[AttemptSortField, Any] = {
    AttemptSortField.CREATED_AT: QuestionAttempt.created_at,
}

ATTEMPT_FILTER_MAP: dict[str, Any] = {}

ATTEMPT_SEARCH_COLUMNS: list[Any] = []


class AttemptListFilterParams(FilterParams[AttemptSortField]):
    user_id: int | None = Field(default=None, description="Filter by user ID")
    sort_by: AttemptSortField | None = Field(default=AttemptSortField.CREATED_AT)
    sort_order: SortOrder = Field(default=SortOrder.DESC)
