"""
"""
Message queue client for pAIssive income microservices.
Message queue client for pAIssive income microservices.


This module provides a client for interacting with the message queue (RabbitMQ).
This module provides a client for interacting with the message queue (RabbitMQ).
"""
"""




import asyncio
import asyncio
import json
import json
import logging
import logging
import threading
import threading
import time
import time
import uuid
import uuid
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union


import aio_pika
import aio_pika
import pika
import pika
from pika.exceptions import AMQPError
from pika.exceptions import AMQPError


from .exceptions import ConnectionError, ConsumeError, PublishError
from .exceptions import ConnectionError, ConsumeError, PublishError
from .message import Message, MessageStatus
from .message import Message, MessageStatus


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


# Type for message handlers
# Type for message handlers
MessageHandler = Callable[[Message], None]
MessageHandler = Callable[[Message], None]
AsyncMessageHandler = Callable[[Message], Union[None, asyncio.Future]]
AsyncMessageHandler = Callable[[Message], Union[None, asyncio.Future]]


# Type variable for generic return types
# Type variable for generic return types
T = TypeVar("T")
T = TypeVar("T")




class MessageQueueClient:
    class MessageQueueClient:
    """
    """
    Client for interacting with the message queue (RabbitMQ).
    Client for interacting with the message queue (RabbitMQ).


    This client provides methods for publishing and consuming messages.
    This client provides methods for publishing and consuming messages.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
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
    service_name: str = "unknown",
    service_name: str = "unknown",
    exchange_type: str = "topic",
    exchange_type: str = "topic",
    exchange_name: str = "paissive_income",
    exchange_name: str = "paissive_income",
    connection_attempts: int = 3,
    connection_attempts: int = 3,
    retry_delay: int = 5,
    retry_delay: int = 5,
    heartbeat: int = 60,
    heartbeat: int = 60,
    ):
    ):
    """
    """
    Initialize the message queue client.
    Initialize the message queue client.


    Args:
    Args:
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
    service_name: Name of the service using this client
    service_name: Name of the service using this client
    exchange_type: Type of exchange to use (topic, direct, fanout, headers)
    exchange_type: Type of exchange to use (topic, direct, fanout, headers)
    exchange_name: Name of the exchange to use
    exchange_name: Name of the exchange to use
    connection_attempts: Number of connection attempts
    connection_attempts: Number of connection attempts
    retry_delay: Delay between connection attempts in seconds
    retry_delay: Delay between connection attempts in seconds
    heartbeat: Heartbeat interval in seconds
    heartbeat: Heartbeat interval in seconds
    """
    """
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
    self.service_name = service_name
    self.service_name = service_name
    self.exchange_type = exchange_type
    self.exchange_type = exchange_type
    self.exchange_name = exchange_name
    self.exchange_name = exchange_name
    self.connection_attempts = connection_attempts
    self.connection_attempts = connection_attempts
    self.retry_delay = retry_delay
    self.retry_delay = retry_delay
    self.heartbeat = heartbeat
    self.heartbeat = heartbeat


    # Connection and channel
    # Connection and channel
    self.connection = None
    self.connection = None
    self.channel = None
    self.channel = None


    # Consumer threads
    # Consumer threads
    self.consumer_threads = {}
    self.consumer_threads = {}


    # Connect to RabbitMQ
    # Connect to RabbitMQ
    self.connect()
    self.connect()


    def __del__(self):
    def __del__(self):
    """Clean up resources when the client is deleted."""
    self.close()

    def connect(self):
    """
    """
    Connect to RabbitMQ.
    Connect to RabbitMQ.


    Raises:
    Raises:
    ConnectionError: If the connection fails
    ConnectionError: If the connection fails
    """
    """
    try:
    try:
    # Create connection parameters
    # Create connection parameters
    credentials = pika.PlainCredentials(self.username, self.password)
    credentials = pika.PlainCredentials(self.username, self.password)
    parameters = pika.ConnectionParameters(
    parameters = pika.ConnectionParameters(
    host=self.host,
    host=self.host,
    port=self.port,
    port=self.port,
    virtual_host=self.virtual_host,
    virtual_host=self.virtual_host,
    credentials=credentials,
    credentials=credentials,
    connection_attempts=self.connection_attempts,
    connection_attempts=self.connection_attempts,
    retry_delay=self.retry_delay,
    retry_delay=self.retry_delay,
    heartbeat=self.heartbeat,
    heartbeat=self.heartbeat,
    )
    )


    # Connect to RabbitMQ
    # Connect to RabbitMQ
    self.connection = pika.BlockingConnection(parameters)
    self.connection = pika.BlockingConnection(parameters)


    # Create a channel
    # Create a channel
    self.channel = self.connection.channel()
    self.channel = self.connection.channel()


    # Declare the exchange
    # Declare the exchange
    self.channel.exchange_declare(
    self.channel.exchange_declare(
    exchange=self.exchange_name,
    exchange=self.exchange_name,
    exchange_type=self.exchange_type,
    exchange_type=self.exchange_type,
    durable=True,
    durable=True,
    )
    )


    logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
    logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")


