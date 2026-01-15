## 1. Domain Layer
- [x] 1.1 Create rate limit domain models (RateLimitResult, RateLimitStatus, TimeWindow)
- [x] 1.2 Create RateLimiter protocol/interface for algorithm extensibility
- [x] 1.3 Create FixedWindowRateLimiter domain class implementing the protocol
- [x] 1.4 Write unit tests for domain models

## 2. Infrastructure Layer
- [x] 2.1 Extend RedisClient with rate limit counter operations (INCR, GET, SET with EXPIRE)
- [x] 2.2 Implement Redis-based rate limit storage with key pattern `rate_limit:{ip}:{window_start}`
- [x] 2.3 Implement atomic counter increment with expiration
- [x] 2.4 Write integration tests for Redis rate limit storage

## 3. Application Layer
- [x] 3.1 Create rate limit use case (check and increment logic)
- [x] 3.2 Implement IP address extraction from X-Forwarded-For header
- [x] 3.3 Implement window start time calculation based on current time
- [x] 3.4 Implement rate limit decision logic (allow vs. reject)
- [x] 3.5 Handle Redis connection failures with fail-open behavior
- [x] 3.6 Write unit tests for rate limit use case

## 4. Interface Layer
- [x] 4.1 Create rate limit HTTP endpoint handler
- [x] 4.2 Implement rate limit response headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- [x] 4.3 Return HTTP 429 when limit is exceeded
- [x] 4.4 Return HTTP 200 when request is allowed
- [x] 4.5 Wire up rate limit use case to endpoint
- [x] 4.6 Write integration tests for HTTP endpoint

## 5. Configuration
- [x] 5.1 Add rate limit configuration to Config class (limit count, window duration, window unit)
- [x] 5.2 Add environment variable support for rate limit configuration
- [x] 5.3 Set sensible default values (e.g., 100 requests per minute)

## 6. Documentation
- [x] 6.1 Update README with rate limiting documentation
- [x] 6.2 Document rate limit endpoint usage and response format
- [x] 6.3 Document rate limit headers and their meanings
- [x] 6.4 Add example curl commands for testing rate limiting

## 7. Validation
- [x] 7.1 Run ruff linting and fix any issues
- [x] 7.2 Run ruff-format and ensure code is formatted
- [x] 7.3 Run pytest with coverage and ensure target coverage is met
- [x] 7.4 Manually test the rate limit endpoint with various scenarios
- [x] 7.5 Test rate limiting behavior across multiple IP addresses
- [x] 7.6 Test rate limiting behavior at window boundaries
