"""
CrewAI Multi-Agent Orchestration.

This module defines example CrewAI agents and teams for collaborative AI workflows.
Adapt and extend these scaffolds to fit your use-case.

- Docs: https://docs.crewai.com/
"""

from __future__ import annotations

# Check if crewai is installed
from typing import Any

try:
    from crewai import Agent, Crew, Task

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

    # Define placeholder classes for type hints
    class AgentPlaceholder:
        """Placeholder for Agent class when crewai is not installed."""

        def __init__(self, role: str = "", goal: str = "", backstory: str = "") -> None:
            """
            Initialize Agent placeholder.

            Args:
                role: The role of the agent
                goal: The goal of the agent
                backstory: The backstory of the agent

            """
            self.role = role
            self.goal = goal
            self.backstory = backstory

    class TaskPlaceholder:
        """Placeholder for Task class when crewai is not installed."""

        def __init__(
            self, description: str = "", agent: AgentPlaceholder = None
        ) -> None:
            """
            Initialize Task placeholder.

            Args:
                description: The task description
                agent: The agent assigned to the task

            """
            self.description = description
            self.agent = agent

    class CrewPlaceholder:
        """Placeholder for Crew class when crewai is not installed."""

        def __init__(
            self, agents: list[Any] | None = None, tasks: list[Any] | None = None
        ) -> None:
            """
            Initialize Crew placeholder.

            Args:
                agents: List of agents
                tasks: List of tasks

            """
            self.agents = agents or []
            self.tasks = tasks or []

        def run(self) -> None:
            """
            Run the crew workflow.

            Raises:
                ImportError: When crewai is not installed

            """
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

    # Use these placeholders instead of the real classes
    Agent = AgentPlaceholder  # type: ignore[misc, assignment]
    Task = TaskPlaceholder  # type: ignore[misc, assignment]
    Crew = CrewPlaceholder  # type: ignore[misc, assignment]

    # Print a warning
    import warnings

    warnings.warn(
        "CrewAI is not installed. This module will not function properly. Install with: pip install '.[agents]'",
        stacklevel=2,
    )

# Example: Define agent roles
data_gatherer = Agent(
    role="Data Gatherer",
    goal="Collect relevant information and data for the project",
    backstory="An AI specialized in data collection from APIs and databases.",
)

analyzer = Agent(
    role="Analyzer",
    goal="Analyze collected data and extract actionable insights",
    backstory="An AI expert in analytics and pattern recognition.",
)

writer = Agent(
    role="Writer",
    goal="Generate clear, readable reports from analyzed data",
    backstory="An AI that excels at communicating insights in natural language.",
)

# Example: Define tasks
task_collect = Task(
    description="Gather all relevant data from internal and external sources.",
    agent=data_gatherer,
)
task_analyze = Task(
    description="Analyze gathered data for trends and anomalies.", agent=analyzer
)
task_report = Task(
    description="Write a summary report based on analysis.", agent=writer
)

# Example: Assemble into a Crew (team)
reporting_team = Crew(
    agents=[data_gatherer, analyzer, writer],
    tasks=[task_collect, task_analyze, task_report],
)

if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create a module logger
    logger = logging.getLogger(__name__)

    if not CREWAI_AVAILABLE:
        logger.error("CrewAI is not installed. Install with: pip install '.[agents]'")
    else:
        # Example: Run the workflow (for demonstration; adapt as needed)
        try:
            reporting_team.run()
            logger.info("CrewAI reporting workflow completed.")
        except Exception:
            logger.exception("Error running CrewAI workflow")


# CrewAI Agent Team implementation
import logging
from common_utils.tooling import list_tools, get_tool