except AMQPError as e:
except AMQPError as e:
    logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
    logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
    raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")
    raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")


    def close(self):
    def close(self):
    """Close the connection to RabbitMQ."""
    # Stop all consumer threads
    for thread in self.consumer_threads.values():
    thread.join(timeout=1.0)

    # Close the channel and connection
    if self.channel is not None and self.channel.is_open:
    self.channel.close()

    if self.connection is not None and self.connection.is_open:
    self.connection.close()

    logger.info("Disconnected from RabbitMQ")

    def reconnect(self):
    """
    """
    Reconnect to RabbitMQ.
    Reconnect to RabbitMQ.


    Raises:
    Raises:
    ConnectionError: If the reconnection fails
    ConnectionError: If the reconnection fails
    """
    """
    # Close the existing connection
    # Close the existing connection
    self.close()
    self.close()


    # Connect again
    # Connect again
    self.connect()
    self.connect()


    def publish(
    def publish(
    self,
    self,
    message: Message,
    message: Message,
    routing_key: Optional[str] = None,
    routing_key: Optional[str] = None,
    mandatory: bool = True,
    mandatory: bool = True,
    persistent: bool = True,
    persistent: bool = True,
    ) -> Message:
    ) -> Message:
    """
    """
    Publish a message to the message queue.
    Publish a message to the message queue.


    Args:
    Args:
    message: Message to publish
    message: Message to publish
    routing_key: Routing key for the message (defaults to message.subject)
    routing_key: Routing key for the message (defaults to message.subject)
    mandatory: Whether the message must be routed to a queue
    mandatory: Whether the message must be routed to a queue
    persistent: Whether the message should be persistent
    persistent: Whether the message should be persistent


    Returns:
    Returns:
    Message: The published message with updated status
    Message: The published message with updated status


    Raises:
    Raises:
    PublishError: If the message cannot be published
    PublishError: If the message cannot be published
    """
    """
    try:
    try:
    # Use the message subject as the routing key if not provided
    # Use the message subject as the routing key if not provided
    if routing_key is None:
    if routing_key is None:
    routing_key = message.subject
    routing_key = message.subject


    # Set message status to PUBLISHED
    # Set message status to PUBLISHED
    message.status = MessageStatus.PUBLISHED
    message.status = MessageStatus.PUBLISHED


    # Convert message to bytes
    # Convert message to bytes
    message_bytes = message.to_json().encode("utf-8")
    message_bytes = message.to_json().encode("utf-8")


    # Set message properties
    # Set message properties
    properties = pika.BasicProperties(
    properties = pika.BasicProperties(
    content_type="application/json",
    content_type="application/json",
    content_encoding="utf-8",
    content_encoding="utf-8",
    delivery_mode=(
    delivery_mode=(
    2 if persistent else 1
    2 if persistent else 1
    ),  # 2 = persistent, 1 = non-persistent
    ),  # 2 = persistent, 1 = non-persistent
    priority=message.priority.value,
    priority=message.priority.value,
    message_id=message.id,
    message_id=message.id,
    correlation_id=message.correlation_id,
    correlation_id=message.correlation_id,
    timestamp=int(message.timestamp),
    timestamp=int(message.timestamp),
    expiration=(
    expiration=(
    str(int((message.expires_at - time.time()) * 1000))
    str(int((message.expires_at - time.time()) * 1000))
    if message.expires_at
    if message.expires_at
    else None
    else None
    ),
    ),
    headers=message.headers,
    headers=message.headers,
    )
    )


    # Publish the message
    # Publish the message
    self.channel.basic_publish(
    self.channel.basic_publish(
    exchange=self.exchange_name,
    exchange=self.exchange_name,
    routing_key=routing_key,
    routing_key=routing_key,
    body=message_bytes,
    body=message_bytes,
    properties=properties,
    properties=properties,
    mandatory=mandatory,
    mandatory=mandatory,
    )
    )


    logger.info(f"Published message {message.id} to {routing_key}")
    logger.info(f"Published message {message.id} to {routing_key}")


    return message
    return message


except AMQPError as e:
except AMQPError as e:
    logger.error(f"Failed to publish message: {str(e)}")
    logger.error(f"Failed to publish message: {str(e)}")
    raise PublishError(f"Failed to publish message: {str(e)}")
    raise PublishError(f"Failed to publish message: {str(e)}")


    def declare_queue(
    def declare_queue(
    self,
    self,
    queue_name: str,
    queue_name: str,
    durable: bool = True,
    durable: bool = True,
    exclusive: bool = False,
    exclusive: bool = False,
    auto_delete: bool = False,
    auto_delete: bool = False,
    arguments: Optional[Dict[str, Any]] = None,
    arguments: Optional[Dict[str, Any]] = None,
    ) -> str:
    ) -> str:
    """
    """
    Declare a queue.
    Declare a queue.


    Args:
    Args:
    queue_name: Name of the queue
    queue_name: Name of the queue
    durable: Whether the queue should survive broker restarts
    durable: Whether the queue should survive broker restarts
    exclusive: Whether the queue should be used by only one connection
    exclusive: Whether the queue should be used by only one connection
    auto_delete: Whether the queue should be deleted when no longer used
    auto_delete: Whether the queue should be deleted when no longer used
    arguments: Additional arguments for the queue
    arguments: Additional arguments for the queue


    Returns:
    Returns:
    str: The queue name
    str: The queue name


    Raises:
    Raises:
    ConnectionError: If the queue cannot be declared
    ConnectionError: If the queue cannot be declared
    """
    """
    try:
    try:
    # Declare the queue
    # Declare the queue
    result = self.channel.queue_declare(
    result = self.channel.queue_declare(
    queue=queue_name,
    queue=queue_name,
    durable=durable,
    durable=durable,
    exclusive=exclusive,
    exclusive=exclusive,
    auto_delete=auto_delete,
    auto_delete=auto_delete,
    arguments=arguments,
    arguments=arguments,
    )
    )


    # Return the queue name (which might be different if queue_name was empty)
    # Return the queue name (which might be different if queue_name was empty)
    return result.method.queue
    return result.method.queue


