"""Tests for the health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_200(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_shape(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert "service" in body["data"]
    assert "version" in body["data"]


@pytest.mark.asyncio
async def test_health_check_version_matches_settings(client: AsyncClient) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    response = await client.get("/api/v1/health")
    body = response.json()
    assert body["data"]["version"] == settings.app_version
    assert body["data"]["service"] == settings.app_name
