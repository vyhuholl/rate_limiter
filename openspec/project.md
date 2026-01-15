# Project Context

## Purpose
A distributed rate limiter for API endpoints using Redis. The service provides configurable rate limiting strategies to protect APIs from abuse, ensure fair resource allocation, and maintain system stability under high load.

## Tech Stack
- Python 3.12+ with asyncio for asynchronous programming
- redis-py with asyncio for Redis client connectivity
- uv for virtual environment management and running code
- ruff for linting
- ruff-format for code formatting (line length: 79)
- pytest with pytest-asyncio for testing
- pytest-cov for code coverage reporting

## Project Conventions

### Code Style
- Use ruff for linting and ruff-format for formatting
- Line length: 79 characters
- Follow PEP 8 style guide with ruff-specific rules
- Use type hints for function signatures and complex types
- Async functions should be explicitly marked with `async def`
- Use dependency injection for managing dependencies
- Prefer composition over inheritance

### Architecture Patterns
- Clean Architecture with clear separation of concerns
- Layers: Domain (business logic), Application (use cases), Infrastructure (external services), Interface (API/CLI)
- Dependency injection for decoupling components
- Async/await pattern for I/O operations
- Strategy pattern for supporting multiple rate limiting algorithms

### Testing Strategy
- pytest with pytest-asyncio for async test support
- pytest-cov for coverage reporting
- Unit tests for individual components and business logic
- Integration tests for Redis interactions
- Mock external dependencies where appropriate
- Aim for high code coverage on core business logic

### Git Workflow
- Git Flow with feature branches
- Main branches: `main` (production), `develop` (integration)
- Feature branches: `feature/` prefix (e.g., `feature/add-token-bucket`)
- Release branches: `release/` prefix
- Hotfix branches: `hotfix/` prefix
- Pull requests required for merging to `develop` or `main`
- Commit messages should be clear and descriptive

## Domain Context
Rate limiting is a technique used to control the rate of incoming requests to an API. Common use cases include:
- Preventing API abuse and DDoS attacks
- Ensuring fair resource allocation among users
- Managing backend load and preventing service degradation
- Implementing usage-based pricing tiers

The service will support multiple rate limiting strategies (algorithms TBD) to accommodate different use cases and performance requirements.

## Important Constraints
No specific constraints defined yet. Constraints will be added as the project evolves and requirements are clarified.

## External Dependencies
- Redis Cluster for distributed state storage (required)
- Prometheus metrics endpoint for monitoring (required)
- Optional logging service integration (TBD)
