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
- `RATE_LIMIT_COUNT`: Maximum requests per time window (default: 100)
- `RATE_LIMIT_WINDOW_DURATION`: Time window duration (default: 1)
- `RATE_LIMIT_WINDOW_UNIT`: Time window unit - "seconds", "minutes", or "hours" (default: "minutes")

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

## Rate Limiting

The service provides a rate limiting endpoint at `/rate-limit` that demonstrates fixed window rate limiting based on IP address.

### Algorithm

- **Fixed Window**: Requests are counted within fixed time windows
- **IP-based**: Rate limits are applied per client IP address
- **Redis-backed**: Distributed state storage ensures consistency across multiple instances

### Configuration

Rate limiting is configured via environment variables:
- Default: 100 requests per minute per IP address
- Configurable window sizes: seconds, minutes, hours

### Endpoint

**GET /rate-limit**

Returns rate limit status for the requesting IP address.

### Response

- **200 OK**: Request allowed
- **429 Too Many Requests**: Rate limit exceeded

Response headers:
- `X-RateLimit-Limit`: Maximum requests allowed per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets

### Examples

Check rate limit status:
```bash
curl -v http://localhost:8000/rate-limit
```

Response headers:
```
< HTTP/1.1 200 OK
< X-RateLimit-Limit: 100
< X-RateLimit-Remaining: 99
< X-RateLimit-Reset: 1704067200
```

When limit exceeded:
```bash
curl -v http://localhost:8000/rate-limit
```

Response:
```
< HTTP/1.1 429 Too Many Requests
< X-RateLimit-Limit: 100
< X-RateLimit-Remaining: 0
< X-RateLimit-Reset: 1704067200
```

### IP Address Detection

The service uses the `X-Forwarded-For` header (first IP if comma-separated) for rate limiting, falling back to the remote address when the header is not present. This supports proxy/load balancer deployments.
