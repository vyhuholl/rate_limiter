# rate_limiter
A distributed rate limiter for API endpoints using Redis. The service provides configurable rate limiting strategies to protect APIs from abuse, ensure fair resource allocation, and maintain system stability under high load.

## Installation

Install dependencies with uv:

```bash
uv install
```

## Running

Run the service:

```bash
uv run python src/main.py
```

The server will start on port 8000 by default.

## Configuration

- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379)
- `PORT`: Server port (default: 8000)

## Health Check

The service provides a health check endpoint at `/health` to verify service availability and Redis connectivity.

### Response

- **200 OK**: Service is healthy
- **503 Service Unavailable**: Service is unhealthy

Response body:

```json
{
  "status": "healthy" | "unhealthy",
  "checks": {
    "redis": {
      "status": "ok" | "error",
      "message": null
    }
  }
}
```

### Example

```bash
curl http://localhost:8000/health
```
