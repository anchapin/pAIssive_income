"""__init__ - Module for common_utils/custom_secrets/__init__.py.

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
    "delete_secret",
    "get_secret",
    "list_secrets",
    "set_secret",
]
