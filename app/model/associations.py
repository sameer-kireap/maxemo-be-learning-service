"""M:N association table between questions and topics."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.constant.schema import LEARNING_SCHEMA
from app.model.base import Base


class QuestionTopic(Base):
    __tablename__ = "question_topics"
    __table_args__ = {"schema": LEARNING_SCHEMA}

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{LEARNING_SCHEMA}.questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{LEARNING_SCHEMA}.topics.id", ondelete="CASCADE"),
        primary_key=True,
    )


question_topic_table = QuestionTopic.__table__
