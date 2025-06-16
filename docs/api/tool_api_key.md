# Tool API Key Configuration

## Overview

The pAIssive_income project uses API keys to secure access to tool endpoints. This document explains how the `TOOL_API_KEY` environment variable is used in both development and CI environments.

## Configuration

### Environment Variable

The `TOOL_API_KEY` environment variable is used to authenticate requests to the FastAPI math tool endpoints. This key is required for all API requests to tool endpoints.

### Development Environment

For local development, a default dummy key is provided in the `tests/api/conftest.py` file:

```python
# For local/dev convenience only: set TOOL_API_KEY if not already set.
# CI should explicitly set TOOL_API_KEY for security.
os.environ.setdefault("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")
```

This default key is only meant for local development and testing. It should never be used in production.

### CI Environment

In CI environments, the `TOOL_API_KEY` should be explicitly set as an environment variable in the CI configuration. This ensures that tests run with a consistent API key across all environments.

### Usage in Tests

The API key is used in test files like `tests/api/test_tool_router.py` to authenticate requests to the tool endpoints:

```python
# Use TOOL_API_KEY from environment for consistency and security.
TOOL_API_KEY = os.getenv("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")
HEADERS = {"x-api-key": TOOL_API_KEY}
```

## Security Considerations

- Never commit real API keys to the repository
- Use environment variables to store sensitive information
- In production, use a secure key management system to manage API keys
- Rotate API keys regularly to maintain security