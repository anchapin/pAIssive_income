"""Utility functions for secure logging."""

import logging
from typing import Any, List, Optional, Union

from common_utils.logging.secure_logging import (
    SecureLogger,
    get_secure_logger,
    prevent_log_injection,
)


def get_logger(name: str) -> SecureLogger:
    """Get a secure logger with the specified name.

    This is a convenience function that should be used throughout the codebase
    to get a logger that automatically masks sensitive information and prevents
    log injection attacks.

    Args:
        name: Name of the logger

    Returns:
        SecureLogger: A secure logger instance
    """
    return get_secure_logger(name)


def sanitize_user_input(value: Any) -> Any:
    """Sanitize user input for logging to prevent log injection.

    This function should be used whenever logging user input to prevent
    log injection attacks. It replaces newline characters with spaces and removes
    other potentially harmful characters in addition to using `prevent_log_injection`.

    Args:
        value: The value to sanitize

    Returns:
        Any: The sanitized value
    """
    if isinstance(value, str):
        # Replace newline characters with spaces
        value = value.replace('\n', ' ').replace('\r', ' ')
        # Remove other control characters
        value = ''.join(ch for ch in value if ch.isprintable())
        # Escape percent signs to prevent format string issues
        value = value.replace('%', '%%')
        # Escape other potentially harmful characters
        value = value.replace('[', '\\[').replace(']', '\\]')
        value = value.replace('{', '\\{').replace('}', '\\}')
        # Remove any remaining non-printable characters
        value = ''.join(ch for ch in value if ord(ch) >= 32)
    return prevent_log_injection(value)


def log_user_input_safely(
    logger: Union[SecureLogger, logging.Logger],
    level: int,
    message: str,
    user_input: Any,
    *args: Any,
    **kwargs: Any
) -> None:
    """Log a message with user input safely.

    This function should be used whenever logging a message that includes
    user input to prevent log injection attacks.

    Args:
        logger: The logger to use
        level: The logging level
        message: The message to log
        user_input: The user input to include in the log
        *args: Additional arguments to pass to the logger
        **kwargs: Additional keyword arguments to pass to the logger
    """
    # Sanitize the user input
    sanitized_input = sanitize_user_input(user_input)

    # Handle the message based on whether it contains format specifiers
    if "%s" in message:
        # Use existing format specifiers with sanitized input
        # Pass sanitized input as a parameter to the logger to prevent log injection
        logger.log(level, message, sanitized_input, *args, **kwargs)
    else:
        # Use a format string with placeholders to ensure proper formatting
        # This ensures that the message and input are properly separated
        logger.log(level, "%s %s", message, sanitized_input, *args, **kwargs)


def log_exception_safely(
    logger: Union[SecureLogger, logging.Logger],
    message: str,
    *args: Any,
    **kwargs: Any
) -> None:
    """Log an exception safely.

    This function should be used whenever logging an exception to prevent
    sensitive information from being exposed.

    Args:
        logger: The logger to use
        message: The message to log
        *args: Additional arguments to pass to the logger
        **kwargs: Additional keyword arguments to pass to the logger
    """
    # Log the exception
    logger.exception(message, *args, **kwargs)


def configure_secure_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    handlers: Optional[List[logging.Handler]] = None
) -> None:
    """Configure secure logging for the entire application.

    This function should be called at application startup to configure
    secure logging for all loggers.

    Args:
        level: The logging level to set
        format_string: The format string to use for log messages
        handlers: A list of handlers to add to the root logger
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Set the logging level
    root_logger.setLevel(level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the specified handlers or create a default one
    if handlers:
        for handler in handlers:
            root_logger.addHandler(handler)
    else:
        handler = logging.StreamHandler()

        # Set the format
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)


def log_user_id_safely(
    logger: Union[SecureLogger, logging.Logger],
    level: int,
    message: str,
    user_id: Any,
    *args: Any,
    **kwargs: Any
) -> None:
    """Log a message with a user ID safely.

    This function should be used whenever logging a message that includes
    a user ID to prevent log injection attacks.

    Args:
        logger: The logger to use
        level: The logging level
        message: The message to log
        user_id: The user ID to include in the log
        *args: Additional arguments to pass to the logger
        **kwargs: Additional keyword arguments to pass to the logger
    """
    # Sanitize the user ID
    sanitized_id = sanitize_user_input(user_id)

    # Handle the message based on whether it contains format specifiers
    if "%s" in message:
        # Use existing format specifiers with sanitized ID
        # Pass sanitized ID as a parameter to the logger to prevent log injection
        logger.log(level, message, sanitized_id, *args, **kwargs)
    else:
        # Use a format string with placeholders to ensure proper formatting
        # This ensures that the message and ID are properly separated
        logger.log(level, "%s %s", message, sanitized_id, *args, **kwargs)


# Example usage:
#
# from common_utils.logging.log_utils import get_logger, log_user_input_safely
#
# logger = get_logger(__name__)
#
# # Instead of:
# # logger.info(f"User {user_id} logged in")
#
# # Use:
# log_user_id_safely(logger, logging.INFO, "User %s logged in", user_id)
#
# # Or:
# logger.info("User logged in")
# log_user_id_safely(logger, logging.INFO, "User ID: %s", user_id)
