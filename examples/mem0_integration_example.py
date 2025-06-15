"""
Example script demonstrating mem0 integration with our project.

This script shows how mem0 could be used to enhance our agents with memory capabilities.
It requires the mem0ai package to be installed:

    uv pip install mem0ai

Note: This is a demonstration script and not intended for production use.
"""

from __future__ import annotations

import os
from typing import Optional  # Added Dict back

# Import mem0 - this requires the package to be installed
try:
    from mem0 import Memory
except ImportError:
    # The type: ignore is required for conditional import patterns and dynamic assignment.
    # This is safe because the variable is always set to a valid implementation or None.
    Memory = None  # type: ignore[assignment]


# Mock our existing agent class for demonstration purposes
class MockAgent:
    """Mock agent class to simulate our existing agent implementation."""

    def __init__(self, name: str) -> None:
        """Initialize the mock agent."""
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

    def __init__(self, name: str, user_id: str) -> None:
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
            print("Warning: mem0 not available, running without memory capabilities")

        self.user_id = user_id

    def process_message(
        self, message: str, additional_context: Optional[str] = None
    ) -> str:
        """
        Process a message with memory enhancement.

        This method:
        1. Retrieves relevant memories based on the message
        2. Enhances the context with these memories
        3. Processes the message with the enhanced context
        4. Stores the interaction in memory

        Args:
            message: The user message to process
            additional_context: Optional additional context for the message

        Returns:
            The agent's response

        """
        # Skip memory enhancement if mem0 is not available
        if self.memory is None:
            return super().process_message(
                message, additional_context=additional_context
            )

        # Retrieve relevant memories
        relevant_memories = self.memory.search(
            query=message, user_id=self.user_id, limit=5
        )

        # Enhance the context with memories
        context = self._build_context_from_memories(relevant_memories)
        if additional_context:  # Combine contexts if both exist
            context = f"{context}\n{additional_context}"

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

    def _build_context_from_memories(self, memories: Optional[dict]) -> str:
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


def main() -> None:
    """Demonstrate mem0 integration."""
    # Check if OpenAI API key is available (required by mem0)
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("mem0 requires an OpenAI API key to function properly.")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")

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
        agent.process_message(message)


if __name__ == "__main__":
    main()
