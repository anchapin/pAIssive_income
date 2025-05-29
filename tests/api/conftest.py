"""conftest - Module for tests/api.conftest."""

# Ensure TOOL_API_KEY is set for FastAPI math tool endpoints under test.
# For security, do not commit realistic or production-like secrets here.
# CI and local devs should set TOOL_API_KEY in their environment if possible.
# This fallback is for local/dev convenience only.
import os

# For local/dev convenience only: set TOOL_API_KEY if not already set.
# CI should explicitly set TOOL_API_KEY for security.
os.environ.setdefault("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")

# Standard library imports

# Third-party imports

# Local imports
