"""
"""
Logging module for pAIssive_income application.
Logging module for pAIssive_income application.


This module provides structured logging functionality for the entire application,
This module provides structured logging functionality for the entire application,
enabling consistent log formats, contextual information, and integration with
enabling consistent log formats, contextual information, and integration with
monitoring systems.
monitoring systems.
"""
"""


from common_utils.logging.logger import (LogLevel, add_context, clear_context,
from common_utils.logging.logger import (LogLevel, add_context, clear_context,
get_logger, setup_logging)
get_logger, setup_logging)


__all__ = [
__all__ = [
"get_logger",
"get_logger",
"setup_logging",
"setup_logging",
"LogLevel",
"LogLevel",
"add_context",
"add_context",
"clear_context",
"clear_context",
]
]

