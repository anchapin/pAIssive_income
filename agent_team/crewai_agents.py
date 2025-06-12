"""
CrewAI Multi-Agent Orchestration.

This module defines example CrewAI agents and teams for collaborative AI workflows.
Adapt and extend these scaffolds to fit your use-case.

- Docs: https://docs.crewai.com/
"""

from __future__ import annotations

from typing import Optional, Protocol, Union, runtime_checkable


# Protocols for type safety
@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol for CrewAI Agent."""

    role: str
    goal: str
    backstory: str

    def __init__(self, role: str = "", goal: str = "", backstory: str = "") -> None:
        """Initialize the Agent with role, goal, and backstory."""


@runtime_checkable
class TaskProtocol(Protocol):
    """Protocol for CrewAI Task."""

    description: str
    agent: Optional[AgentProtocol]

    def __init__(
        self, description: str = "", agent: Optional[AgentProtocol] = None
    ) -> None:
        """Initialize the Task with description and optional agent."""


@runtime_checkable
class CrewProtocol(Protocol):
    """Protocol for CrewAI Crew (team)."""

    agents: list[AgentProtocol]
    tasks: list[TaskProtocol]

    def __init__(
        self,
        agents: Optional[list[AgentProtocol]] = None,
        tasks: Optional[list[TaskProtocol]] = None,
    ) -> None:
        """Initialize the Crew with agents and tasks."""

    def run(self) -> None:
        """Run the Crew."""

    def kickoff(self) -> None:
        """Kickoff the Crew."""


crewai_available = False

try:
    from crewai import Agent as RealAgent
    from crewai import Crew as RealCrew
    from crewai import Task as RealTask

    crewai_available = True
    # The type: ignore is required for conditional import patterns and dynamic assignment to Protocol types.
    # This is safe because the variable is always set to a valid implementation or placeholder.
    Agent: type[AgentProtocol] = RealAgent  # type: ignore[assignment]
    # The type: ignore is required for conditional import patterns and dynamic assignment to Protocol types.
    # This is safe because the variable is always set to a valid implementation or placeholder.
    Task: type[TaskProtocol] = RealTask  # type: ignore[assignment]
    # The type: ignore is required for conditional import patterns and dynamic assignment to Protocol types.
    # This is safe because the variable is always set to a valid implementation or placeholder.
    Crew: type[CrewProtocol] = RealCrew  # type: ignore[assignment]
except ImportError:

    class AgentPlaceholder:
        """Placeholder for Agent class when crewai is not installed."""

        def __init__(self, role: str = "", goal: str = "", backstory: str = "") -> None:
            """Initialize the placeholder Agent with role, goal, and backstory."""
            self.role = role
            self.goal = goal
            self.backstory = backstory

    class TaskPlaceholder:
        """Placeholder for Task class when crewai is not installed."""

        def __init__(
            self, description: str = "", agent: Optional[AgentProtocol] = None
        ) -> None:
            """Initialize the placeholder Task with description and agent."""
            self.description = description
            self.agent = agent

    class CrewPlaceholder:
        """Placeholder for Crew class when crewai is not installed."""

        def __init__(
            self,
            agents: Optional[list[AgentProtocol]] = None,
            tasks: Optional[list[TaskProtocol]] = None,
        ) -> None:
            """Initialize the placeholder Crew with agents and tasks."""
            self.agents = agents or []
            self.tasks = tasks or []

        def run(self) -> None:
            """Raise ImportError because CrewAI is not installed."""
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

        def kickoff(self) -> None:
            """Raise ImportError because CrewAI is not installed."""
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

    Agent: type[AgentProtocol] = AgentPlaceholder
    Task: type[TaskProtocol] = TaskPlaceholder
    Crew: type[CrewProtocol] = CrewPlaceholder

    import warnings

    warnings.warn(
        "CrewAI is not installed. This module will not function properly. Install with: pip install '.[agents]'",
        stacklevel=2,
    )

# Example: Define agent roles
data_gatherer: AgentProtocol = Agent(
    role="Data Gatherer",
    goal="Collect relevant information and data for the project",
    backstory="An AI specialized in data collection from APIs and databases.",
)

analyzer: AgentProtocol = Agent(
    role="Analyzer",
    goal="Analyze collected data and extract actionable insights",
    backstory="An AI expert in analytics and pattern recognition.",
)

writer: AgentProtocol = Agent(
    role="Writer",
    goal="Generate clear, readable reports from analyzed data",
    backstory="An AI that excels at communicating insights in natural language.",
)

# Example: Define tasks
task_collect: TaskProtocol = Task(
    description="Gather all relevant data from internal and external sources.",
    agent=data_gatherer,
)
task_analyze: TaskProtocol = Task(
    description="Analyze gathered data for trends and anomalies.", agent=analyzer
)
task_report: TaskProtocol = Task(
    description="Write a summary report based on analysis.", agent=writer
)

# Example: Assemble into a Crew (team)
reporting_team: CrewProtocol = Crew(
    agents=[data_gatherer, analyzer, writer],
    tasks=[task_collect, task_analyze, task_report],
)

if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    if not crewai_available:
        logger.error("CrewAI is not installed. Install with: pip install '.[agents]'")
    else:
        try:
            reporting_team.run()
            logger.info("CrewAI reporting workflow completed.")
        except Exception:
            logger.exception("Error running CrewAI workflow")


class CrewAIAgentTeam:
    """
    CrewAI Agent Team implementation for integration with other modules.

    This class provides a higher-level interface for working with CrewAI agents,
    tasks, and crews. It can be used to create and run agent teams from other
    parts of the application.
    """

    def __init__(self, llm_provider: object = None) -> None:
        """Initialize CrewAIAgentTeam with optional LLM provider."""
        self.llm_provider = llm_provider
        self.agents: list[AgentProtocol] = []
        self.tasks: list[TaskProtocol] = []
        self.api_client = None

    def add_agent(self, role: str, goal: str, backstory: str) -> AgentProtocol:
        """Add an agent to the team."""
        agent = Agent(role=role, goal=goal, backstory=backstory)
        self.agents.append(agent)
        return agent

    def add_task(
        self, description: str, agent: Union[str, AgentProtocol]
    ) -> TaskProtocol:
        """Add a task to the team."""
        if isinstance(agent, str):
            agent_obj = next(
                (a for a in self.agents if getattr(a, "role", None) == agent), None
            )
            if not agent_obj:
                error_msg = f"Agent with role '{agent}' not found"
                raise ValueError(error_msg)
        else:
            agent_obj = agent
        task = Task(description=description, agent=agent_obj)
        self.tasks.append(task)
        return task

    def _create_crew(self) -> CrewProtocol:
        """Create a Crew instance from the current agents and tasks."""
        return Crew(agents=self.agents, tasks=self.tasks)

    def run(self) -> object:
        """Run the CrewAIAgentTeam."""
        if not crewai_available:
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)
        crew = self._create_crew()
        return crew.kickoff()


# Next steps:
# - Replace example agents, goals, and tasks with project-specific logic.
# - Integrate with application triggers or API endpoints as needed.
# - See agent_team/README.md (to be created) for setup and usage.
