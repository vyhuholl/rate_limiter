from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class CheckStatus(Enum):
    OK = "ok"
    ERROR = "error"


@dataclass
class CheckResult:
    status: CheckStatus
    message: str | None = None


@dataclass
class HealthCheckResult:
    status: HealthStatus
    checks: dict[str, CheckResult]
