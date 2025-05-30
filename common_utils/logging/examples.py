"""
Example usage patterns for secure logging.

This module contains example code demonstrating how to use secure logging features.
All sensitive values are examples/placeholders and are never used in production.
"""

import logging
import os

from common_utils.logging.secure_logging import get_secure_logger, mask_sensitive_data

logger = get_secure_logger(__name__)


def example_secure_logging() -> None:
    """Demonstrate secure logging with demo values only."""
    # Note: These are placeholders for demonstration/docs only
    demo_token = "DEMO_TOKEN_PLACEHOLDER"  # nosec B105
    demo_auth = "DEMO_AUTH_PLACEHOLDER"  # nosec B105
    os.environ["DEMO_TOKEN"] = demo_token
    os.environ["DEMO_AUTH"] = demo_auth

    # Using placeholder values for demonstration only - get from env vars in production
    demo_access_token = os.environ.get("DEMO_TOKEN", "demo_only")  # For testing only
    demo_auth_material = os.environ.get("DEMO_AUTH", "demo_only")  # For testing only

    logger.info(
        "Processing request",
        extra={"token": demo_access_token, "auth": demo_auth_material},
    )

    # Clean up demo environment variables
    for key in ("DEMO_TOKEN", "DEMO_AUTH"):
        os.environ.pop(key, None)


def example_mask_sensitive_data() -> None:
    """Demonstrate direct usage of the mask_sensitive_data function."""
    sensitive_data = {
        "username": "demo_user",
        "auth_token": "secret_token_123",  # nosec B105
        "request": {
            "auth_material": "sensitive_auth_data",  # nosec B105
            "metadata": {"public": "ok", "private": "secret"},  # nosec B105
        },
    }

    masked_data = mask_sensitive_data(sensitive_data)
    logger.info("Masked data example: %s", masked_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Example of using secure logger:")
    example_secure_logging()

    logger.info("Example of using mask_sensitive_data function:")
    example_mask_sensitive_data()
