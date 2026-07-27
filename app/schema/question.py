"""Question request and response DTO schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.constant.difficulty import DifficultyLevel
from app.schema.topic import TopicResponse


class QuestionCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Question stem text")
    options: list[str] = Field(..., min_length=2, description="List of MCQ options")
    correct_option_index: int = Field(..., ge=0, description="0-based index of the correct option")
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM, description="Difficulty level"
    )
    topic_ids: list[uuid.UUID] = Field(default_factory=list, description="Associated topic IDs")


class QuestionUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    options: list[str] | None = Field(default=None, min_length=2)
    correct_option_index: int | None = Field(default=None, ge=0)
    difficulty: DifficultyLevel | None = Field(default=None)
    topic_ids: list[uuid.UUID] | None = Field(default=None)


class QuestionResponse(BaseModel):
    """Learner-facing question payload — correct_option_index is excluded to prevent cheating."""

    id: uuid.UUID
    text: str
    options: list[str]
    difficulty: DifficultyLevel
    topics: list[TopicResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class QuestionAdminResponse(QuestionResponse):
    """Admin-facing question payload — includes correct_option_index for internal authoring."""

    correct_option_index: int
