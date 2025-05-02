"""
Shared message queue utilities for pAIssive income microservices.

This package provides utilities for asynchronous communication between
microservices using a message queue (RabbitMQ).
"""

from .client import (
    MessageQueueClient,
    AsyncMessageQueueClient,
    MessageHandler,
    AsyncMessageHandler
)

from .message import (
    Message,
    MessageSchema,
    MessagePriority,
    MessageStatus,
    MessageType
)

from .exceptions import (
    MessageQueueError,
    ConnectionError,
    PublishError,
    ConsumeError,
    SchemaError
)

__all__ = [
    'MessageQueueClient',
    'AsyncMessageQueueClient',
    'MessageHandler',
    'AsyncMessageHandler',
    'Message',
    'MessageSchema',
    'MessagePriority',
    'MessageStatus',
    'MessageType',
    'MessageQueueError',
    'ConnectionError',
    'PublishError',
    'ConsumeError',
    'SchemaError'
]
