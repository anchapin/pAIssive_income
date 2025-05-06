"""__init__ - Module for common_utils/secrets.__init__.

This package provides utilities for managing secrets across different backends.
"""

# Standard library imports

# Third-party imports

# Local imports
from .secrets_manager import (
    SecretsBackend,
    SecretsManager,
    delete_secret,
    get_secret,
    list_secrets,
    set_secret,
)

__all__ = [
    "SecretsBackend",
    "SecretsManager",
    "get_secret",
    "set_secret",
    "delete_secret",
    "list_secrets",
]
