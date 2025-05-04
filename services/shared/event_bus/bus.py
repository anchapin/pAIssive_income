"""
"""
Event bus implementation for pAIssive income microservices.
Event bus implementation for pAIssive income microservices.


This module provides an event bus implementation for event-driven architecture.
This module provides an event bus implementation for event-driven architecture.
"""
"""




import logging
import logging
import re
import re
from typing import Dict, Optional, Union
from typing import Dict, Optional, Union


from .event import AsyncEventHandler, Event, EventHandler
from .event import AsyncEventHandler, Event, EventHandler
from .exceptions import EventPublishError, EventSubscribeError
from .exceptions import EventPublishError, EventSubscribeError


(
(
AsyncMessageQueueClient,
AsyncMessageQueueClient,
Message,
Message,
MessageQueueClient,
MessageQueueClient,
MessageQueueError,
MessageQueueError,
MessageSchema,
MessageSchema,
MessageType,
MessageType,
)
)
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




class EventSubscription:
    class EventSubscription:
    """
    """
    Subscription to events on the event bus.
    Subscription to events on the event bus.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    event_pattern: str,
    event_pattern: str,
    handler: Union[EventHandler, AsyncEventHandler],
    handler: Union[EventHandler, AsyncEventHandler],
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    is_async: bool = False,
    is_async: bool = False,
    ):
    ):
    """
    """
    Initialize the event subscription.
    Initialize the event subscription.


    Args:
    Args:
    event_pattern: Pattern to match event names (supports wildcards)
    event_pattern: Pattern to match event names (supports wildcards)
    handler: Function to handle matching events
    handler: Function to handle matching events
    subscription_id: ID for the subscription (defaults to a generated ID)
    subscription_id: ID for the subscription (defaults to a generated ID)
    is_async: Whether the handler is asynchronous
    is_async: Whether the handler is asynchronous
    """
    """
    self.event_pattern = event_pattern
    self.event_pattern = event_pattern
    self.handler = handler
    self.handler = handler
    self.subscription_id = subscription_id or f"sub_{id(self)}"
    self.subscription_id = subscription_id or f"sub_{id(self)}"
    self.is_async = is_async
    self.is_async = is_async


    # Convert the event pattern to a regex pattern
    # Convert the event pattern to a regex pattern
    pattern = (
    pattern = (
    event_pattern.replace(".", r"\.").replace("*", r"[^.]+").replace("#", r".+")
    event_pattern.replace(".", r"\.").replace("*", r"[^.]+").replace("#", r".+")
    )
    )
    self.pattern = re.compile(f"^{pattern}$")
    self.pattern = re.compile(f"^{pattern}$")


    def matches(self, event_name: str) -> bool:
    def matches(self, event_name: str) -> bool:
    """
    """
    Check if the subscription matches an event name.
    Check if the subscription matches an event name.


    Args:
    Args:
    event_name: Name of the event
    event_name: Name of the event


    Returns:
    Returns:
    bool: True if the subscription matches, False otherwise
    bool: True if the subscription matches, False otherwise
    """
    """
    return bool(self.pattern.match(event_name))
    return bool(self.pattern.match(event_name))




    class EventPublisher:
    class EventPublisher:
    """
    """
    Publisher for the event bus.
    Publisher for the event bus.


    This class provides methods for publishing events to the event bus.
    This class provides methods for publishing events to the event bus.
    """
    """


    def __init__(self, service_name: str, message_queue_client: MessageQueueClient):
    def __init__(self, service_name: str, message_queue_client: MessageQueueClient):
    """
    """
    Initialize the event publisher.
    Initialize the event publisher.


    Args:
    Args:
    service_name: Name of the service using this publisher
    service_name: Name of the service using this publisher
    message_queue_client: Message queue client to use for publishing
    message_queue_client: Message queue client to use for publishing
    """
    """
    self.service_name = service_name
    self.service_name = service_name
    self.message_queue_client = message_queue_client
    self.message_queue_client = message_queue_client


    # Create a message schema for events
    # Create a message schema for events
    self.event_schema = MessageSchema(Event)
    self.event_schema = MessageSchema(Event)


    def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
    def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
    """
    """
    Publish an event to the event bus.
    Publish an event to the event bus.


    Args:
    Args:
    event: Event to publish
    event: Event to publish
    routing_key: Routing key for the event (defaults to event.name)
    routing_key: Routing key for the event (defaults to event.name)


    Returns:
    Returns:
    Event: The published event
    Event: The published event


    Raises:
    Raises:
    EventPublishError: If the event cannot be published
    EventPublishError: If the event cannot be published
    """
    """
    try:
    try:
    # Use the event name as the routing key if not provided
    # Use the event name as the routing key if not provided
    if routing_key is None:
    if routing_key is None:
    routing_key = f"events.{event.name}"
    routing_key = f"events.{event.name}"


    # Create a message from the event
    # Create a message from the event
    message = self.event_schema.create_message(
    message = self.event_schema.create_message(
    source=self.service_name,
    source=self.service_name,
    destination="*",  # Broadcast to all interested services
    destination="*",  # Broadcast to all interested services
    subject=event.name,
    subject=event.name,
    payload=event,
    payload=event,
    message_type=MessageType.EVENT,
    message_type=MessageType.EVENT,
    )
    )


    # Publish the message
    # Publish the message
    self.message_queue_client.publish(message=message, routing_key=routing_key)
    self.message_queue_client.publish(message=message, routing_key=routing_key)


    logger.info(f"Published event {event.name} with ID {event.metadata.id}")
    logger.info(f"Published event {event.name} with ID {event.metadata.id}")


    return event
    return event


