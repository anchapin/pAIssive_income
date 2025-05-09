"""Examples of how to use the secure logging utilities.

This module provides examples of how to use the secure logging utilities
to prevent sensitive information from being logged in clear text.
"""

import logging

from .secure_logging import get_secure_logger
from .secure_logging import mask_sensitive_data

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def example_secure_logger():
    """Demonstrate the secure logger usage."""
    # Get a secure logger
    logger = get_secure_logger("example")

    # Log messages with sensitive information
    demo_access_token = "EXAMPLE_ACCESS_TOKEN_NOT_REAL_VALUE"
    demo_auth_material = "EXAMPLE_PLACEHOLDER_NOT_A_REAL_VALUE"

    # These will be automatically masked
    logger.info(f"Using access token: {demo_access_token}")
    logger.info(f"Authentication material: {demo_auth_material}")

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

    logger.info(f"User data: {user_data}")


def example_mask_sensitive_data():
    """Demonstrate direct usage of the mask_sensitive_data function."""
    # Standard logger
    logger = logging.getLogger("standard_logger")

    # Sensitive data - not using actual patterns
    demo_access_token = "EXAMPLE_ACCESS_TOKEN_FOR_DEMONSTRATION_ONLY"

    # Manually mask sensitive data
    masked_message = mask_sensitive_data(f"Using access token: {demo_access_token}")
    logger.info(masked_message)

    # Mask sensitive data in a dictionary
    config = {
        "access_token": demo_access_token,
        "endpoint": "https://api.example.com",
        "timeout": 30,
    }

    masked_config = mask_sensitive_data(config)
    logger.info(f"Configuration: {masked_config}")


if __name__ == "__main__":
    print("Example of using secure logger:")
    example_secure_logger()

    print("\nExample of using mask_sensitive_data function:")
    example_mask_sensitive_data()
