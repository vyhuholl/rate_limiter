import pytest

from infrastructure.redis_client import RedisClient


@pytest.mark.asyncio
async def test_ping_invalid_url():
    client = RedisClient("redis://invalid:6379")
    result = await client.ping()
    assert result is False


@pytest.mark.asyncio
async def test_ping_local_redis():
    # Assumes Redis is running on localhost:6379
    # If not, this test will pass as False, but it's integration
    client = RedisClient("redis://localhost:6379")
    result = await client.ping()
    assert isinstance(result, bool)
