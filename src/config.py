import os
from dataclasses import dataclass

from domain import TimeUnit


@dataclass
class Config:
    redis_url: str
    port: int
    rate_limit_count: int
    rate_limit_window_duration: int
    rate_limit_window_unit: TimeUnit


def load_config() -> Config:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    port = int(os.getenv("PORT", "8000"))

    # Rate limit configuration with defaults
    rate_limit_count = int(os.getenv("RATE_LIMIT_COUNT", "100"))
    rate_limit_window_duration = int(
        os.getenv("RATE_LIMIT_WINDOW_DURATION", "1")
    )
    rate_limit_window_unit_str = os.getenv(
        "RATE_LIMIT_WINDOW_UNIT", "minutes"
    ).lower()

    # Parse time unit
    if rate_limit_window_unit_str == "seconds":
        rate_limit_window_unit = TimeUnit.SECONDS
    elif rate_limit_window_unit_str == "hours":
        rate_limit_window_unit = TimeUnit.HOURS
    else:  # default to minutes
        rate_limit_window_unit = TimeUnit.MINUTES

    return Config(
        redis_url=redis_url,
        port=port,
        rate_limit_count=rate_limit_count,
        rate_limit_window_duration=rate_limit_window_duration,
        rate_limit_window_unit=rate_limit_window_unit,
    )
