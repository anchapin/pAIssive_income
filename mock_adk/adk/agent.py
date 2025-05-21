"""Mock Agent class for ADK."""
from typing import Optional, Any
from .communication import Message, AgentCommunicator

class Agent:
    """Base agent class."""
    
    def __init__(self, name: str) -> None:
        """Initialize an agent."""
        self.name = name
        self.communicator: Optional[AgentCommunicator] = None
        
    def set_communicator(self, communicator: AgentCommunicator) -> None:
        """Set the communicator for this agent."""
        self.communicator = communicator
        
    def start(self) -> None:
        """Start the agent. Override in subclasses."""
        pass
        
    def handle_message(self, message: Message) -> Optional[Message]:
        """Handle a received message. Override in subclasses."""
        return None
