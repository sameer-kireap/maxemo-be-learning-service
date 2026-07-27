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
    assert body["status"] == "healthy"
    assert "service" in body
    assert "version" in body


@pytest.mark.asyncio
async def test_health_check_version_matches_settings(client: AsyncClient) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    response = await client.get("/api/v1/health")
    body = response.json()
    assert body["version"] == settings.app_version
    assert body["service"] == settings.app_name
