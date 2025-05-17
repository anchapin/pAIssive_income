"""Mock implementation of CrewAI Crew class for testing."""

from __future__ import annotations

from typing import Any, Optional


class Crew:
    """Mock implementation of CrewAI Crew class."""

    def __init__(
        self,
        agents: Optional[list[Any]] = None,
        tasks: Optional[list[Any]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a mock Crew.

        Args:
            agents: List of agents in the crew
            tasks: List of tasks for the crew
            kwargs: Additional keyword arguments

        """
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs

    def kickoff(self, inputs=None) -> str:
        """
        Execute the crew's tasks and return a result.

        Args:
            inputs: Optional inputs for the crew execution

        Returns:
            A string representing the crew execution result

        """
        if inputs:
            return f"Mock crew output with inputs: {inputs}"
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff

    def __str__(self):
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"

    def __repr__(self):
        return f"Crew(agents={self.agents}, tasks={self.tasks})"
