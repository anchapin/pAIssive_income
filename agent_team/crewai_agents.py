"""
CrewAI Multi-Agent Orchestration.

This module defines example CrewAI agents and teams for collaborative AI workflows.
Adapt and extend these scaffolds to fit your use-case.

- Docs: https://docs.crewai.com/
"""

from __future__ import annotations

import logging
import re
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

from common_utils.tooling import list_tools

try:
    from crewai import Agent as RealAgent
    from crewai import Crew as RealCrew
    from crewai import Task as RealTask

    crewai_available = True
    # type: ignore required for conditional import patterns and Protocol assignment
    # This is safe because the variable is always set to a valid implementation
    Agent: type[AgentProtocol] = RealAgent  # type: ignore[assignment]
    # type: ignore required for conditional import patterns and Protocol assignment
    # This is safe because the variable is always set to a valid implementation
    Task: type[TaskProtocol] = RealTask  # type: ignore[assignment]
    # type: ignore required for conditional import patterns and Protocol assignment
    # This is safe because the variable is always set to a valid implementation
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
            self, description: str = "", agent: AgentPlaceholder | None = None
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
        "CrewAI is not installed. This module will not function properly. "
        "Install with: pip install '.[agents]'",
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
    agent=data_gatherer,  # type: ignore[arg-type]
)
task_analyze = Task(
    description="Analyze gathered data for trends and anomalies.",
    agent=analyzer,  # type: ignore[arg-type]
)
task_report = Task(
    description="Write a summary report based on analysis.",
    agent=writer,  # type: ignore[arg-type]
)

# Example: Assemble into a Crew (team)
reporting_team = Crew(
    agents=[data_gatherer, analyzer, writer],  # type: ignore[arg-type]
    tasks=[task_collect, task_analyze, task_report],  # type: ignore[arg-type]
)

if __name__ == "__main__":
    # Configure logging
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


# CrewAI Agent Team implementation
class CrewAIAgentTeam:
    """
    CrewAI Agent Team implementation for integration with other modules.

    This class provides a higher-level interface for working with CrewAI agents,
    tasks, and crews. Now with autonomous agentic reasoning, tool selection,
    and detailed logging.

    **Autonomous Tool Selection and Agentic Reasoning:**
    - The agent/team can access all registered tools via the tool registry in
      `common_utils.tooling`.
    - When running a task, CrewAIAgentTeam will analyze the task description and,
      using simple heuristics, will attempt to select a tool to use. If a tool
      name or relevant keyword matches the task description, that tool is selected
      and invoked with inferred parameters (for demo, the description itself).
    - All reasoning steps, tool considerations, selection, invocations, and results
      are logged via a dedicated logger ('agentic_reasoning').
    - If no tool is selected, a fallback is logged and normal workflow is followed.
    - See tests for examples of this autonomous tool use and logging.

    Usage:
        team = CrewAIAgentTeam()
        team.add_agent(...)
        team.add_task(...)
        team.run()  # Agentic reasoning with tool selection and logging

    """

    def __init__(self, llm_provider: object = None) -> None:
        """
        Initialize a CrewAI Agent Team with agentic reasoning and logging.

        Args:
            llm_provider: The LLM provider to use for agent interactions

        """
        self.llm_provider = llm_provider
        self.agents: list[object] = []
        self.tasks: list[object] = []
        self.api_client: object | None = None

        # Dedicated logger for agentic reasoning
        # Note: Logger configuration is deferred to the application
        self.logger = logging.getLogger("agentic_reasoning")

    def add_agent(self, role: str, goal: str, backstory: str) -> AgentProtocol:
        """
        Add an agent to the team.

        Args:
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent

        Returns:
            The created agent

        """
        agent = Agent(role=role, goal=goal, backstory=backstory)
        self.agents.append(agent)
        return agent

    def add_task(
        self, description: str, agent: Union[str, AgentProtocol]
    ) -> TaskProtocol:
        """
        Add a task to the team.

        Args:
            description: The task description
            agent: The agent assigned to the task (role name or Agent instance)

        Returns:
            The created task

        """
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

    def _heuristic_tool_selection(
        self, description: str
    ) -> tuple[str, dict] | tuple[None, None]:
        """
        Select a tool based on task description using extensible heuristic matching.

        This method uses a more generic tool registration mechanism that leverages
        tool metadata including keywords and custom input preprocessors.

        Args:
            description: The task description

        Returns:
            (tool_name, tool_metadata) if found, else (None, None)

        """
        # Gather all registered tools with their metadata
        available_tools = list_tools()
        description_lower = description.lower()
        self.logger.info("Considering tools for task: '%s'", description)

        # Enhanced heuristic: Use tool metadata for better matching
        for tool_name, tool_metadata in available_tools.items():
            # Check if tool name appears in description
            if tool_name.lower() in description_lower:
                self.logger.info("Tool '%s' matched by name in description.", tool_name)
                return tool_name, tool_metadata

            # Check keywords if available in tool metadata
            keywords = tool_metadata.get("keywords", [])
            if keywords and any(
                keyword.lower() in description_lower for keyword in keywords
            ):
                self.logger.info(
                    "Tool '%s' matched by keyword in description.", tool_name
                )
                return tool_name, tool_metadata

        self.logger.info("No tool matched by heuristic.")
        return None, None

    def run(self) -> object:
        """
        Run the agent team workflow with agentic reasoning and logging.

        For each task:
            - Attempts to select and invoke a tool if heuristics match.
            - Logs all reasoning, tool consideration, invocation, and results.
            - Proceeds with standard CrewAI workflow.

        Returns:
            The result of the workflow

        """
        if not crewai_available:
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

        # For each task, perform agentic reasoning/tool selection
        for task in self.tasks:
            description = getattr(task, "description", "")
            self.logger.info("---\nEvaluating task: '%s'", description)
            tool_name, tool_metadata = self._heuristic_tool_selection(description)
            if tool_name and tool_metadata:
                # Use input preprocessor if available, otherwise use description
                input_preprocessor = tool_metadata.get("input_preprocessor")
                if input_preprocessor:
                    tool_input = input_preprocessor(description)
                else:
                    # Fallback: try to extract expression for calculator-like tools
                    tool_input = description
                    if tool_name == "calculator":
                        # NOTE: This regex is intentionally simple for demonstration
                        # and will match the first contiguous block of math-like
                        # characters, which may include extra spaces. For more robust
                        # extraction in production, consider improving this to handle
                        # more complex/natural language task descriptions.
                        match = re.search(r"([0-9\+\-\*\/\.\s\%\(\)]+)", description)
                        if match:
                            tool_input = match.group(1)

                self.logger.info(
                    "Invoking tool '%s' with input: %r", tool_name, tool_input
                )
                try:
                    # Get the actual function from the tool metadata
                    func = tool_metadata["func"]
                    # Strip whitespace from the input to avoid indentation errors
                    result = func(tool_input.strip())
                    self.logger.info("Tool '%s' returned: %r", tool_name, result)
                    # Optionally, set as context for agent (not implemented here)
                except Exception:
                    self.logger.exception("Error invoking tool '%s'", tool_name)
            else:
                self.logger.info(
                    "No tool selected for this task. Proceeding without tool."
                )

        # Create and run the crew as usual
        crew = self._create_crew()
        return crew.kickoff()


# Next steps:
# - Replace example agents, goals, and tasks with project-specific logic.
# - Integrate with application triggers or API endpoints as needed.
# - See agent_team/README.md (to be created) for setup and usage.
