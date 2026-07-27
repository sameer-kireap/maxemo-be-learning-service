"""SQLAlchemy declarative base and timestamp/audit mixins."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.constant.schema import LEARNING_SCHEMA


class Base(DeclarativeBase):
    metadata = MetaData(schema=LEARNING_SCHEMA)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
