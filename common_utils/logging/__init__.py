"""
Common utilities for secure logging and log management.

import logging
from typing import cast

# Third-party imports
# Local imports
from .secure_logging import (
    SENSITIVE_FIELDS,
    SecureLogger,
    get_secure_logger,
    mask_sensitive_data,
)

__all__ = [
    "SENSITIVE_FIELDS",
    "SecureLogger",
    "get_logger",
    "get_secure_logger",
    "mask_sensitive_data",
]


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    This is a convenience function that returns a secure logger by default,
    which automatically masks sensitive information.

    Args:
    ----
        name: Name of the logger

    Returns:
    -------
        logging.Logger: The secure logger or a standard logger as fallback

    """
    try:
        # Return a SecureLogger that masks sensitive information
        logger = get_secure_logger(name)
        # Cast to logging.Logger to satisfy type checking
        return cast("logging.Logger", logger)
    except (ImportError, AttributeError) as e:
        # Fall back to standard logger if secure logger is not available
        setup_logger = logging.getLogger("logging_setup")
        setup_logger.warning(
            "Failed to create secure logger, falling back to standard logger: %s",
            str(e),
        )

        # Add console handler
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.addHandler(console)

        # Set default level
        self.setLevel(logging.INFO)

    def error(self, msg: str, *args, **kwargs):
        """Log error message with secure formatting.
        
        Args:
            msg: Error message
            args: Additional positional args
            kwargs: Additional keyword args
        """
        # Add security context if available
        if kwargs.get('secure_context'):
            msg = f"[SECURE] {msg}"
        super().error(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message with secure formatting.
        
        Args:
            msg: Warning message
            args: Additional positional args
            kwargs: Additional keyword args
        """
        if kwargs.get('secure_context'):
            msg = f"[SECURE] {msg}"
        super().warning(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message with secure formatting.
        
        Args:
            msg: Info message
            args: Additional positional args 
            kwargs: Additional keyword args
        """
        if kwargs.get('secure_context'):
            msg = f"[SECURE] {msg}"
        super().info(msg, *args, **kwargs)

# Logger cache to avoid creating duplicate loggers
_logger_cache: Dict[str, Union[SecureLogger, Logger]] = {}

def get_logger(name: str, secure: bool = True) -> Union[SecureLogger, Logger]:
    """Get a logger instance.
    
    Args:
        name: Logger name
        secure: Whether to return a secure logger (default True)
        
    Returns:
        Logger instance (SecureLogger if secure=True)
    """
    if name in _logger_cache:
        return _logger_cache[name]

    if secure:
        logger = SecureLogger(name)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

    _logger_cache[name] = logger
    return logger

# Create global secure logger instance
secure_logger = get_logger("secure_logger")
