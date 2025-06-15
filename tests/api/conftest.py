"""conftest - Module for tests/api.conftest."""

# Ensure TOOL_API_KEY is set for FastAPI math tool endpoints under test.
# For security, do not commit realistic or production-like secrets here.
# CI and local devs should set TOOL_API_KEY in their environment if possible.
# This fallback is for local/dev convenience only.
import os

# For local/dev convenience only: set TOOL_API_KEY if not already set.
# CI should explicitly set TOOL_API_KEY for security.
os.environ.setdefault("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")

# Set DATABASE_URL for test environment
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

# Set other required environment variables for testing
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-development-only")
os.environ.setdefault("ENVIRONMENT", "test")

# Standard library imports

# Third-party imports

# Local imports