except MessageQueueError as e:
except MessageQueueError as e:
    logger.error(f"Failed to publish event {event.name}: {str(e)}")
    logger.error(f"Failed to publish event {event.name}: {str(e)}")
    raise EventPublishError(f"Failed to publish event: {str(e)}")
    raise EventPublishError(f"Failed to publish event: {str(e)}")
except Exception as e:
except Exception as e:
    logger.error(f"Error publishing event {event.name}: {str(e)}")
    logger.error(f"Error publishing event {event.name}: {str(e)}")
    raise EventPublishError(f"Error publishing event: {str(e)}")
    raise EventPublishError(f"Error publishing event: {str(e)}")




    class EventSubscriber:
    class EventSubscriber:
    """
    """
    Subscriber for the event bus.
    Subscriber for the event bus.


    This class provides methods for subscribing to events on the event bus.
    This class provides methods for subscribing to events on the event bus.
    """
    """


    def __init__(self, service_name: str, message_queue_client: MessageQueueClient):
    def __init__(self, service_name: str, message_queue_client: MessageQueueClient):
    """
    """
    Initialize the event subscriber.
    Initialize the event subscriber.


    Args:
    Args:
    service_name: Name of the service using this subscriber
    service_name: Name of the service using this subscriber
    message_queue_client: Message queue client to use for subscribing
    message_queue_client: Message queue client to use for subscribing
    """
    """
    self.service_name = service_name
    self.service_name = service_name
    self.message_queue_client = message_queue_client
    self.message_queue_client = message_queue_client


    # Create a message schema for events
    # Create a message schema for events
    self.event_schema = MessageSchema(Event)
    self.event_schema = MessageSchema(Event)


    # Queue name for this service
    # Queue name for this service
    self.queue_name = f"{service_name}.events"
    self.queue_name = f"{service_name}.events"


    # Subscriptions
    # Subscriptions
    self.subscriptions: Dict[str, EventSubscription] = {}
    self.subscriptions: Dict[str, EventSubscription] = {}


    # Consumer tag
    # Consumer tag
    self.consumer_tag = None
    self.consumer_tag = None


    def subscribe(
    def subscribe(
    self,
    self,
    event_pattern: str,
    event_pattern: str,
    handler: EventHandler,
    handler: EventHandler,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    ) -> EventSubscription:
    ) -> EventSubscription:
    """
    """
    Subscribe to events matching a pattern.
    Subscribe to events matching a pattern.


    Args:
    Args:
    event_pattern: Pattern to match event names (supports wildcards)
    event_pattern: Pattern to match event names (supports wildcards)
    handler: Function to handle matching events
    handler: Function to handle matching events
    subscription_id: ID for the subscription (defaults to a generated ID)
    subscription_id: ID for the subscription (defaults to a generated ID)


    Returns:
    Returns:
    EventSubscription: The created subscription
    EventSubscription: The created subscription


    Raises:
    Raises:
    EventSubscribeError: If the subscription cannot be created
    EventSubscribeError: If the subscription cannot be created
    """
    """
    try:
    try:
    # Create a subscription
    # Create a subscription
    subscription = EventSubscription(
    subscription = EventSubscription(
    event_pattern=event_pattern,
    event_pattern=event_pattern,
    handler=handler,
    handler=handler,
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    )
    )


    # Store the subscription
    # Store the subscription
    self.subscriptions[subscription.subscription_id] = subscription
    self.subscriptions[subscription.subscription_id] = subscription


    logger.info(
    logger.info(
    f"Created subscription {subscription.subscription_id} for pattern {event_pattern}"
    f"Created subscription {subscription.subscription_id} for pattern {event_pattern}"
    )
    )


    return subscription
    return subscription