except AMQPError as e:
except AMQPError as e:
    logger.error(f"Failed to declare queue {queue_name}: {str(e)}")
    logger.error(f"Failed to declare queue {queue_name}: {str(e)}")
    raise ConnectionError(f"Failed to declare queue {queue_name}: {str(e)}")
    raise ConnectionError(f"Failed to declare queue {queue_name}: {str(e)}")


    def bind_queue(
    def bind_queue(
    self, queue_name: str, routing_key: str, exchange_name: Optional[str] = None
    self, queue_name: str, routing_key: str, exchange_name: Optional[str] = None
    ):
    ):
    """
    """
    Bind a queue to an exchange with a routing key.
    Bind a queue to an exchange with a routing key.


    Args:
    Args:
    queue_name: Name of the queue
    queue_name: Name of the queue
    routing_key: Routing key to bind with
    routing_key: Routing key to bind with
    exchange_name: Name of the exchange (defaults to self.exchange_name)
    exchange_name: Name of the exchange (defaults to self.exchange_name)


    Raises:
    Raises:
    ConnectionError: If the queue cannot be bound
    ConnectionError: If the queue cannot be bound
    """
    """
    try:
    try:
    # Use the default exchange if not provided
    # Use the default exchange if not provided
    if exchange_name is None:
    if exchange_name is None:
    exchange_name = self.exchange_name
    exchange_name = self.exchange_name


    # Bind the queue
    # Bind the queue
    self.channel.queue_bind(
    self.channel.queue_bind(
    queue=queue_name, exchange=exchange_name, routing_key=routing_key
    queue=queue_name, exchange=exchange_name, routing_key=routing_key
    )
    )


    logger.info(
    logger.info(
    f"Bound queue {queue_name} to exchange {exchange_name} with routing key {routing_key}"
    f"Bound queue {queue_name} to exchange {exchange_name} with routing key {routing_key}"
    )
    )


except AMQPError as e:
except AMQPError as e:
    logger.error(
    logger.error(
    f"Failed to bind queue {queue_name} to {routing_key}: {str(e)}"
    f"Failed to bind queue {queue_name} to {routing_key}: {str(e)}"
    )
    )
    raise ConnectionError(
    raise ConnectionError(
    f"Failed to bind queue {queue_name} to {routing_key}: {str(e)}"
    f"Failed to bind queue {queue_name} to {routing_key}: {str(e)}"
    )
    )


    def consume(
    def consume(
    self,
    self,
    queue_name: str,
    queue_name: str,
    handler: MessageHandler,
    handler: MessageHandler,
    auto_ack: bool = False,
    auto_ack: bool = False,
    exclusive: bool = False,
    exclusive: bool = False,
    consumer_tag: Optional[str] = None,
    consumer_tag: Optional[str] = None,
    arguments: Optional[Dict[str, Any]] = None,
    arguments: Optional[Dict[str, Any]] = None,
    ) -> str:
    ) -> str:
    """
    """
    Start consuming messages from a queue.
    Start consuming messages from a queue.


    Args:
    Args:
    queue_name: Name of the queue to consume from
    queue_name: Name of the queue to consume from
    handler: Function to handle received messages
    handler: Function to handle received messages
    auto_ack: Whether to automatically acknowledge messages
    auto_ack: Whether to automatically acknowledge messages
    exclusive: Whether to request exclusive consumer access
    exclusive: Whether to request exclusive consumer access
    consumer_tag: Consumer tag to use (defaults to a generated tag)
    consumer_tag: Consumer tag to use (defaults to a generated tag)
    arguments: Additional arguments for the consumer
    arguments: Additional arguments for the consumer


    Returns:
    Returns:
    str: The consumer tag
    str: The consumer tag


    Raises:
    Raises:
    ConsumeError: If consumption cannot be started
    ConsumeError: If consumption cannot be started
    """
    """
    try:
    try:
    # Generate a consumer tag if not provided
    # Generate a consumer tag if not provided
    if consumer_tag is None:
    if consumer_tag is None:
    consumer_tag = f"{self.service_name}-{str(uuid.uuid4())}"
    consumer_tag = f"{self.service_name}-{str(uuid.uuid4())}"


    # Define the message handler
    # Define the message handler
    def on_message(ch, method, properties, body):
    def on_message(ch, method, properties, body):
    try:
    try:
    # Parse the message
    # Parse the message
    message_dict = json.loads(body.decode("utf-8"))
    message_dict = json.loads(body.decode("utf-8"))
    message = Message.from_dict(message_dict)
    message = Message.from_dict(message_dict)


    # Set message status to DELIVERED
    # Set message status to DELIVERED
    message.status = MessageStatus.DELIVERED
    message.status = MessageStatus.DELIVERED


    # Call the handler
    # Call the handler
    handler(message)
    handler(message)


    # Acknowledge the message if not auto_ack
    # Acknowledge the message if not auto_ack
    if not auto_ack:
    if not auto_ack:
    ch.basic_ack(delivery_tag=method.delivery_tag)
    ch.basic_ack(delivery_tag=method.delivery_tag)


    # Set message status to ACKNOWLEDGED
    # Set message status to ACKNOWLEDGED
    message.status = MessageStatus.ACKNOWLEDGED
    message.status = MessageStatus.ACKNOWLEDGED


except Exception as e:
except Exception as e:
    logger.error(f"Error handling message: {str(e)}")
    logger.error(f"Error handling message: {str(e)}")


    # Reject the message if not auto_ack
    # Reject the message if not auto_ack
    if not auto_ack:
    if not auto_ack:
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


    # Set message status to FAILED
    # Set message status to FAILED
    message.status = MessageStatus.FAILED
    message.status = MessageStatus.FAILED


    # Start consuming
    # Start consuming
    self.channel.basic_consume(
    self.channel.basic_consume(
    queue=queue_name,
    queue=queue_name,
    on_message_callback=on_message,
    on_message_callback=on_message,
    auto_ack=auto_ack,
    auto_ack=auto_ack,
    exclusive=exclusive,
    exclusive=exclusive,
    consumer_tag=consumer_tag,
    consumer_tag=consumer_tag,
    arguments=arguments,
    arguments=arguments,
    )
    )


    # Start a thread to run the consumer
    # Start a thread to run the consumer
    def consumer_thread():
    def consumer_thread():
    try:
    try:
    logger.info(
    logger.info(
    f"Started consuming from queue {queue_name} with tag {consumer_tag}"
    f"Started consuming from queue {queue_name} with tag {consumer_tag}"
    )
    )
    self.channel.start_consuming()
    self.channel.start_consuming()
