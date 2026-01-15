## Context
The rate limiter service needs to implement core rate limiting functionality using the fixed window algorithm. This is the foundational feature of the service and will be used to protect API endpoints from abuse. The service already has Redis infrastructure for distributed state management, which will be leveraged for storing rate limit counters.

### Constraints
- Must use Redis for distributed state storage (already in project)
- Must follow Clean Architecture pattern (Domain, Application, Infrastructure, Interface)
- Must support asyncio for non-blocking operations
- Must be thread-safe for concurrent requests
- Must handle Redis connection failures gracefully

### Stakeholders
- API consumers who need rate limiting protection
- System operators who need to monitor and configure rate limits
- Developers who will extend with additional algorithms in the future

## Goals / Non-Goals

### Goals
- Implement a simple, correct fixed window rate limiting algorithm
- Store rate limit state in Redis for distributed consistency
- Provide HTTP endpoint for rate limit checking and incrementing
- Return appropriate HTTP status codes and headers
- Support configurable time windows and limits
- Write comprehensive tests for all components

### Non-Goals
- Implementing other rate limiting algorithms (token bucket, sliding window, etc.)
- Per-identifier rate limit configuration (global only for now)
- Rate limit bypass mechanisms
- Advanced analytics or dashboards
- Distributed locking (not needed for fixed window with Redis INCR)

## Decisions

### Decision 1: Use Redis INCR with expiration for fixed window counters
**What**: Store rate limit counters as Redis keys with INCR operations and automatic expiration using EXPIRE or SET with EX option.

**Why**:
- Atomic operations ensure thread safety without distributed locks
- Automatic expiration prevents stale data
- Simple and efficient for fixed window algorithm
- Redis handles TTL automatically

**Alternatives considered**:
- Use Redis Lua scripts: More complex, but could combine INCR and EXPIRE in one atomic operation
- Use Redis sorted sets for sliding window: More complex, better for sliding window but overkill for fixed window
- Use in-memory counters: Not distributed, would require coordination

### Decision 2: Identify requests by IP address from X-Forwarded-For header
**What**: Extract the client IP address from the `X-Forwarded-For` header (or fall back to remote address) to use as the rate limit identifier.

**Why**:
- Standard practice for rate limiting behind proxies/load balancers
- Simple and doesn't require authentication
- Aligns with common rate limiting patterns

**Alternatives considered**:
- Use API keys: Requires authentication, more complex
- Use user ID: Requires authentication, more complex
- Use custom headers: Less standard, requires client cooperation

### Decision 3: Return HTTP 429 with rate limit headers on over-limit
**What**: When a request exceeds the rate limit, return HTTP 429 (Too Many Requests) with headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

**Why**:
- HTTP 429 is the standard status code for rate limiting
- Headers provide clients with visibility into their rate limit status
- Follows RFC 6585 and common API practices

**Alternatives considered**:
- Return HTTP 403: Less specific, typically for authorization
- Return HTTP 503: Implies service is down, not rate limited
- Return HTTP 200 with error body: Non-standard, confusing

### Decision 4: Use strategy pattern for future algorithm extensibility
**What**: Define a `RateLimiter` interface/protocol that can be implemented by different algorithms (fixed window, token bucket, etc.).

**Why**:
- Makes it easy to add new algorithms in the future
- Follows Open/Closed Principle
- Aligns with project's stated architecture pattern
- Allows swapping algorithms via configuration

**Alternatives considered**:
- Hardcode fixed window only: Simpler, but less flexible
- Use abstract base classes: More Pythonic, but protocols work well for duck typing

### Decision 5: Store rate limit state with key pattern `rate_limit:{ip}:{window_start}`
**What**: Use Redis key pattern `rate_limit:{ip}:{window_start}` where `window_start` is the timestamp of the window start.

**Why**:
- Clear key structure makes debugging easier
- Natural TTL expiration aligns with window duration
- Easy to query for specific IP and window

**Alternatives considered**:
- Use hash-based keys: More complex, less readable
- Use sorted sets: Overkill for fixed window

## Risks / Trade-offs

### Risk 1: Redis connection failure causes service degradation
**Impact**: If Redis is unavailable, rate limiting cannot function properly.

**Mitigation**:
- Fail open (allow requests) when Redis is unavailable to avoid breaking legitimate traffic
- Log failures for monitoring
- Return degraded status in health check

### Risk 2: Fixed window allows burst traffic at window boundaries
**Impact**: Clients could send 2x the limit by sending requests at the end of one window and start of the next.

**Mitigation**:
- Document this limitation clearly
- Consider sliding window algorithm as future enhancement
- This is an accepted trade-off for simplicity

### Risk 3: IP-based rate limiting can be bypassed
**Impact**: Sophisticated attackers can use multiple IPs or proxies.

**Mitigation**:
- Document this limitation
- Consider API key or user ID-based limiting as future enhancement
- Accept this as a basic protection mechanism

### Trade-off 1: Simplicity vs. Precision
Fixed window is simpler but less precise than sliding window. We choose simplicity for the initial implementation.

### Trade-off 2: Fail open vs. fail closed
We choose to fail open (allow requests) when Redis is unavailable to avoid breaking legitimate traffic, but this reduces protection during outages.

## Migration Plan
No migration needed as this is a new feature. The implementation will be additive.

## Open Questions
- Should we include a `Retry-After` header when returning 429?
- What should be the default rate limit configuration (limit count and window duration)?
- Should we log rate limit violations for monitoring?
