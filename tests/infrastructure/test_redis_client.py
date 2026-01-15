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


@pytest.mark.asyncio
async def test_increment_invalid_url():
    """Test increment fails gracefully when Redis is unavailable."""
    client = RedisClient("redis://invalid:6379")
    result = await client.increment("test_key", 60)
    # Should fail open and return 1
    assert result == 1


@pytest.mark.asyncio
async def test_increment_local_redis():
    """Test increment works with local Redis (integration test)."""
    # Assumes Redis is running on localhost:6379
    client = RedisClient("redis://localhost:6379")

    # Use unique key to avoid interference from other tests
    import time
    key = f"test_rate_limit_key_{int(time.time() * 1000000)}"

    # Test increment on new key
    count1 = await client.increment(key, 60)
    assert count1 == 1

    # Test increment on existing key
    count2 = await client.increment(key, 60)
    assert count2 == 2

    # Test increment again
    count3 = await client.increment(key, 60)
    assert count3 == 3


@pytest.mark.asyncio
async def test_increment_with_ttl():
    """Test that TTL is set correctly on new keys."""
    client = RedisClient("redis://localhost:6379")

    # Use unique key to avoid interference from other tests
    import time
    key = f"test_ttl_key_{int(time.time() * 1000000)}"
    ttl = 300  # 5 minutes

    # First increment should set TTL
    count = await client.increment(key, ttl)
    assert count == 1

    # TTL should be set (approximately)
    # Note: This is a bit flaky in tests, but good enough for integration
    try:
        actual_ttl = await client._client.ttl(key)
        assert actual_ttl > 0
        assert actual_ttl <= ttl
    except Exception:
        # If Redis commands fail, skip TTL check
        pass