except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Failed to create subscription for pattern {event_pattern}: {str(e)}"
    f"Failed to create subscription for pattern {event_pattern}: {str(e)}"
    )
    )
    raise EventSubscribeError(f"Failed to create subscription: {str(e)}")
    raise EventSubscribeError(f"Failed to create subscription: {str(e)}")


    def unsubscribe(self, subscription_id: str) -> bool:
    def unsubscribe(self, subscription_id: str) -> bool:
    """
    """
    Unsubscribe from events.
    Unsubscribe from events.


    Args:
    Args:
    subscription_id: ID of the subscription to remove
    subscription_id: ID of the subscription to remove


    Returns:
    Returns:
    bool: True if the subscription was removed, False otherwise
    bool: True if the subscription was removed, False otherwise
    """
    """
    if subscription_id in self.subscriptions:
    if subscription_id in self.subscriptions:
    del self.subscriptions[subscription_id]
    del self.subscriptions[subscription_id]
    logger.info(f"Removed subscription {subscription_id}")
    logger.info(f"Removed subscription {subscription_id}")
    return True
    return True


    logger.warning(f"Subscription {subscription_id} not found")
    logger.warning(f"Subscription {subscription_id} not found")
    return False
    return False


    def start(self) -> str:
    def start(self) -> str:
    """
    """
    Start consuming events.
    Start consuming events.


    Returns:
    Returns:
    str: The consumer tag
    str: The consumer tag


    Raises:
    Raises:
    EventSubscribeError: If consumption cannot be started
    EventSubscribeError: If consumption cannot be started
    """
    """
    try:
    try:
    # Declare a queue for this service
    # Declare a queue for this service
    self.message_queue_client.declare_queue(
    self.message_queue_client.declare_queue(
    queue_name=self.queue_name, durable=True
    queue_name=self.queue_name, durable=True
    )
    )


    # Bind the queue to the events exchange with a wildcard routing key
    # Bind the queue to the events exchange with a wildcard routing key
    self.message_queue_client.bind_queue(
    self.message_queue_client.bind_queue(
    queue_name=self.queue_name,
    queue_name=self.queue_name,
    routing_key="events.#",  # Listen for all events
    routing_key="events.#",  # Listen for all events
    )
    )


    # Define the message handler
    # Define the message handler
    def handle_message(message: Message):
    def handle_message(message: Message):
    try:
    try:
    # Parse the event
    # Parse the event
    event = self.event_schema.parse_message(message)
    event = self.event_schema.parse_message(message)


    # Find matching subscriptions
    # Find matching subscriptions
    matching_subscriptions = [
    matching_subscriptions = [
    subscription
    subscription
    for subscription in self.subscriptions.values()
    for subscription in self.subscriptions.values()
    if subscription.matches(event.name)
    if subscription.matches(event.name)
    ]
    ]


    if not matching_subscriptions:
    if not matching_subscriptions:
    logger.debug(f"No subscriptions match event {event.name}")
    logger.debug(f"No subscriptions match event {event.name}")
    return # Call the handlers for matching subscriptions
    return # Call the handlers for matching subscriptions
    for subscription in matching_subscriptions:
    for subscription in matching_subscriptions:
    try:
    try:
    subscription.handler(event)
    subscription.handler(event)
