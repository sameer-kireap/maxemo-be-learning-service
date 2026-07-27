"""QuestionAttempt model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant.schema import LEARNING_SCHEMA
from app.model.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.model.question import Question


class QuestionAttempt(Base, TimestampMixin):
    __tablename__ = "question_attempts"
    __table_args__ = (
        Index("idx_attempts_user_id", "user_id"),
        Index("idx_attempts_user_created_at", "user_id", "created_at"),
        {"schema": LEARNING_SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[int] = mapped_column(Integer)

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{LEARNING_SCHEMA}.questions.id"),
        index=True,
    )

    selected_option_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_correct: Mapped[bool] = mapped_column(Boolean)

    time_taken_seconds: Mapped[int] = mapped_column(Integer)

    question: Mapped["Question"] = relationship(  # noqa: F821
        "Question",
        back_populates="attempts",
        lazy="raise",
        foreign_keys="[QuestionAttempt.question_id]",
    )

    def __repr__(self) -> str:
        return (
            f"QuestionAttempt("
            f"id={self.id!r}, user_id={self.user_id!r}, is_correct={self.is_correct!r})"
        )
