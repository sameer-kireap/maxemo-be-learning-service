"""Unified error response schema."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: dict[str, Any] | list[Any] = Field(
        default_factory=dict, description="Additional contextual information"
    )


class ErrorResponse(BaseModel):
    error: ErrorDetail