except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error handling event {event.name} in subscription {subscription.subscription_id}: {str(e)}"
    f"Error handling event {event.name} in subscription {subscription.subscription_id}: {str(e)}"
    )
    )


except Exception as e:
except Exception as e:
    logger.error(f"Error processing event message: {str(e)}")
    logger.error(f"Error processing event message: {str(e)}")


    # Start consuming
    # Start consuming
    self.consumer_tag = self.message_queue_client.consume(
    self.consumer_tag = self.message_queue_client.consume(
    queue_name=self.queue_name, handler=handle_message, auto_ack=True
    queue_name=self.queue_name, handler=handle_message, auto_ack=True
    )
    )


    logger.info(f"Started consuming events with tag {self.consumer_tag}")
    logger.info(f"Started consuming events with tag {self.consumer_tag}")


    return self.consumer_tag
    return self.consumer_tag


except MessageQueueError as e:
except MessageQueueError as e:
    logger.error(f"Failed to start consuming events: {str(e)}")
    logger.error(f"Failed to start consuming events: {str(e)}")
    raise EventSubscribeError(f"Failed to start consuming events: {str(e)}")
    raise EventSubscribeError(f"Failed to start consuming events: {str(e)}")
except Exception as e:
except Exception as e:
    logger.error(f"Error starting event consumption: {str(e)}")
    logger.error(f"Error starting event consumption: {str(e)}")
    raise EventSubscribeError(f"Error starting event consumption: {str(e)}")
    raise EventSubscribeError(f"Error starting event consumption: {str(e)}")


    def stop(self):
    def stop(self):
    """Stop consuming events."""
    if self.consumer_tag:
    try:
    self.message_queue_client.stop_consuming(self.consumer_tag)
    self.consumer_tag = None
    logger.info("Stopped consuming events")
