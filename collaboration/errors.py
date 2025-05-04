"""
Error handling for the collaboration module.

This module defines custom exception classes and error handling utilities
for the collaboration module.
"""


import logging
import traceback
from typing import Any, Callable, Dict, Optional

# Set up logging
logger = logging.getLogger(__name__)


class CollaborationError(Exception):
    """Base exception class for all collaboration module errors."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
    """
    Initialize a collaboration error.

    Args:
    message: Error message
    original_exception: Optional original exception that caused this error
    """
    super().__init__(message)
    self.message = message
    self.original_exception = original_exception


    class WorkspaceError(CollaborationError):
    """Exception raised for errors related to workspace operations."""

    pass


    class PermissionError(CollaborationError):

    pass


    class SharingError(CollaborationError):

    pass


    class VersionControlError(CollaborationError):

    pass


    class CommentError(CollaborationError):
    """Exception raised for errors related to comments and reactions."""

    pass


    class IntegrationError(CollaborationError):

    pass


    class ActivityError(CollaborationError):

    pass


    class NotificationError(CollaborationError):

    pass


    def handle_exception(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in collaboration module functions.

    This decorator catches exceptions, logs them, and re-raises them as
    appropriate collaboration module exceptions.

    Args:
    func: Function to decorate

    Returns:
    Decorated function
    """

    def wrapper(*args, **kwargs):
    try:
    return func(*args, **kwargs)
except CollaborationError:
    # Re-raise collaboration module exceptions
    raise
except Exception as e:
    # Log the exception
    logger.error(f"Error in {func.__name__}: {str(e)}")
    logger.debug(traceback.format_exc())

    # Determine the appropriate exception type based on the function name
    if "workspace" in func.__name__.lower():
    raise WorkspaceError(f"Workspace operation failed: {str(e)}", e)
    elif (
    "permission" in func.__name__.lower() or "role" in func.__name__.lower()
    ):
    raise PermissionError(f"Permission operation failed: {str(e)}", e)
    elif "shar" in func.__name__.lower():
    raise SharingError(f"Sharing operation failed: {str(e)}", e)
    elif "version" in func.__name__.lower():
    raise VersionControlError(
    f"Version control operation failed: {str(e)}", e
    )
    elif (
    "comment" in func.__name__.lower()
    or "reaction" in func.__name__.lower()
    ):
    raise CommentError(f"Comment operation failed: {str(e)}", e)
    elif "integrat" in func.__name__.lower():
    raise IntegrationError(f"Integration operation failed: {str(e)}", e)
    elif "activity" in func.__name__.lower():
    raise ActivityError(f"Activity tracking operation failed: {str(e)}", e)
    elif "noti" in func.__name__.lower():
    raise NotificationError(f"Notification operation failed: {str(e)}", e)
    else:
    raise CollaborationError(f"Operation failed: {str(e)}", e)

    return wrapper


    def format_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception as a dictionary.

    Args:
    error: Exception to format

    Returns:
    Dictionary with error information
    """
    result = {"error": error.__class__.__name__, "message": str(error)}

    if isinstance(error, CollaborationError) and error.original_exception:
    result["original_error"] = error.original_exception.__class__.__name__
    result["original_message"] = str(error.original_exception)

    return result