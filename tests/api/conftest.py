"""conftest - Module for tests/api.conftest."""

# Set TOOL_API_KEY for FastAPI math tool endpoints.
# This ensures tests pass both locally and in CI by providing the required API key.
import os
os.environ["TOOL_API_KEY"] = "supersecretkey"

# Standard library imports

# Third-party imports

# Local imports
