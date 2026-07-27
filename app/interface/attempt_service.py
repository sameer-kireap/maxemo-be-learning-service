"""Attempt service interface contract."""

from abc import ABC, abstractmethod
from typing import Any

from app.schema.attempt import (
    AttemptResponse,
    AttemptSubmit,
    TopicRevisionResponse,
    UserPerformanceResponse,
)
from app.schema.filter import FilterParams
from app.schema.question import QuestionResponse
from app.schema.response import PaginatedResponse


class IAttemptService(ABC):
    """Interface contract for QuestionAttempt business logic services."""

    @abstractmethod
    async def submit_attempt(self, payload: AttemptSubmit) -> AttemptResponse:
        ...

    @abstractmethod
    async def list_user_attempts_paginated(
        self, user_id: int, filter_params: FilterParams[Any]
    ) -> PaginatedResponse[AttemptResponse]:
        ...

    @abstractmethod
    async def get_user_performance_summary(self, user_id: int) -> UserPerformanceResponse:
        ...

    @abstractmethod
    async def get_topic_revision_recommendations(
        self, user_id: int, limit: int = 5
    ) -> TopicRevisionResponse:
        ...

    @abstractmethod
    async def get_question_revision_recommendations(
        self, user_id: int, limit: int = 10
    ) -> list[QuestionResponse]:
        ...
