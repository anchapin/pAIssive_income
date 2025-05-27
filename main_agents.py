"""
ADK Demo Agents Module.

This module defines the agents and skills used in the ADK demonstration.
It showcases basic agent communication patterns and skill implementation.
It now includes memory-enhanced versions of agents using mem0 for persistent memory.

Message Types:
    DataGathererAgent:
        Receives: 'gather' with payload {'query': str}
        Sends: 'summarize' with payload {'data': str, 'original_sender': str}

    SummarizerAgent:
        Receives: 'summarize' with payload {'data': str, 'original_sender': str}
        Sends: 'summary_result' with payload {'summary': str}
"""
from __future__ import annotations

import logging
import os
from typing import Optional

# Import standard ADK components
from adk.agent import Agent
from adk.communication import Message
from adk.memory import SimpleMemory
from adk.skill import Skill

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging


# Configure logging


# Import memory-enhanced agents
try:
    from adk_demo.mem0_enhanced_adk_agents import (
        MEM0_AVAILABLE,
        MemoryEnhancedDataGathererAgent,
        MemoryEnhancedSummarizerAgent,
    )
except ImportError:
    MEM0_AVAILABLE = False
    # If adk_demo.mem0_enhanced_adk_agents is not available,
    # create dummy classes to avoid NameError later.
    class MemoryEnhancedDataGathererAgent:  # type: ignore[no-redef]
        pass
    class MemoryEnhancedSummarizerAgent:  # type: ignore[no-redef]
        pass




class DataGathererSkill(Skill):
    """
    Simulates data gathering functionality.

    In a real application, this would interact with databases, APIs, etc.
    """

    def run(self, query: str) -> str:
        """
        Simulate data collection process.

        Args:
            query (str): The search query to gather data for

        Returns:
            str: Simulated data results

        """
        return f"Data found for '{query}': [Example data about '{query}']."


class DataGathererAgent(Agent):
    """
    Agent responsible for handling data gathering requests.

    Uses SimpleMemory for state management and implements a data gathering skill.

    Message Types:
        Receives: 'gather' with payload {'query': str}
        Sends: 'summarize' with payload {'data': str, 'original_sender': str}
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the DataGathererAgent.

        Args:
            name (str): The name of the agent

        """
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("gather", DataGathererSkill())

    def on_message(self, message: Message) -> None:
        """
        Process incoming messages.

        Args:
            message (Message): The message to process

        """
        if message.type == "gather":
            data = self.skills["gather"].run(message.payload["query"])
            # Send gathered data to SummarizerAgent
            self.communicator.send(
                Message(
                    sender=self.name,
                    receiver="summarizer",
                    type="summarize",
                    payload={"data": data, "original_sender": message.sender},
                )
            )


class SummarizerSkill(Skill):
    """
    Simulates data summarization functionality.

    In a real application, this might use an LLM or other summarization technique.
    """

    def run(self, data: str) -> str:
        """
        Summarize text by truncating to a maximum length.

        Args:
            data (str): The text to summarize

        Returns:
            str: Shortened version of the input text

        """
        # Define a constant for the maximum summary length
        max_summary_length = 75
        return (
            data[:max_summary_length] + "..."
            if len(data) > max_summary_length
            else data
        )


class SummarizerAgent(Agent):
    """
    Agent responsible for summarizing gathered data.

    Uses SimpleMemory for state management and implements a summarization skill.

    Message Types:
        Receives: 'summarize' with payload {'data': str, 'original_sender': str}
        Sends: 'summary_result' with payload {'summary': str}
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the SummarizerAgent.

        Args:
            name (str): The name of the agent

        """
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("summarize", SummarizerSkill())

    def on_message(self, message: Message) -> None:
        """
        Process incoming messages.

        Args:
            message (Message): The message to process

        """
        if message.type == "summarize":
            summary = self.skills["summarize"].run(message.payload["data"])
            # Return summary to original requester (user)
            self.communicator.send(
                Message(
                    sender=self.name,
                    receiver=message.payload["original_sender"],
                    type="summary_result",
                    payload={"summary": summary},
                )
            )


def create_agents(use_memory: bool = False, user_id: Optional[str] = None) -> tuple[Agent, Agent]:
    """
    Create and return a pair of agents, optionally using memory enhancement.

    Args:
        use_memory: Whether to use memory-enhanced agents
        user_id: User ID for memory operations (required if use_memory is True)

    Returns:
        A tuple containing (data_gatherer, summarizer) agents

    """
    if use_memory and MEM0_AVAILABLE:
        if not user_id:
            user_id = "default_user"
            logger.warning("No user_id provided, using 'default_user'")

        logger.info(f"Creating memory-enhanced agents with user_id: {user_id}")
        data_gatherer = MemoryEnhancedDataGathererAgent(name="data_gatherer", user_id=user_id)
        summarizer = MemoryEnhancedSummarizerAgent(name="summarizer", user_id=user_id)
    else:
        if use_memory and not MEM0_AVAILABLE:
            logger.warning("mem0 not available, falling back to standard agents")

        logger.info("Creating standard agents without memory enhancement")
        data_gatherer = DataGathererAgent(name="data_gatherer")
        summarizer = SummarizerAgent(name="summarizer")

    return data_gatherer, summarizer


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Check if mem0 is available
    if not MEM0_AVAILABLE:
        logger.warning("mem0 is not installed. Install with: pip install mem0ai")

    # Create agents with memory enhancement if available
    use_memory = os.environ.get("USE_MEMORY", "1") == "1"
    user_id = os.environ.get("USER_ID", "example_user")

    data_gatherer, summarizer = create_agents(use_memory=use_memory, user_id=user_id)

    # Connect the agents
    data_gatherer.communicator.connect(summarizer.communicator)
    summarizer.communicator.connect(data_gatherer.communicator)

    # Example: Send a gather message to the data gatherer
    data_gatherer.on_message(
        Message(
            sender="user",
            receiver="data_gatherer",
            type="gather",
            payload={"query": "AI memory systems"}
        )
    )

    logger.info("Message processing complete")