except Exception as e:
    logger.warning(f"Error stopping event consumption: {str(e)}")


    class EventBus:
    """
    """
    Event bus for event-driven architecture.
    Event bus for event-driven architecture.


    This class provides a unified interface for publishing and subscribing to events.
    This class provides a unified interface for publishing and subscribing to events.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    service_name: str,
    service_name: str,
    host: str = "localhost",
    host: str = "localhost",
    port: int = 5672,
    port: int = 5672,
    username: str = "guest",
    username: str = "guest",
    password: str = "guest",
    password: str = "guest",
    virtual_host: str = "/",
    virtual_host: str = "/",
    exchange_name: str = "paissive_income",
    exchange_name: str = "paissive_income",
    ):
    ):
    """
    """
    Initialize the event bus.
    Initialize the event bus.


    Args:
    Args:
    service_name: Name of the service using this event bus
    service_name: Name of the service using this event bus
    host: RabbitMQ host
    host: RabbitMQ host
    port: RabbitMQ port
    port: RabbitMQ port
    username: RabbitMQ username
    username: RabbitMQ username
    password: RabbitMQ password
    password: RabbitMQ password
    virtual_host: RabbitMQ virtual host
    virtual_host: RabbitMQ virtual host
    exchange_name: Name of the exchange to use
    exchange_name: Name of the exchange to use
    """
    """
    self.service_name = service_name
    self.service_name = service_name


    # Create a message queue client
    # Create a message queue client
    self.message_queue_client = MessageQueueClient(
    self.message_queue_client = MessageQueueClient(
    host=host,
    host=host,
    port=port,
    port=port,
    username=username,
    username=username,
    password=password,
    password=password,
    virtual_host=virtual_host,
    virtual_host=virtual_host,
    service_name=service_name,
    service_name=service_name,
    exchange_type="topic",
    exchange_type="topic",
    exchange_name=exchange_name,
    exchange_name=exchange_name,
    )
    )


    # Create publisher and subscriber
    # Create publisher and subscriber
    self.publisher = EventPublisher(
    self.publisher = EventPublisher(
    service_name=service_name, message_queue_client=self.message_queue_client
    service_name=service_name, message_queue_client=self.message_queue_client
    )
    )


    self.subscriber = EventSubscriber(
    self.subscriber = EventSubscriber(
    service_name=service_name, message_queue_client=self.message_queue_client
    service_name=service_name, message_queue_client=self.message_queue_client
    )
    )


    def __del__(self):
    def __del__(self):
    """Clean up resources when the event bus is deleted."""
    self.close()

    def close(self):
    """Close the event bus."""
    self.subscriber.stop()
    self.message_queue_client.close()

    def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
    """
    """
    Publish an event to the event bus.
    Publish an event to the event bus.


    Args:
    Args:
    event: Event to publish
    event: Event to publish
    routing_key: Routing key for the event (defaults to event.name)
    routing_key: Routing key for the event (defaults to event.name)


    Returns:
    Returns:
    Event: The published event
    Event: The published event


    Raises:
    Raises:
    EventPublishError: If the event cannot be published
    EventPublishError: If the event cannot be published
    """
    """
    return self.publisher.publish(event, routing_key)
    return self.publisher.publish(event, routing_key)


    def subscribe(
    def subscribe(
    self,
    self,
    event_pattern: str,
    event_pattern: str,
    handler: EventHandler,
    handler: EventHandler,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    ) -> EventSubscription:
    ) -> EventSubscription:
    """
    """
    Subscribe to events matching a pattern.
    Subscribe to events matching a pattern.


    Args:
    Args:
    event_pattern: Pattern to match event names (supports wildcards)
    event_pattern: Pattern to match event names (supports wildcards)
    handler: Function to handle matching events
    handler: Function to handle matching events
    subscription_id: ID for the subscription (defaults to a generated ID)
    subscription_id: ID for the subscription (defaults to a generated ID)


    Returns:
    Returns:
    EventSubscription: The created subscription
    EventSubscription: The created subscription


    Raises:
    Raises:
    EventSubscribeError: If the subscription cannot be created
    EventSubscribeError: If the subscription cannot be created
    """
    """
    return self.subscriber.subscribe(event_pattern, handler, subscription_id)
    return self.subscriber.subscribe(event_pattern, handler, subscription_id)


    def unsubscribe(self, subscription_id: str) -> bool:
    def unsubscribe(self, subscription_id: str) -> bool:
    """
    """
    Unsubscribe from events.
    Unsubscribe from events.


    Args:
    Args:
    subscription_id: ID of the subscription to remove
    subscription_id: ID of the subscription to remove


    Returns:
    Returns:
    bool: True if the subscription was removed, False otherwise
    bool: True if the subscription was removed, False otherwise
    """
    """
    return self.subscriber.unsubscribe(subscription_id)
    return self.subscriber.unsubscribe(subscription_id)


    def start(self) -> str:
    def start(self) -> str:
    """
    """
    Start consuming events.
    Start consuming events.


    Returns:
    Returns:
    str: The consumer tag
    str: The consumer tag


    Raises:
    Raises:
    EventSubscribeError: If consumption cannot be started
    EventSubscribeError: If consumption cannot be started
    """
    """
    return self.subscriber.start()
    return self.subscriber.start()


    def stop(self):
    def stop(self):
    """Stop consuming events."""
    self.subscriber.stop()


    class AsyncEventBus:
    """
    """
    Asynchronous event bus for event-driven architecture.
    Asynchronous event bus for event-driven architecture.


    This class provides a unified interface for publishing and subscribing to events asynchronously.
    This class provides a unified interface for publishing and subscribing to events asynchronously.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    service_name: str,
    service_name: str,
    host: str = "localhost",
    host: str = "localhost",
    port: int = 5672,
    port: int = 5672,
    username: str = "guest",
    username: str = "guest",
    password: str = "guest",
    password: str = "guest",
    virtual_host: str = "/",
    virtual_host: str = "/",
    exchange_name: str = "paissive_income",
    exchange_name: str = "paissive_income",
    ):
    ):
    """
    """
    Initialize the asynchronous event bus.
    Initialize the asynchronous event bus.


    Args:
    Args:
    service_name: Name of the service using this event bus
    service_name: Name of the service using this event bus
    host: RabbitMQ host
    host: RabbitMQ host
    port: RabbitMQ port
    port: RabbitMQ port
    username: RabbitMQ username
    username: RabbitMQ username
    password: RabbitMQ password
    password: RabbitMQ password
    virtual_host: RabbitMQ virtual host
    virtual_host: RabbitMQ virtual host
    exchange_name: Name of the exchange to use
    exchange_name: Name of the exchange to use
    """
    """
    self.service_name = service_name
    self.service_name = service_name
    self.host = host
    self.host = host
    self.port = port
    self.port = port
    self.username = username
    self.username = username
    self.password = password
    self.password = password
    self.virtual_host = virtual_host
    self.virtual_host = virtual_host
    self.exchange_name = exchange_name
    self.exchange_name = exchange_name


    # Message queue client
    # Message queue client
    self.message_queue_client = None
    self.message_queue_client = None


    # Subscriptions
    # Subscriptions
    self.subscriptions: Dict[str, EventSubscription] = {}
    self.subscriptions: Dict[str, EventSubscription] = {}


    # Consumer tag
    # Consumer tag
    self.consumer_tag = None
    self.consumer_tag = None


    # Event schema
    # Event schema
    self.event_schema = MessageSchema(Event)
    self.event_schema = MessageSchema(Event)


    async def __aenter__(self):
    async def __aenter__(self):
    """Enter async context manager."""
    await self.connect()
    return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Exit async context manager."""
    await self.close()

    async def connect(self):
    """
    """
    Connect to the message queue asynchronously.
    Connect to the message queue asynchronously.


    Raises:
    Raises:
    EventBusError: If the connection fails
    EventBusError: If the connection fails
    """
    """
    # Create a message queue client
    # Create a message queue client
    self.message_queue_client = AsyncMessageQueueClient(
    self.message_queue_client = AsyncMessageQueueClient(
    host=self.host,
    host=self.host,
    port=self.port,
    port=self.port,
    username=self.username,
    username=self.username,
    password=self.password,
    password=self.password,
    virtual_host=self.virtual_host,
    virtual_host=self.virtual_host,
    service_name=self.service_name,
    service_name=self.service_name,
    exchange_type="topic",
    exchange_type="topic",
    exchange_name=self.exchange_name,
    exchange_name=self.exchange_name,
    )
    )


    await self.message_queue_client.connect()
    await self.message_queue_client.connect()


    async def close(self):
    async def close(self):
    """Close the event bus asynchronously."""
    if self.consumer_tag:
    await self.stop()

    if self.message_queue_client:
    await self.message_queue_client.close()

    async def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
    """
    """
    Publish an event to the event bus asynchronously.
    Publish an event to the event bus asynchronously.


    Args:
    Args:
    event: Event to publish
    event: Event to publish
    routing_key: Routing key for the event (defaults to event.name)
    routing_key: Routing key for the event (defaults to event.name)


    Returns:
    Returns:
    Event: The published event
    Event: The published event


    Raises:
    Raises:
    EventPublishError: If the event cannot be published
    EventPublishError: If the event cannot be published
    """
    """
    try:
    try:
    # Use the event name as the routing key if not provided
    # Use the event name as the routing key if not provided
    if routing_key is None:
    if routing_key is None:
    routing_key = f"events.{event.name}"
    routing_key = f"events.{event.name}"


    # Create a message from the event
    # Create a message from the event
    message = self.event_schema.create_message(
    message = self.event_schema.create_message(
    source=self.service_name,
    source=self.service_name,
    destination="*",  # Broadcast to all interested services
    destination="*",  # Broadcast to all interested services
    subject=event.name,
    subject=event.name,
    payload=event,
    payload=event,
    message_type=MessageType.EVENT,
    message_type=MessageType.EVENT,
    )
    )


    # Publish the message
    # Publish the message
    await self.message_queue_client.publish(
    await self.message_queue_client.publish(
    message=message, routing_key=routing_key
    message=message, routing_key=routing_key
    )
    )


    logger.info(f"Published event {event.name} with ID {event.metadata.id}")
    logger.info(f"Published event {event.name} with ID {event.metadata.id}")


    return event
    return event


except MessageQueueError as e:
except MessageQueueError as e:
    logger.error(f"Failed to publish event {event.name}: {str(e)}")
    logger.error(f"Failed to publish event {event.name}: {str(e)}")
    raise EventPublishError(f"Failed to publish event: {str(e)}")
    raise EventPublishError(f"Failed to publish event: {str(e)}")
except Exception as e:
except Exception as e:
    logger.error(f"Error publishing event {event.name}: {str(e)}")
    logger.error(f"Error publishing event {event.name}: {str(e)}")
    raise EventPublishError(f"Error publishing event: {str(e)}")
    raise EventPublishError(f"Error publishing event: {str(e)}")


    async def subscribe(
    async def subscribe(
    self,
    self,
    event_pattern: str,
    event_pattern: str,
    handler: AsyncEventHandler,
    handler: AsyncEventHandler,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    ) -> EventSubscription:
    ) -> EventSubscription:
    """
    """
    Subscribe to events matching a pattern asynchronously.
    Subscribe to events matching a pattern asynchronously.


    Args:
    Args:
    event_pattern: Pattern to match event names (supports wildcards)
    event_pattern: Pattern to match event names (supports wildcards)
    handler: Async function to handle matching events
    handler: Async function to handle matching events
    subscription_id: ID for the subscription (defaults to a generated ID)
    subscription_id: ID for the subscription (defaults to a generated ID)


    Returns:
    Returns:
    EventSubscription: The created subscription
    EventSubscription: The created subscription


    Raises:
    Raises:
    EventSubscribeError: If the subscription cannot be created
    EventSubscribeError: If the subscription cannot be created
    """
    """
    try:
    try:
    # Create a subscription
    # Create a subscription
    subscription = EventSubscription(
    subscription = EventSubscription(
    event_pattern=event_pattern,
    event_pattern=event_pattern,
    handler=handler,
    handler=handler,
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    is_async=True,
    is_async=True,
    )
    )


    # Store the subscription
    # Store the subscription
    self.subscriptions[subscription.subscription_id] = subscription
    self.subscriptions[subscription.subscription_id] = subscription


    logger.info(
    logger.info(
    f"Created subscription {subscription.subscription_id} for pattern {event_pattern}"
    f"Created subscription {subscription.subscription_id} for pattern {event_pattern}"
    )
    )


    return subscription
    return subscription


except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Failed to create subscription for pattern {event_pattern}: {str(e)}"
    f"Failed to create subscription for pattern {event_pattern}: {str(e)}"
    )
    )
    raise EventSubscribeError(f"Failed to create subscription: {str(e)}")
    raise EventSubscribeError(f"Failed to create subscription: {str(e)}")


    def unsubscribe(self, subscription_id: str) -> bool:
    def unsubscribe(self, subscription_id: str) -> bool:
    """
    """
    Unsubscribe from events.
    Unsubscribe from events.


    Args:
    Args:
    subscription_id: ID of the subscription to remove
    subscription_id: ID of the subscription to remove


    Returns:
    Returns:
    bool: True if the subscription was removed, False otherwise
    bool: True if the subscription was removed, False otherwise
    """
    """
    if subscription_id in self.subscriptions:
    if subscription_id in self.subscriptions:
    del self.subscriptions[subscription_id]
    del self.subscriptions[subscription_id]
    logger.info(f"Removed subscription {subscription_id}")
    logger.info(f"Removed subscription {subscription_id}")
    return True
    return True


    logger.warning(f"Subscription {subscription_id} not found")
    logger.warning(f"Subscription {subscription_id} not found")
    return False
    return False


    async def start(self) -> str:
    async def start(self) -> str:
    """
    """
    Start consuming events asynchronously.
    Start consuming events asynchronously.


    Returns:
    Returns:
    str: The consumer tag
    str: The consumer tag


    Raises:
    Raises:
    EventSubscribeError: If consumption cannot be started
    EventSubscribeError: If consumption cannot be started
    """
    """
    try:
    try:
    # Declare a queue for this service
    # Declare a queue for this service
    queue = await self.message_queue_client.declare_queue(
    queue = await self.message_queue_client.declare_queue(
    queue_name=f"{self.service_name}.events", durable=True
    queue_name=f"{self.service_name}.events", durable=True
    )
    )


    # Bind the queue to the events exchange with a wildcard routing key
    # Bind the queue to the events exchange with a wildcard routing key
    await self.message_queue_client.bind_queue(
    await self.message_queue_client.bind_queue(
    queue=queue, routing_key="events.#"  # Listen for all events
    queue=queue, routing_key="events.#"  # Listen for all events
    )
    )


    # Define the message handler
    # Define the message handler
    async def handle_message(message: Message):
    async def handle_message(message: Message):
    try:
    try:
    # Parse the event
    # Parse the event
    event = self.event_schema.parse_message(message)
    event = self.event_schema.parse_message(message)


    # Find matching subscriptions
    # Find matching subscriptions
    matching_subscriptions = [
    matching_subscriptions = [
    subscription
    subscription
    for subscription in self.subscriptions.values()
    for subscription in self.subscriptions.values()
    if subscription.matches(event.name)
    if subscription.matches(event.name)
    ]
    ]


    if not matching_subscriptions:
    if not matching_subscriptions:
    logger.debug(f"No subscriptions match event {event.name}")
    logger.debug(f"No subscriptions match event {event.name}")
    return # Call the handlers for matching subscriptions
    return # Call the handlers for matching subscriptions
    for subscription in matching_subscriptions:
    for subscription in matching_subscriptions:
    try:
    try:
    if subscription.is_async:
    if subscription.is_async:
    await subscription.handler(event)
    await subscription.handler(event)
    else:
    else:
    subscription.handler(event)
    subscription.handler(event)
except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error handling event {event.name} in subscription {subscription.subscription_id}: {str(e)}"
    f"Error handling event {event.name} in subscription {subscription.subscription_id}: {str(e)}"
    )
    )


except Exception as e:
except Exception as e:
    logger.error(f"Error processing event message: {str(e)}")
    logger.error(f"Error processing event message: {str(e)}")


    # Start consuming
    # Start consuming
    self.consumer_tag = await self.message_queue_client.consume(
    self.consumer_tag = await self.message_queue_client.consume(
    queue_name=queue.name, handler=handle_message, auto_ack=True
    queue_name=queue.name, handler=handle_message, auto_ack=True
    )
    )


    logger.info(f"Started consuming events with tag {self.consumer_tag}")
    logger.info(f"Started consuming events with tag {self.consumer_tag}")


    return self.consumer_tag
    return self.consumer_tag


except MessageQueueError as e:
except MessageQueueError as e:
    logger.error(f"Failed to start consuming events: {str(e)}")
    logger.error(f"Failed to start consuming events: {str(e)}")
    raise EventSubscribeError(f"Failed to start consuming events: {str(e)}")
    raise EventSubscribeError(f"Failed to start consuming events: {str(e)}")
except Exception as e:
except Exception as e:
    logger.error(f"Error starting event consumption: {str(e)}")
    logger.error(f"Error starting event consumption: {str(e)}")
    raise EventSubscribeError(f"Error starting event consumption: {str(e)}")
    raise EventSubscribeError(f"Error starting event consumption: {str(e)}")


    async def stop(self):
    async def stop(self):
    """Stop consuming events asynchronously."""
    if self.consumer_tag and self.message_queue_client:
    try:
    await self.message_queue_client.stop_consuming(self.consumer_tag)
    self.consumer_tag = None
    logger.info("Stopped consuming events")
except Exception as e:
    logger.warning(f"Error stopping event consumption: {str(e)}")