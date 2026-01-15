# Change: Add Fixed Window Rate Limiter

## Why
The rate limiter service needs core rate limiting functionality to protect API endpoints from abuse, ensure fair resource allocation, and maintain system stability under high load. Implementing the fixed window algorithm first provides a solid foundation that can be extended with additional algorithms (token bucket, sliding window) in the future.

## What Changes
- Add fixed window rate limiting algorithm using Redis for distributed state management
- Add HTTP endpoint for checking and incrementing rate limits
- Rate limit requests by IP address
- Return HTTP 429 (Too Many Requests) when limit is exceeded
- Support configurable time windows (seconds, minutes, hours)
- Global rate limit configuration (limit count per window)
- Include rate limit headers in responses (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)

## Impact
- Affected specs: New capability `rate-limiting`
- Affected code: New domain models for rate limiting, Redis storage implementation, HTTP endpoint handler, configuration updates
