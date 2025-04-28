"""
Exceptions for the message queue.

This module provides exceptions for the message queue client.
"""


class MessageQueueError(Exception):
    """Base exception for message queue errors."""
    pass


class ConnectionError(MessageQueueError):
    """Exception raised when a connection to the message queue fails."""
    pass


class PublishError(MessageQueueError):
    """Exception raised when a message cannot be published."""
    pass


class ConsumeError(MessageQueueError):
    """Exception raised when a message cannot be consumed."""
    pass


class SchemaError(MessageQueueError):
    """Exception raised when a message does not match its schema."""
    pass
