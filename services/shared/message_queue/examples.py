"""
"""
Examples of using the message queue for different services.
Examples of using the message queue for different services.


This module provides examples of how to use the message queue for different services.
This module provides examples of how to use the message queue for different services.
"""
"""




import asyncio
import asyncio
import logging
import logging
import time
import time
from typing import Any, Dict, List
from typing import Any, Dict, List


from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, ConfigDict


(
(
MessageQueueClient,
MessageQueueClient,
AsyncMessageQueueClient,
AsyncMessageQueueClient,
Message,
Message,
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




# Example 1: Niche Analysis Service - Synchronous
# Example 1: Niche Analysis Service - Synchronous
def niche_analysis_service_example():
    def niche_analysis_service_example():
    """Example of using the message queue in the Niche Analysis Service."""

    # Define message payload schemas
    class NicheAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())))

    niche_name: str
    force_refresh: bool = False

    class NicheAnalysisResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))

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

    # Define message payload schemas
    class TextGenerationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))


    model_id: str
    model_id: str
    prompt: str
    prompt: str
    max_tokens: int = 100
    max_tokens: int = 100
    temperature: float = 0.7
    temperature: float = 0.7


    class TextGenerationResponse(BaseModel):
    class TextGenerationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))


    model_id: str
    model_id: str
    prompt: str
    prompt: str
    generated_text: str
    generated_text: str
    tokens_used: int
    tokens_used: int
    processing_time: float
    processing_time: float


    # Create message schemas
    # Create message schemas
    request_schema = MessageSchema(TextGenerationRequest)
    request_schema = MessageSchema(TextGenerationRequest)
    response_schema = MessageSchema(TextGenerationResponse)
    response_schema = MessageSchema(TextGenerationResponse)


    # Create an async message queue client
    # Create an async message queue client
    async with AsyncMessageQueueClient(
    async with AsyncMessageQueueClient(
    service_name="ai-models-service", exchange_name="paissive_income"
    service_name="ai-models-service", exchange_name="paissive_income"
    ) as client:
    ) as client:
    # Declare a queue for the service
    # Declare a queue for the service
    queue = await client.declare_queue(queue_name="ai-models-service", durable=True)
    queue = await client.declare_queue(queue_name="ai-models-service", durable=True)


    # Bind the queue to the exchange with a routing key
    # Bind the queue to the exchange with a routing key
    await client.bind_queue(
    await client.bind_queue(
    queue=queue,
    queue=queue,
    routing_key="ai-models.text-generation.#",  # Listen for text generation requests
    routing_key="ai-models.text-generation.#",  # Listen for text generation requests
    )
    )


    # Define a message handler
    # Define a message handler
    async def handle_text_generation_request(message: Message):
    async def handle_text_generation_request(message: Message):
    logger.info(f"Received text generation request: {message.id}")
    logger.info(f"Received text generation request: {message.id}")


    # Parse the request
    # Parse the request
    request = request_schema.parse_message(message)
    request = request_schema.parse_message(message)


    # Process the request (in a real service, this would use an AI model)
    # Process the request (in a real service, this would use an AI model)
    logger.info(f"Generating text with model: {request.model_id}")
    logger.info(f"Generating text with model: {request.model_id}")
    start_time = time.time()
    start_time = time.time()
    await asyncio.sleep(1)  # Simulate processing time
    await asyncio.sleep(1)  # Simulate processing time


    # Create a response
    # Create a response
    response_payload = TextGenerationResponse(
    response_payload = TextGenerationResponse(
    model_id=request.model_id,
    model_id=request.model_id,
    prompt=request.prompt,
    prompt=request.prompt,
    generated_text=f"Generated text for prompt: {request.prompt}",
    generated_text=f"Generated text for prompt: {request.prompt}",
    tokens_used=50,
    tokens_used=50,
    processing_time=time.time() - start_time,
    processing_time=time.time() - start_time,
    )
    )


    # Create a response message
    # Create a response message
    response_message = response_schema.create_message(
    response_message = response_schema.create_message(
    source="ai-models-service",
    source="ai-models-service",
    destination=message.source,
    destination=message.source,
    subject="ai-models.text-generation.response",
    subject="ai-models.text-generation.response",
    payload=response_payload,
    payload=response_payload,
    message_type=MessageType.RESPONSE,
    message_type=MessageType.RESPONSE,
    correlation_id=message.id,
    correlation_id=message.id,
    )
    )


    # Publish the response
    # Publish the response
    await client.publish(
    await client.publish(
    message=response_message, routing_key=f"response.{message.source}"
    message=response_message, routing_key=f"response.{message.source}"
    )
    )


    logger.info(f"Sent text generation response: {response_message.id}")
    logger.info(f"Sent text generation response: {response_message.id}")


    # Start consuming messages
    # Start consuming messages
    consumer_tag = await client.consume(
    consumer_tag = await client.consume(
    queue_name=queue.name, handler=handle_text_generation_request
    queue_name=queue.name, handler=handle_text_generation_request
    )
    )


    logger.info("AI Models Service is running...")
    logger.info("AI Models Service is running...")


    # Keep the service running
    # Keep the service running
    try:
    try:
    while True:
    while True:
    await asyncio.sleep(1)
    await asyncio.sleep(1)
