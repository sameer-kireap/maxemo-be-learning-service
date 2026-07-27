"""Question service interface contract."""

import uuid
from typing import Protocol

from app.constant.difficulty import DifficultyLevel
from app.model.question import Question


class QuestionServiceProtocol(Protocol):
    """Interface contract for Question business logic services."""

    async def create_question(
        self,
        text: str,
        options: list[str],
        correct_option_index: int,
        difficulty: DifficultyLevel,
        topic_ids: list[uuid.UUID],
    ) -> Question:
        ...

    async def get_question_by_id(self, question_id: uuid.UUID) -> Question:
        ...

    async def list_questions(
        self,
        topic_id: uuid.UUID | None = None,
        difficulty: DifficultyLevel | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Question]:
        ...

    async def get_practice_questions(
        self, topic_ids: list[uuid.UUID], limit: int = 10
    ) -> list[Question]:
        ...

    async def update_question(
        self,
        question_id: uuid.UUID,
        text: str | None = None,
        options: list[str] | None = None,
        correct_option_index: int | None = None,
        difficulty: DifficultyLevel | None = None,
        topic_ids: list[uuid.UUID] | None = None,
    ) -> Question:
        ...

    async def delete_question(self, question_id: uuid.UUID) -> None:
        ...
