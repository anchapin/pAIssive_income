# Event Bus for pAIssive Income Microservices

This package provides an event bus implementation for event-driven architecture in the pAIssive Income microservices platform.

## Overview

The Event Bus enables:

- Event-driven architecture across microservices
- Loose coupling between services
- Asynchronous communication
- Domain events for business processes
- Integration events for cross-service communication

## Getting Started

### Prerequisites

- RabbitMQ (provided by the Message Queue Service)
- Python 3.8+

### Installation

```bash
pip install -r services/shared/event_bus/requirements.txt
```

## Usage

### Basic Usage

```python
from services.shared.event_bus import EventBus, Event, EventType

# Create an event bus
event_bus = EventBus(service_name="my-service")

# Subscribe to events
def handle_user_registered(event):
    print(f"User registered: {event.data['username']}")
    # Process the event...

event_bus.subscribe(
    event_pattern="user.registered",
    handler=handle_user_registered
)

# Start the event bus
event_bus.start()

# Create and publish an event
event = Event.create(
    name="user.registered",
    source="my-service",
    event_type=EventType.DOMAIN,
    data={
        "user_id": "123",
        "username": "john_doe",
        "email": "john.doe@example.com"
    }
)

event_bus.publish(event)
```

### Using Event Schemas

```python
from pydantic import BaseModel
from services.shared.event_bus import EventBus, EventSchema, EventType

# Define event data schema
class UserRegistered(BaseModel):
    user_id: str
    username: str
    email: str

# Create event schema
user_registered_schema = EventSchema(
    data_model=UserRegistered,
    event_name="user.registered"
)

# Create an event bus
event_bus = EventBus(service_name="my-service")

# Subscribe to events
def handle_user_registered(event):
    # Parse the event data
    user_data = user_registered_schema.parse_event(event)
    print(f"User registered: {user_data.username}")
    # Process the event...

event_bus.subscribe(
    event_pattern="user.registered",
    handler=handle_user_registered
)

# Start the event bus
event_bus.start()

# Create and publish an event
user_data = UserRegistered(
    user_id="123",
    username="john_doe",
    email="john.doe@example.com"
)

event = user_registered_schema.create_event(
    source="my-service",
    data=user_data,
    event_type=EventType.DOMAIN
)

event_bus.publish(event)
```

### Asynchronous Usage

```python
import asyncio
from services.shared.event_bus import AsyncEventBus, EventSchema, EventType

# Define event data schema and create event schema (as above)

async def main():
    # Create an async event bus
    async with AsyncEventBus(service_name="my-service") as event_bus:
        # Subscribe to events
        async def handle_user_registered(event):
            # Parse the event data
            user_data = user_registered_schema.parse_event(event)
            print(f"User registered: {user_data.username}")
            # Process the event...
            await asyncio.sleep(1)  # Simulate async processing
            print(f"Finished processing user: {user_data.username}")

        await event_bus.subscribe(
            event_pattern="user.registered",
            handler=handle_user_registered
        )

        # Start the event bus
        await event_bus.start()

        # Create and publish an event
        user_data = UserRegistered(
            user_id="123",
            username="john_doe",
            email="john.doe@example.com"
        )

        event = user_registered_schema.create_event(
            source="my-service",
            data=user_data,
            event_type=EventType.DOMAIN
        )

        await event_bus.publish(event)

        # Wait for events to be processed
        await asyncio.sleep(2)

asyncio.run(main())
```

## Event Patterns

The event bus supports pattern matching for event subscriptions:

- `user.registered` - Exact match
- `user.*` - Wildcard for one segment
- `user.#` - Wildcard for multiple segments
- `*.registered` - Wildcard for first segment
- `#.completed` - Wildcard for any number of segments before "completed"

## Event Types

The event bus supports different types of events:

- `EventType.DOMAIN` - Business events within a service
- `EventType.INTEGRATION` - Events shared between services
- `EventType.SYSTEM` - Infrastructure and technical events
- `EventType.USER` - User-initiated events
- `EventType.NOTIFICATION` - Alerts and notifications

## Examples

See the `services/shared/event_bus/examples.py` file for examples of how to use the event bus for different services and scenarios:

1. Niche Analysis Service - Domain Events
2. Marketing Service - Event Handling
3. Asynchronous Event Handling
4. Event-Driven Workflow

## Best Practices

1. **Use Event Schemas**: Define clear schemas for your events to ensure consistency.
2. **Meaningful Event Names**: Use descriptive, hierarchical names (e.g., `user.registered`, `order.created`).
3. **Include Metadata**: Add correlation IDs, timestamps, and other metadata to facilitate tracing.
4. **Idempotent Handlers**: Design event handlers to be idempotent (can be processed multiple times without side effects).
5. **Error Handling**: Implement proper error handling in event handlers to prevent message loss.
6. **Event Versioning**: Include version information in events to handle schema evolution.

## Troubleshooting

- If events are not being received, check that the RabbitMQ service is running.
- Verify that the event pattern in the subscription matches the event name.
- Check the logs for any errors in event handling.
- Ensure that the event bus is started before publishing or subscribing to events.
