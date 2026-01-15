from domain import (
    FixedWindowRateLimiter,
    RateLimitConfig,
    RateLimitResult,
    TimeUnit,
    TimeWindow,
)
from infrastructure import RedisClient


class RateLimitUseCase:
    """Use case for checking and incrementing rate limits."""

    def __init__(
        self,
        redis_client: RedisClient,
        limit: int = 100,
        window_duration: int = 1,
        window_unit: TimeUnit = TimeUnit.MINUTES,
    ):
        """
        Initialize the rate limit use case.

        Args:
            redis_client: Redis client for storage
            limit: Maximum requests allowed per window
            window_duration: Window duration
            window_unit: Unit for window duration
        """
        config = RateLimitConfig(
            limit=limit,
            window=TimeWindow(duration=window_duration, unit=window_unit),
        )
        self.rate_limiter = FixedWindowRateLimiter(config, redis_client)

    def _extract_ip_address(
        self, headers: dict[str, str], remote_addr: str
    ) -> str:
        """
        Extract client IP address from headers or remote address.

        Priority:
        1. X-Forwarded-For header (first IP if comma-separated)
        2. Remote address

        Args:
            headers: Request headers
            remote_addr: Remote address from connection

        Returns:
            IP address string
        """
        x_forwarded_for = headers.get(
            "x-forwarded-for", headers.get("X-Forwarded-For")
        )
        if x_forwarded_for:
            # Take the first IP if there are multiple (comma-separated)
            ip = x_forwarded_for.split(",")[0].strip()
            if ip:
                return ip

        # Fallback to remote address
        return remote_addr or "127.0.0.1"

    async def check_and_increment(
        self, headers: dict[str, str], remote_addr: str
    ) -> RateLimitResult:
        """
        Check and increment the rate limit for the given request.

        Args:
            headers: Request headers
            remote_addr: Remote address

        Returns:
            Rate limit result
        """
        identifier = self._extract_ip_address(headers, remote_addr)
        return await self.rate_limiter.check_and_increment(identifier)
