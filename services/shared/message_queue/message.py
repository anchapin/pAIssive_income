"""
Message schemas and utilities for the message queue.

This module provides schemas and utilities for messages sent through the message queue.
"""


import json
import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

import msgpack
from pydantic import BaseModel, ConfigDict, Field, field_validator



# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages that can be sent through the message queue."""

    # Command messages (requests to perform an action)
    COMMAND = "command"

    # Event messages (notifications that something has happened)
    EVENT = "event"

    # Query messages (requests for information)
    QUERY = "query"

    # Response messages (responses to queries or commands)
    RESPONSE = "response"

    # Error messages (notifications of errors)
    ERROR = "error"


class MessagePriority(int, Enum):
    """Priority levels for messages."""

    # Highest priority (urgent messages)
    HIGH = 0

    # Normal priority (default)
    NORMAL = 1

    # Low priority (background tasks)
    LOW = 2


class MessageStatus(str, Enum):
    """Status of a message."""

    # Message has been created but not yet published
    CREATED = "created"

    # Message has been published to the message queue
    PUBLISHED = "published"

    # Message has been delivered to a consumer
    DELIVERED = "delivered"

    # Message has been acknowledged by a consumer
    ACKNOWLEDGED = "acknowledged"

    # Message processing has failed
    FAILED = "failed"


class Message(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """
    Base message schema for all messages sent through the message queue.
    """

    # Message ID (UUID)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Message type
    type: MessageType = Field(...)

    # Message source (service name)
    source: str = Field(...)

    # Message destination (service name or exchange)
    destination: str = Field(...)

    # Message subject (topic or command name)
    subject: str = Field(...)

    # Message priority
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)

    # Message timestamp (Unix timestamp)
    timestamp: float = Field(default_factory=time.time)

    # Message expiration time (Unix timestamp, optional)
    expires_at: Optional[float] = Field(default=None)

    # Message correlation ID (for request-response patterns)
    correlation_id: Optional[str] = Field(default=None)

    # Message payload
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Message headers (metadata)
    headers: Dict[str, Any] = Field(default_factory=dict)

    # Message status
    status: MessageStatus = Field(default=MessageStatus.CREATED)

    @field_validator("correlation_id", pre=True, always=True)
    def set_correlation_id(cls, v, values):
        """Set correlation ID if not provided."""
        if v is None and "id" in values:
                    return values["id"]
                return v

    def is_expired(self) -> bool:
        """
        Check if the message has expired.

        Returns:
            bool: True if the message has expired, False otherwise
        """
        if self.expires_at is None:
                    return False

                return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the message
        """
                return self.dict()

    def to_json(self) -> str:
        """
        Convert the message to a JSON string.

        Returns:
            str: JSON string representation of the message
        """
                return self.json()

    def to_msgpack(self) -> bytes:
        """
        Convert the message to a MessagePack binary.

        Returns:
            bytes: MessagePack binary representation of the message
        """
                return msgpack.packb(self.dict(), use_bin_type=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """
        Create a message from a dictionary.

        Args:
            data: Dictionary representation of the message

        Returns:
            Message: Message instance
        """
                return cls(**data)

    @classmethod
    def from_json(cls, data: str) -> "Message":
        """
        Create a message from a JSON string.

        Args:
            data: JSON string representation of the message

        Returns:
            Message: Message instance
        """
                return cls(**json.loads(data))

    @classmethod
    def from_msgpack(cls, data: bytes) -> "Message":
        """
        Create a message from a MessagePack binary.

        Args:
            data: MessagePack binary representation of the message

        Returns:
            Message: Message instance
        """
                return cls(**msgpack.unpackb(data, raw=False))


# Generic type for message payload
T = TypeVar("T", bound=BaseModel)


class MessageSchema(Generic[T]):
    """
    Schema for messages with a specific payload type.
    """

    def __init__(self, payload_model: Type[T]):
        """
        Initialize the message schema.

        Args:
            payload_model: Pydantic model for the message payload
        """
        self.payload_model = payload_model

    def create_message(
        self,
        source: str,
        destination: str,
        subject: str,
        payload: Union[T, Dict[str, Any]],
        message_type: MessageType = MessageType.EVENT,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None,
        expires_in: Optional[float] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Create a message with the specified payload.

        Args:
            source: Source service name
            destination: Destination service name or exchange
            subject: Message subject (topic or command name)
            payload: Message payload (instance of payload_model or dict)
            message_type: Message type
            priority: Message priority
            correlation_id: Correlation ID for request-response patterns
            expires_in: Message expiration time in seconds from now
            headers: Message headers (metadata)

        Returns:
            Message: Message instance
        """
        # Convert payload to dict if it's a model instance
        if isinstance(payload, BaseModel):
            payload_dict = payload.dict()
        else:
            # Validate payload against the model
            payload_dict = self.payload_model(**payload).dict()

        # Calculate expiration time if provided
        expires_at = None
        if expires_in is not None:
            expires_at = time.time() + expires_in

        # Create the message
                return Message(
            type=message_type,
            source=source,
            destination=destination,
            subject=subject,
            payload=payload_dict,
            priority=priority,
            correlation_id=correlation_id,
            expires_at=expires_at,
            headers=headers or {},
        )

    def parse_message(self, message: Message) -> T:
        """
        Parse the payload of a message.

        Args:
            message: Message instance

        Returns:
            T: Parsed payload
        """
                return self.payload_model(**message.payload