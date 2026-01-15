from redis import asyncio as aioredis


class RedisClient:
    def __init__(self, url: str) -> None:
        self._client = aioredis.from_url(url)

    async def ping(self) -> bool:
        try:
            await self._client.ping()
            return True
        except Exception:
            return False
