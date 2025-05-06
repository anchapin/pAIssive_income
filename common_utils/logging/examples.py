"""Examples of how to use the secure logging utilities.

This module provides examples of how to use the secure logging utilities
to prevent sensitive information from being logged in clear text.
"""

import logging

from .secure_logging import get_secure_logger, mask_sensitive_data

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def example_secure_logger():
    """Demonstrate the secure logger usage."""
    # Get a secure logger
    logger = get_secure_logger("example")

    # Log messages with sensitive information
    api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
    password = "super_secret_password123"

    # These will be automatically masked
    logger.info(f"Using API key: {api_key}")
    logger.info(f"User password: {password}")

    # You can also log dictionaries with sensitive information
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": password,
        "api_keys": {
            "openai": api_key,
            "github": "ghp_abcdefghijklmnopqrstuvwxyz1234567890",
        },
    }

    logger.info(f"User data: {user_data}")


def example_mask_sensitive_data():
    """Demonstrate direct usage of the mask_sensitive_data function."""
    # Standard logger
    logger = logging.getLogger("standard_logger")

    # Sensitive data
    api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"

    # Manually mask sensitive data
    masked_message = mask_sensitive_data(f"Using API key: {api_key}")
    logger.info(masked_message)

    # Mask sensitive data in a dictionary
    config = {"api_key": api_key, "endpoint": "https://api.example.com", "timeout": 30}

    masked_config = mask_sensitive_data(config)
    logger.info(f"Configuration: {masked_config}")


if __name__ == "__main__":
    print("Example of using secure logger:")
    example_secure_logger()

    print("\nExample of using mask_sensitive_data function:")
    example_mask_sensitive_data()
