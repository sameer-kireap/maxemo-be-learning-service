"""Question model."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant.difficulty import DifficultyLevel
from app.constant.schema import LEARNING_SCHEMA
from app.model.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.model.attempt import QuestionAttempt
    from app.model.topic import Topic


class Question(Base, TimestampMixin):
    __tablename__ = "questions"
    __table_args__ = {"schema": LEARNING_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(Text)

    options: Mapped[Any] = mapped_column(JSON)

    correct_option_index: Mapped[int] = mapped_column(Integer)

    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", schema=LEARNING_SCHEMA, create_type=True),
        default=DifficultyLevel.MEDIUM,
        server_default=DifficultyLevel.MEDIUM.value,
    )

    topics: Mapped[list["Topic"]] = relationship(  # noqa: F821
        "Topic",
        secondary=f"{LEARNING_SCHEMA}.question_topics",
        back_populates="questions",
        lazy="raise",
    )
    attempts: Mapped[list["QuestionAttempt"]] = relationship(  # noqa: F821
        "QuestionAttempt",
        back_populates="question",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, difficulty={self.difficulty!r})"