except Exception as e:
except Exception as e:
    logger.error(f"Consumer thread error: {str(e)}")
    logger.error(f"Consumer thread error: {str(e)}")


    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    thread.start()


    # Store the thread
    # Store the thread
    self.consumer_threads[consumer_tag] = thread
    self.consumer_threads[consumer_tag] = thread


    return consumer_tag
    return consumer_tag


except AMQPError as e:
except AMQPError as e:
    logger.error(f"Failed to start consuming from queue {queue_name}: {str(e)}")
    logger.error(f"Failed to start consuming from queue {queue_name}: {str(e)}")
    raise ConsumeError(
    raise ConsumeError(
    f"Failed to start consuming from queue {queue_name}: {str(e)}"
    f"Failed to start consuming from queue {queue_name}: {str(e)}"
    )
    )


    def stop_consuming(self, consumer_tag: str):
    def stop_consuming(self, consumer_tag: str):
    """
    """
    Stop consuming messages.
    Stop consuming messages.


    Args:
    Args:
    consumer_tag: Consumer tag to stop
    consumer_tag: Consumer tag to stop
    """
    """
    try:
    try:
    # Stop consuming
    # Stop consuming
    self.channel.basic_cancel(consumer_tag=consumer_tag)
    self.channel.basic_cancel(consumer_tag=consumer_tag)


    # Wait for the thread to finish
    # Wait for the thread to finish
    if consumer_tag in self.consumer_threads:
    if consumer_tag in self.consumer_threads:
    self.consumer_threads[consumer_tag].join(timeout=1.0)
    self.consumer_threads[consumer_tag].join(timeout=1.0)
    del self.consumer_threads[consumer_tag]
    del self.consumer_threads[consumer_tag]


    logger.info(f"Stopped consuming with tag {consumer_tag}")
    logger.info(f"Stopped consuming with tag {consumer_tag}")


except AMQPError as e:
except AMQPError as e:
    logger.warning(f"Error stopping consumer {consumer_tag}: {str(e)}")
    logger.warning(f"Error stopping consumer {consumer_tag}: {str(e)}")


    def create_response_queue(self) -> Tuple[str, str]:
    def create_response_queue(self) -> Tuple[str, str]:
    """
    """
    Create a temporary queue for receiving responses.
    Create a temporary queue for receiving responses.


    Returns:
    Returns:
    Tuple[str, str]: Queue name and correlation ID
    Tuple[str, str]: Queue name and correlation ID
    """
    """
    # Generate a correlation ID
    # Generate a correlation ID
    correlation_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())


    # Declare a temporary queue
    # Declare a temporary queue
    queue_name = self.declare_queue(
    queue_name = self.declare_queue(
    queue_name="",  # Let RabbitMQ generate a name
    queue_name="",  # Let RabbitMQ generate a name
    durable=False,
    durable=False,
    exclusive=True,
    exclusive=True,
    auto_delete=True,
    auto_delete=True,
    )
    )


    return queue_name, correlation_id
    return queue_name, correlation_id


    def request(
    def request(
    self, message: Message, routing_key: Optional[str] = None, timeout: float = 30.0
    self, message: Message, routing_key: Optional[str] = None, timeout: float = 30.0
    ) -> Optional[Message]:
    ) -> Optional[Message]:
    """
    """
    Send a request and wait for a response.
    Send a request and wait for a response.


    Args:
    Args:
    message: Request message
    message: Request message
    routing_key: Routing key for the request (defaults to message.subject)
    routing_key: Routing key for the request (defaults to message.subject)
    timeout: Timeout in seconds
    timeout: Timeout in seconds


    Returns:
    Returns:
    Optional[Message]: Response message, or None if timed out
    Optional[Message]: Response message, or None if timed out


    Raises:
    Raises:
    PublishError: If the request cannot be sent
    PublishError: If the request cannot be sent
    ConsumeError: If the response cannot be received
    ConsumeError: If the response cannot be received
    """
    """
    # Create a temporary queue for the response
    # Create a temporary queue for the response
    queue_name, correlation_id = self.create_response_queue()
    queue_name, correlation_id = self.create_response_queue()


    # Set the correlation ID in the message
    # Set the correlation ID in the message
    message.correlation_id = correlation_id
    message.correlation_id = correlation_id


    # Set up a response holder
    # Set up a response holder
    response = {"message": None, "received": False}
    response = {"message": None, "received": False}


    # Define the response handler
    # Define the response handler
    def handle_response(msg):
    def handle_response(msg):
    response["message"] = msg
    response["message"] = msg
    response["received"] = True
    response["received"] = True


    # Start consuming from the response queue
    # Start consuming from the response queue
    consumer_tag = self.consume(
    consumer_tag = self.consume(
    queue_name=queue_name,
    queue_name=queue_name,
    handler=handle_response,
    handler=handle_response,
    auto_ack=True,
    auto_ack=True,
    exclusive=True,
    exclusive=True,
    )
    )


    try:
    try:
    # Publish the request
    # Publish the request
    self.publish(message=message, routing_key=routing_key, mandatory=True)
    self.publish(message=message, routing_key=routing_key, mandatory=True)


    # Wait for the response
    # Wait for the response
    start_time = time.time()
    start_time = time.time()
    while not response["received"] and time.time() - start_time < timeout:
    while not response["received"] and time.time() - start_time < timeout:
    time.sleep(0.1)
    time.sleep(0.1)


    # Check if we got a response
    # Check if we got a response
    if not response["received"]:
    if not response["received"]:
    logger.warning(
    logger.warning(
    f"Request {message.id} timed out after {timeout} seconds"
    f"Request {message.id} timed out after {timeout} seconds"
    )
    )
    return None
    return None


    return response["message"]
    return response["message"]


