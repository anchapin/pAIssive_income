"""
Event bus implementation for pAIssive income microservices.

This module provides an event bus implementation for event-driven architecture.
"""

import re
import logging
from typing import Dict, Optional, Union

from services.shared.message_queue import (
    MessageQueueClient,
    AsyncMessageQueueClient,
    Message,
    MessageType,
    MessageSchema,
    MessageQueueError,
)

from .event import Event, EventHandler, AsyncEventHandler
from .exceptions import EventPublishError, EventSubscribeError

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EventSubscription:
    """
    Subscription to events on the event bus.
    """

    def __init__(
        self,
        event_pattern: str,
        handler: Union[EventHandler, AsyncEventHandler],
        subscription_id: Optional[str] = None,
        is_async: bool = False,
    ):
        """
        Initialize the event subscription.

        Args:
            event_pattern: Pattern to match event names (supports wildcards)
            handler: Function to handle matching events
            subscription_id: ID for the subscription (defaults to a generated ID)
            is_async: Whether the handler is asynchronous
        """
        self.event_pattern = event_pattern
        self.handler = handler
        self.subscription_id = subscription_id or f"sub_{id(self)}"
        self.is_async = is_async

        # Convert the event pattern to a regex pattern
        pattern = (
            event_pattern.replace(".", r"\.").replace("*", r"[^.]+").replace("#", r".+")
        )
        self.pattern = re.compile(f"^{pattern}$")

    def matches(self, event_name: str) -> bool:
        """
        Check if the subscription matches an event name.

        Args:
            event_name: Name of the event

        Returns:
            bool: True if the subscription matches, False otherwise
        """
        return bool(self.pattern.match(event_name))


class EventPublisher:
    """
    Publisher for the event bus.

    This class provides methods for publishing events to the event bus.
    """

    def __init__(self, service_name: str, message_queue_client: MessageQueueClient):
        """
        Initialize the event publisher.

        Args:
            service_name: Name of the service using this publisher
            message_queue_client: Message queue client to use for publishing
        """
        self.service_name = service_name
        self.message_queue_client = message_queue_client

        # Create a message schema for events
        self.event_schema = MessageSchema(Event)

    def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
        """
        Publish an event to the event bus.

        Args:
            event: Event to publish
            routing_key: Routing key for the event (defaults to event.name)

        Returns:
            Event: The published event

        Raises:
            EventPublishError: If the event cannot be published
        """
        try:
            # Use the event name as the routing key if not provided
            if routing_key is None:
                routing_key = f"events.{event.name}"

            # Create a message from the event
            message = self.event_schema.create_message(
                source=self.service_name,
                destination="*",  # Broadcast to all interested services
                subject=event.name,
                payload=event,
                message_type=MessageType.EVENT,
            )

            # Publish the message
            self.message_queue_client.publish(message=message, routing_key=routing_key)

            logger.info(f"Published event {event.name} with ID {event.metadata.id}")

            return event

        except MessageQueueError as e:
            logger.error(f"Failed to publish event {event.name}: {str(e)}")
            raise EventPublishError(f"Failed to publish event: {str(e)}")
        except Exception as e:
            logger.error(f"Error publishing event {event.name}: {str(e)}")
            raise EventPublishError(f"Error publishing event: {str(e)}")


class EventSubscriber:
    """
    Subscriber for the event bus.

    This class provides methods for subscribing to events on the event bus.
    """

    def __init__(self, service_name: str, message_queue_client: MessageQueueClient):
        """
        Initialize the event subscriber.

        Args:
            service_name: Name of the service using this subscriber
            message_queue_client: Message queue client to use for subscribing
        """
        self.service_name = service_name
        self.message_queue_client = message_queue_client

        # Create a message schema for events
        self.event_schema = MessageSchema(Event)

        # Queue name for this service
        self.queue_name = f"{service_name}.events"

        # Subscriptions
        self.subscriptions: Dict[str, EventSubscription] = {}

        # Consumer tag
        self.consumer_tag = None

    def subscribe(
        self,
        event_pattern: str,
        handler: EventHandler,
        subscription_id: Optional[str] = None,
    ) -> EventSubscription:
        """
        Subscribe to events matching a pattern.

        Args:
            event_pattern: Pattern to match event names (supports wildcards)
            handler: Function to handle matching events
            subscription_id: ID for the subscription (defaults to a generated ID)

        Returns:
            EventSubscription: The created subscription

        Raises:
            EventSubscribeError: If the subscription cannot be created
        """
        try:
            # Create a subscription
            subscription = EventSubscription(
                event_pattern=event_pattern,
                handler=handler,
                subscription_id=subscription_id,
            )

            # Store the subscription
            self.subscriptions[subscription.subscription_id] = subscription

            logger.info(
                f"Created subscription {subscription.subscription_id} for pattern {event_pattern}"
            )

            return subscription

        except Exception as e:
            logger.error(
                f"Failed to create subscription for pattern {event_pattern}: {str(e)}"
            )
            raise EventSubscribeError(f"Failed to create subscription: {str(e)}")

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: ID of the subscription to remove

        Returns:
            bool: True if the subscription was removed, False otherwise
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"Removed subscription {subscription_id}")
            return True

        logger.warning(f"Subscription {subscription_id} not found")
        return False

    def start(self) -> str:
        """
        Start consuming events.

        Returns:
            str: The consumer tag

        Raises:
            EventSubscribeError: If consumption cannot be started
        """
        try:
            # Declare a queue for this service
            self.message_queue_client.declare_queue(
                queue_name=self.queue_name, durable=True
            )

            # Bind the queue to the events exchange with a wildcard routing key
            self.message_queue_client.bind_queue(
                queue_name=self.queue_name,
                routing_key="events.#",  # Listen for all events
            )

            # Define the message handler
            def handle_message(message: Message):
                try:
                    # Parse the event
                    event = self.event_schema.parse_message(message)

                    # Find matching subscriptions
                    matching_subscriptions = [
                        subscription
                        for subscription in self.subscriptions.values()
                        if subscription.matches(event.name)
                    ]

                    if not matching_subscriptions:
                        logger.debug(f"No subscriptions match event {event.name}")
                        return

                    # Call the handlers for matching subscriptions
                    for subscription in matching_subscriptions:
                        try:
                            subscription.handler(event)
                        except Exception as e:
                            logger.error(
                                f"Error handling event {event.name} in subscription {subscription.subscription_id}: {str(e)}"
                            )

                except Exception as e:
                    logger.error(f"Error processing event message: {str(e)}")

            # Start consuming
            self.consumer_tag = self.message_queue_client.consume(
                queue_name=self.queue_name, handler=handle_message, auto_ack=True
            )

            logger.info(f"Started consuming events with tag {self.consumer_tag}")

            return self.consumer_tag

        except MessageQueueError as e:
            logger.error(f"Failed to start consuming events: {str(e)}")
            raise EventSubscribeError(f"Failed to start consuming events: {str(e)}")
        except Exception as e:
            logger.error(f"Error starting event consumption: {str(e)}")
            raise EventSubscribeError(f"Error starting event consumption: {str(e)}")

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
    Event bus for event-driven architecture.

    This class provides a unified interface for publishing and subscribing to events.
    """

    def __init__(
        self,
        service_name: str,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        exchange_name: str = "paissive_income",
    ):
        """
        Initialize the event bus.

        Args:
            service_name: Name of the service using this event bus
            host: RabbitMQ host
            port: RabbitMQ port
            username: RabbitMQ username
            password: RabbitMQ password
            virtual_host: RabbitMQ virtual host
            exchange_name: Name of the exchange to use
        """
        self.service_name = service_name

        # Create a message queue client
        self.message_queue_client = MessageQueueClient(
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host,
            service_name=service_name,
            exchange_type="topic",
            exchange_name=exchange_name,
        )

        # Create publisher and subscriber
        self.publisher = EventPublisher(
            service_name=service_name, message_queue_client=self.message_queue_client
        )

        self.subscriber = EventSubscriber(
            service_name=service_name, message_queue_client=self.message_queue_client
        )

    def __del__(self):
        """Clean up resources when the event bus is deleted."""
        self.close()

    def close(self):
        """Close the event bus."""
        self.subscriber.stop()
        self.message_queue_client.close()

    def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
        """
        Publish an event to the event bus.

        Args:
            event: Event to publish
            routing_key: Routing key for the event (defaults to event.name)

        Returns:
            Event: The published event

        Raises:
            EventPublishError: If the event cannot be published
        """
        return self.publisher.publish(event, routing_key)

    def subscribe(
        self,
        event_pattern: str,
        handler: EventHandler,
        subscription_id: Optional[str] = None,
    ) -> EventSubscription:
        """
        Subscribe to events matching a pattern.

        Args:
            event_pattern: Pattern to match event names (supports wildcards)
            handler: Function to handle matching events
            subscription_id: ID for the subscription (defaults to a generated ID)

        Returns:
            EventSubscription: The created subscription

        Raises:
            EventSubscribeError: If the subscription cannot be created
        """
        return self.subscriber.subscribe(event_pattern, handler, subscription_id)

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: ID of the subscription to remove

        Returns:
            bool: True if the subscription was removed, False otherwise
        """
        return self.subscriber.unsubscribe(subscription_id)

    def start(self) -> str:
        """
        Start consuming events.

        Returns:
            str: The consumer tag

        Raises:
            EventSubscribeError: If consumption cannot be started
        """
        return self.subscriber.start()

    def stop(self):
        """Stop consuming events."""
        self.subscriber.stop()


class AsyncEventBus:
    """
    Asynchronous event bus for event-driven architecture.

    This class provides a unified interface for publishing and subscribing to events asynchronously.
    """

    def __init__(
        self,
        service_name: str,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        exchange_name: str = "paissive_income",
    ):
        """
        Initialize the asynchronous event bus.

        Args:
            service_name: Name of the service using this event bus
            host: RabbitMQ host
            port: RabbitMQ port
            username: RabbitMQ username
            password: RabbitMQ password
            virtual_host: RabbitMQ virtual host
            exchange_name: Name of the exchange to use
        """
        self.service_name = service_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.exchange_name = exchange_name

        # Message queue client
        self.message_queue_client = None

        # Subscriptions
        self.subscriptions: Dict[str, EventSubscription] = {}

        # Consumer tag
        self.consumer_tag = None

        # Event schema
        self.event_schema = MessageSchema(Event)

    async def __aenter__(self):
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        await self.close()

    async def connect(self):
        """
        Connect to the message queue asynchronously.

        Raises:
            EventBusError: If the connection fails
        """
        # Create a message queue client
        self.message_queue_client = AsyncMessageQueueClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            virtual_host=self.virtual_host,
            service_name=self.service_name,
            exchange_type="topic",
            exchange_name=self.exchange_name,
        )

        await self.message_queue_client.connect()

    async def close(self):
        """Close the event bus asynchronously."""
        if self.consumer_tag:
            await self.stop()

        if self.message_queue_client:
            await self.message_queue_client.close()

    async def publish(self, event: Event, routing_key: Optional[str] = None) -> Event:
        """
        Publish an event to the event bus asynchronously.

        Args:
            event: Event to publish
            routing_key: Routing key for the event (defaults to event.name)

        Returns:
            Event: The published event

        Raises:
            EventPublishError: If the event cannot be published
        """
        try:
            # Use the event name as the routing key if not provided
            if routing_key is None:
                routing_key = f"events.{event.name}"

            # Create a message from the event
            message = self.event_schema.create_message(
                source=self.service_name,
                destination="*",  # Broadcast to all interested services
                subject=event.name,
                payload=event,
                message_type=MessageType.EVENT,
            )

            # Publish the message
            await self.message_queue_client.publish(
                message=message, routing_key=routing_key
            )

            logger.info(f"Published event {event.name} with ID {event.metadata.id}")

            return event

        except MessageQueueError as e:
            logger.error(f"Failed to publish event {event.name}: {str(e)}")
            raise EventPublishError(f"Failed to publish event: {str(e)}")
        except Exception as e:
            logger.error(f"Error publishing event {event.name}: {str(e)}")
            raise EventPublishError(f"Error publishing event: {str(e)}")

    async def subscribe(
        self,
        event_pattern: str,
        handler: AsyncEventHandler,
        subscription_id: Optional[str] = None,
    ) -> EventSubscription:
        """
        Subscribe to events matching a pattern asynchronously.

        Args:
            event_pattern: Pattern to match event names (supports wildcards)
            handler: Async function to handle matching events
            subscription_id: ID for the subscription (defaults to a generated ID)

        Returns:
            EventSubscription: The created subscription

        Raises:
            EventSubscribeError: If the subscription cannot be created
        """
        try:
            # Create a subscription
            subscription = EventSubscription(
                event_pattern=event_pattern,
                handler=handler,
                subscription_id=subscription_id,
                is_async=True,
            )

            # Store the subscription
            self.subscriptions[subscription.subscription_id] = subscription

            logger.info(
                f"Created subscription {subscription.subscription_id} for pattern {event_pattern}"
            )

            return subscription

        except Exception as e:
            logger.error(
                f"Failed to create subscription for pattern {event_pattern}: {str(e)}"
            )
            raise EventSubscribeError(f"Failed to create subscription: {str(e)}")

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: ID of the subscription to remove

        Returns:
            bool: True if the subscription was removed, False otherwise
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"Removed subscription {subscription_id}")
            return True

        logger.warning(f"Subscription {subscription_id} not found")
        return False

    async def start(self) -> str:
        """
        Start consuming events asynchronously.

        Returns:
            str: The consumer tag

        Raises:
            EventSubscribeError: If consumption cannot be started
        """
        try:
            # Declare a queue for this service
            queue = await self.message_queue_client.declare_queue(
                queue_name=f"{self.service_name}.events", durable=True
            )

            # Bind the queue to the events exchange with a wildcard routing key
            await self.message_queue_client.bind_queue(
                queue=queue, routing_key="events.#"  # Listen for all events
            )

            # Define the message handler
            async def handle_message(message: Message):
                try:
                    # Parse the event
                    event = self.event_schema.parse_message(message)

                    # Find matching subscriptions
                    matching_subscriptions = [
                        subscription
                        for subscription in self.subscriptions.values()
                        if subscription.matches(event.name)
                    ]

                    if not matching_subscriptions:
                        logger.debug(f"No subscriptions match event {event.name}")
                        return

                    # Call the handlers for matching subscriptions
                    for subscription in matching_subscriptions:
                        try:
                            if subscription.is_async:
                                await subscription.handler(event)
                            else:
                                subscription.handler(event)
                        except Exception as e:
                            logger.error(
                                f"Error handling event {event.name} in subscription {subscription.subscription_id}: {str(e)}"
                            )

                except Exception as e:
                    logger.error(f"Error processing event message: {str(e)}")

            # Start consuming
            self.consumer_tag = await self.message_queue_client.consume(
                queue_name=queue.name, handler=handle_message, auto_ack=True
            )

            logger.info(f"Started consuming events with tag {self.consumer_tag}")

            return self.consumer_tag

        except MessageQueueError as e:
            logger.error(f"Failed to start consuming events: {str(e)}")
            raise EventSubscribeError(f"Failed to start consuming events: {str(e)}")
        except Exception as e:
            logger.error(f"Error starting event consumption: {str(e)}")
            raise EventSubscribeError(f"Error starting event consumption: {str(e)}")

    async def stop(self):
        """Stop consuming events asynchronously."""
        if self.consumer_tag and self.message_queue_client:
            try:
                await self.message_queue_client.stop_consuming(self.consumer_tag)
                self.consumer_tag = None
                logger.info("Stopped consuming events")
            except Exception as e:
                logger.warning(f"Error stopping event consumption: {str(e)}")