class CrewAIAgentTeam:
    """
    CrewAI Agent Team implementation for integration with other modules.

    This class provides a higher-level interface for working with CrewAI agents,
    tasks, and crews. Now with autonomous agentic reasoning, tool selection,
    and detailed logging.

    **Autonomous Tool Selection and Agentic Reasoning:**
    - The agent/team can access all registered tools via the tool registry in `common_utils.tooling`.
    - When running a task, CrewAIAgentTeam will analyze the task description and, using simple heuristics,
      will attempt to select a tool to use. If a tool name or relevant keyword matches the task description,
      that tool is selected and invoked with inferred parameters (for demo, the description itself).
    - All reasoning steps, tool considerations, selection, invocations, and results are logged via a dedicated logger ('agentic_reasoning').
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
        self.api_client = None

        # Dedicated logger for agentic reasoning
        self.logger = logging.getLogger("agentic_reasoning")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def add_agent(self, role: str, goal: str, backstory: str) -> object:
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

    def add_task(self, description: str, agent: object) -> object:
        """
        Add a task to the team.

        Args:
            description: The task description
            agent: The agent assigned to the task (role name or Agent instance)

        Returns:
            The created task

        """
        if isinstance(agent, str):
            agent_obj = next((a for a in self.agents if a.role == agent), None)  # type: ignore[attr-defined]
            if not agent_obj:
                error_msg = f"Agent with role '{agent}' not found"
                raise ValueError(error_msg)
        else:
            agent_obj = agent

        task = Task(description=description, agent=agent_obj)  # type: ignore[arg-type]
        self.tasks.append(task)
        return task

    def _create_crew(self) -> object:
        """
        Create a Crew instance from the current agents and tasks.

        Returns:
            A Crew instance

        """
        return Crew(agents=self.agents, tasks=self.tasks)  # type: ignore[arg-type]

    def _heuristic_tool_selection(self, description: str) -> tuple[str, callable] | tuple[None, None]:
        """
        Select a tool based on task description using heuristic matching.

        Args:
            description: The task description

        Returns:
            (tool_name, tool_func) if found, else (None, None)
        """
        # Gather all registered tools
        available_tools = list_tools()
        description_lower = description.lower()
        self.logger.info(f"Considering tools for task: '{description}'")
        # Heuristic: Match tool name or keywords
        for tool_name, tool_func in available_tools.items():
            if tool_name.lower() in description_lower:
                self.logger.info(f"Tool '{tool_name}' matched by name in description.")
                return tool_name, tool_func
            # Example: additional heuristics for calculator
            if tool_name == "calculator":
                key_words = ["calculate", "math", "add", "subtract", "multiply", "divide", "+", "-", "*", "/", "%"]
                if any(word in description_lower for word in key_words):
                    self.logger.info(f"Tool '{tool_name}' matched by keyword in description.")
                    return tool_name, tool_func
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
        if not CREWAI_AVAILABLE:
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

        # For each task, perform agentic reasoning/tool selection
        for task in self.tasks:
            description = getattr(task, "description", "")
            self.logger.info(f"---\nEvaluating task: '{description}'")
            tool_name, tool_func = self._heuristic_tool_selection(description)
            if tool_name and tool_func:
                # For demonstration, pass the description as the parameter (or extract expr for calculator)
                tool_input = description
                # Try to extract a math expression if it's the calculator
                if tool_name == "calculator":
                    import re
                    match = re.search(r"([0-9\+\-\*\/\.\s\%\(\)]+)", description)
                    if match:
                        tool_input = match.group(1)
                self.logger.info(f"Invoking tool '{tool_name}' with input: {tool_input!r}")
                try:
                    result = tool_func(tool_input)
                    self.logger.info(f"Tool '{tool_name}' returned: {result!r}")
                    # Optionally, set as context for agent (not implemented here)
                except Exception as e:
                    self.logger.exception(f"Error invoking tool '{tool_name}': {e}")
            else:
                self.logger.info("No tool selected for this task. Proceeding without tool.")

        # Create and run the crew as usual
        crew = self._create_crew()
        return crew.kickoff()  # type: ignore[attr-defined]


# Next steps:
# - Replace example agents, goals, and tasks with project-specific logic.
# - Integrate with application triggers or API endpoints as needed.
# - See agent_team/README.md (to be created) for setup and usage.