finally:
finally:
    # Stop consuming from the response queue
    # Stop consuming from the response queue
    self.stop_consuming(consumer_tag)
    self.stop_consuming(consumer_tag)




    class AsyncMessageQueueClient:
    class AsyncMessageQueueClient:
    """
    """
    Asynchronous client for interacting with the message queue (RabbitMQ).
    Asynchronous client for interacting with the message queue (RabbitMQ).


    This client provides methods for publishing and consuming messages asynchronously.
    This client provides methods for publishing and consuming messages asynchronously.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
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
    service_name: str = "unknown",
    service_name: str = "unknown",
    exchange_type: str = "topic",
    exchange_type: str = "topic",
    exchange_name: str = "paissive_income",
    exchange_name: str = "paissive_income",
    connection_attempts: int = 3,
    connection_attempts: int = 3,
    retry_delay: int = 5,
    retry_delay: int = 5,
    heartbeat: int = 60,
    heartbeat: int = 60,
    ):
    ):
    """
    """
    Initialize the asynchronous message queue client.
    Initialize the asynchronous message queue client.


    Args:
    Args:
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
    service_name: Name of the service using this client
    service_name: Name of the service using this client
    exchange_type: Type of exchange to use (topic, direct, fanout, headers)
    exchange_type: Type of exchange to use (topic, direct, fanout, headers)
    exchange_name: Name of the exchange to use
    exchange_name: Name of the exchange to use
    connection_attempts: Number of connection attempts
    connection_attempts: Number of connection attempts
    retry_delay: Delay between connection attempts in seconds
    retry_delay: Delay between connection attempts in seconds
    heartbeat: Heartbeat interval in seconds
    heartbeat: Heartbeat interval in seconds
    """
    """
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
    self.service_name = service_name
    self.service_name = service_name
    self.exchange_type = exchange_type
    self.exchange_type = exchange_type
    self.exchange_name = exchange_name
    self.exchange_name = exchange_name
    self.connection_attempts = connection_attempts
    self.connection_attempts = connection_attempts
    self.retry_delay = retry_delay
    self.retry_delay = retry_delay
    self.heartbeat = heartbeat
    self.heartbeat = heartbeat


    # Connection and channel
    # Connection and channel
    self.connection = None
    self.connection = None
    self.channel = None
    self.channel = None


    # Consumer tasks
    # Consumer tasks
    self.consumer_tasks = {}
    self.consumer_tasks = {}


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
    Connect to RabbitMQ asynchronously.
    Connect to RabbitMQ asynchronously.


    Raises:
    Raises:
    ConnectionError: If the connection fails
    ConnectionError: If the connection fails
    """
    """
    try:
    try:
    # Create connection URL
    # Create connection URL
    connection_url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"
    connection_url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"


    # Connect to RabbitMQ
    # Connect to RabbitMQ
    self.connection = await aio_pika.connect_robust(
    self.connection = await aio_pika.connect_robust(
    connection_url,
    connection_url,
    reconnect_interval=self.retry_delay,
    reconnect_interval=self.retry_delay,
    heartbeat=self.heartbeat,
    heartbeat=self.heartbeat,
    )
    )


    # Create a channel
    # Create a channel
    self.channel = await self.connection.channel()
    self.channel = await self.connection.channel()


    # Declare the exchange
    # Declare the exchange
    await self.channel.declare_exchange(
    await self.channel.declare_exchange(
    name=self.exchange_name, type=self.exchange_type, durable=True
    name=self.exchange_name, type=self.exchange_type, durable=True
    )
    )


    logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
    logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")


