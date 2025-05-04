"""
"""
Message schemas and utilities for the message queue.
Message schemas and utilities for the message queue.


This module provides schemas and utilities for messages sent through the message queue.
This module provides schemas and utilities for messages sent through the message queue.
"""
"""




import json
import json
import logging
import logging
import time
import time
import uuid
import uuid
from enum import Enum
from enum import Enum
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union


import msgpack
import msgpack
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import BaseModel, ConfigDict, Field, field_validator


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class MessageType(str, Enum):
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

    # Highest priority (urgent messages)
    HIGH = 0

    # Normal priority (default)
    NORMAL = 1

    # Low priority (background tasks)
    LOW = 2


    class MessageStatus(str, Enum):

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
    """
    Base message schema for all messages sent through the message queue.
    Base message schema for all messages sent through the message queue.
    """
    """


    # Message ID (UUID)
    # Message ID (UUID)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


    # Message type
    # Message type
    type: MessageType = Field(...)
    type: MessageType = Field(...)


    # Message source (service name)
    # Message source (service name)
    source: str = Field(...)
    source: str = Field(...)


    # Message destination (service name or exchange)
    # Message destination (service name or exchange)
    destination: str = Field(...)
    destination: str = Field(...)


    # Message subject (topic or command name)
    # Message subject (topic or command name)
    subject: str = Field(...)
    subject: str = Field(...)


    # Message priority
    # Message priority
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)


    # Message timestamp (Unix timestamp)
    # Message timestamp (Unix timestamp)
    timestamp: float = Field(default_factory=time.time)
    timestamp: float = Field(default_factory=time.time)


    # Message expiration time (Unix timestamp, optional)
    # Message expiration time (Unix timestamp, optional)
    expires_at: Optional[float] = Field(default=None)
    expires_at: Optional[float] = Field(default=None)


    # Message correlation ID (for request-response patterns)
    # Message correlation ID (for request-response patterns)
    correlation_id: Optional[str] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None)


    # Message payload
    # Message payload
    payload: Dict[str, Any] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)


    # Message headers (metadata)
    # Message headers (metadata)
    headers: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, Any] = Field(default_factory=dict)


    # Message status
    # Message status
    status: MessageStatus = Field(default=MessageStatus.CREATED)
    status: MessageStatus = Field(default=MessageStatus.CREATED)


    @field_validator("correlation_id", pre=True, always=True)
    @field_validator("correlation_id", pre=True, always=True)
    def set_correlation_id(cls, v, values):
    def set_correlation_id(cls, v, values):
    """Set correlation ID if not provided."""
    if v is None and "id" in values:
    return values["id"]
    return v

    def is_expired(self) -> bool:
    """
    """
    Check if the message has expired.
    Check if the message has expired.


    Returns:
    Returns:
    bool: True if the message has expired, False otherwise
    bool: True if the message has expired, False otherwise
    """
    """
    if self.expires_at is None:
    if self.expires_at is None:
    return False
    return False


    return time.time() > self.expires_at
    return time.time() > self.expires_at


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the message to a dictionary.
    Convert the message to a dictionary.


    Returns:
    Returns:
    Dict[str, Any]: Dictionary representation of the message
    Dict[str, Any]: Dictionary representation of the message
    """
    """
    return self.dict()
    return self.dict()


    def to_json(self) -> str:
    def to_json(self) -> str:
    """
    """
    Convert the message to a JSON string.
    Convert the message to a JSON string.


    Returns:
    Returns:
    str: JSON string representation of the message
    str: JSON string representation of the message
    """
    """
    return self.json()
    return self.json()


    def to_msgpack(self) -> bytes:
    def to_msgpack(self) -> bytes:
    """
    """
    Convert the message to a MessagePack binary.
    Convert the message to a MessagePack binary.


    Returns:
    Returns:
    bytes: MessagePack binary representation of the message
    bytes: MessagePack binary representation of the message
    """
    """
    return msgpack.packb(self.dict(), use_bin_type=True)
    return msgpack.packb(self.dict(), use_bin_type=True)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
    """
    """
    Create a message from a dictionary.
    Create a message from a dictionary.


    Args:
    Args:
    data: Dictionary representation of the message
    data: Dictionary representation of the message


    Returns:
    Returns:
    Message: Message instance
    Message: Message instance
    """
    """
    return cls(**data)
    return cls(**data)


    @classmethod
    @classmethod
    def from_json(cls, data: str) -> "Message":
    def from_json(cls, data: str) -> "Message":
    """
    """
    Create a message from a JSON string.
    Create a message from a JSON string.


    Args:
    Args:
    data: JSON string representation of the message
    data: JSON string representation of the message


    Returns:
    Returns:
    Message: Message instance
    Message: Message instance
    """
    """
    return cls(**json.loads(data))
    return cls(**json.loads(data))


    @classmethod
    @classmethod
    def from_msgpack(cls, data: bytes) -> "Message":
    def from_msgpack(cls, data: bytes) -> "Message":
    """
    """
    Create a message from a MessagePack binary.
    Create a message from a MessagePack binary.


    Args:
    Args:
    data: MessagePack binary representation of the message
    data: MessagePack binary representation of the message


    Returns:
    Returns:
    Message: Message instance
    Message: Message instance
    """
    """
    return cls(**msgpack.unpackb(data, raw=False))
    return cls(**msgpack.unpackb(data, raw=False))




    # Generic type for message payload
    # Generic type for message payload
    T = TypeVar("T", bound=BaseModel)
    T = TypeVar("T", bound=BaseModel)




    class MessageSchema(Generic[T]):
    class MessageSchema(Generic[T]):
    """
    """
    Schema for messages with a specific payload type.
    Schema for messages with a specific payload type.
    """
    """


    def __init__(self, payload_model: Type[T]):
    def __init__(self, payload_model: Type[T]):
    """
    """
    Initialize the message schema.
    Initialize the message schema.


    Args:
    Args:
    payload_model: Pydantic model for the message payload
    payload_model: Pydantic model for the message payload
    """
    """
    self.payload_model = payload_model
    self.payload_model = payload_model


    def create_message(
    def create_message(
    self,
    self,
    source: str,
    source: str,
    destination: str,
    destination: str,
    subject: str,
    subject: str,
    payload: Union[T, Dict[str, Any]],
    payload: Union[T, Dict[str, Any]],
    message_type: MessageType = MessageType.EVENT,
    message_type: MessageType = MessageType.EVENT,
    priority: MessagePriority = MessagePriority.NORMAL,
    priority: MessagePriority = MessagePriority.NORMAL,
    correlation_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    expires_in: Optional[float] = None,
    expires_in: Optional[float] = None,
    headers: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    ) -> Message:
    ) -> Message:
    """
    """
    Create a message with the specified payload.
    Create a message with the specified payload.


    Args:
    Args:
    source: Source service name
    source: Source service name
    destination: Destination service name or exchange
    destination: Destination service name or exchange
    subject: Message subject (topic or command name)
    subject: Message subject (topic or command name)
    payload: Message payload (instance of payload_model or dict)
    payload: Message payload (instance of payload_model or dict)
    message_type: Message type
    message_type: Message type
    priority: Message priority
    priority: Message priority
    correlation_id: Correlation ID for request-response patterns
    correlation_id: Correlation ID for request-response patterns
    expires_in: Message expiration time in seconds from now
    expires_in: Message expiration time in seconds from now
    headers: Message headers (metadata)
    headers: Message headers (metadata)


    Returns:
    Returns:
    Message: Message instance
    Message: Message instance
    """
    """
    # Convert payload to dict if it's a model instance
    # Convert payload to dict if it's a model instance
    if isinstance(payload, BaseModel):
    if isinstance(payload, BaseModel):
    payload_dict = payload.dict()
    payload_dict = payload.dict()
    else:
    else:
    # Validate payload against the model
    # Validate payload against the model
    payload_dict = self.payload_model(**payload).dict()
    payload_dict = self.payload_model(**payload).dict()


    # Calculate expiration time if provided
    # Calculate expiration time if provided
    expires_at = None
    expires_at = None
    if expires_in is not None:
    if expires_in is not None:
    expires_at = time.time() + expires_in
    expires_at = time.time() + expires_in


    # Create the message
    # Create the message
    return Message(
    return Message(
    type=message_type,
    type=message_type,
    source=source,
    source=source,
    destination=destination,
    destination=destination,
    subject=subject,
    subject=subject,
    payload=payload_dict,
    payload=payload_dict,
    priority=priority,
    priority=priority,
    correlation_id=correlation_id,
    correlation_id=correlation_id,
    expires_at=expires_at,
    expires_at=expires_at,
    headers=headers or {},
    headers=headers or {},
    )
    )


    def parse_message(self, message: Message) -> T:
    def parse_message(self, message: Message) -> T:
    """
    """
    Parse the payload of a message.
    Parse the payload of a message.


    Args:
    Args:
    message: Message instance
    message: Message instance


    Returns:
    Returns:
    T: Parsed payload
    T: Parsed payload
    """
    """
    return self.payload_model(**message.payload
    return self.payload_model(**message.payload