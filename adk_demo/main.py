"""
ADK Demo Main Module.

This module serves as the entry point for the ADK demonstration.
It sets up the agent communication infrastructure and provides a simple CLI interface.

Features:
- Agent initialization and communication setup
- User input handling
- Message routing with retry mechanism
- Proper cleanup on completion

Configuration:
- max_retries: 10 attempts for message reception
- TIMEOUT: 5.0 seconds per attempt
- Total wait time: 50 seconds (max_retries * TIMEOUT)

Message Flow:
1. User → DataGatherer:
   - Type: 'gather'
   - Payload: {'query': str}

2. DataGatherer → Summarizer:
   - Type: 'summarize'
   - Payload: {'data': str, 'original_sender': str}

3. Summarizer → User:
   - Type: 'summary_result'
   - Payload: {'summary': str}

Error Handling:
- Implements timeout per attempt
- Progressive retry mechanism
- Graceful cleanup on failure
"""

import logging

from adk.communication import AgentCommunicator, Message
from agents import DataGathererAgent, SummarizerAgent

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Orchestrate the ADK demonstration.

    Flow:
    1. Sets up communication infrastructure
    2. Initializes and starts agents
    3. Handles user input
    4. Manages message flow with retry mechanism
    5. Performs cleanup

    Configuration:
    - max_retries: 10 attempts for message reception
    - Timeout: 5.0 seconds per attempt
    """
    # Set up communicator
    communicator = AgentCommunicator()

    # Instantiate agents
    gatherer = DataGathererAgent(name="gatherer")
    summarizer = SummarizerAgent(name="summarizer")

    # Register agents with communicator
    gatherer.set_communicator(communicator)
    summarizer.set_communicator(communicator)

    # Start agents (non-blocking)
    gatherer.start()
    summarizer.start()

    # Simple CLI user interface
    user_name = "user"
    query = input("Enter your research query: ").strip()
    if not query:
        logger.info("No query entered. Exiting.")
        return

    # Send initial message to DataGathererAgent
    communicator.send(
        Message(
            sender=user_name,
            receiver="gatherer",
            type="gather",
            payload={"query": query},
        )
    )

    # Wait for summary result (with retry limit)
    max_retries = 10  # Changed from MAX_RETRIES to follow Python naming conventions
    retries = 0
    while retries < max_retries:
        msg = communicator.receive(receiver=user_name, timeout=5.0)
        if msg and msg.type == "summary_result":
            logger.info("Summary: %s", msg.payload["summary"])
            break
        retries += 1
    else:
        logger.error(
            "\nFailed to receive summary message after multiple attempts. Exiting."
        )

    # Clean up
    gatherer.stop()
    summarizer.stop()


if __name__ == "__main__":
    main()
