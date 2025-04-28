"""
Exceptions for the event bus.

This module provides exceptions for the event bus.
"""


class EventBusError(Exception):
    """Base exception for event bus errors."""
    pass


class EventPublishError(EventBusError):
    """Exception raised when an event cannot be published."""
    pass


class EventSubscribeError(EventBusError):
    """Exception raised when a subscription cannot be created."""
    pass


class EventHandlingError(EventBusError):
    """Exception raised when an event cannot be handled."""
    pass


class EventValidationError(EventBusError):
    """Exception raised when an event fails validation."""
    pass
