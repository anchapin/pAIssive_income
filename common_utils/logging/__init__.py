"""
Logging module for pAIssive_income application.

This module provides structured logging functionality for the entire application,
enabling consistent log formats, contextual information, and integration with
monitoring systems.
"""

from common_utils.logging.logger import (
    get_logger,
    setup_logging,
    LogLevel,
    add_context,
    clear_context,
)

__all__ = [
    "get_logger",
    "setup_logging",
    "LogLevel",
    "add_context",
    "clear_context",
]