except aio_pika.exceptions.AMQPException as e:
except aio_pika.exceptions.AMQPException as e:
    logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
    logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
    raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")
    raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")


    async def close(self):
    async def close(self):
    """Close the connection to RabbitMQ asynchronously."""
    # Cancel all consumer tasks
    for task in self.consumer_tasks.values():
    task.cancel()

    # Close the channel and connection
    if self.channel is not None:
    await self.channel.close()

    if self.connection is not None:
    await self.connection.close()

    logger.info("Disconnected from RabbitMQ")

    async def reconnect(self):
    """
    """
    Reconnect to RabbitMQ asynchronously.
    Reconnect to RabbitMQ asynchronously.


    Raises:
    Raises:
    ConnectionError: If the reconnection fails
    ConnectionError: If the reconnection fails
    """
    """
    # Close the existing connection
    # Close the existing connection
    await self.close()
    await self.close()


    # Connect again
    # Connect again
    await self.connect()
    await self.connect()


    async def publish(
    async def publish(
    self,
    self,
    message: Message,
    message: Message,
    routing_key: Optional[str] = None,
    routing_key: Optional[str] = None,
    mandatory: bool = True,
    mandatory: bool = True,
    persistent: bool = True,
    persistent: bool = True,
    ) -> Message:
    ) -> Message:
    """
    """
    Publish a message to the message queue asynchronously.
    Publish a message to the message queue asynchronously.


    Args:
    Args:
    message: Message to publish
    message: Message to publish
    routing_key: Routing key for the message (defaults to message.subject)
    routing_key: Routing key for the message (defaults to message.subject)
    mandatory: Whether the message must be routed to a queue
    mandatory: Whether the message must be routed to a queue
    persistent: Whether the message should be persistent
    persistent: Whether the message should be persistent


    Returns:
    Returns:
    Message: The published message with updated status
    Message: The published message with updated status


    Raises:
    Raises:
    PublishError: If the message cannot be published
    PublishError: If the message cannot be published
    """
    """
    try:
    try:
    # Use the message subject as the routing key if not provided
    # Use the message subject as the routing key if not provided
    if routing_key is None:
    if routing_key is None:
    routing_key = message.subject
    routing_key = message.subject


    # Set message status to PUBLISHED
    # Set message status to PUBLISHED
    message.status = MessageStatus.PUBLISHED
    message.status = MessageStatus.PUBLISHED


    # Convert message to bytes
    # Convert message to bytes
    message_bytes = message.to_json().encode("utf-8")
    message_bytes = message.to_json().encode("utf-8")


    # Get the exchange
    # Get the exchange
    exchange = await self.channel.get_exchange(self.exchange_name)
    exchange = await self.channel.get_exchange(self.exchange_name)


    # Set message properties
    # Set message properties
    properties = aio_pika.Message(
    properties = aio_pika.Message(
    body=message_bytes,
    body=message_bytes,
    content_type="application/json",
    content_type="application/json",
    content_encoding="utf-8",
    content_encoding="utf-8",
    delivery_mode=(
    delivery_mode=(
    aio_pika.DeliveryMode.PERSISTENT
    aio_pika.DeliveryMode.PERSISTENT
    if persistent
    if persistent
    else aio_pika.DeliveryMode.NOT_PERSISTENT
    else aio_pika.DeliveryMode.NOT_PERSISTENT
    ),
    ),
    priority=message.priority.value,
    priority=message.priority.value,
    message_id=message.id,
    message_id=message.id,
    correlation_id=message.correlation_id,
    correlation_id=message.correlation_id,
    timestamp=int(message.timestamp),
    timestamp=int(message.timestamp),
    expiration=(
    expiration=(
    str(int((message.expires_at - time.time()) * 1000))
    str(int((message.expires_at - time.time()) * 1000))
    if message.expires_at
    if message.expires_at
    else None
    else None
    ),
    ),
    headers=message.headers,
    headers=message.headers,
    )
    )


    # Publish the message
    # Publish the message
    await exchange.publish(
    await exchange.publish(
    message=properties, routing_key=routing_key, mandatory=mandatory
    message=properties, routing_key=routing_key, mandatory=mandatory
    )
    )


    logger.info(f"Published message {message.id} to {routing_key}")
    logger.info(f"Published message {message.id} to {routing_key}")


    return message
    return message


except aio_pika.exceptions.AMQPException as e:
except aio_pika.exceptions.AMQPException as e:
    logger.error(f"Failed to publish message: {str(e)}")
    logger.error(f"Failed to publish message: {str(e)}")
    raise PublishError(f"Failed to publish message: {str(e)}")
    raise PublishError(f"Failed to publish message: {str(e)}")


    async def declare_queue(
    async def declare_queue(
    self,
    self,
    queue_name: str,
    queue_name: str,
    durable: bool = True,
    durable: bool = True,
    exclusive: bool = False,
    exclusive: bool = False,
    auto_delete: bool = False,
    auto_delete: bool = False,
    arguments: Optional[Dict[str, Any]] = None,
    arguments: Optional[Dict[str, Any]] = None,
    ) -> aio_pika.Queue:
    ) -> aio_pika.Queue:
    """
    """
    Declare a queue asynchronously.
    Declare a queue asynchronously.


    Args:
    Args:
    queue_name: Name of the queue
    queue_name: Name of the queue
    durable: Whether the queue should survive broker restarts
    durable: Whether the queue should survive broker restarts
    exclusive: Whether the queue should be used by only one connection
    exclusive: Whether the queue should be used by only one connection
    auto_delete: Whether the queue should be deleted when no longer used
    auto_delete: Whether the queue should be deleted when no longer used
    arguments: Additional arguments for the queue
    arguments: Additional arguments for the queue


    Returns:
    Returns:
    aio_pika.Queue: The declared queue
    aio_pika.Queue: The declared queue


    Raises:
    Raises:
    ConnectionError: If the queue cannot be declared
    ConnectionError: If the queue cannot be declared
    """
    """
    try:
    try:
    # Declare the queue
    # Declare the queue
    queue = await self.channel.declare_queue(
    queue = await self.channel.declare_queue(
    name=queue_name,
    name=queue_name,
    durable=durable,
    durable=durable,
    exclusive=exclusive,
    exclusive=exclusive,
    auto_delete=auto_delete,
    auto_delete=auto_delete,
    arguments=arguments,
    arguments=arguments,
    )
    )


    return queue
    return queue


