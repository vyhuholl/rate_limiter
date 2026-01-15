## 1. Project Setup
- [x] 1.1 Create project directory structure following Clean Architecture (src/domain, src/application, src/infrastructure, src/interface)
- [x] 1.2 Initialize uv project with Python 3.12+ requirement
- [x] 1.3 Add dependencies: aiohttp, redis, pytest, pytest-asyncio, pytest-cov, ruff
- [x] 1.4 Configure ruff and ruff-format with line length 79
- [x] 1.5 Create pyproject.toml with project metadata and tool configurations

## 2. Domain Layer
- [x] 2.1 Create health check domain models (HealthStatus, CheckResult)
- [x] 2.2 Write unit tests for domain models

## 3. Infrastructure Layer
- [x] 3.1 Create Redis client wrapper with redis
- [x] 3.2 Implement Redis connectivity check (PING command)
- [x] 3.3 Write integration tests for Redis client

## 4. Application Layer
- [x] 4.1 Create health check use case
- [x] 4.2 Implement health check logic (check Redis, aggregate results)
- [x] 4.3 Write unit tests for health check use case

## 5. Interface Layer
- [x] 5.1 Create aiohttp application setup
- [x] 5.2 Implement /health endpoint handler
- [x] 5.3 Wire up health check use case to endpoint
- [x] 5.4 Write integration tests for HTTP endpoint

## 6. Configuration and Entry Point
- [x] 6.1 Create configuration module for Redis connection settings
- [x] 6.2 Create main entry point to start the HTTP server
- [x] 6.3 Add environment variable support for configuration

## 7. Documentation
- [x] 7.1 Update README with health check endpoint documentation
- [x] 7.2 Add example curl commands for testing

## 8. Validation
- [x] 8.1 Run ruff linting and fix any issues
- [x] 8.2 Run ruff-format and ensure code is formatted
- [x] 8.3 Run pytest with coverage and ensure target coverage is met
- [x] 8.4 Manually test the health check endpoint
