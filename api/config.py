"""config - Module for api.config."""

# Standard library imports
import os

# Third-party imports

# Local imports


def get_database_url() -> str:
    """Get database URL from environment or return default."""
    return os.getenv("DATABASE_URL", "sqlite:///default.db")


def get_redis_url() -> str:
    """Get Redis URL from environment or return default."""
    return os.getenv("REDIS_URL", "redis://localhost:6379")
