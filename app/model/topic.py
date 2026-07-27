"""Topic model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant.schema import LEARNING_SCHEMA
from app.model.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.model.question import Question


class Topic(Base, TimestampMixin):
    __tablename__ = "topics"
    __table_args__ = {"schema": LEARNING_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    questions: Mapped[list["Question"]] = relationship(  # noqa: F821
        "Question",
        secondary=f"{LEARNING_SCHEMA}.question_topics",
        back_populates="topics",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"Topic(id={self.id!r}, name={self.name!r})"
