"""
Examples of using the message queue for different services.

This module provides examples of how to use the message queue for different services.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel, ConfigDict

from services.shared.message_queue import (
    MessageQueueClient,
    AsyncMessageQueueClient,
    Message,
    MessageSchema,
    MessageType,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Example 1: Niche Analysis Service - Synchronous
def niche_analysis_service_example():
    """Example of using the message queue in the Niche Analysis Service."""

    # Define message payload schemas
    class NicheAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
        """Request for niche analysis."""

        niche_name: str
        force_refresh: bool = False

    class NicheAnalysisResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
        """Response from niche analysis."""

        niche_name: str
        problems: List[Dict[str, Any]]
        competition: Dict[str, Any]
        opportunities: List[Dict[str, Any]]
        summary: str

    # Create message schemas
    request_schema = MessageSchema(NicheAnalysisRequest)
    response_schema = MessageSchema(NicheAnalysisResponse)

    # Create a message queue client
    client = MessageQueueClient(
        service_name="niche-analysis-service", exchange_name="paissive_income"
    )

    try:
        # Declare a queue for the service
        queue_name = client.declare_queue(
            queue_name="niche-analysis-service", durable=True
        )

        # Bind the queue to the exchange with a routing key
        client.bind_queue(
            queue_name=queue_name,
            routing_key="niche-analysis.#",  # Listen for all niche analysis messages
        )

        # Define a message handler
        def handle_niche_analysis_request(message: Message):
            logger.info(f"Received niche analysis request: {message.id}")

            # Parse the request
            request = request_schema.parse_message(message)

            # Process the request (in a real service, this would do actual analysis)
            logger.info(f"Analyzing niche: {request.niche_name}")
            time.sleep(2)  # Simulate processing time

            # Create a response
            response_payload = NicheAnalysisResponse(
                niche_name=request.niche_name,
                problems=[
                    {"name": "Problem 1", "description": "Description of problem 1"}
                ],
                competition={"level": "medium", "competitors": 5},
                opportunities=[{"name": "Opportunity 1", "score": 0.8}],
                summary=f"Analysis of {request.niche_name} completed successfully.",
            )

            # Create a response message
            response_message = response_schema.create_message(
                source="niche-analysis-service",
                destination=message.source,
                subject="niche-analysis.response",
                payload=response_payload,
                message_type=MessageType.RESPONSE,
                correlation_id=message.id,
            )

            # Publish the response
            client.publish(
                message=response_message, routing_key=f"response.{message.source}"
            )

            logger.info(f"Sent niche analysis response: {response_message.id}")

        # Start consuming messages
        client.consume(queue_name=queue_name, handler=handle_niche_analysis_request)

        logger.info("Niche Analysis Service is running...")

        # Keep the service running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Niche Analysis Service...")

    finally:
        # Close the client
        client.close()


# Example 2: AI Models Service - Asynchronous
async def ai_models_service_example():
    """Example of using the message queue in the AI Models Service."""

    # Define message payload schemas
    class TextGenerationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
        """Request for text generation."""

        model_id: str
        prompt: str
        max_tokens: int = 100
        temperature: float = 0.7

    class TextGenerationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
        """Response from text generation."""

        model_id: str
        prompt: str
        generated_text: str
        tokens_used: int
        processing_time: float

    # Create message schemas
    request_schema = MessageSchema(TextGenerationRequest)
    response_schema = MessageSchema(TextGenerationResponse)

    # Create an async message queue client
    async with AsyncMessageQueueClient(
        service_name="ai-models-service", exchange_name="paissive_income"
    ) as client:
        # Declare a queue for the service
        queue = await client.declare_queue(queue_name="ai-models-service", durable=True)

        # Bind the queue to the exchange with a routing key
        await client.bind_queue(
            queue=queue,
            routing_key="ai-models.text-generation.#",  # Listen for text generation requests
        )

        # Define a message handler
        async def handle_text_generation_request(message: Message):
            logger.info(f"Received text generation request: {message.id}")

            # Parse the request
            request = request_schema.parse_message(message)

            # Process the request (in a real service, this would use an AI model)
            logger.info(f"Generating text with model: {request.model_id}")
            start_time = time.time()
            await asyncio.sleep(1)  # Simulate processing time

            # Create a response
            response_payload = TextGenerationResponse(
                model_id=request.model_id,
                prompt=request.prompt,
                generated_text=f"Generated text for prompt: {request.prompt}",
                tokens_used=50,
                processing_time=time.time() - start_time,
            )

            # Create a response message
            response_message = response_schema.create_message(
                source="ai-models-service",
                destination=message.source,
                subject="ai-models.text-generation.response",
                payload=response_payload,
                message_type=MessageType.RESPONSE,
                correlation_id=message.id,
            )

            # Publish the response
            await client.publish(
                message=response_message, routing_key=f"response.{message.source}"
            )

            logger.info(f"Sent text generation response: {response_message.id}")

        # Start consuming messages
        consumer_tag = await client.consume(
            queue_name=queue.name, handler=handle_text_generation_request
        )

        logger.info("AI Models Service is running...")

        # Keep the service running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down AI Models Service...")
            await client.stop_consuming(consumer_tag)


# Example 3: API Gateway - Request-Response Pattern
async def api_gateway_example():
    """Example of using the message queue in the API Gateway."""

    # Define message payload schemas
    class NicheAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
        """Request for niche analysis."""

        niche_name: str
        force_refresh: bool = False

    # Create message schemas
    request_schema = MessageSchema(NicheAnalysisRequest)

    # Create an async message queue client
    async with AsyncMessageQueueClient(
        service_name="api-gateway", exchange_name="paissive_income"
    ) as client:
        # Create a request message
        request_payload = NicheAnalysisRequest(
            niche_name="fitness-apps", force_refresh=True
        )

        request_message = request_schema.create_message(
            source="api-gateway",
            destination="niche-analysis-service",
            subject="niche-analysis.request",
            payload=request_payload,
            message_type=MessageType.COMMAND,
        )

        logger.info(f"Sending niche analysis request: {request_message.id}")

        # Send the request and wait for a response
        response = await client.request(
            message=request_message, routing_key="niche-analysis.request", timeout=10.0
        )

        if response:
            logger.info(f"Received niche analysis response: {response.id}")
            logger.info(f"Response payload: {response.payload}")
        else:
            logger.warning("No response received within timeout")


# Example 4: Event-Driven Communication
def event_driven_example():
    """Example of event-driven communication between services."""

    # Define message payload schemas
    class NicheAnalysisCompleted(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
        """Event for when a niche analysis is completed."""

        niche_id: str
        niche_name: str
        timestamp: float
        score: float

    # Create message schemas
    event_schema = MessageSchema(NicheAnalysisCompleted)

    # Create a message queue client for the publisher (Niche Analysis Service)
    publisher = MessageQueueClient(
        service_name="niche-analysis-service", exchange_name="paissive_income"
    )

    # Create a message queue client for the subscriber (Marketing Service)
    subscriber = MessageQueueClient(
        service_name="marketing-service", exchange_name="paissive_income"
    )

    try:
        # Declare a queue for the subscriber
        queue_name = subscriber.declare_queue(
            queue_name="marketing-service.niche-events", durable=True
        )

        # Bind the queue to the exchange with a routing key
        subscriber.bind_queue(
            queue_name=queue_name, routing_key="events.niche-analysis.completed"
        )

        # Define an event handler
        def handle_niche_analysis_completed(message: Message):
            logger.info(f"Received niche analysis completed event: {message.id}")

            # Parse the event
            event = event_schema.parse_message(message)

            # Process the event (in a real service, this would trigger marketing actions)
            logger.info(f"Processing niche analysis completion for: {event.niche_name}")
            logger.info(f"Niche score: {event.score}")

        # Start consuming events
        subscriber.consume(
            queue_name=queue_name,
            handler=handle_niche_analysis_completed,
            auto_ack=True,
        )

        logger.info("Marketing Service is listening for niche analysis events...")

        # Publish an event (from Niche Analysis Service)
        event_payload = NicheAnalysisCompleted(
            niche_id="123456",
            niche_name="fitness-apps",
            timestamp=time.time(),
            score=0.85,
        )

        event_message = event_schema.create_message(
            source="niche-analysis-service",
            destination="*",  # Broadcast to all interested services
            subject="events.niche-analysis.completed",
            payload=event_payload,
            message_type=MessageType.EVENT,
        )

        logger.info(f"Publishing niche analysis completed event: {event_message.id}")

        publisher.publish(
            message=event_message, routing_key="events.niche-analysis.completed"
        )

        # Keep the subscriber running
        try:
            time.sleep(5)  # Wait for the event to be processed
        except KeyboardInterrupt:
            logger.info("Shutting down Marketing Service...")

    finally:
        # Close the clients
        publisher.close()
        subscriber.close()


# Run the examples
if __name__ == "__main__":
    # Example 1: Niche Analysis Service - Synchronous
    # niche_analysis_service_example()

    # Example 2: AI Models Service - Asynchronous
    # asyncio.run(ai_models_service_example())

    # Example 3: API Gateway - Request-Response Pattern
    # asyncio.run(api_gateway_example())

    # Example 4: Event-Driven Communication
    event_driven_example()
