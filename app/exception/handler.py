"""Global exception handlers for FastAPI application."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exception.base import CustomException

logger = logging.getLogger(__name__)


async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles all CustomException subclasses and returns a unified error response."""
    if not isinstance(exc, CustomException):
        return await global_unhandled_exception_handler(request, exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handles FastAPI/Pydantic request validation errors."""
    if not isinstance(exc, RequestValidationError):
        return await global_unhandled_exception_handler(request, exc)

    formatted_errors: list[dict[str, Any]] = [
        {"loc": list(err.get("loc", [])), "msg": err.get("msg", ""), "type": err.get("type", "")}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed.",
                "details": formatted_errors,
            }
        },
    )


async def global_unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler for unhandled service crashes and internal errors (500)."""
    logger.exception(
        "Unhandled error processing request: %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request.",
                "details": {},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers exception handlers with the FastAPI application instance."""
    app.add_exception_handler(CustomException, custom_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_unhandled_exception_handler)
