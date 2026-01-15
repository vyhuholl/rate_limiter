import pytest

from config import Config
from domain import TimeUnit
from interface.web_app import create_app


@pytest.fixture
async def client_unhealthy(aiohttp_client):
    # Use invalid Redis URL so ping fails, resulting in unhealthy
    config = Config(
        redis_url="redis://invalid:6379",
        port=8000,
        rate_limit_count=100,
        rate_limit_window_duration=1,
        rate_limit_window_unit=TimeUnit.MINUTES
    )
    app = create_app(config)
    return await aiohttp_client(app)


@pytest.fixture
async def client_healthy(aiohttp_client):
    # Use what should be a valid Redis URL for integration tests
    # This assumes Redis is running locally
    config = Config(
        redis_url="redis://localhost:6379",
        port=8000,
        rate_limit_count=100,
        rate_limit_window_duration=1,
        rate_limit_window_unit=TimeUnit.MINUTES
    )
    app = create_app(config)
    return await aiohttp_client(app)


@pytest.mark.asyncio
async def test_health_endpoint_unhealthy(client_unhealthy):
    resp = await client_unhealthy.get("/health")
    assert resp.status == 503
    data = await resp.json()
    assert data["status"] == "unhealthy"
    assert "redis" in data["checks"]
    assert data["checks"]["redis"]["status"] == "error"
    assert data["checks"]["redis"]["message"] is None


@pytest.mark.asyncio
async def test_rate_limit_endpoint_allowed(client_healthy):
    """Test rate limit endpoint allows requests within limit."""
    resp = await client_healthy.get("/rate-limit")

    # Should return 200 for allowed requests
    assert resp.status == 200

    # Check rate limit headers are present
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers
    assert "X-RateLimit-Reset" in resp.headers

    # Parse header values
    limit = int(resp.headers["X-RateLimit-Limit"])
    remaining = int(resp.headers["X-RateLimit-Remaining"])
    reset = int(resp.headers["X-RateLimit-Reset"])

    # Basic sanity checks
    assert limit > 0  # Default limit should be positive
    assert remaining >= 0  # Remaining should be non-negative
    assert remaining <= limit  # Remaining should not exceed limit
    assert reset > 0  # Reset time should be in the future


@pytest.mark.asyncio
async def test_rate_limit_endpoint_with_x_forwarded_for(client_healthy):
    """Test rate limit endpoint uses X-Forwarded-For header."""
    headers = {"X-Forwarded-For": "192.168.1.100"}
    resp = await client_healthy.get("/rate-limit", headers=headers)

    assert resp.status == 200
    assert "X-RateLimit-Limit" in resp.headers


@pytest.mark.asyncio
async def test_rate_limit_endpoint_multiple_requests(client_healthy):
    """Test rate limit counting works across multiple requests from same IP."""
    # Use a unique IP for this test to avoid interference from other tests
    import time
    unique_ip = f"192.168.{int(time.time() * 1000000) % 256}.{(int(time.time() * 1000000) // 256) % 256}"
    headers = {"X-Forwarded-For": unique_ip}

    # Make multiple requests from the same IP
    for i in range(3):
        resp = await client_healthy.get("/rate-limit", headers=headers)
        assert resp.status == 200

        limit = int(resp.headers["X-RateLimit-Limit"])
        remaining = int(resp.headers["X-RateLimit-Remaining"])

        # Remaining should decrease with each request
        expected_remaining = limit - (i + 1)
        assert remaining == expected_remaining


@pytest.mark.asyncio
async def test_rate_limit_endpoint_fails_open_when_redis_unavailable(client_unhealthy):
    """Test rate limit endpoint allows requests when Redis is unavailable (fail-open)."""
    resp = await client_unhealthy.get("/rate-limit")

    # Should still return 200 (fail open) even when Redis is unavailable
    assert resp.status == 200

    # Headers should still be present (with default/degraded values)
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers
    assert "X-RateLimit-Reset" in resp.headers
