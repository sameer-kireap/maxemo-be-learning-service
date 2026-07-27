"""Pydantic schemas."""

from app.schema.attempt import AttemptResponse, AttemptSubmit
from app.schema.error import ErrorDetail, ErrorResponse
from app.schema.filter import FilterParams
from app.schema.health import HealthResponse
from app.schema.performance import TopicPerformanceResponse, UserPerformanceResponse
from app.schema.question import (
    QuestionAdminResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.schema.response import APIResponse, PaginatedResponse
from app.schema.topic import TopicCreate, TopicResponse

__all__ = [
    "APIResponse",
    "AttemptResponse",
    "AttemptSubmit",
    "ErrorDetail",
    "ErrorResponse",
    "FilterParams",
    "HealthResponse",
    "PaginatedResponse",
    "QuestionAdminResponse",
    "QuestionCreate",
    "QuestionResponse",
    "QuestionUpdate",
    "TopicCreate",
    "TopicPerformanceResponse",
    "TopicResponse",
    "UserPerformanceResponse",
]
