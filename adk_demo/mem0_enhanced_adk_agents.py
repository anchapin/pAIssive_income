"""
mem0-Enhanced ADK Agents.

This module provides memory-enhanced versions of the ADK agents using mem0.
It extends the ADK agent implementation with persistent memory capabilities.

Usage:
    from adk_demo.mem0_enhanced_adk_agents import MemoryEnhancedDataGathererAgent

    # Create a memory-enhanced agent
    agent = MemoryEnhancedDataGathererAgent(name="DataGatherer", user_id="user123")

    # Process messages with memory enhancement
    response = agent.process_message(message)

Requirements:
    - mem0ai package: pip install mem0ai
    - adk package: pip install adk
"""

from __future__ import annotations

import logging
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging

# Import ADK components
try:
    from adk.agent import Agent
    from adk.communication import Message
    from adk.memory import SimpleMemory
    from adk.skill import Skill
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    # Define placeholder classes for type hints
    class Agent:
        """Placeholder for Agent class when ADK is not installed."""

        def __init__(self, name: str) -> None:
            self.name = name
        
        def handle_message(self, message: "Message") -> Optional["Message"]:
            """Handle a received message. Override in subclasses."""
            return None
        
        def add_skill(self, name: str, skill: "Skill") -> None:
            """Add a skill to the agent."""
            if not hasattr(self, 'skills'):
                self.skills = {}
            self.skills[name] = skill

    class Message:
        """Placeholder for Message class when ADK is not installed."""

        def __init__(self, type: str, payload: Dict[str, Any], sender: str) -> None:
            self.type = type
            self.payload = payload
            self.sender = sender

    class SimpleMemory:
        """Placeholder for SimpleMemory class when ADK is not installed."""

        def __init__(self) -> None:
            pass

    class Skill:
        """Placeholder for Skill class when ADK is not installed."""

        def run(self, *args: Any, **kwargs: Any) -> Any:
            pass

# Import mem0 components
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None  # type: ignore

# Import existing skills from adk_demo
if ADK_AVAILABLE:
    try:
        from adk_demo.agents import DataGathererSkill, SummarizerSkill
    except ImportError:
        # Define placeholder skills if not available
        class DataGathererSkill(Skill):
            """Placeholder for DataGathererSkill."""

            def run(self, query: str) -> str:
                return f"Data found for '{query}': [Example data]"

        class SummarizerSkill(Skill):
            """Placeholder for SummarizerSkill."""

            def run(self, data: str) -> str:
                return f"Summary of data: {data[:50]}..."
else:
    # Define placeholder skills if ADK is not available
    class DataGathererSkill(Skill):
        """Placeholder for DataGathererSkill."""

        def run(self, query: str) -> str:
            return f"Data found for '{query}': [Example data]"

    class SummarizerSkill(Skill):
        """Placeholder for SummarizerSkill."""

        def run(self, data: str) -> str:
            return f"Summary of data: {data[:50]}..."

# logger is now initialized globally earlier

