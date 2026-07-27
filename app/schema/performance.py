"""Performance analytics DTO schemas."""

import uuid

from pydantic import BaseModel, Field


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
