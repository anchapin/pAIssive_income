"""
Examples of how to use the secure logging utilities.

This module provides examples of how to use the secure logging utilities
to prevent sensitive information from being logged in clear text.
"""

import logging
import sys

# Configure logging at module level for testing
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

try:
    from common_utils.logging.secure_logging import (
        get_secure_logger,
        mask_sensitive_data,
    )
except ImportError as e:
    logger.exception("common_utils.logging.secure_logging module not found.", exc_info=e)
    sys.exit(1)

# Note: Use get_secure_logger("examples") when needed


def example_secure_logger() -> None:
    """Demonstrate the secure logger usage."""
    # Get a secure logger
    logger = get_secure_logger("example")

    # Log messages with sensitive information
    # Using placeholder values for demonstration only
    demo_access_token = "DEMO_TOKEN_PLACEHOLDER"
    demo_auth_material = "DEMO_AUTH_PLACEHOLDER"

    # These will be automatically masked
    logger.info("Using access token: %s", demo_access_token)
    logger.info("Authentication material: %s", demo_auth_material)

    # You can also log dictionaries with sensitive information
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "auth_material": demo_auth_material,
        "secure_data": {
            "service_1": demo_access_token,
            "service_2": "EXAMPLE_AUTH_PLACEHOLDER_NOT_REAL",
        },
    }

    logger.info("User data: %s", user_data)


def example_mask_sensitive_data() -> None:
    """Demonstrate direct usage of the mask_sensitive_data function."""
    # Standard logger
    logger = logging.getLogger("standard_logger")  # Use the logger expected by the test

    # Sensitive data - using placeholder for demonstration
    demo_access_token = "DEMO_TOKEN_PLACEHOLDER"

    # Manually mask sensitive data
    masked_message = mask_sensitive_data(f"Using access token: {demo_access_token}")
    logger.info("%s", masked_message)

    # Mask sensitive data in a dictionary
    config = {
        "access_token": demo_access_token,
        "endpoint": "https://api.example.com",
        "timeout": 30,
    }

    masked_config = mask_sensitive_data(config)
    logger.info("Configuration: %s", masked_config)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info("Example of using secure logger:")
    example_secure_logger()

    logger.info("\nExample of using mask_sensitive_data function:")
    example_mask_sensitive_data()
