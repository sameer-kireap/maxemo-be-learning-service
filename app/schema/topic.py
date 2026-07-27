"""Topic request and response DTO schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique name of the topic")


class TopicResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime
