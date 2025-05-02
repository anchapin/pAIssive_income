"""
Integration tests for message queue integration with other services.

This module contains integration tests for the message queue service
and its integration with other microservices.
"""

import threading
import time
from datetime import datetime

import pytest

from services.messaging import (
    DeadLetterQueue,
    MessageConsumer,
    MessagePublisher,
    MessageQueueClient,
    QueueConfig,
)


class TestMessageQueueIntegration:
    """Integration tests for message queue integration with other services."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = QueueConfig(
            broker_url="amqp://localhost:5672",
            exchange_name="test_integration_exchange",
            queue_prefix="test_integration",
            dead_letter_exchange="test_integration_dlx",
            max_retries=3,
            retry_delay=1000,  # milliseconds
            consumer_timeout=5000,  # milliseconds
        )
        self.publisher = MessagePublisher(self.config)
        self.consumer = MessageConsumer(self.config)
        self.dlq = DeadLetterQueue(self.config)
        self.client = MessageQueueClient(self.config)

    def test_service_communication(self):
        """Test communication between services using message queue."""
        # Define test services
        services = ["auth-service", "user-service", "order-service"]

        # Create a consumer for each service
        consumers = {service: MessageConsumer(self.config) for service in services}

        # Create a publisher for each service
        publishers = {service: MessagePublisher(self.config) for service in services}

        # Track received messages
        received_messages = {service: [] for service in services}

        # Define message handlers for each service
        def create_handler(service_name):
            def handler(message, headers):
                received_messages[service_name].append(
                    {"message": message, "headers": headers}
                )
                return True

            return handler

        # Register handlers
        for service in services:
            consumers[service].register_handler(
                routing_key=f"{service}.events", handler=create_handler(service)
            )

        # Start consumers in separate threads
        consumer_threads = {}
        for service in services:
            thread = threading.Thread(
                target=consumers[service].start_consuming,
                kwargs={
                    "queue_name": f"{service}_events",
                    "routing_keys": [f"{service}.events"],
                    "timeout": 1000,
                },
            )
            thread.daemon = True
            thread.start()
            consumer_threads[service] = thread

        # Allow consumers to start
        time.sleep(1)

        # Send test messages between services
        test_messages = [
            {
                "from": "auth-service",
                "to": "user-service",
                "routing_key": "user-service.events",
                "message": {
                    "type": "user_authenticated",
                    "user_id": "123",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
            {
                "from": "user-service",
                "to": "order-service",
                "routing_key": "order-service.events",
                "message": {
                    "type": "user_updated",
                    "user_id": "123",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
            {
                "from": "order-service",
                "to": "auth-service",
                "routing_key": "auth-service.events",
                "message": {
                    "type": "order_created",
                    "order_id": "456",
                    "user_id": "123",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        ]

        # Publish messages
        for msg in test_messages:
            publishers[msg["from"]].publish(
                routing_key=msg["routing_key"],
                message=msg["message"],
                headers={"source": msg["from"]},
            )

        # Wait for messages to be processed
        time.sleep(2)

        # Stop consumers
        for service in services:
            consumers[service].stop_consuming()
            consumer_threads[service].join(timeout=1)

        # Verify messages were received
        for msg in test_messages:
            target_service = msg["to"]
            assert any(
                received["message"]["type"] == msg["message"]["type"]
                for received in received_messages[target_service]
            )

            # Verify headers
            matching_messages = [
                received
                for received in received_messages[target_service]
                if received["message"]["type"] == msg["message"]["type"]
            ]
            assert len(matching_messages) > 0
            assert matching_messages[0]["headers"]["source"] == msg["from"]

    def test_event_driven_workflow(self):
        """Test event-driven workflow across multiple services."""
        # Define workflow steps
        workflow = [
            {
                "service": "user-service",
                "event": "user_registered",
                "data": {"user_id": "789", "email": "user@example.com"},
            },
            {
                "service": "email-service",
                "event": "welcome_email_sent",
                "data": {"user_id": "789", "email_id": "welcome-123"},
            },
            {
                "service": "auth-service",
                "event": "user_activated",
                "data": {"user_id": "789", "status": "active"},
            },
        ]

        # Track workflow state
        workflow_state = {"completed_steps": [], "current_step": 0}

        # Create publishers and consumers
        publishers = {}
        consumers = {}

        for step in workflow:
            service = step["service"]
            if service not in publishers:
                publishers[service] = MessagePublisher(self.config)
                consumers[service] = MessageConsumer(self.config)

        # Define handlers for each service
        def create_workflow_handler(service_name, next_step_index):
            def handler(message, headers):
                # Record step completion
                current_step = workflow[workflow_state["current_step"]]
                workflow_state["completed_steps"].append(current_step["event"])

                # Move to next step if available
                if next_step_index < len(workflow):
                    workflow_state["current_step"] = next_step_index
                    next_step = workflow[next_step_index]

                    # Publish event for next step
                    publishers[next_step["service"]].publish(
                        routing_key=f"{next_step['service']}.events",
                        message={
                            "type": next_step["event"],
                            "data": next_step["data"],
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        headers={
                            "workflow_id": headers.get("workflow_id", "test-workflow"),
                            "step": next_step_index,
                        },
                    )

                return True

            return handler

        # Register handlers
        for i, step in enumerate(workflow):
            service = step["service"]
            next_step = i + 1
            consumers[service].register_handler(
                routing_key=f"{service}.events",
                handler=create_workflow_handler(service, next_step),
            )

        # Start consumers in separate threads
        consumer_threads = {}
        for service in consumers:
            thread = threading.Thread(
                target=consumers[service].start_consuming,
                kwargs={
                    "queue_name": f"{service}_workflow_events",
                    "routing_keys": [f"{service}.events"],
                    "timeout": 1000,
                },
            )
            thread.daemon = True
            thread.start()
            consumer_threads[service] = thread

        # Allow consumers to start
        time.sleep(1)

        # Start the workflow by publishing the first event
        first_step = workflow[0]
        publishers[first_step["service"]].publish(
            routing_key=f"{first_step['service']}.events",
            message={
                "type": first_step["event"],
                "data": first_step["data"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            headers={"workflow_id": "test-workflow", "step": 0},
        )

        # Wait for workflow to complete
        time.sleep(3)

        # Stop consumers
        for service in consumers:
            consumers[service].stop_consuming()
            consumer_threads[service].join(timeout=1)

        # Verify all workflow steps were completed
        assert len(workflow_state["completed_steps"]) == len(workflow)
        for step in workflow:
            assert step["event"] in workflow_state["completed_steps"]

    def test_message_routing_patterns(self):
        """Test different message routing patterns."""
        # Test topic-based routing
        topic_handlers = {
            "user.created": [],
            "user.updated": [],
            "user.deleted": [],
            "order.created": [],
            "order.updated": [],
            "order.deleted": [],
        }

        # Create consumers with different routing patterns
        user_consumer = MessageConsumer(self.config)
        order_consumer = MessageConsumer(self.config)
        all_consumer = MessageConsumer(self.config)

        # Define handlers
        def create_topic_handler(topic):
            def handler(message, headers):
                topic_handlers[topic].append({"message": message, "headers": headers})
                return True

            return handler

        # Register handlers with different routing patterns
        for topic in topic_handlers:
            if topic.startswith("user."):
                user_consumer.register_handler(
                    routing_key=topic, handler=create_topic_handler(topic)
                )
            elif topic.startswith("order."):
                order_consumer.register_handler(
                    routing_key=topic, handler=create_topic_handler(topic)
                )

            # All consumer listens to everything
            all_consumer.register_handler(
                routing_key="#",  # Wildcard for all topics
                handler=create_topic_handler(topic),
            )

        # Start consumers in separate threads
        user_thread = threading.Thread(
            target=user_consumer.start_consuming,
            kwargs={
                "queue_name": "user_events",
                "routing_keys": ["user.#"],
                "timeout": 1000,
            },
        )
        user_thread.daemon = True
        user_thread.start()

        order_thread = threading.Thread(
            target=order_consumer.start_consuming,
            kwargs={
                "queue_name": "order_events",
                "routing_keys": ["order.#"],
                "timeout": 1000,
            },
        )
        order_thread.daemon = True
        order_thread.start()

        all_thread = threading.Thread(
            target=all_consumer.start_consuming,
            kwargs={"queue_name": "all_events", "routing_keys": ["#"], "timeout": 1000},
        )
        all_thread.daemon = True
        all_thread.start()

        # Allow consumers to start
        time.sleep(1)

        # Publish test messages
        publisher = MessagePublisher(self.config)
        test_topics = list(topic_handlers.keys())

        for topic in test_topics:
            publisher.publish(
                routing_key=topic,
                message={"type": topic, "timestamp": datetime.utcnow().isoformat()},
                headers={"topic": topic},
            )

        # Wait for messages to be processed
        time.sleep(2)

        # Stop consumers
        user_consumer.stop_consuming()
        order_consumer.stop_consuming()
        all_consumer.stop_consuming()

        user_thread.join(timeout=1)
        order_thread.join(timeout=1)
        all_thread.join(timeout=1)

        # Verify routing
        # User consumer should only receive user events
        user_topics = [topic for topic in test_topics if topic.startswith("user.")]
        for topic in user_topics:
            assert len(topic_handlers[topic]) >= 1

        # Order consumer should only receive order events
        order_topics = [topic for topic in test_topics if topic.startswith("order.")]
        for topic in order_topics:
            assert len(topic_handlers[topic]) >= 1

        # All consumer should receive all events
        for topic in test_topics:
            assert len(topic_handlers[topic]) >= 1


if __name__ == "__main__":
    pytest.main(["-v", "test_message_queue_integration.py"])
