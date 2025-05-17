"""Mock implementation of CrewAI Task class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .types import AgentType


class Task:
    """Mock implementation of CrewAI Task class."""

    def __init__(
        self,
        description: str = "",
        agent: Optional[AgentType] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a mock Task.

        Args:
            description: The description of the task
            agent: The agent assigned to the task
            kwargs: Additional keyword arguments

        """
        self.description = description
        self.agent = agent
        self.kwargs = kwargs

    def __str__(self):
        return f"Task(description='{self.description}')"

    def __repr__(self):
        agent_repr = f"Agent(role='{self.agent.role}')" if self.agent else "None"
        return f"Task(description='{self.description}', agent={agent_repr})"
