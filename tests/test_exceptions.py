"""Tests for custom and global exception handling."""

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.exception import NotFoundException
from app.main import create_app

dummy_error_router = APIRouter(prefix="/api/v1/dummy-errors")


@dummy_error_router.get("/custom-not-found")
async def trigger_custom_not_found() -> None:
    raise NotFoundException(entity="Topic", entity_id="12345")


@dummy_error_router.get("/unhandled-service-error")
async def trigger_unhandled_error() -> None:
    raise RuntimeError("Database connection suddenly dropped!")


@pytest.mark.asyncio
async def test_custom_exception_returns_formatted_json() -> None:
    app = create_app()
    app.include_router(dummy_error_router)
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/dummy-errors/custom-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "TOPIC_NOT_FOUND"
        assert "Topic not found: 12345" in data["error"]["message"]
        assert data["error"]["details"]["entity"] == "Topic"


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500_internal_server_error() -> None:
    app = create_app()
    app.include_router(dummy_error_router)
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/dummy-errors/unhandled-service-error")
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "unexpected error" in data["error"]["message"].lower()
