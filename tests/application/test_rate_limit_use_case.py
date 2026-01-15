import pytest
from unittest.mock import AsyncMock, Mock

from application.rate_limit import RateLimitUseCase
from domain import RateLimitResult, RateLimitStatus, TimeUnit
from infrastructure import RedisClient


class TestRateLimitUseCase:
    @pytest.fixture
    def mock_redis_client(self):
        return AsyncMock(spec=RedisClient)

    @pytest.fixture
    def use_case(self, mock_redis_client):
        return RateLimitUseCase(
            redis_client=mock_redis_client,
            limit=100,
            window_duration=5,
            window_unit=TimeUnit.MINUTES
        )

    def test_initialization(self, mock_redis_client):
        """Test use case initializes correctly."""
        use_case = RateLimitUseCase(mock_redis_client)
        assert use_case.rate_limiter.config.limit == 100
        assert use_case.rate_limiter.config.window.duration == 1
        assert use_case.rate_limiter.config.window.unit == TimeUnit.MINUTES

    def test_custom_initialization(self, mock_redis_client):
        """Test use case initializes with custom parameters."""
        use_case = RateLimitUseCase(
            mock_redis_client,
            limit=50,
            window_duration=10,
            window_unit=TimeUnit.SECONDS
        )
        assert use_case.rate_limiter.config.limit == 50
        assert use_case.rate_limiter.config.window.duration == 10
        assert use_case.rate_limiter.config.window.unit == TimeUnit.SECONDS

    def test_extract_ip_address_x_forwarded_for(self, use_case):
        """Test IP extraction from X-Forwarded-For header."""
        headers = {"X-Forwarded-For": "192.168.1.100, 10.0.0.1"}
        remote_addr = "127.0.0.1"

        ip = use_case._extract_ip_address(headers, remote_addr)
        assert ip == "192.168.1.100"

    def test_extract_ip_address_x_forwarded_for_case_insensitive(self, use_case):
        """Test IP extraction from case-insensitive X-Forwarded-For header."""
        headers = {"x-forwarded-for": "192.168.1.100"}
        remote_addr = "127.0.0.1"

        ip = use_case._extract_ip_address(headers, remote_addr)
        assert ip == "192.168.1.100"

    def test_extract_ip_address_fallback_to_remote_addr(self, use_case):
        """Test IP extraction falls back to remote address when header missing."""
        headers = {}
        remote_addr = "10.0.0.50"

        ip = use_case._extract_ip_address(headers, remote_addr)
        assert ip == "10.0.0.50"

    def test_extract_ip_address_fallback_to_default(self, use_case):
        """Test IP extraction falls back to default when remote addr is None."""
        headers = {}
        remote_addr = None

        ip = use_case._extract_ip_address(headers, remote_addr)
        assert ip == "127.0.0.1"

    def test_extract_ip_address_empty_header(self, use_case):
        """Test IP extraction handles empty header."""
        headers = {"X-Forwarded-For": ""}
        remote_addr = "10.0.0.50"

        ip = use_case._extract_ip_address(headers, remote_addr)
        assert ip == "10.0.0.50"

    def test_extract_ip_address_whitespace_header(self, use_case):
        """Test IP extraction handles whitespace in header."""
        headers = {"X-Forwarded-For": "  "}
        remote_addr = "10.0.0.50"

        ip = use_case._extract_ip_address(headers, remote_addr)
        assert ip == "10.0.0.50"

    @pytest.mark.asyncio
    async def test_check_and_increment_allowed(self, use_case, mock_redis_client):
        """Test successful rate limit check returns allowed."""
        # Mock the rate limiter to return allowed result
        mock_result = RateLimitResult(
            status=RateLimitStatus.ALLOWED,
            limit=100,
            remaining=95,
            reset_time=1234567890
        )
        use_case.rate_limiter.check_and_increment = AsyncMock(return_value=mock_result)

        headers = {"X-Forwarded-For": "192.168.1.100"}
        remote_addr = "127.0.0.1"

        result = await use_case.check_and_increment(headers, remote_addr)

        assert result.status == RateLimitStatus.ALLOWED
        assert result.limit == 100
        assert result.remaining == 95
        assert result.reset_time == 1234567890

        # Verify the rate limiter was called with extracted IP
        use_case.rate_limiter.check_and_increment.assert_called_once_with("192.168.1.100")

    @pytest.mark.asyncio
    async def test_check_and_increment_rejected(self, use_case, mock_redis_client):
        """Test rate limit check returns rejected when over limit."""
        # Mock the rate limiter to return rejected result
        mock_result = RateLimitResult(
            status=RateLimitStatus.REJECTED,
            limit=100,
            remaining=0,
            reset_time=1234567890
        )
        use_case.rate_limiter.check_and_increment = AsyncMock(return_value=mock_result)

        headers = {}
        remote_addr = "192.168.1.100"

        result = await use_case.check_and_increment(headers, remote_addr)

        assert result.status == RateLimitStatus.REJECTED
        assert result.limit == 100
        assert result.remaining == 0
        assert result.reset_time == 1234567890

        # Verify the rate limiter was called with remote addr
        use_case.rate_limiter.check_and_increment.assert_called_once_with("192.168.1.100")