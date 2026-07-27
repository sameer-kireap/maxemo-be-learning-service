"""Attempt service interface contract."""

import uuid
from abc import ABC, abstractmethod
from typing import Any

from app.model.attempt import QuestionAttempt
from app.model.question import Question


class IAttemptService(ABC):
    """Interface contract for QuestionAttempt business logic services."""

    @abstractmethod
    async def submit_attempt(
        self,
        user_id: int,
        question_id: uuid.UUID,
        selected_option_index: int | None,
        time_taken_seconds: int,
    ) -> QuestionAttempt:
        ...

    @abstractmethod
    async def get_user_attempts(
        self, user_id: int, offset: int = 0, limit: int = 100
    ) -> list[QuestionAttempt]:
        ...

    @abstractmethod
    async def get_user_performance_summary(self, user_id: int) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_user_topic_performance(self, user_id: int) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_revision_recommendations(
        self, user_id: int, limit: int = 10
    ) -> list[Question]:
        ...
