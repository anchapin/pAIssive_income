"""Mock implementation of CrewAI Agent class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .types import TaskVar, AgentType


class Agent:
    """Mock implementation of CrewAI Agent class."""

    def __init__(
        self,
        role: str = "",
        goal: str = "",
        backstory: str = "",
        agent_type: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a mock Agent.

        Args:
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent
            agent_type: The type of agent (from AgentType enum)
            kwargs: Additional keyword arguments

        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.agent_type = agent_type
        self.kwargs = kwargs

    def execute_task(self, task: 'TaskVar', context=None) -> str:
        """
        Execute a task and return a result.

        Args:
            task: The task to execute
            context: Optional context for the task execution

        Returns:
            A string representing the task execution result

        """
        if context:
            return f"Executed task: {task.description} with context: {context}"
        return f"Executed task: {task.description}"

    def __str__(self) -> str:
        """Return a string representation of the agent."""
        return f"Agent(role='{self.role}')"

    def __repr__(self) -> str:
        """Return a string representation of the agent for debugging."""
        return f"Agent(role='{self.role}', goal='{self.goal}', backstory='{self.backstory}')"
