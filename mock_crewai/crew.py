"""Mock implementation of CrewAI Crew class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from .agent import Agent
    from .task import Task


class Crew:
    """Mock implementation of CrewAI Crew class."""

    def __init__(
        self,
        agents: Optional[list[Union[Agent, Any]]] = None,
        tasks: Optional[list[Union[Task, Any]]] = None,
        **kwargs: dict[str, Any],
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

    def kickoff(self) -> str:
        """
        Execute the crew's tasks and return a result.

        Returns:
            A string representing the crew execution result

        """
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff
