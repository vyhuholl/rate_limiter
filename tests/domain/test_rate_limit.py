import pytest
from unittest.mock import AsyncMock, Mock

from domain import (
    FixedWindowRateLimiter,
    RateLimitConfig,
    RateLimitResult,
    RateLimitStatus,
    RateLimitStorage,
    TimeUnit,
    TimeWindow,
)


class TestRateLimitStatus:
    def test_enum_values(self):
        assert RateLimitStatus.ALLOWED.value == "allowed"
        assert RateLimitStatus.REJECTED.value == "rejected"

    def test_all_values(self):
        expected = {"allowed", "rejected"}
        actual = {status.value for status in RateLimitStatus}
        assert actual == expected


class TestTimeUnit:
    def test_enum_values(self):
        assert TimeUnit.SECONDS.value == "seconds"
        assert TimeUnit.MINUTES.value == "minutes"
        assert TimeUnit.HOURS.value == "hours"

    def test_all_values(self):
        expected = {"seconds", "minutes", "hours"}
        actual = {unit.value for unit in TimeUnit}
        assert actual == expected


class TestTimeWindow:
    def test_creation(self):
        window = TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        assert window.duration == 5
        assert window.unit == TimeUnit.MINUTES

    def test_equality(self):
        window1 = TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        window2 = TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        window3 = TimeWindow(duration=10, unit=TimeUnit.SECONDS)
        assert window1 == window2
        assert window1 != window3


class TestRateLimitResult:
    def test_creation_allowed(self):
        result = RateLimitResult(
            status=RateLimitStatus.ALLOWED,
            limit=100,
            remaining=95,
            reset_time=1234567890
        )
        assert result.status == RateLimitStatus.ALLOWED
        assert result.limit == 100
        assert result.remaining == 95
        assert result.reset_time == 1234567890

    def test_creation_rejected(self):
        result = RateLimitResult(
            status=RateLimitStatus.REJECTED,
            limit=100,
            remaining=0,
            reset_time=1234567890
        )
        assert result.status == RateLimitStatus.REJECTED
        assert result.limit == 100
        assert result.remaining == 0
        assert result.reset_time == 1234567890

    def test_equality(self):
        result1 = RateLimitResult(
            status=RateLimitStatus.ALLOWED,
            limit=100,
            remaining=95,
            reset_time=1234567890
        )
        result2 = RateLimitResult(
            status=RateLimitStatus.ALLOWED,
            limit=100,
            remaining=95,
            reset_time=1234567890
        )
        result3 = RateLimitResult(
            status=RateLimitStatus.REJECTED,
            limit=100,
            remaining=0,
            reset_time=1234567890
        )
        assert result1 == result2
        assert result1 != result3


class TestRateLimitConfig:
    def test_creation(self):
        window = TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        config = RateLimitConfig(limit=100, window=window)
        assert config.limit == 100
        assert config.window == window

    def test_equality(self):
        window1 = TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        window2 = TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        config1 = RateLimitConfig(limit=100, window=window1)
        config2 = RateLimitConfig(limit=100, window=window2)
        config3 = RateLimitConfig(limit=50, window=window1)
        assert config1 == config2
        assert config1 != config3


class TestFixedWindowRateLimiter:
    @pytest.fixture
    def mock_storage(self):
        return AsyncMock(spec=RateLimitStorage)

    @pytest.fixture
    def config(self):
        return RateLimitConfig(
            limit=100,
            window=TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        )

    @pytest.fixture
    def limiter(self, config, mock_storage):
        return FixedWindowRateLimiter(config, mock_storage)

    def test_window_seconds_seconds(self):
        config = RateLimitConfig(
            limit=100,
            window=TimeWindow(duration=30, unit=TimeUnit.SECONDS)
        )
        limiter = FixedWindowRateLimiter(config, Mock())
        assert limiter._get_window_seconds() == 30

    def test_window_seconds_minutes(self):
        config = RateLimitConfig(
            limit=100,
            window=TimeWindow(duration=5, unit=TimeUnit.MINUTES)
        )
        limiter = FixedWindowRateLimiter(config, Mock())
        assert limiter._get_window_seconds() == 300  # 5 * 60

    def test_window_seconds_hours(self):
        config = RateLimitConfig(
            limit=100,
            window=TimeWindow(duration=2, unit=TimeUnit.HOURS)
        )
        limiter = FixedWindowRateLimiter(config, Mock())
        assert limiter._get_window_seconds() == 7200  # 2 * 3600

    def test_window_start(self, limiter):
        # For a 5-minute window (300 seconds)
        # Timestamp 1234567890 should be in window starting at 1234567800
        # (1234567890 // 300) * 300 = 41152263 * 300 = 12345678900, wait let me calculate properly
        # Actually, let's use a simpler timestamp
        current_time = 1000  # Simple timestamp
        window_seconds = 300  # 5 minutes
        expected_start = (1000 // 300) * 300  # (3) * 300 = 900
        assert limiter._get_window_start(1000) == 900

    def test_key_generation(self, limiter):
        key = limiter._get_key("192.168.1.1", 900)
        assert key == "rate_limit:192.168.1.1:900"

    @pytest.mark.asyncio
    async def test_check_and_increment_allowed(self, limiter, mock_storage):
        # Mock storage returns count of 5 (within limit of 100)
        mock_storage.increment.return_value = 5

        result = await limiter.check_and_increment("192.168.1.1")

        assert result.status == RateLimitStatus.ALLOWED
        assert result.limit == 100
        assert result.remaining == 95  # 100 - 5
        assert isinstance(result.reset_time, int)
        mock_storage.increment.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_and_increment_at_limit(self, limiter, mock_storage):
        # Mock storage returns count of 100 (at limit)
        mock_storage.increment.return_value = 100

        result = await limiter.check_and_increment("192.168.1.1")

        assert result.status == RateLimitStatus.ALLOWED  # At limit is still allowed
        assert result.limit == 100
        assert result.remaining == 0  # 100 - 100

    @pytest.mark.asyncio
    async def test_check_and_increment_over_limit(self, limiter, mock_storage):
        # Mock storage returns count of 101 (over limit)
        mock_storage.increment.return_value = 101

        result = await limiter.check_and_increment("192.168.1.1")

        assert result.status == RateLimitStatus.REJECTED
        assert result.limit == 100
        assert result.remaining == 0  # max(0, 100 - 101) = 0

    @pytest.mark.asyncio
    async def test_check_and_increment_negative_remaining(self, limiter, mock_storage):
        # Mock storage returns count of 150 (way over limit)
        mock_storage.increment.return_value = 150

        result = await limiter.check_and_increment("192.168.1.1")

        assert result.status == RateLimitStatus.REJECTED
        assert result.limit == 100
        assert result.remaining == 0  # max(0, 100 - 150) = 0