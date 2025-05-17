"""
CrewAI Multi-Agent Orchestration

This module defines example CrewAI agents and teams for collaborative AI workflows.
Adapt and extend these scaffolds to fit your use-case.

- Docs: https://docs.crewai.com/
"""

import logging
from typing import Union

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Check if crewai is installed
try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Define placeholder classes for type hints
    class Agent:
        def __init__(self, role="", goal="", backstory="", **kwargs):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            self.kwargs = kwargs

    class Task:
        def __init__(self, description="", agent=None, **kwargs):
            self.description = description
            self.agent = agent
            self.kwargs = kwargs

    class Crew:
        def __init__(self, agents=None, tasks=None, **kwargs):
            self.agents = agents or []
            self.tasks = tasks or []
            self.kwargs = kwargs

        def run(self):
            raise ImportError("CrewAI is not installed. Install with: pip install '.[agents]'")

        def kickoff(self):
            return "Mock crew output"

    # Print a warning
    import warnings
    warnings.warn(
        "CrewAI is not installed. This module will not function properly. Install with: pip install '.[agents]'",
        stacklevel=2
    )


class CrewAIAgentTeam:
    """
    A team of CrewAI agents that can collaborate on tasks.

    This class provides a high-level interface for creating and managing
    CrewAI agent teams, including adding agents, defining tasks, and
    running workflows.
    """

    def __init__(self, llm_provider=None):
        """
        Initialize a CrewAI agent team.

        Args:
            llm_provider: The language model provider to use for agent interactions.
        """
        self.llm_provider = llm_provider
        self.agents = []
        self.tasks = []
        self.agent_map = {}  # Maps agent roles to agent objects

    def add_agent(self, role: str, goal: str, backstory: str, **kwargs) -> Agent:
        """
        Add an agent to the team.

        Args:
            role: The role of the agent.
            goal: The goal of the agent.
            backstory: The backstory of the agent.
            **kwargs: Additional arguments to pass to the Agent constructor.

        Returns:
            The created Agent object.
        """
        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            **kwargs
        )
        self.agents.append(agent)
        self.agent_map[role] = agent
        return agent

    def add_task(self, description: str, agent: Union[str, Agent], **kwargs) -> Task:
        """
        Add a task to the team.

        Args:
            description: The description of the task.
            agent: The agent to assign the task to (either a role string or an Agent object).
            **kwargs: Additional arguments to pass to the Task constructor.

        Returns:
            The created Task object.
        """
        # If agent is a string (role), look it up in the agent_map
        if isinstance(agent, str):
            if agent not in self.agent_map:
                raise ValueError(f"Agent with role '{agent}' not found. Add the agent first.")
            agent_obj = self.agent_map[agent]
        else:
            agent_obj = agent

        task = Task(
            description=description,
            agent=agent_obj,
            **kwargs
        )
        self.tasks.append(task)
        return task

    def _create_crew(self, **kwargs) -> Crew:
        """
        Create a CrewAI Crew object from the team's agents and tasks.

        Args:
            **kwargs: Additional arguments to pass to the Crew constructor.

        Returns:
            A CrewAI Crew object.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            **kwargs
        )

    def run(self, **kwargs) -> str:
        """
        Run the agent team workflow.

        Args:
            **kwargs: Additional arguments to pass to the Crew constructor.

        Returns:
            The result of the workflow execution.
        """
        if not self.agents:
            raise ValueError("No agents added to the team. Add at least one agent.")
        if not self.tasks:
            raise ValueError("No tasks added to the team. Add at least one task.")

        crew = self._create_crew(**kwargs)

        # Use kickoff() instead of run() for newer versions of CrewAI
        if hasattr(crew, 'kickoff'):
            return crew.kickoff()
        else:
            return crew.run()


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

    if not CREWAI_AVAILABLE:
        logging.error("CrewAI is not installed. Install with: pip install '.[agents]'")
    else:
        # Example: Run the workflow (for demonstration; adapt as needed)
        try:
            reporting_team.run()
            logging.info("CrewAI reporting workflow completed.")
        except Exception as e:
            logging.exception("Error running CrewAI workflow")

# Next steps:
# - Replace example agents, goals, and tasks with project-specific logic.
# - Integrate with application triggers or API endpoints as needed.
# - See agent_team/README.md (to be created) for setup and usage.
