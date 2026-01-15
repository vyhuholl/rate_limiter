# Change: Add Health Check Endpoint

## Why
The rate limiter service needs a health check endpoint to enable monitoring systems and orchestrators (like Kubernetes) to verify service availability and Redis Cluster connectivity. This is essential for production deployment and operational observability.

## What Changes
- Add HTTP health check endpoint at `/health`
- Endpoint returns service status and Redis Cluster connectivity verification
- Return appropriate HTTP status codes (200 for healthy, 503 for unhealthy)
- Include response body with detailed health status information

## Impact
- Affected specs: New capability `health-check`
- Affected code: New HTTP server infrastructure, Redis client integration
