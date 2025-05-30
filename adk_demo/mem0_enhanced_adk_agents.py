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
from abc import abstractmethod
from typing import Any, Optional, Protocol, TypeVar, Union, runtime_checkable

# Define type variables with proper naming convention
MemoryResult_co = TypeVar("MemoryResult_co", bound=dict[str, object], covariant=True)


@runtime_checkable
class Agent(Protocol):
    """Protocol defining the required interface for agents."""

    name: str

    def __init__(self, name: str) -> None:
        """Initialize an agent with a name."""
        ...

    def handle_message(self, message: Message) -> Optional[Message]:
        """Handle an incoming message and optionally return a response."""
        ...


@runtime_checkable
class Message(Protocol):
    """Protocol defining the required interface for messages."""

    type: str
    payload: dict[str, object]
    sender: str

    def __init__(self, msg_type: str, payload: dict[str, object], sender: str) -> None:
        """Initialize a message with type, payload, and sender."""
        ...


@runtime_checkable
class Skill(Protocol):
    """Protocol defining the required interface for skills."""

    @abstractmethod
    def run(self, *args: object, **kwargs: dict[str, object]) -> object:
        """Run the skill with given arguments."""
        ...


# Import ADK components
try:
    from adk.agent import Agent as AdkAgent
    from adk.communication import Message as AdkMessage
    from adk.memory import SimpleMemory
    from adk.skill import Skill as AdkSkill

    ADK_AVAILABLE = True
    BaseAgent = AdkAgent
    BaseMessage = AdkMessage
    BaseSkill = AdkSkill
except ImportError:
    ADK_AVAILABLE = False

    class SimpleMemory:
        """Placeholder for SimpleMemory when ADK is not installed."""

        def __init__(self) -> None:
            """Initialize an empty SimpleMemory placeholder."""

    BaseAgent = Agent
    BaseMessage = Message
    BaseSkill = Skill

# Import mem0 components
try:
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None  # type: ignore[assignment]

# Import existing skills from adk_demo
if ADK_AVAILABLE:
    try:
        from adk_demo.agents import DataGathererSkill, SummarizerSkill
    except ImportError:
        # Define placeholder skills if not available
        class DataGathererSkill(BaseSkill):
            """Data gatherer skill placeholder."""

            def run(self, query: str) -> str:
                """Run the data gatherer skill."""
                return f"Data found for '{query}': [Example data]"

        class SummarizerSkill(BaseSkill):
            """Summarizer skill placeholder."""

            def run(self, data: str) -> str:
                """Run the summarizer skill."""
                return f"Summary of data: {data[:50]}..."
else:
    # Define placeholder skills if ADK is not available
    class DataGathererSkill(BaseSkill):
        """Data gatherer skill placeholder."""

        def run(self, query: str) -> str:
            """Run the data gatherer skill."""
            return f"Data found for '{query}': [Example data]"

    class SummarizerSkill(BaseSkill):
        """Summarizer skill placeholder."""

        def run(self, data: str) -> str:
            """Run the summarizer skill."""
            return f"Summary of data: {data[:50]}..."


# Configure logging
logger = logging.getLogger(__name__)


