from domain import (
    CheckResult,
    CheckStatus,
    HealthCheckResult,
    HealthStatus,
)
from infrastructure.redis_client import RedisClient


class HealthCheckUseCase:
    def __init__(self, redis_client: RedisClient) -> None:
        self.redis_client = redis_client

    async def execute(self) -> HealthCheckResult:
        ping_ok = await self.redis_client.ping()
        check_status = CheckStatus.OK if ping_ok else CheckStatus.ERROR
        checks = {"redis": CheckResult(status=check_status)}
        overall_status = (
            HealthStatus.HEALTHY if ping_ok else HealthStatus.UNHEALTHY
        )
        return HealthCheckResult(status=overall_status, checks=checks)
