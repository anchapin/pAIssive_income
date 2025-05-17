"""Mock implementation of CrewAI Agent class for testing."""

from __future__ import annotations

from typing import Any


class Agent:
    """Mock implementation of CrewAI Agent class."""

    def __init__(
        self,
        role: str = "",
        goal: str = "",
        backstory: str = "",
        **kwargs: dict[str, Any],
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

    def execute_task(
        self, task: object
    ) -> str:  # Using object to avoid circular import
        """
        Execute a task and return a result.

        Args:
            task: The task to execute

        Returns:
            A string representing the task execution result

        """
        # Access task.description dynamically to avoid circular import issues
        return f"Executed task: {getattr(task, 'description', 'Unknown task')}"
