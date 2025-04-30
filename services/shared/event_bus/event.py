"""
Event schemas and utilities for the event bus.

This module provides schemas and utilities for events published through the event bus.
"""

import uuid
import time
import logging
from enum import Enum
from typing import Dict, Any, Optional, List, Union, TypeVar, Generic, Type, Callable

from pydantic import BaseModel, Field, validator

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of events that can be published through the event bus."""

    # Domain events (business events)
    DOMAIN = "domain"

    # Integration events (cross-service events)
    INTEGRATION = "integration"

    # System events (infrastructure events)
    SYSTEM = "system"

    # User events (user-initiated events)
    USER = "user"

    # Notification events (alerts and notifications)
    NOTIFICATION = "notification"


class EventMetadata(BaseModel):
    """Metadata for events."""

    # Event ID (UUID)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Event timestamp (Unix timestamp)
    timestamp: float = Field(default_factory=time.time)

    # Event type
    event_type: EventType = Field(...)

    # Event source (service name)
    source: str = Field(...)

    # Event version (for schema versioning)
    version: str = Field(default="1.0")

    # Correlation ID (for tracing)
    correlation_id: Optional[str] = Field(default=None)

    # Causation ID (event that caused this event)
    causation_id: Optional[str] = Field(default=None)

    # User ID (if applicable)
    user_id: Optional[str] = Field(default=None)

    # Additional metadata
    additional: Dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    """
    Base event schema for all events published through the event bus.
    """

    # Event name (e.g., "niche.analysis.completed")
    name: str = Field(...)

    # Event metadata
    metadata: EventMetadata = Field(...)

    # Event data
    data: Dict[str, Any] = Field(default_factory=dict)

    @validator("metadata", pre=True)
    def validate_metadata(cls, v, values):
        """Validate and convert metadata if needed."""
        if isinstance(v, dict):
            return EventMetadata(**v)
        return v

    @classmethod
    def create(
        cls,
        name: str,
        source: str,
        event_type: EventType,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        version: str = "1.0",
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> "Event":
        """
        Create a new event.

        Args:
            name: Event name
            source: Event source (service name)
            event_type: Event type
            data: Event data
            correlation_id: Correlation ID for tracing
            causation_id: Causation ID (event that caused this event)
            user_id: User ID (if applicable)
            version: Event version
            additional_metadata: Additional metadata

        Returns:
            Event: The created event
        """
        metadata = EventMetadata(
            event_type=event_type,
            source=source,
            version=version,
            correlation_id=correlation_id,
            causation_id=causation_id,
            user_id=user_id,
            additional=additional_metadata or {},
        )

        return cls(name=name, metadata=metadata, data=data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the event
        """
        return self.dict()


# Type variable for event data
T = TypeVar("T", bound=BaseModel)


class EventSchema(Generic[T]):
    """
    Schema for events with a specific data type.
    """

    def __init__(self, data_model: Type[T], event_name: str):
        """
        Initialize the event schema.

        Args:
            data_model: Pydantic model for the event data
            event_name: Name of the event
        """
        self.data_model = data_model
        self.event_name = event_name

    def create_event(
        self,
        source: str,
        data: Union[T, Dict[str, Any]],
        event_type: EventType = EventType.DOMAIN,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        version: str = "1.0",
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        Create an event with the specified data.

        Args:
            source: Source service name
            data: Event data (instance of data_model or dict)
            event_type: Event type
            correlation_id: Correlation ID for tracing
            causation_id: Causation ID (event that caused this event)
            user_id: User ID (if applicable)
            version: Event version
            additional_metadata: Additional metadata

        Returns:
            Event: Event instance
        """
        # Convert data to dict if it's a model instance
        if isinstance(data, BaseModel):
            data_dict = data.dict()
        else:
            # Validate data against the model
            data_dict = self.data_model(**data).dict()

        # Create the event
        return Event.create(
            name=self.event_name,
            source=source,
            event_type=event_type,
            data=data_dict,
            correlation_id=correlation_id,
            causation_id=causation_id,
            user_id=user_id,
            version=version,
            additional_metadata=additional_metadata,
        )

    def parse_event(self, event: Event) -> T:
        """
        Parse the data of an event.

        Args:
            event: Event instance

        Returns:
            T: Parsed data
        """
        return self.data_model(**event.data)


# Type for event handlers
EventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], Union[None, Any]]
