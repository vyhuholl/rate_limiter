# health-check Specification

## Purpose
TBD - created by archiving change add-health-check-endpoint. Update Purpose after archive.
## Requirements
### Requirement: Health Check Endpoint
The system SHALL provide an HTTP endpoint at `/health` that returns the service health status including Redis Cluster connectivity verification.

#### Scenario: Successful health check when Redis is available
- **WHEN** a GET request is made to `/health` and Redis Cluster is responsive
- **THEN** the response SHALL have HTTP status code 200
- **AND** the response body SHALL contain JSON with `status` field set to `"healthy"`
- **AND** the response body SHALL contain a `checks` object with `redis` check result showing `"status": "ok"`

#### Scenario: Health check returns degraded status when Redis is slow
- **WHEN** a GET request is made to `/health` and Redis Cluster responds within timeout threshold but slowly
- **THEN** the response SHALL have HTTP status code 200
- **AND** the response body SHALL contain JSON with `status` field set to `"degraded"`
- **AND** the response body SHALL contain a `checks` object with `redis` check result including response time details

#### Scenario: Health check returns unhealthy status when Redis is unavailable
- **WHEN** a GET request is made to `/health` and Redis Cluster is unreachable
- **THEN** the response SHALL have HTTP status code 503
- **AND** the response body SHALL contain JSON with `status` field set to `"unhealthy"`
- **AND** the response body SHALL contain a `checks` object with `redis` check result showing `"status": "error"` and an error message

#### Scenario: Health check returns unhealthy status when Redis connection times out
- **WHEN** a GET request is made to `/health` and Redis Cluster connection times out
- **THEN** the response SHALL have HTTP status code 503
- **AND** the response body SHALL contain JSON with `status` field set to `"unhealthy"`
- **AND** the response body SHALL contain a `checks` object with `redis` check result showing `"status": "error"` and timeout message

### Requirement: Redis Connectivity Verification
The system SHALL verify Redis Cluster connectivity by executing a PING command against the Redis cluster.

#### Scenario: Successful PING command
- **WHEN** the health check executes a PING command against Redis Cluster
- **THEN** the Redis client SHALL receive a PONG response
- **AND** the check result SHALL be marked as successful

#### Scenario: PING command fails
- **WHEN** the health check executes a PING command and Redis returns an error
- **THEN** the check result SHALL be marked as failed
- **AND** the error message SHALL be included in the check result

### Requirement: Health Check Response Format
The health check endpoint SHALL return a JSON response with a standardized format.

#### Scenario: Response format for healthy status
- **WHEN** the service is healthy
- **THEN** the response SHALL be JSON with the following structure:
  ```json
  {
    "status": "healthy",
    "checks": {
      "redis": {
        "status": "ok"
      }
    }
  }
  ```

#### Scenario: Response format for degraded status
- **WHEN** the service is degraded
- **THEN** the response SHALL be JSON with the following structure:
  ```json
  {
    "status": "degraded",
    "checks": {
      "redis": {
        "status": "ok",
        "message": "optional details"
      }
    }
  }
  ```

#### Scenario: Response format for unhealthy status
- **WHEN** the service is unhealthy
- **THEN** the response SHALL be JSON with the following structure:
  ```json
  {
    "status": "unhealthy",
    "checks": {
      "redis": {
        "status": "error",
        "message": "error details"
      }
    }
  }
  ```