except aio_pika.exceptions.AMQPException as e:
except aio_pika.exceptions.AMQPException as e:
    logger.error(f"Failed to declare queue {queue_name}: {str(e)}")
    logger.error(f"Failed to declare queue {queue_name}: {str(e)}")
    raise ConnectionError(f"Failed to declare queue {queue_name}: {str(e)}")
    raise ConnectionError(f"Failed to declare queue {queue_name}: {str(e)}")


    async def bind_queue(
    async def bind_queue(
    self,
    self,
    queue: aio_pika.Queue,
    queue: aio_pika.Queue,
    routing_key: str,
    routing_key: str,
    exchange_name: Optional[str] = None,
    exchange_name: Optional[str] = None,
    ):
    ):
    """
    """
    Bind a queue to an exchange with a routing key asynchronously.
    Bind a queue to an exchange with a routing key asynchronously.


    Args:
    Args:
    queue: Queue to bind
    queue: Queue to bind
    routing_key: Routing key to bind with
    routing_key: Routing key to bind with
    exchange_name: Name of the exchange (defaults to self.exchange_name)
    exchange_name: Name of the exchange (defaults to self.exchange_name)


    Raises:
    Raises:
    ConnectionError: If the queue cannot be bound
    ConnectionError: If the queue cannot be bound
    """
    """
    try:
    try:
    # Use the default exchange if not provided
    # Use the default exchange if not provided
    if exchange_name is None:
    if exchange_name is None:
    exchange_name = self.exchange_name
    exchange_name = self.exchange_name


    # Get the exchange
    # Get the exchange
    exchange = await self.channel.get_exchange(exchange_name)
    exchange = await self.channel.get_exchange(exchange_name)


    # Bind the queue
    # Bind the queue
    await queue.bind(exchange=exchange, routing_key=routing_key)
    await queue.bind(exchange=exchange, routing_key=routing_key)


    logger.info(
    logger.info(
    f"Bound queue {queue.name} to exchange {exchange_name} with routing key {routing_key}"
    f"Bound queue {queue.name} to exchange {exchange_name} with routing key {routing_key}"
    )
    )


except aio_pika.exceptions.AMQPException as e:
except aio_pika.exceptions.AMQPException as e:
    logger.error(
    logger.error(
    f"Failed to bind queue {queue.name} to {routing_key}: {str(e)}"
    f"Failed to bind queue {queue.name} to {routing_key}: {str(e)}"
    )
    )
    raise ConnectionError(
    raise ConnectionError(
    f"Failed to bind queue {queue.name} to {routing_key}: {str(e)}"
    f"Failed to bind queue {queue.name} to {routing_key}: {str(e)}"
    )
    )


    async def consume(
    async def consume(
    self,
    self,
    queue_name: str,
    queue_name: str,
    handler: AsyncMessageHandler,
    handler: AsyncMessageHandler,
    auto_ack: bool = False,
    auto_ack: bool = False,
    exclusive: bool = False,
    exclusive: bool = False,
    arguments: Optional[Dict[str, Any]] = None,
    arguments: Optional[Dict[str, Any]] = None,
    ) -> str:
    ) -> str:
    """
    """
    Start consuming messages from a queue asynchronously.
    Start consuming messages from a queue asynchronously.


    Args:
    Args:
    queue_name: Name of the queue to consume from
    queue_name: Name of the queue to consume from
    handler: Async function to handle received messages
    handler: Async function to handle received messages
    auto_ack: Whether to automatically acknowledge messages
    auto_ack: Whether to automatically acknowledge messages
    exclusive: Whether to request exclusive consumer access
    exclusive: Whether to request exclusive consumer access
    arguments: Additional arguments for the consumer
    arguments: Additional arguments for the consumer


    Returns:
    Returns:
    str: The consumer tag
    str: The consumer tag


    Raises:
    Raises:
    ConsumeError: If consumption cannot be started
    ConsumeError: If consumption cannot be started
    """
    """
    try:
    try:
    # Declare the queue
    # Declare the queue
    queue = await self.declare_queue(
    queue = await self.declare_queue(
    queue_name=queue_name,
    queue_name=queue_name,
    durable=True,
    durable=True,
    exclusive=exclusive,
    exclusive=exclusive,
    auto_delete=False,
    auto_delete=False,
    arguments=arguments,
    arguments=arguments,
    )
    )


    # Generate a consumer tag
    # Generate a consumer tag
    consumer_tag = f"{self.service_name}-{str(uuid.uuid4())}"
    consumer_tag = f"{self.service_name}-{str(uuid.uuid4())}"


    # Define the message handler
    # Define the message handler
    async def on_message(message: aio_pika.IncomingMessage):
    async def on_message(message: aio_pika.IncomingMessage):
    async with message.process(auto_ack=auto_ack):
    async with message.process(auto_ack=auto_ack):
    try:
    try:
    # Parse the message
    # Parse the message
    message_dict = json.loads(message.body.decode("utf-8"))
    message_dict = json.loads(message.body.decode("utf-8"))
    msg = Message.from_dict(message_dict)
    msg = Message.from_dict(message_dict)


    # Set message status to DELIVERED
    # Set message status to DELIVERED
    msg.status = MessageStatus.DELIVERED
    msg.status = MessageStatus.DELIVERED


    # Call the handler
    # Call the handler
    await handler(msg)
    await handler(msg)


    # Set message status to ACKNOWLEDGED if auto_ack
    # Set message status to ACKNOWLEDGED if auto_ack
    if auto_ack:
    if auto_ack:
    msg.status = MessageStatus.ACKNOWLEDGED
    msg.status = MessageStatus.ACKNOWLEDGED


except Exception as e:
except Exception as e:
    logger.error(f"Error handling message: {str(e)}")
    logger.error(f"Error handling message: {str(e)}")


    # Set message status to FAILED
    # Set message status to FAILED
    msg.status = MessageStatus.FAILED
    msg.status = MessageStatus.FAILED


    # Reject the message if not auto_ack
    # Reject the message if not auto_ack
    if not auto_ack:
    if not auto_ack:
    await message.reject(requeue=True)
    await message.reject(requeue=True)


    # Start consuming
    # Start consuming
    consumer_tag = await queue.consume(
    consumer_tag = await queue.consume(
    callback=on_message, consumer_tag=consumer_tag
    callback=on_message, consumer_tag=consumer_tag
    )
    )


    logger.info(
    logger.info(
    f"Started consuming from queue {queue_name} with tag {consumer_tag}"
    f"Started consuming from queue {queue_name} with tag {consumer_tag}"
    )
    )


    return consumer_tag
    return consumer_tag