class MemoryEnhancedAgent(Agent):
    """
    Base class for memory-enhanced ADK agents.

    This class extends the ADK Agent with persistent memory capabilities
    using mem0. It adds memory hooks to key lifecycle points:
    - Message processing
    - Skill execution
    - Response generation
    """

    def __init__(self, name: str, user_id: str) -> None:
        """
        Initialize a memory-enhanced agent.

        Args:
            name: The name of the agent
            user_id: The user ID for memory storage and retrieval

        """
        super().__init__(name)

        # Initialize skills dictionary
        self.skills = {}

        # Initialize ADK SimpleMemory for compatibility
        self.simple_memory = SimpleMemory()

        # Initialize mem0 memory if available
        if MEM0_AVAILABLE:
            self.memory = Memory()
            logger.info(f"mem0 memory initialized for agent {name}")
        else:
            self.memory = None
            logger.warning("mem0 not available. Install with: pip install mem0ai")

        # Set user ID for memory operations
        self.user_id = user_id

        # Store agent creation in memory
        self._store_memory(f"Agent {name} created with user ID: {user_id}")

    def add_skill(self, name: str, skill: "Skill") -> None:
        """
        Add a skill to the agent.

        Args:
            name: The name of the skill
            skill: The skill instance
        """
        self.skills[name] = skill

    def handle_message(self, message: Message) -> Optional[Message]:
        """
        Handle a message with memory enhancement.

        This method:
        1. Retrieves relevant memories based on the message
        2. Enhances the message with these memories
        3. Processes the message with the enhanced context
        4. Stores the interaction in memory

        Args:
            message: The message to handle

        Returns:
            The response message

        """
        # Skip memory enhancement if mem0 is not available
        if self.memory is None:
            return super().handle_message(message)

        # Extract query from message payload
        query = self._extract_query_from_message(message)

        # Retrieve relevant memories
        memories = self._retrieve_relevant_memories(query)
        logger.debug(f"Retrieved {len(memories)} relevant memories")

        # Enhance message with memories (in a real implementation, this would modify the message)
        enhanced_message = self._enhance_message_with_memories(message, memories)

        # Process the enhanced message
        response = super().handle_message(enhanced_message)

        # Store the interaction in memory
        if response is not None:
            self._store_interaction(message, response)

        return response

    def _extract_query_from_message(self, message: Message) -> str:
        """
        Extract a query string from a message.

        Args:
            message: The message to extract from

        Returns:
            A query string for memory retrieval

        """
        # Extract query based on message type
        if message.type == "gather":
            return message.payload.get("query", "")
        if message.type == "summarize":
            return message.payload.get("data", "")
        # Default to message type as query
        return f"Message of type {message.type} from {message.sender}"

    def _enhance_message_with_memories(self, message: Message, memories: List[Dict[str, Any]]) -> Message:
        """
        Enhance a message with relevant memories.

        Args:
            message: The original message
            memories: The relevant memories

        Returns:
            The enhanced message

        """
        # TODO: This is intentionally a placeholder for future enhancement.
        # In future iterations, this method will be implemented to inject
        # relevant memories into the message context to provide the agent
        # with historical context for better decision making.
        #
        # For now, we simply return the original message unchanged.
        return message

    def _store_interaction(self, message: Message, response: Message) -> None:
        """
        Store an interaction in memory.

        Args:
            message: The incoming message
            response: The outgoing response

        """
        # Create a conversation-style memory
        conversation = [
            {"role": "user", "content": f"{message.type}: {message.payload}"},
            {"role": "assistant", "content": f"{response.type}: {response.payload}"}
        ]

        # Store in memory
        self._store_memory(
            conversation,
            metadata={
                "message_type": message.type,
                "response_type": response.type,
                "sender": message.sender
            }
        )

    def _store_memory(self, content: Union[str, List[Dict[str, str]]], metadata: Optional[Dict[str, str]] = None) -> None:
        """
        Store a memory using mem0.

        Args:
            content: The content to store (string or conversation messages)
            metadata: Optional metadata for the memory

        """
        if self.memory is None:
            return

        try:
            self.memory.add(
                content,
                user_id=self.user_id,
                metadata=metadata or {}
            )
            logger.debug(f"Memory stored: {content[:50]}..." if isinstance(content, str) else "Conversation stored")
        except Exception as e:
            logger.exception(f"Error storing memory: {e}")

    def _retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for a query.

        Args:
            query: The query string
            limit: Maximum number of memories to retrieve

        Returns:
            List of relevant memories

        """
        if self.memory is None or not query:
            return []

        try:
            # Search for relevant memories
            return self.memory.search(
                query=query,
                user_id=self.user_id,
                limit=limit
            )
        except Exception as e:
            logger.exception(f"Error retrieving memories: {e}")
            return []


class MemoryEnhancedDataGathererAgent(MemoryEnhancedAgent):
    """
    Memory-enhanced version of the DataGathererAgent.

    This agent is responsible for handling data gathering requests
    and has persistent memory capabilities.
    """

    def __init__(self, name: str, user_id: str) -> None:
        """
        Initialize a memory-enhanced data gatherer agent.

        Args:
            name: The name of the agent
            user_id: The user ID for memory storage and retrieval

        """
        super().__init__(name, user_id)

        # Add the data gatherer skill
        self.add_skill("gather", DataGathererSkill())

        # Store agent specialization in memory
        self._store_memory(
            f"Agent {name} specialized in data gathering",
            metadata={"specialization": "data_gathering"}
        )


class MemoryEnhancedSummarizerAgent(MemoryEnhancedAgent):
    """
    Memory-enhanced version of the SummarizerAgent.

    This agent is responsible for summarizing gathered data
    and has persistent memory capabilities.
    """

    def __init__(self, name: str, user_id: str) -> None:
        """
        Initialize a memory-enhanced summarizer agent.

        Args:
            name: The name of the agent
            user_id: The user ID for memory storage and retrieval

        """
        super().__init__(name, user_id)

        # Add the summarizer skill
        self.add_skill("summarize", SummarizerSkill())

        # Store agent specialization in memory
        self._store_memory(
            f"Agent {name} specialized in data summarization",
            metadata={"specialization": "summarization"}
        )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    try:
        # Check if dependencies are available
        if not ADK_AVAILABLE:
            logger.error("ADK is not installed. Install with: pip install adk")
        elif not MEM0_AVAILABLE:
            logger.error("mem0 is not installed. Install with: pip install mem0ai")
        else:
            # Create memory-enhanced agents
            gatherer = MemoryEnhancedDataGathererAgent(name="DataGatherer", user_id="example_user")
            summarizer = MemoryEnhancedSummarizerAgent(name="Summarizer", user_id="example_user")

            # Create a gather message
            gather_message = Message(
                type="gather",
                payload={"query": "AI memory systems"},
                sender="user"
            )

            # Process the message
            logger.info("Sending gather message to data gatherer agent")
            response = gatherer.handle_message(gather_message)

            if response:
                logger.info(f"Received response: {response.type} - {response.payload}")

                # Forward to summarizer
                logger.info("Forwarding data to summarizer agent")
                summarize_message = Message(
                    type="summarize",
                    payload={"data": response.payload.get("data", ""), "original_sender": "DataGatherer"},
                    sender="DataGatherer"
                )

                summary_response = summarizer.handle_message(summarize_message)

                if summary_response:
                    logger.info(f"Received summary: {summary_response.payload.get('summary', '')}")
            else:
                logger.error("No response received from data gatherer agent")
    except Exception as e:
        logger.exception(f"An error occurred during example execution: {e}")
