"""
Exceptions for the event bus.

This module provides exceptions for the event bus.
"""


class EventBusError(Exception):
    """Base exception for event bus errors."""

    pass


    class EventPublishError(EventBusError):

    pass


    class EventSubscribeError(EventBusError):

    pass


    class EventHandlingError(EventBusError):

    pass


    class EventValidationError(EventBusError):
    """Exception raised when an event fails validation."""

    pass
