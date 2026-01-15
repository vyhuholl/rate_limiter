from redis import asyncio as aioredis
from typing import Protocol


class RateLimitStorage(Protocol):
    """Protocol for rate limit storage operations."""

    async def increment(self, key: str, ttl: int) -> int:
        """
        Atomically increment the counter for the given key and set TTL.

        Args:
            key: The key to increment
            ttl: Time-to-live in seconds

        Returns:
            The new counter value after increment
        """
        ...


class RedisClient(RateLimitStorage):
    def __init__(self, url: str) -> None:
        self._client = aioredis.from_url(url)

    async def ping(self) -> bool:
        try:
            await self._client.ping()
            return True
        except Exception:
            return False

    async def increment(self, key: str, ttl: int) -> int:
        """
        Atomically increment the counter for the given key and set TTL if it's a new key.

        Uses a Lua script to ensure atomicity:
        - INCR increments the counter
        - EXPIRE sets TTL only if the key didn't exist before (ttl > 0 check)

        Args:
            key: The key to increment
            ttl: Time-to-live in seconds

        Returns:
            The new counter value after increment
        """
        try:
            # Lua script for atomic increment with conditional expiration
            lua_script = """
            local count = redis.call('INCR', KEYS[1])
            if count == 1 then
                redis.call('EXPIRE', KEYS[1], ARGV[1])
            end
            return count
            """

            count = await self._client.eval(lua_script, 1, key, ttl)
            return count
        except Exception:
            # If Redis is unavailable, return 1 (fail open)
            return 1
