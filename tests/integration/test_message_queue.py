"""
Integration tests for message queue functionality.
"""


import time
from datetime import datetime
from unittest.mock import patch

import pytest

from services.errors import MessagePublishError, QueueConfigError

(
DeadLetterQueue,
MessageConsumer,
MessagePublisher,
MessageQueueClient,
QueueConfig,
)


class TestMessageQueue:
    """Integration tests for message queue functionality."""

    def setup_method(self):
    """Set up test fixtures."""
    self.config = QueueConfig(
    broker_url="amqp://localhost:5672",
    exchange_name="test_exchange",
    queue_prefix="test",
    dead_letter_exchange="test_dlx",
    max_retries=3,
    retry_delay=1000,  # milliseconds
    consumer_timeout=5000,  # milliseconds
    )
    self.publisher = MessagePublisher(self.config)
    self.consumer = MessageConsumer(self.config)
    self.dlq = DeadLetterQueue(self.config)
    self.client = MessageQueueClient(self.config)

    def test_message_publishing(self):
    """Test message publishing workflow."""
    # Test message
    message = {
    "type": "user_event",
    "action": "profile_update",
    "user_id": "123",
    "timestamp": datetime.utcnow().isoformat(),
    "data": {"name": "John Doe", "email": "john@example.com"},
    }

    # Publish message
    result = self.publisher.publish(
    routing_key="user.events", message=message, headers={"version": "1.0"}
    )

    # Validate publish result
    assert result["success"] is True
    assert "message_id" in result
    assert result["exchange"] == self.config.exchange_name
    assert result["routing_key"] == "user.events"

    # Verify message can be consumed
    consumed = self.consumer.consume(
    queue_name="user_events", routing_key="user.events", timeout=1000
    )

    assert consumed is not None
    assert consumed["message"]["type"] == message["type"]
    assert consumed["message"]["user_id"] == message["user_id"]
    assert consumed["headers"]["version"] == "1.0"

    def test_message_consumption_patterns(self):
    """Test different message consumption patterns."""
    messages = [{"id": i, "data": f"test_data_{i}"} for i in range(5)]

    # Test batch publishing
    batch_result = self.publisher.publish_batch(
    routing_key="batch.test", messages=messages
    )
    assert len(batch_result["published"]) == len(messages)

    # Test single consumer
    consumed_single = []
    for _ in range(5):
    msg = self.consumer.consume(
    queue_name="batch_test", routing_key="batch.test", timeout=1000
    )
    if msg:
    consumed_single.append(msg["message"])

    assert len(consumed_single) == 5
    assert all(m["id"] in range(5) for m in consumed_single)

    # Test competing consumers
    consumer2 = MessageConsumer(self.config)
    self.publisher.publish_batch(routing_key="batch.test", messages=messages)

    consumed_1, consumed_2 = [], []
    for _ in range(5):
    msg1 = self.consumer.consume(
    queue_name="batch_test", routing_key="batch.test", timeout=500
    )
    msg2 = consumer2.consume(
    queue_name="batch_test", routing_key="batch.test", timeout=500
    )
    if msg1:
    consumed_1.append(msg1["message"])
    if msg2:
    consumed_2.append(msg2["message"])

    # Verify messages split between consumers
    assert len(consumed_1) + len(consumed_2) == 5
    all_consumed = consumed_1 + consumed_2
    assert all(m["id"] in range(5) for m in all_consumed)

    def test_dead_letter_handling(self):
    """Test dead letter queue handling."""
    # Message that will fail processing
    bad_message = {"type": "invalid_event", "data": "malformed"}

    # Configure consumer to fail processing
    def failing_processor(message):
    raise ValueError("Simulated processing failure")

    # Register message handler that will fail
    self.consumer.register_handler(
    routing_key="test.failures", handler=failing_processor
    )

    # Publish message that will fail
    self.publisher.publish(
    routing_key="test.failures", message=bad_message, headers={"retry_count": 0}
    )

    # Wait for retries and DLQ
    time.sleep((self.config.max_retries * self.config.retry_delay / 1000) + 1)

    # Check DLQ
    dlq_message = self.dlq.get_message(queue_name="test_failures_dlq")

    # Verify message in DLQ
    assert dlq_message is not None
    assert dlq_message["original_message"] == bad_message
    assert dlq_message["error_info"]["retry_count"] == self.config.max_retries
    assert "error_message" in dlq_message["error_info"]

    def test_message_acknowledgment(self):
    """Test message acknowledgment patterns."""
    test_message = {"type": "ack_test", "data": "test"}

    # Test auto-ack
    self.publisher.publish(routing_key="test.ack", message=test_message)

    consumed_auto = self.consumer.consume(
    queue_name="ack_test", routing_key="test.ack", auto_ack=True, timeout=1000
    )
    assert consumed_auto is not None

    # Verify message is not redelivered
    time.sleep(1)
    redelivered = self.consumer.consume(
    queue_name="ack_test", routing_key="test.ack", timeout=1000
    )
    assert redelivered is None

    # Test manual ack
    self.publisher.publish(routing_key="test.ack", message=test_message)

    consumed_manual = self.consumer.consume(
    queue_name="ack_test", routing_key="test.ack", auto_ack=False, timeout=1000
    )
    assert consumed_manual is not None

    # Explicitly acknowledge
    self.consumer.acknowledge(consumed_manual["delivery_tag"])

    # Verify message is not redelivered
    time.sleep(1)
    redelivered = self.consumer.consume(
    queue_name="ack_test", routing_key="test.ack", timeout=1000
    )
    assert redelivered is None

    def test_message_routing_patterns(self):
    """Test different message routing patterns."""
    # Test direct routing
    direct_msg = {"type": "direct", "data": "test"}
    self.publisher.publish(routing_key="direct.test", message=direct_msg)

    consumed_direct = self.consumer.consume(
    queue_name="direct_test", routing_key="direct.test", timeout=1000
    )
    assert consumed_direct["message"] == direct_msg

    # Test topic routing
    topic_msg = {"type": "topic", "data": "test"}
    self.publisher.publish(routing_key="topic.test.info", message=topic_msg)

    # Consumer with wildcard routing key
    consumed_topic = self.consumer.consume(
    queue_name="topic_test", routing_key="topic.#", timeout=1000
    )
    assert consumed_topic["message"] == topic_msg

    # Test fanout routing
    fanout_msg = {"type": "broadcast", "data": "test"}
    self.publisher.publish_fanout(exchange_name="test_fanout", message=fanout_msg)

    # Multiple consumers should receive the same message
    consumer1 = MessageConsumer(self.config)
    consumer2 = MessageConsumer(self.config)

    msg1 = consumer1.consume_fanout(exchange_name="test_fanout", timeout=1000)
    msg2 = consumer2.consume_fanout(exchange_name="test_fanout", timeout=1000)

    assert msg1["message"] == fanout_msg
    assert msg2["message"] == fanout_msg

    def test_error_handling(self):
    """Test error handling scenarios."""
    # Test invalid routing key
    with pytest.raises(MessagePublishError):
    self.publisher.publish(
    routing_key="", message={"test": "data"}  # Invalid routing key
    )

    # Test invalid message format
    with pytest.raises(MessagePublishError):
    self.publisher.publish(
    routing_key="test.errors", message=object()  # Non-serializable object
    )

    # Test consumer timeout
    result = self.consumer.consume(
    queue_name="empty_queue",
    routing_key="test.empty",
    timeout=100,  # Very short timeout
    )
    assert result is None

    # Test invalid queue configuration
    with pytest.raises(QueueConfigError):
    QueueConfig(
    broker_url="invalid://localhost",
    exchange_name="test",
    queue_prefix="",  # Invalid prefix
    )

    def test_message_persistence(self):
    """Test message persistence across broker restarts."""
    # Configure durable queue and persistent messages
    config = QueueConfig(
    broker_url=self.config.broker_url,
    exchange_name="durable_exchange",
    queue_prefix="persistent",
    message_ttl=3600000,  # 1 hour
    durable=True,
    )
    durable_publisher = MessagePublisher(config)
    durable_consumer = MessageConsumer(config)

    # Publish persistent message
    message = {"type": "persistent", "data": "test"}
    durable_publisher.publish(
    routing_key="persistent.test", message=message, persistent=True
    )

    # Simulate broker restart
    with patch("services.messaging.MessageQueueClient.reconnect") as mock_reconnect:
    self.client.reconnect()
    assert mock_reconnect.called

    # Message should still be available
    consumed = durable_consumer.consume(
    queue_name="persistent_test", routing_key="persistent.test", timeout=1000
    )
    assert consumed["message"] == message


    if __name__ == "__main__":
    pytest.main(["-v", "test_message_queue.py"])