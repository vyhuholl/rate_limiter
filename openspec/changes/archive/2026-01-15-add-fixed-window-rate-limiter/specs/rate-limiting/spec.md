## ADDED Requirements

### Requirement: Fixed Window Rate Limiting Algorithm
The system SHALL implement a fixed window rate limiting algorithm that tracks request counts per time window and rejects requests that exceed the configured limit.

#### Scenario: Request within limit is allowed
- **WHEN** a request is made and the request count for the current window is below the limit
- **THEN** the request SHALL be allowed
- **AND** the request count SHALL be incremented
- **AND** the response SHALL include rate limit headers

#### Scenario: Request at limit is allowed
- **WHEN** a request is made and the request count for the current window equals the limit
- **THEN** the request SHALL be allowed
- **AND** the request count SHALL be incremented to limit + 1
- **AND** the response SHALL include rate limit headers

#### Scenario: Request exceeding limit is rejected
- **WHEN** a request is made and the request count for the current window exceeds the limit
- **THEN** the request SHALL be rejected
- **AND** the response SHALL have HTTP status code 429
- **AND** the response SHALL include rate limit headers

#### Scenario: New window resets counter
- **WHEN** a new time window starts
- **THEN** the request counter SHALL reset to zero
- **AND** subsequent requests SHALL be counted against the new window

### Requirement: IP Address Based Rate Limiting
The system SHALL identify requests for rate limiting by extracting the client IP address from the X-Forwarded-For header, falling back to the remote address if the header is not present.

#### Scenario: Rate limiting uses X-Forwarded-For header
- **WHEN** a request includes the X-Forwarded-For header
- **THEN** the first IP address in the header SHALL be used as the rate limit identifier

#### Scenario: Rate limiting uses remote address when header missing
- **WHEN** a request does not include the X-Forwarded-For header
- **THEN** the remote address SHALL be used as the rate limit identifier

#### Scenario: Different IPs have independent rate limits
- **WHEN** requests come from different IP addresses
- **THEN** each IP SHALL have an independent rate limit counter

### Requirement: Rate Limit HTTP Endpoint
The system SHALL provide an HTTP endpoint that checks and increments the rate limit for a request.

#### Scenario: Endpoint accepts request with IP identification
- **WHEN** a request is made to the rate limit endpoint
- **THEN** the system SHALL identify the request by IP address
- **AND** the system SHALL check the current request count for that IP
- **AND** the system SHALL increment the request count

#### Scenario: Endpoint returns 200 for allowed requests
- **WHEN** a request is within the rate limit
- **THEN** the endpoint SHALL return HTTP status code 200
- **AND** the response SHALL include rate limit headers

#### Scenario: Endpoint returns 429 for rejected requests
- **WHEN** a request exceeds the rate limit
- **THEN** the endpoint SHALL return HTTP status code 429
- **AND** the response SHALL include rate limit headers

### Requirement: Rate Limit Response Headers
The system SHALL include rate limit information in HTTP response headers for all rate limit checks.

#### Scenario: Headers include limit, remaining, and reset
- **WHEN** a rate limit check is performed
- **THEN** the response SHALL include X-RateLimit-Limit header with the configured limit
- **AND** the response SHALL include X-RateLimit-Remaining header with the remaining requests
- **AND** the response SHALL include X-RateLimit-Reset header with the window end timestamp

#### Scenario: Remaining header shows available requests
- **WHEN** the request count is 3 and the limit is 10
- **THEN** the X-RateLimit-Remaining header SHALL be 7

#### Scenario: Remaining header is zero when limit reached
- **WHEN** the request count equals the limit
- **THEN** the X-RateLimit-Remaining header SHALL be 0

#### Scenario: Remaining header is negative when limit exceeded
- **WHEN** the request count exceeds the limit
- **THEN** the X-RateLimit-Remaining header SHALL be negative

### Requirement: Configurable Time Windows
The system SHALL support configurable time window durations including seconds, minutes, and hours.

#### Scenario: Window duration is in seconds
- **WHEN** the window duration is configured as 60 seconds
- **THEN** the rate limit counter SHALL reset every 60 seconds

#### Scenario: Window duration is in minutes
- **WHEN** the window duration is configured as 5 minutes
- **THEN** the rate limit counter SHALL reset every 5 minutes

#### Scenario: Window duration is in hours
- **WHEN** the window duration is configured as 1 hour
- **THEN** the rate limit counter SHALL reset every hour

### Requirement: Global Rate Limit Configuration
The system SHALL use a global rate limit configuration that applies to all IP addresses.

#### Scenario: All IPs share same limit
- **WHEN** the global limit is configured as 100 requests per window
- **THEN** all IP addresses SHALL be limited to 100 requests per window

#### Scenario: Limit is configurable
- **WHEN** the limit configuration is changed
- **THEN** the new limit SHALL apply to new time windows

### Requirement: Redis Storage for Rate Limit State
The system SHALL use Redis to store rate limit counters for distributed consistency.

#### Scenario: Counter is stored in Redis
- **WHEN** a request is rate limited
- **THEN** the request counter SHALL be stored in Redis
- **AND** the counter SHALL be keyed by IP address and window start time

#### Scenario: Counter expires with window
- **WHEN** a time window expires
- **THEN** the corresponding Redis key SHALL expire automatically

#### Scenario: Counter increment is atomic
- **WHEN** multiple requests increment the same counter concurrently
- **THEN** the increment operation SHALL be atomic
- **AND** the final count SHALL be accurate

### Requirement: Redis Connection Failure Handling
The system SHALL handle Redis connection failures gracefully by failing open to allow requests.

#### Scenario: Redis unavailable allows requests
- **WHEN** Redis is unreachable during a rate limit check
- **THEN** the request SHALL be allowed
- **AND** the error SHALL be logged

#### Scenario: Redis timeout allows requests
- **WHEN** Redis connection times out during a rate limit check
- **THEN** the request SHALL be allowed
- **AND** the error SHALL be logged

#### Scenario: Redis error returns degraded headers
- **WHEN** Redis returns an error during a rate limit check
- **THEN** the request SHALL be allowed
- **AND** the response SHALL indicate degraded rate limiting status
