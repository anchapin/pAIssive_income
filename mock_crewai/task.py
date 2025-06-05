"""Mock implementation of CrewAI Task class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .types import AgentVar


class Task:
    """Mock implementation of CrewAI Task class."""

    def __init__(
        self,
        description: str = "",
        agent: Optional[AgentVar] = None,
        task_type: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a mock Task.

        Args:
            description: The description of the task
            agent: The agent assigned to the task
            task_type: The type of task (from TaskType enum)
            kwargs: Additional keyword arguments

        """
        self.description = description
        self.agent = agent
        self.task_type = task_type
        self.async_execution = kwargs.get("async_execution", False)  # Add missing attribute
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"Task(description='{self.description}')"

    def __repr__(self) -> str:
        agent_repr = f"Agent(role='{self.agent.role}')" if self.agent else "None"
        return f"Task(description='{self.description}', agent={agent_repr})"

    def execute(self, context=None) -> str:
        """Mock task execution."""
        if self.agent:
            agent_name = self.agent.name if hasattr(self.agent, "name") else "Agent"
            agent_role = self.agent.role if hasattr(self.agent, "role") else "Unknown Role"
            return f"Executed: {self.description} by {agent_name} ({agent_role})"
        return f"Executed: {self.description}"
