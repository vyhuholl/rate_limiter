from domain import (
    CheckResult,
    CheckStatus,
    HealthCheckResult,
    HealthStatus,
)


class TestHealthStatus:
    def test_enum_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"

    def test_all_values(self):
        expected = {"healthy", "degraded", "unhealthy"}
        actual = {status.value for status in HealthStatus}
        assert actual == expected


class TestCheckStatus:
    def test_enum_values(self):
        assert CheckStatus.OK.value == "ok"
        assert CheckStatus.ERROR.value == "error"

    def test_all_values(self):
        expected = {"ok", "error"}
        actual = {status.value for status in CheckStatus}
        assert actual == expected


class TestCheckResult:
    def test_creation_without_message(self):
        result = CheckResult(status=CheckStatus.OK)
        assert result.status == CheckStatus.OK
        assert result.message is None

    def test_creation_with_message(self):
        result = CheckResult(
            status=CheckStatus.ERROR, message="Connection failed"
        )
        assert result.status == CheckStatus.ERROR
        assert result.message == "Connection failed"

    def test_equality(self):
        result1 = CheckResult(status=CheckStatus.OK)
        result2 = CheckResult(status=CheckStatus.OK)
        assert result1 == result2

        result3 = CheckResult(status=CheckStatus.ERROR, message="Error")
        assert result1 != result3


class TestHealthCheckResult:
    def test_creation(self):
        checks = {"redis": CheckResult(status=CheckStatus.OK)}
        result = HealthCheckResult(status=HealthStatus.HEALTHY, checks=checks)
        assert result.status == HealthStatus.HEALTHY
        assert result.checks == checks

    def test_equality(self):
        checks1 = {"redis": CheckResult(status=CheckStatus.OK)}
        checks2 = {"redis": CheckResult(status=CheckStatus.OK)}
        result1 = HealthCheckResult(
            status=HealthStatus.HEALTHY, checks=checks1
        )
        result2 = HealthCheckResult(
            status=HealthStatus.HEALTHY, checks=checks2
        )
        assert result1 == result2