except aio_pika.exceptions.AMQPException as e:
except aio_pika.exceptions.AMQPException as e:
    logger.error(f"Failed to start consuming from queue {queue_name}: {str(e)}")
    logger.error(f"Failed to start consuming from queue {queue_name}: {str(e)}")
    raise ConsumeError(
    raise ConsumeError(
    f"Failed to start consuming from queue {queue_name}: {str(e)}"
    f"Failed to start consuming from queue {queue_name}: {str(e)}"
    )
    )


    async def stop_consuming(self, consumer_tag: str):
    async def stop_consuming(self, consumer_tag: str):
    """
    """
    Stop consuming messages asynchronously.
    Stop consuming messages asynchronously.


    Args:
    Args:
    consumer_tag: Consumer tag to stop
    consumer_tag: Consumer tag to stop
    """
    """
    try:
    try:
    # Cancel the consumer
    # Cancel the consumer
    await self.channel.basic_cancel(consumer_tag=consumer_tag)
    await self.channel.basic_cancel(consumer_tag=consumer_tag)


    # Cancel the task if it exists
    # Cancel the task if it exists
    if consumer_tag in self.consumer_tasks:
    if consumer_tag in self.consumer_tasks:
    self.consumer_tasks[consumer_tag].cancel()
    self.consumer_tasks[consumer_tag].cancel()
    del self.consumer_tasks[consumer_tag]
    del self.consumer_tasks[consumer_tag]


    logger.info(f"Stopped consuming with tag {consumer_tag}")
    logger.info(f"Stopped consuming with tag {consumer_tag}")


except aio_pika.exceptions.AMQPException as e:
except aio_pika.exceptions.AMQPException as e:
    logger.warning(f"Error stopping consumer {consumer_tag}: {str(e)}")
    logger.warning(f"Error stopping consumer {consumer_tag}: {str(e)}")


    async def create_response_queue(self) -> Tuple[aio_pika.Queue, str]:
    async def create_response_queue(self) -> Tuple[aio_pika.Queue, str]:
    """
    """
    Create a temporary queue for receiving responses asynchronously.
    Create a temporary queue for receiving responses asynchronously.


    Returns:
    Returns:
    Tuple[aio_pika.Queue, str]: Queue and correlation ID
    Tuple[aio_pika.Queue, str]: Queue and correlation ID
    """
    """
    # Generate a correlation ID
    # Generate a correlation ID
    correlation_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())


    # Declare a temporary queue
    # Declare a temporary queue
    queue = await self.declare_queue(
    queue = await self.declare_queue(
    queue_name="",  # Let RabbitMQ generate a name
    queue_name="",  # Let RabbitMQ generate a name
    durable=False,
    durable=False,
    exclusive=True,
    exclusive=True,
    auto_delete=True,
    auto_delete=True,
    )
    )


    return queue, correlation_id
    return queue, correlation_id


    async def request(
    async def request(
    self, message: Message, routing_key: Optional[str] = None, timeout: float = 30.0
    self, message: Message, routing_key: Optional[str] = None, timeout: float = 30.0
    ) -> Optional[Message]:
    ) -> Optional[Message]:
    """
    """
    Send a request and wait for a response asynchronously.
    Send a request and wait for a response asynchronously.


    Args:
    Args:
    message: Request message
    message: Request message
    routing_key: Routing key for the request (defaults to message.subject)
    routing_key: Routing key for the request (defaults to message.subject)
    timeout: Timeout in seconds
    timeout: Timeout in seconds


    Returns:
    Returns:
    Optional[Message]: Response message, or None if timed out
    Optional[Message]: Response message, or None if timed out


    Raises:
    Raises:
    PublishError: If the request cannot be sent
    PublishError: If the request cannot be sent
    ConsumeError: If the response cannot be received
    ConsumeError: If the response cannot be received
    """
    """
    # Create a temporary queue for the response
    # Create a temporary queue for the response
    queue, correlation_id = await self.create_response_queue()
    queue, correlation_id = await self.create_response_queue()


    # Set the correlation ID in the message
    # Set the correlation ID in the message
    message.correlation_id = correlation_id
    message.correlation_id = correlation_id


    # Set up a future for the response
    # Set up a future for the response
    future = asyncio.Future()
    future = asyncio.Future()


    # Define the response handler
    # Define the response handler
    async def handle_response(msg):
    async def handle_response(msg):
    if not future.done():
    if not future.done():
    future.set_result(msg)
    future.set_result(msg)


    # Start consuming from the response queue
    # Start consuming from the response queue
    consumer_tag = await queue.consume(
    consumer_tag = await queue.consume(
    callback=handle_response, consumer_tag=f"request-{correlation_id}"
    callback=handle_response, consumer_tag=f"request-{correlation_id}"
    )
    )


    try:
    try:
    # Publish the request
    # Publish the request
    await self.publish(message=message, routing_key=routing_key, mandatory=True)
    await self.publish(message=message, routing_key=routing_key, mandatory=True)


    # Wait for the response
    # Wait for the response
    try:
    try:
    response = await asyncio.wait_for(future, timeout=timeout)
    response = await asyncio.wait_for(future, timeout=timeout)
    return response
    return response
except asyncio.TimeoutError:
except asyncio.TimeoutError:
    logger.warning(
    logger.warning(
    f"Request {message.id} timed out after {timeout} seconds"
    f"Request {message.id} timed out after {timeout} seconds"
    )
    )
    return None
    return None


finally:
finally:
    # Cancel the consumer
    # Cancel the consumer
    await self.channel.basic_cancel(consumer_tag=consumer_tag)
    await self.channel.basic_cancel(consumer_tag=consumer_tag)