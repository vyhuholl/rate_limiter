import pytest

from application.health_check import HealthCheckUseCase
from domain import CheckStatus, HealthStatus


@pytest.mark.asyncio
async def test_execute_ping_success(mocker):
    mock_redis = mocker.AsyncMock()
    mock_redis.ping.return_value = True

    use_case = HealthCheckUseCase(mock_redis)
    result = await use_case.execute()

    assert result.status == HealthStatus.HEALTHY
    assert "redis" in result.checks
    assert result.checks["redis"].status == CheckStatus.OK
    assert result.checks["redis"].message is None


@pytest.mark.asyncio
async def test_execute_ping_failure(mocker):
    mock_redis = mocker.AsyncMock()
    mock_redis.ping.return_value = False

    use_case = HealthCheckUseCase(mock_redis)
    result = await use_case.execute()

    assert result.status == HealthStatus.UNHEALTHY
    assert result.checks["redis"].status == CheckStatus.ERROR
    assert result.checks["redis"].message is None
