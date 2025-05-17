"""
Fallback mock CrewAI module for testing and development.

This module provides mock implementations of the CrewAI classes
when the actual CrewAI package is not installed.
"""

from __future__ import annotations

from typing import Optional

# Define version attribute at the module level
__version__ = "0.120.0"


class Agent:
    """Mock implementation of CrewAI Agent class."""

    def __init__(
        self, role: str = "", goal: str = "", backstory: str = "", **kwargs: dict
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

    def execute_task(self, task: Task) -> str:
        """
        Execute a task.

        Args:
            task: The task to execute

        Returns:
            A string indicating the task was executed

        """
        return f"Executed task: {task.description}"

    def __str__(self) -> str:
        """Return a string representation of the agent."""
        return f"Agent(role='{self.role}', goal='{self.goal}')"

    def __repr__(self) -> str:
        """Return a string representation of the agent for debugging."""
        return f"Agent(role='{self.role}', goal='{self.goal}', backstory='{self.backstory}')"


class Task:
    """Mock implementation of CrewAI Task class."""

    def __init__(
        self, description: str = "", agent: Agent = None, **kwargs: dict
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

    def __str__(self) -> str:
        """Return a string representation of the task."""
        agent_role = self.agent.role if self.agent else "None"
        return f"Task(description='{self.description}', agent='{agent_role}')"

    def __repr__(self) -> str:
        """Return a string representation of the task for debugging."""
        agent_role = self.agent.role if self.agent else "None"
        return f"Task(description='{self.description}', agent='{agent_role}', kwargs={self.kwargs})"


class Crew:
    """Mock implementation of CrewAI Crew class."""

    def __init__(
        self,
        agents: Optional[list[Agent]] = None,
        tasks: Optional[list[Task]] = None,
        **kwargs: dict,
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
        Start the crew's execution.

        Args:
            inputs: Optional inputs for the crew execution

        Returns:
            A mock output string

        """
        if inputs:
            return f"Mock crew output with inputs: {inputs}"
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff

    def __str__(self) -> str:
        """Return a string representation of the crew."""
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"

    def __repr__(self) -> str:
        """Return a string representation of the crew for debugging."""
        return f"Crew(agents={self.agents}, tasks={self.tasks}, kwargs={self.kwargs})"
