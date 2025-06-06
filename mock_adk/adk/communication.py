"""Mock message and communication classes for ADK."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """Message class for agent communication."""
    type: str
    payload: Dict[str, Any]
    sender: str

class AgentCommunicator:
    """Mock communicator for agent message passing."""
    
    def __init__(self) -> None:
        """Initialize communicator."""
        self.messages: List[Message] = []
        
    def send_message(self, message: Message) -> None:
        """Send a message (store in list)."""
        self.messages.append(message)
        
    def receive_message(self) -> Optional[Message]:
        """Receive a message (pop from list)."""
        return self.messages.pop(0) if self.messages else None
