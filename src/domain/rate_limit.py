from dataclasses import dataclass
from enum import Enum
from typing import Protocol
import time


class RateLimitStatus(Enum):
    ALLOWED = "allowed"
    REJECTED = "rejected"


class TimeUnit(Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


@dataclass
class TimeWindow:
    duration: int
    unit: TimeUnit


@dataclass
class RateLimitResult:
    status: RateLimitStatus
    limit: int
    remaining: int
    reset_time: int  # Unix timestamp when window resets


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


class RateLimiter(Protocol):
    """Protocol for rate limiting algorithms."""

    async def check_and_increment(self, identifier: str) -> RateLimitResult:
        """
        Check if the identifier is within the rate limit and increment the counter.

        Args:
            identifier: The identifier to check (e.g., IP address)

        Returns:
            RateLimitResult with the decision and metadata
        """
        ...


@dataclass
class RateLimitConfig:
    limit: int
    window: TimeWindow


class FixedWindowRateLimiter(RateLimiter):
    """Fixed window rate limiter implementation."""

    def __init__(self, config: RateLimitConfig, storage: RateLimitStorage):
        self.config = config
        self.storage = storage

    def _get_window_seconds(self) -> int:
        """Convert window duration to seconds."""
        match self.config.window.unit:
            case TimeUnit.SECONDS:
                return self.config.window.duration
            case TimeUnit.MINUTES:
                return self.config.window.duration * 60
            case TimeUnit.HOURS:
                return self.config.window.duration * 3600

    def _get_window_start(self, current_time: int) -> int:
        """Get the start time of the current window."""
        window_seconds = self._get_window_seconds()
        return (current_time // window_seconds) * window_seconds

    def _get_key(self, identifier: str, window_start: int) -> str:
        """Generate the storage key for the identifier and window."""
        return f"rate_limit:{identifier}:{window_start}"

    async def check_and_increment(self, identifier: str) -> RateLimitResult:
        """Check rate limit and increment counter."""
        current_time = int(time.time())
        window_start = self._get_window_start(current_time)
        window_seconds = self._get_window_seconds()
        reset_time = window_start + window_seconds

        key = self._get_key(identifier, window_start)
        count = await self.storage.increment(key, window_seconds)

        remaining = self.config.limit - count
        status = (
            RateLimitStatus.ALLOWED
            if count <= self.config.limit
            else RateLimitStatus.REJECTED
        )

        return RateLimitResult(
            status=status,
            limit=self.config.limit,
            remaining=max(0, remaining),  # Ensure remaining is never negative
            reset_time=reset_time,
        )
