"""Question service interface contract."""

import uuid
from abc import ABC, abstractmethod

from app.constant.difficulty import DifficultyLevel
from app.schema.filter import FilterParams
from app.schema.question import (
    QuestionAdminResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.schema.response import PaginatedResponse


class IQuestionService(ABC):
    """Interface contract for Question business logic services."""

    @abstractmethod
    async def create_question(self, payload: QuestionCreate) -> QuestionAdminResponse:
        ...

    @abstractmethod
    async def get_question_by_id(self, question_id: uuid.UUID) -> QuestionResponse:
        ...

    @abstractmethod
    async def list_questions_paginated(
        self,
        filter_params: FilterParams,
        topic_id: uuid.UUID | None = None,
        difficulty: DifficultyLevel | None = None,
    ) -> PaginatedResponse[QuestionResponse]:
        ...

    @abstractmethod
    async def get_practice_questions(
        self, topic_ids: list[uuid.UUID], limit: int = 10
    ) -> list[QuestionResponse]:
        ...

    @abstractmethod
    async def update_question(
        self, question_id: uuid.UUID, payload: QuestionUpdate
    ) -> QuestionAdminResponse:
        ...

    @abstractmethod
    async def delete_question(self, question_id: uuid.UUID) -> None:
        ...