except KeyboardInterrupt:
except KeyboardInterrupt:
    logger.info("Shutting down AI Models Service...")
    logger.info("Shutting down AI Models Service...")
    await client.stop_consuming(consumer_tag)
    await client.stop_consuming(consumer_tag)




    # Example 3: API Gateway - Request-Response Pattern
    # Example 3: API Gateway - Request-Response Pattern
    async def api_gateway_example():
    async def api_gateway_example():


    # Define message payload schemas
    # Define message payload schemas
    class NicheAnalysisRequest(BaseModel):
    class NicheAnalysisRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())))
    model_config = ConfigDict(protected_namespaces=())))


    niche_name: str
    niche_name: str
    force_refresh: bool = False
    force_refresh: bool = False


    # Create message schemas
    # Create message schemas
    request_schema = MessageSchema(NicheAnalysisRequest)
    request_schema = MessageSchema(NicheAnalysisRequest)


    # Create an async message queue client
    # Create an async message queue client
    async with AsyncMessageQueueClient(
    async with AsyncMessageQueueClient(
    service_name="api-gateway", exchange_name="paissive_income"
    service_name="api-gateway", exchange_name="paissive_income"
    ) as client:
    ) as client:
    # Create a request message
    # Create a request message
    request_payload = NicheAnalysisRequest(
    request_payload = NicheAnalysisRequest(
    niche_name="fitness-apps", force_refresh=True
    niche_name="fitness-apps", force_refresh=True
    )
    )


    request_message = request_schema.create_message(
    request_message = request_schema.create_message(
    source="api-gateway",
    source="api-gateway",
    destination="niche-analysis-service",
    destination="niche-analysis-service",
    subject="niche-analysis.request",
    subject="niche-analysis.request",
    payload=request_payload,
    payload=request_payload,
    message_type=MessageType.COMMAND,
    message_type=MessageType.COMMAND,
    )
    )


    logger.info(f"Sending niche analysis request: {request_message.id}")
    logger.info(f"Sending niche analysis request: {request_message.id}")


    # Send the request and wait for a response
    # Send the request and wait for a response
    response = await client.request(
    response = await client.request(
    message=request_message, routing_key="niche-analysis.request", timeout=10.0
    message=request_message, routing_key="niche-analysis.request", timeout=10.0
    )
    )


    if response:
    if response:
    logger.info(f"Received niche analysis response: {response.id}")
    logger.info(f"Received niche analysis response: {response.id}")
    logger.info(f"Response payload: {response.payload}")
    logger.info(f"Response payload: {response.payload}")
    else:
    else:
    logger.warning("No response received within timeout")
    logger.warning("No response received within timeout")




    # Example 4: Event-Driven Communication
    # Example 4: Event-Driven Communication
    def event_driven_example():
    def event_driven_example():
    """Example of event-driven communication between services."""

    # Define message payload schemas
    class NicheAnalysisCompleted(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))

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
    # asyncio.run(api_gateway_example()

    # Example 4: Event-Driven Communication
    event_driven_example(