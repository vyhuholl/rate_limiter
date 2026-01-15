from aiohttp import web

from application.health_check import HealthCheckUseCase
from domain import HealthStatus
from infrastructure.redis_client import RedisClient


def create_app(redis_url: str) -> web.Application:
    redis_client = RedisClient(redis_url)
    use_case = HealthCheckUseCase(redis_client)

    async def health_handler(request):
        result = await use_case.execute()
        data = {
            "status": result.status.value,
            "checks": {
                name: {"status": check.status.value, "message": check.message}
                for name, check in result.checks.items()
            },
        }
        status_code = 200 if result.status == HealthStatus.HEALTHY else 503
        return web.json_response(data, status=status_code)

    app = web.Application()
    app.router.add_get("/health", health_handler)
    return app
