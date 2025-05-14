"""
ADK Demo Agents Module

This module defines the agents and skills used in the ADK demonstration.
It showcases basic agent communication patterns and skill implementation.

Message Types:
    DataGathererAgent:
        Receives: 'gather' with payload {'query': str}
        Sends: 'summarize' with payload {'data': str, 'original_sender': str}

    SummarizerAgent:
        Receives: 'summarize' with payload {'data': str, 'original_sender': str}
        Sends: 'summary_result' with payload {'summary': str}
"""

from adk.agent import Agent
from adk.communication import Message
from adk.memory import SimpleMemory
from adk.skill import Skill


class DataGathererSkill(Skill):
    """
    Simulates data gathering functionality.
    In a real application, this would interact with databases, APIs, etc.
    """

    def run(self, query: str) -> str:
        """
        Simulates data collection process.

        Args:
            query: The search query to gather data for

        Returns:
            Simulated data results
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
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("gather", DataGathererSkill())

    def on_message(self, message: Message) -> None:
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

    # Maximum length for summarized text
    MAX_SUMMARY_LENGTH = 75

    def run(self, data: str) -> str:
        """
        Simulates text summarization.

        Args:
            data: The text to summarize

        Returns:
            Shortened version of the input text
        """
        return (
            data[: self.MAX_SUMMARY_LENGTH] + "..."
            if len(data) > self.MAX_SUMMARY_LENGTH
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
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("summarize", SummarizerSkill())

    def on_message(self, message: Message) -> None:
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
