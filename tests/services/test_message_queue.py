"""
Tests for message queue functionality.

This module contains tests for the message queue implementation.
"""


import json
import time
from unittest.mock import MagicMock, patch

import pytest

from services.shared.message_queue.message import Message, MessagePriority
from services.shared.message_queue.queue_client import MessageQueueClient
from services.shared.message_queue.queue_config import QueueConfig


class TestMessageQueue:

    pass  # Added missing block
    """Tests for message queue functionality."""

    @patch("pika.BlockingConnection")
    @patch("pika.ConnectionParameters")
    def test_queue_connection(self, mock_connection_params, mock_connection):
    """Test connecting to the message queue."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    virtual_host="/",
    )

    client = MessageQueueClient(config)

    # Verify connection was established
    mock_connection_params.assert_called_once_with(
    host="localhost",
    port=5672,
    virtual_host="/",
    credentials=pytest.approx(any),
    )
    mock_connection.assert_called_once()
    mock_connection.return_value.channel.assert_called_once()

    # Verify channel was created
    assert client._channel == mock_channel

    @patch("pika.BlockingConnection")
    def test_queue_declaration(self, mock_connection):
    """Test declaring a queue."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Declare a queue
    client.declare_queue("test-queue", durable=True, auto_delete=False)

    # Verify queue was declared
    mock_channel.queue_declare.assert_called_once_with(
    queue="test-queue", durable=True, auto_delete=False
    )

    @patch("pika.BlockingConnection")
    def test_exchange_declaration(self, mock_connection):
    """Test declaring an exchange."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Declare an exchange
    client.declare_exchange("test-exchange", exchange_type="topic")

    # Verify exchange was declared
    mock_channel.exchange_declare.assert_called_once_with(
    exchange="test-exchange", exchange_type="topic", durable=True
    )

    @patch("pika.BlockingConnection")
    def test_queue_binding(self, mock_connection):
    """Test binding a queue to an exchange."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Bind queue to exchange
    client.bind_queue("test-queue", "test-exchange", "test.routing.key")

    # Verify queue was bound
    mock_channel.queue_bind.assert_called_once_with(
    queue="test-queue", exchange="test-exchange", routing_key="test.routing.key"
    )

    @patch("pika.BlockingConnection")
    def test_message_publishing(self, mock_connection):
    """Test publishing a message."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Create a message
    message = Message(
    body={"key": "value"},
    message_type="test-type",
    correlation_id="test-correlation-id",
    priority=MessagePriority.HIGH,
    )

    # Publish message
    client.publish_message("test-exchange", "test.routing.key", message)

    # Verify message was published
    mock_channel.basic_publish.assert_called_once()

    # Verify publish parameters
    call_args = mock_channel.basic_publish.call_args[1]
    assert call_args["exchange"] == "test-exchange"
    assert call_args["routing_key"] == "test.routing.key"

    # Verify message properties
    properties = call_args["properties"]
    assert properties.content_type == "application/json"
    assert properties.correlation_id == "test-correlation-id"
    assert properties.priority == MessagePriority.HIGH.value

    # Verify message body
    body = call_args["body"]
    decoded_body = json.loads(body)
    assert decoded_body["key"] == "value"
    assert decoded_body["_metadata"]["message_type"] == "test-type"

    @patch("pika.BlockingConnection")
    def test_message_consuming(self, mock_connection):
    """Test consuming messages."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Define callback function
    callback_called = False
    received_message = None

    def callback(message):
    nonlocal callback_called, received_message
    callback_called = True
    received_message = message
    return True

    # Start consuming
    client.consume("test-queue", callback)

    # Verify consumer was started
    mock_channel.basic_consume.assert_called_once()

    # Verify consumer parameters
    call_args = mock_channel.basic_consume.call_args[1]
    assert call_args["queue"] == "test-queue"
    assert callable(call_args["on_message_callback"])

    # Simulate message delivery
    method = MagicMock()
    method.delivery_tag = "test-tag"

    properties = MagicMock()
    properties.correlation_id = "test-correlation-id"
    properties.priority = MessagePriority.HIGH.value

    body = json.dumps(
    {
    "key": "value",
    "_metadata": {"message_type": "test-type", "timestamp": time.time()},
    }
    ).encode()

    # Call the callback function
    call_args["on_message_callback"](mock_channel, method, properties, body)

    # Verify our callback was called
    assert callback_called
    assert received_message is not None
    assert received_message.body["key"] == "value"
    assert received_message.message_type == "test-type"
    assert received_message.correlation_id == "test-correlation-id"
    assert received_message.priority == MessagePriority.HIGH

    # Verify message was acknowledged
    mock_channel.basic_ack.assert_called_once_with(delivery_tag="test-tag")

    @patch("pika.BlockingConnection")
    def test_message_rejection(self, mock_connection):
    """Test rejecting a message."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Define callback function that rejects the message
    def callback(message):
    return False

    # Start consuming
    client.consume("test-queue", callback)

    # Simulate message delivery
    method = MagicMock()
    method.delivery_tag = "test-tag"

    properties = MagicMock()
    body = json.dumps({"key": "value"}).encode()

    # Call the callback function
    mock_channel.basic_consume.call_args[1]["on_message_callback"](
    mock_channel, method, properties, body
    )

    # Verify message was rejected
    mock_channel.basic_nack.assert_called_once_with(
    delivery_tag="test-tag", requeue=True
    )

    @patch("pika.BlockingConnection")
    def test_dead_letter_queue(self, mock_connection):
    """Test dead letter queue configuration."""
    # Configure mocks
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    # Create queue client
    config = QueueConfig(
    host="localhost", port=5672, username="guest", password="guest"
    )

    client = MessageQueueClient(config)

    # Declare queue with dead letter exchange
    client.declare_queue(
    "test-queue",
    durable=True,
    arguments={
    "x-dead-letter-exchange": "dead-letter-exchange",
    "x-dead-letter-routing-key": "dead-letter",
    },
    )

    # Verify queue was declared with dead letter arguments
    mock_channel.queue_declare.assert_called_once()
    call_args = mock_channel.queue_declare.call_args[1]
    assert call_args["queue"] == "test-queue"
    assert call_args["durable"] is True
    assert "x-dead-letter-exchange" in call_args["arguments"]
    assert (
    call_args["arguments"]["x-dead-letter-exchange"] == "dead-letter-exchange"
    )
    assert call_args["arguments"]["x-dead-letter-routing-key"] == "dead-letter"

    @patch("pika.BlockingConnection")
    def test_connection_error_handling(self, mock_connection):
    """Test handling connection errors."""
    # Configure mocks to raise an exception
    mock_connection.side_effect = Exception("Connection error")

    # Create queue client
    config = QueueConfig(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    connection_attempts=3,
    retry_delay=0.1,
    )

    # Verify connection error is handled
    with pytest.raises(Exception) as excinfo:
    MessageQueueClient(config)

    assert "Connection error" in str(excinfo.value)
    assert mock_connection.call_count == 3  # Should retry 3 times


    if __name__ == "__main__":
    pytest.main(["-v", "test_message_queue.py"])