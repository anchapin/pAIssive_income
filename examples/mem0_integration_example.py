"""
Example script demonstrating mem0 integration with our project.

This script shows how mem0 could be used to enhance our agents with memory capabilities.
It requires the mem0ai package to be installed:

    pip install mem0ai

Note: This is a demonstration script and not intended for production use.
"""

import os
from typing import Dict, Optional
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import mem0 - this requires the package to be installed
try:
    from mem0 import Memory
except ImportError:
    logger.error("mem0ai package not installed. Please install it with: pip install mem0ai")
    Memory = None  # type: ignore[assignment]


# Mock our existing agent class for demonstration purposes
class MockAgent:
    """Mock agent class to simulate our existing agent implementation."""

    def __init__(self, name: str):
        self.name = name

    def process_message(
        self, message: str, additional_context: Optional[str] = None
    ) -> str:
        """Process a message and return a response."""
        if additional_context:
            return f"Agent {self.name} responding to '{message}' with context: {additional_context}"
        return f"Agent {self.name} responding to '{message}'"


class MemoryEnhancedAgent(MockAgent):
    """Agent enhanced with mem0 memory capabilities."""

    def __init__(self, name: str, user_id: str):
        """
        Initialize a memory-enhanced agent.

        Args:
            name: The name of the agent
            user_id: The ID of the user interacting with the agent

        """
        super().__init__(name)

        # Initialize mem0 memory
        if Memory is not None:
            self.memory = Memory()
        else:
            # Fallback if mem0 is not installed
            self.memory = None
            logger.warning("mem0 not available, running without memory capabilities")

        self.user_id = user_id

    def process_message(self, message: str) -> str:
        """
        Process a message with memory enhancement.

        This method:
        1. Retrieves relevant memories based on the message
        2. Enhances the context with these memories
        3. Processes the message with the enhanced context
        4. Stores the interaction in memory

        Args:
            message: The user message to process

        Returns:
            The agent's response

        """
        # Skip memory enhancement if mem0 is not available
        if self.memory is None:
            return super().process_message(message)

        # Retrieve relevant memories
        relevant_memories = self.memory.search(
            query=message, user_id=self.user_id, limit=5
        )

        # Enhance the context with memories
        context = self._build_context_from_memories(relevant_memories)

        # Process with enhanced context
        response = super().process_message(message, additional_context=context)

        # Store the interaction in memory
        self.memory.add(
            [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response},
            ],
            user_id=self.user_id,
        )

        return response

    def _build_context_from_memories(self, memories: Optional[Dict]) -> str:
        """
        Convert memories to a format usable by the agent.

        Args:
            memories: The memories retrieved from mem0

        Returns:
            A string representation of the memories

        """
        # Handle case where no memories are found
        if not memories or "results" not in memories:
            return "No relevant memories found."

        # Format memories as a bulleted list
        memory_str = "\n".join([f"- {m['memory']}" for m in memories["results"]])
        return f"Relevant user information:\n{memory_str}"


def main():
    """Main function to demonstrate mem0 integration."""
    # Check if OpenAI API key is available (required by mem0)
    if "OPENAI_API_KEY" not in os.environ:
        logger.warning("OPENAI_API_KEY environment variable not set.")
        logger.warning("mem0 requires an OpenAI API key to function properly.")
        logger.warning("Set it with: export OPENAI_API_KEY='your-api-key'")

    # Create a memory-enhanced agent
    agent = MemoryEnhancedAgent(name="MemoryBot", user_id="demo_user")

    # Simulate a conversation
    messages = [
        "Hi, my name is Alex and I like Italian food.",
        "What kind of food do I like?",
        "I also enjoy hiking on weekends.",
        "What are my hobbies?",
        "I'm allergic to peanuts, so please remember that.",
        "What should I avoid eating?",
    ]

    # Process each message and print the response
    for message in messages:
        logger.info("\nUser: %s", message)
        response = agent.process_message(message)
        logger.info("Agent: %s", response)


if __name__ == "__main__":
    main()
