"""Mock Agent class for ADK."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .communication import AgentCommunicator, Message


class Agent:
    """Base agent class."""

    def __init__(self, name: str) -> None:
        """Initialize an agent."""
        self.name = name
        self.communicator: AgentCommunicator | None = None

    def set_communicator(self, communicator: AgentCommunicator) -> None:
        """Set the communicator for this agent."""
        self.communicator = communicator

    def start(self) -> None:
        """Start the agent. Override in subclasses."""

    def handle_message(self, message: Message) -> Message | None:  # noqa: ARG002
        """Handle a received message. Override in subclasses."""
        return None
