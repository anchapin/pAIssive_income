"""Mock implementation of CrewAI Agent class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import TaskType


class Agent:
    """Mock implementation of CrewAI Agent class."""

    def __init__(
        self,
        role: str = "",
        goal: str = "",
        backstory: str = "",
        **kwargs,
    ) -> None:
        """
        Initialize a mock Agent.

        Args:
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent
            kwargs: Additional keyword arguments

        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs

    def execute_task(self, task: TaskType, context=None) -> str:
        """
        Execute a task and return a result.

        Args:
            task: The task to execute
            context: Optional context for the task execution

        Returns:
            A string representing the task execution result

        """
        # Access task.description dynamically to avoid circular import issues
        task_desc = getattr(task, 'description', 'Unknown task')
        if context:
            return f"Executed task: {task_desc} with context: {context}"
        return f"Executed task: {task_desc}"

    def __str__(self) -> str:
        """Return a string representation of the agent."""
        return f"Agent(role='{self.role}')"

    def __repr__(self) -> str:
        """Return a string representation of the agent for debugging."""
        return f"Agent(role='{self.role}', goal='{self.goal}', backstory='{self.backstory}')"
