"""Logging utilities module."""

import logging
from logging import Logger
from typing import Dict, Union

class SecureLogger(Logger):
    """Secure logger with enhanced security features."""

    def __init__(self, name: str):
        """Initialize secure logger.
        
        Args:
            name: Logger name
        """
        super().__init__(name)
        self._configure()

    def _configure(self):
        """Configure logger with security settings."""
        # Set secure logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
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
