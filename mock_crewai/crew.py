"""Mock implementation of CrewAI Crew class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .types import AgentVar, TaskVar


class Crew:
    """Mock implementation of CrewAI Crew class."""

    def __init__(
        self,
        agents: Optional[list[AgentVar]] = None,
        tasks: Optional[list[TaskVar]] = None,
        crew_type: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a mock Crew.

        Args:
            agents: List of agents in the crew
            tasks: List of tasks for the crew
            crew_type: The type of crew (from CrewType enum)
            kwargs: Additional keyword arguments

        """
        self.agents = agents or []
        self.tasks = tasks or []
        self.crew_type = crew_type
        self.memory = kwargs.get("memory", False)  # Add missing attribute
        self.kwargs = kwargs

    def kickoff(self, inputs=None):
        """
        Execute the crew's tasks and return a result.

        Args:
            inputs: Optional inputs for the crew execution

        Returns:
            A string or list representing the crew execution result

        """
        if inputs:
            return f"Mock crew output with inputs: {inputs}"
        # Return list format for some tests that expect it
        if self.agents and self.tasks:
            results = []
            for task in self.tasks:
                if task.agent:
                    results.append(f"Executed: {task.description} by {task.agent.name if hasattr(task.agent, 'name') else 'Agent'} ({task.agent.role})")
                else:
                    results.append(f"Executed: {task.description}")
            return results
        return "Mock crew output"

    # Alias for backward compatibility (same method object)
    run = kickoff

    def __str__(self):
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"

    def __repr__(self):
        return f"Crew(agents={self.agents}, tasks={self.tasks})"
