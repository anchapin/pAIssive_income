"""
Shared event bus utilities for pAIssive income microservices.

This package provides utilities for event-driven architecture in the
pAIssive income microservices platform.
"""

from .event import (
    Event,
    EventSchema,
    EventType,
    EventMetadata,
    EventHandler,
    AsyncEventHandler
)

from .bus import (
    EventBus,
    AsyncEventBus,
    EventSubscription,
    EventPublisher,
    EventSubscriber
)

from .exceptions import (
    EventBusError,
    EventPublishError,
    EventSubscribeError,
    EventHandlingError,
    EventValidationError
)

__all__ = [
    'Event',
    'EventSchema',
    'EventType',
    'EventMetadata',
    'EventHandler',
    'AsyncEventHandler',
    'EventBus',
    'AsyncEventBus',
    'EventSubscription',
    'EventPublisher',
    'EventSubscriber',
    'EventBusError',
    'EventPublishError',
    'EventSubscribeError',
    'EventHandlingError',
    'EventValidationError'
]
