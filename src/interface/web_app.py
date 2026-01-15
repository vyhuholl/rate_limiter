from aiohttp import web

from application.health_check import HealthCheckUseCase
from application.rate_limit import RateLimitUseCase
from domain import HealthStatus, RateLimitStatus
from infrastructure.redis_client import RedisClient


def create_app(config) -> web.Application:
    redis_client = RedisClient(config.redis_url)
    health_use_case = HealthCheckUseCase(redis_client)
    rate_limit_use_case = RateLimitUseCase(
        redis_client,
        limit=config.rate_limit_count,
        window_duration=config.rate_limit_window_duration,
        window_unit=config.rate_limit_window_unit,
    )

    async def health_handler(request):
        result = await health_use_case.execute()
        data = {
            "status": result.status.value,
            "checks": {
                name: {"status": check.status.value, "message": check.message}
                for name, check in result.checks.items()
            },
        }
        status_code = 200 if result.status == HealthStatus.HEALTHY else 503
        return web.json_response(data, status=status_code)

    async def rate_limit_handler(request):
        # Extract headers and remote address
        headers = dict(request.headers)
        remote_addr = request.remote or "127.0.0.1"

        # Check and increment rate limit
        result = await rate_limit_use_case.check_and_increment(
            headers, remote_addr
        )

        # Determine HTTP status code
        status_code = 200 if result.status == RateLimitStatus.ALLOWED else 429

        # Create response with rate limit headers
        response = web.Response(status=status_code)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset_time)

        return response

    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/rate-limit", rate_limit_handler)
    return app
