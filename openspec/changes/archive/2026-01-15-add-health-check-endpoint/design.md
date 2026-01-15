## Context
This is the foundational feature for the rate limiter service. The health check endpoint will be the first HTTP endpoint implemented and will establish the HTTP server infrastructure. It needs to verify connectivity to Redis Cluster, which is the primary external dependency for the rate limiter.

## Goals / Non-Goals
- Goals:
  - Provide a simple, fast health check endpoint for monitoring
  - Verify Redis Cluster connectivity
  - Return structured health status information
  - Follow Clean Architecture principles
  - Use async/await patterns throughout
- Non-Goals:
  - Detailed metrics collection (deferred to Prometheus integration)
  - Advanced health checks (deferred to future work)
  - Authentication/authorization on health endpoint (deferred to future work)

## Decisions
- Decision: Use aiohttp as the HTTP server framework
  - Rationale: Native async support, lightweight, well-maintained, fits the asyncio tech stack
  - Alternatives considered: FastAPI (overkill for health check only), Starlette (similar but aiohttp more mature for pure HTTP), custom asyncio server (too much boilerplate)

- Decision: Health check returns JSON response with `status` field and optional `checks` object
  - Rationale: Standard format that monitoring systems can parse easily
  - Structure:
    ```json
    {
      "status": "healthy" | "degraded" | "unhealthy",
      "checks": {
        "redis": {
          "status": "ok" | "error",
          "message": "optional details"
        }
      }
    }
    ```

- Decision: Use HTTP 200 for healthy, 503 for unhealthy/degraded
  - Rationale: Standard HTTP semantics that orchestrators understand

- Decision: Implement health check as a use case in Application layer
  - Rationale: Follows Clean Architecture - domain logic in Domain layer, use cases in Application layer, HTTP handling in Interface layer

## Risks / Trade-offs
- Risk: Redis connection pool exhaustion under heavy health check traffic
  - Mitigation: Use a dedicated Redis connection for health checks or implement connection pooling with limits
- Trade-off: Simple health check vs comprehensive diagnostics
  - Decision: Start simple, add detailed checks as needed
- Risk: False positives in health checks (service appears healthy but rate limiting fails)
  - Mitigation: Health check verifies actual Redis operations (PING command), not just connection status

## Migration Plan
No migration required - this is a new feature.

## Open Questions
- Should the health check endpoint be configurable (path, response format)?
- Should there be a readiness probe separate from liveness probe?
- What timeout should be used for Redis connectivity check?
