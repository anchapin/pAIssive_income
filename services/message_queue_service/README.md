# Message Queue Service

This service provides a message queue for asynchronous communication between microservices in the pAIssive Income platform.

## Overview

The Message Queue Service uses RabbitMQ as the message broker to enable:

- Asynchronous communication between services
- Event-driven architecture
- Reliable message delivery
- Load balancing and scaling

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Running the Service

To start the RabbitMQ service:

```bash
cd services/message_queue_service
docker-compose up -d
```

This will start RabbitMQ with the management UI accessible at http://localhost:15672 (username: guest, password: [default_guest_password_for_local_dev_only]).

## Usage

The Message Queue Service provides a shared library for interacting with the message queue. See the `services/shared/message_queue` package for details.

### Basic Usage

```python
from services.shared.message_queue import MessageQueueClient, Message, MessageType

# Create a client
client = MessageQueueClient(service_name="my-service")

# Create a message
message = Message(
    type=MessageType.EVENT,
    source="my-service",
    destination="target-service",
    subject="my-event",
    payload={"key": "value"}
)

# Publish a message
client.publish(message, routing_key="my-event")

# Consume messages
def handle_message(message):
    print(f"Received message: {message.id}")
    print(f"Payload: {message.payload}")

client.consume(
    queue_name="my-service-queue",
    handler=handle_message
)
```

### Asynchronous Usage

```python
import asyncio
from services.shared.message_queue import AsyncMessageQueueClient, Message, MessageType

async def main():
    # Create an async client
    async with AsyncMessageQueueClient(service_name="my-service") as client:
        # Create a message
        message = Message(
            type=MessageType.EVENT,
            source="my-service",
            destination="target-service",
            subject="my-event",
            payload={"key": "value"}
        )

        # Publish a message
        await client.publish(message, routing_key="my-event")

        # Consume messages
        async def handle_message(message):
            print(f"Received message: {message.id}")
            print(f"Payload: {message.payload}")

        await client.consume(
            queue_name="my-service-queue",
            handler=handle_message
        )

        # Wait for messages
        await asyncio.sleep(60)

asyncio.run(main())
```

## Configuration

The Message Queue Service can be configured using environment variables:

- `RABBITMQ_HOST`: RabbitMQ host (default: localhost)
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USER`: RabbitMQ username (default: guest)
- `RABBITMQ_PASS`: RabbitMQ password (default: guest)
- `RABBITMQ_VHOST`: RabbitMQ virtual host (default: /)

## Examples

See the `services/shared/message_queue/examples.py` file for examples of how to use the message queue for different services.

## Monitoring

The RabbitMQ Management UI provides monitoring and management capabilities for the message queue. Access it at http://localhost:15672.

## Troubleshooting

- If you can't connect to RabbitMQ, check that the service is running with `docker-compose ps`.
- Check the RabbitMQ logs with `docker-compose logs rabbitmq`.
- Ensure that your service has the correct connection parameters.
