import os
from dataclasses import dataclass


@dataclass
class Config:
    redis_url: str
    port: int


def load_config() -> Config:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    port = int(os.getenv("PORT", "8000"))
    return Config(redis_url=redis_url, port=port)
