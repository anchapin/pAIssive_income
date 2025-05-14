"""
ADK Demo Main Module

This module serves as the entry point for the ADK demonstration.
It sets up the agent communication infrastructure and provides a simple CLI interface.

Features:
- Agent initialization and communication setup
- User input handling
- Message routing with retry mechanism
- Proper cleanup on completion
"""

from adk.communication import AgentCommunicator, Message
from agents import DataGathererAgent, SummarizerAgent

def main():
    """
    Main function that orchestrates the ADK demonstration.
    
    Flow:
    1. Sets up communication infrastructure
    2. Initializes and starts agents
    3. Handles user input
    4. Manages message flow with retry mechanism
    5. Performs cleanup
    
    Configuration:
    - MAX_RETRIES: 10 attempts for message reception
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
        print("No query entered. Exiting.")
        return

    # Send initial message to DataGathererAgent
    communicator.send(
        Message(
            sender=user_name,
            receiver="gatherer",
            type="gather",
            payload={"query": query}
        )
    )

    # Wait for summary result (with retry limit)
    MAX_RETRIES = 10
    retries = 0
    while retries < MAX_RETRIES:
        msg = communicator.receive(receiver=user_name, timeout=5.0)
        if msg and msg.type == "summary_result":
            print(f"\nSummary: {msg.payload['summary']}")
            break
        retries += 1
    else:
        print("\nFailed to receive summary message after multiple attempts. Exiting.")

    # Clean up
    gatherer.stop()
    summarizer.stop()

if __name__ == "__main__":
    main()
