"""Pydantic schemas."""

from app.schema.error import ErrorDetail, ErrorResponse
from app.schema.health import HealthResponse

__all__ = ["ErrorDetail", "ErrorResponse", "HealthResponse"]
