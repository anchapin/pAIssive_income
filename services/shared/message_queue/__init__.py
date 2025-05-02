"""
Shared message queue utilities for pAIssive income microservices.

This package provides utilities for asynchronous communication between
microservices using a message queue (RabbitMQ).
"""

from .client import (
    AsyncMessageHandler,
    AsyncMessageQueueClient,
    MessageHandler,
    MessageQueueClient,
)
from .exceptions import (
    ConnectionError,
    ConsumeError,
    MessageQueueError,
    PublishError,
    SchemaError,
)
from .message import Message, MessagePriority, MessageSchema, MessageStatus, MessageType

__all__ = [
    "MessageQueueClient",
    "AsyncMessageQueueClient",
    "MessageHandler",
    "AsyncMessageHandler",
    "Message",
    "MessageSchema",
    "MessagePriority",
    "MessageStatus",
    "MessageType",
    "MessageQueueError",
    "ConnectionError",
    "PublishError",
    "ConsumeError",
    "SchemaError",
]