class MemoryEnhancedAgent(BaseAgent):
    """Base class for memory-enhanced ADK agents."""

    def __init__(self, name: str, user_id: str) -> None:
        """Initialize a memory-enhanced agent."""
        super().__init__(name)

        # Initialize ADK SimpleMemory for compatibility
        self.simple_memory = SimpleMemory()

        # Initialize mem0 memory if available
        if MEM0_AVAILABLE:
            self.memory = Memory()
            logger.info("mem0 memory initialized for agent %s", name)
        else:
            self.memory = None
            logger.warning("mem0 not available. Install with: pip install mem0ai")

        # Set user ID for memory operations
        self.user_id = user_id

        # Store agent creation in memory
        self._store_memory(f"Agent {name} created with user ID: {user_id}")

    def handle_message(self, message: BaseMessage) -> Optional[BaseMessage]:
        """Handle a message with memory enhancement."""
        if self.memory is None:
            return super().handle_message(message)

        # Extract query from message payload
        query = self._extract_query_from_message(message)

        # Retrieve relevant memories
        memories = self._retrieve_relevant_memories(query)
        logger.debug("Retrieved %d relevant memories", len(memories))

        # Enhance message with memories
        enhanced_message = self._enhance_message_with_memories(message, memories)

        # Process the enhanced message
        response = super().handle_message(enhanced_message)

        # Store the interaction in memory
        if response is not None:
            self._store_interaction(message, response)

        return response

    def _extract_query_from_message(self, message: BaseMessage) -> str:
        """Extract a query string from a message."""
        if message.type == "gather":
            return str(message.payload.get("query", ""))
        if message.type == "summarize":
            return str(message.payload.get("data", ""))
        return f"Message of type {message.type} from {message.sender}"

    def _enhance_message_with_memories(
        self, message: BaseMessage, memories: list[dict[str, Any]]
    ) -> BaseMessage:
        """
        Enhance a message with relevant memories.

        Args:
            message: The original message
            memories: The relevant memories to enhance the message with

        Returns:
            The enhanced message with memories incorporated into its payload

        """
        if not memories:
            return message

        # Format memories as a string
        memory_text = "\n".join(
            f"- {memory.get('text', memory.get('memory', str(memory)))}"
            for memory in memories
        )

        # Create enhanced payload with memories
        enhanced_payload = dict(message.payload)
        enhanced_payload["memories"] = f"""
Previous relevant memories:
{memory_text}
"""  # Create a new message with the enhanced payload
        return type(message)(
            type=message.type, payload=enhanced_payload, sender=message.sender
        )

    def _store_interaction(self, message: BaseMessage, response: BaseMessage) -> None:
        """Store an interaction in memory."""
        conversation = [
            {"role": "user", "content": f"{message.type}: {message.payload}"},
            {"role": "assistant", "content": f"{response.type}: {response.payload}"},
        ]

        self._store_memory(
            conversation,
            metadata={
                "message_type": message.type,
                "response_type": response.type,
                "sender": message.sender,
            },
        )

    def _store_memory(
        self,
        content: Union[str, list[dict[str, str]]],
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Store a memory using mem0."""
        if self.memory is None:
            return

        try:
            self.memory.add(content, user_id=self.user_id, metadata=metadata or {})
            if isinstance(content, str):
                logger.debug("Memory stored: %.50s...", content)
            else:
                logger.debug("Conversation stored")
        except (OSError, ValueError):
            logger.exception("Error storing memory")

    def _retrieve_relevant_memories(
        self, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve relevant memories for a query."""
        if self.memory is None or not query:
            return []

        try:
            # Search for relevant memories
            return self.memory.search(query=query, user_id=self.user_id, limit=limit)
        except (OSError, ValueError):
            logger.exception("Error retrieving memories")
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
            metadata={"specialization": "data_gathering"},
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
            metadata={"specialization": "summarization"},
        )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Check if dependencies are available
    if not ADK_AVAILABLE:
        logger.error("ADK is not installed. Install with: pip install adk")
    elif not MEM0_AVAILABLE:
        logger.error("mem0 is not installed. Install with: pip install mem0ai")
    else:
        # Create memory-enhanced agents
        gatherer = MemoryEnhancedDataGathererAgent(
            name="DataGatherer", user_id="example_user"
        )
        summarizer = MemoryEnhancedSummarizerAgent(
            name="Summarizer", user_id="example_user"
        )

        # Create a gather message
        gather_message = Message(
            type="gather", payload={"query": "AI memory systems"}, sender="user"
        )

        # Process the message
        logger.info("Sending gather message to data gatherer agent")
        response = gatherer.handle_message(gather_message)

        if response:
            logger.info("Received response: %s - %s", response.type, response.payload)

            # Forward to summarizer
            logger.info("Forwarding data to summarizer agent")
            summarize_message = Message(
                type="summarize",
                payload={
                    "data": response.payload.get("data", ""),
                    "original_sender": "DataGatherer",
                },
                sender="DataGatherer",
            )

            summary_response = summarizer.handle_message(summarize_message)

            if summary_response:
                logger.info(
                    "Received summary: %s", summary_response.payload.get("summary", "")
                )
        else:
            logger.error("No response received from data gatherer agent")
