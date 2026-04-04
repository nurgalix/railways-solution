"""
Integration tests for REST API endpoints.
Uses httpx async client with the FastAPI TestClient pattern.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from httpx import AsyncClient, ASGITransport

# We need to set env vars BEFORE importing the app
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/railways")
os.environ.setdefault("SIMULATOR_ENABLED", "false")  # Don't start simulator in tests


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_root():
    """Test root endpoint returns service info."""
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Locomotive Digital Twin API"
        assert "version" in data


@pytest.mark.anyio
async def test_healthcheck():
    """Test healthcheck endpoint."""
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/healthcheck")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_health_formula():
    """Test health formula endpoint returns formula description."""
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health/formula")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "scoring" in data


@pytest.mark.anyio
async def test_config_thresholds():
    """Test config thresholds endpoint returns config."""
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/config/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert "parameters" in data
        assert "speed" in data["parameters"]


@pytest.mark.anyio
async def test_openapi_docs():
    """Test OpenAPI docs are accessible."""
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Locomotive Digital Twin API"
