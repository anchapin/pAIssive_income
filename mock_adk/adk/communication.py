"""Mock message and communication classes for ADK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    """Message class for agent communication."""

    type: str
    payload: dict[str, Any]
    sender: str


class AgentCommunicator:
    """Mock communicator for agent message passing."""

    def __init__(self) -> None:
        """Initialize communicator."""
        self.messages: list[Message] = []

    def send_message(self, message: Message) -> None:
        """Send a message (store in list)."""
        self.messages.append(message)

    def receive_message(self) -> Message | None:
        """Receive a message (pop from list)."""
        return self.messages.pop(0) if self.messages else None
