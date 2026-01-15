import pytest

from interface.web_app import create_app


@pytest.fixture
async def client(aiohttp_client):
    # Use invalid Redis URL so ping fails, resulting in unhealthy
    app = create_app("redis://invalid:6379")
    return await aiohttp_client(app)


@pytest.mark.asyncio
async def test_health_endpoint_unhealthy(client):
    resp = await client.get("/health")
    assert resp.status == 503
    data = await resp.json()
    assert data["status"] == "unhealthy"
    assert "redis" in data["checks"]
    assert data["checks"]["redis"]["status"] == "error"
    assert data["checks"]["redis"]["message"] is None
