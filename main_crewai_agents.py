"""
CrewAI Multi-Agent Orchestration with Memory Enhancement.

This module defines example CrewAI agents and teams for collaborative AI workflows,
now enhanced with mem0 for persistent memory capabilities.
Adapt and extend these scaffolds to fit your use-case.

- Docs: https://docs.crewai.com/
- mem0 Docs: https://mem0.ai
"""

import logging
import os
from typing import Optional, Protocol

# Import standard CrewAI components
from crewai import Agent, Crew, Task


class TeamProtocol(Protocol):
    """Protocol for team objects that can run workflows."""

    def run(self) -> object:
        """Run the team workflow."""
        ...


# Import memory-enhanced agent team
try:
    from agent_team.mem0_enhanced_agents import (
        MEM0_AVAILABLE,
        MemoryEnhancedCrewAIAgentTeam,
    )

    CREWAI_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    CREWAI_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

# Example: Define agent roles

# Example: Assemble into a Crew (team)


def create_team(
    use_memory: bool = False, user_id: Optional[str] = None
) -> TeamProtocol:
    """
    Create and return a CrewAI team, optionally using memory enhancement.

    Args:
        use_memory: Whether to use memory-enhanced team
        user_id: User ID for memory operations (required if use_memory is True)

    Returns:
        A CrewAI team or memory-enhanced team

    """
    if use_memory and MEM0_AVAILABLE:
        if not user_id:
            user_id = "default_user"
            logger.warning("No user_id provided, using 'default_user'")

        logger.info(f"Creating memory-enhanced team with user_id: {user_id}")
        team = MemoryEnhancedCrewAIAgentTeam(user_id=user_id)

        # Add agents with memory capabilities
        data_gatherer = team.add_agent(
            role="Data Gatherer",
            goal="Collect relevant information and data for the project",
            backstory="An AI specialized in data collection from APIs and databases.",
        )

        analyzer = team.add_agent(
            role="Analyzer",
            goal="Analyze collected data and extract actionable insights",
            backstory="An AI expert in analytics and pattern recognition.",
        )

        writer = team.add_agent(
            role="Writer",
            goal="Generate clear, readable reports from analyzed data",
            backstory="An AI that excels at communicating insights in natural language.",
        )

        # Add tasks
        team.add_task(
            description="Gather all relevant data from internal and external sources.",
            agent=data_gatherer,
        )

        team.add_task(
            description="Analyze gathered data for trends and anomalies.",
            agent=analyzer,
        )

        team.add_task(
            description="Write a summary report based on analysis.", agent=writer
        )

        return team
    if use_memory and not MEM0_AVAILABLE:
        logger.warning("mem0 not available, falling back to standard team")

    logger.info("Creating standard team without memory enhancement")
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

    task_collect = Task(
        description="Gather all relevant data from internal and external sources.",
        agent=data_gatherer,
    )
    task_analyze = Task(
        description="Analyze gathered data for trends and anomalies.",
        agent=analyzer,
    )
    task_report = Task(
        description="Write a summary report based on analysis.", agent=writer
    )

    reporting_team = Crew(
        agents=[data_gatherer, analyzer, writer],
        tasks=[task_collect, task_analyze, task_report],
    )
    return reporting_team


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Check if dependencies are available
    if not CREWAI_AVAILABLE:
        logger.error("CrewAI is not installed. Install with: pip install '.[agents]'")
        exit(1)

    if not MEM0_AVAILABLE:
        logger.warning("mem0 is not installed. Install with: pip install mem0ai")

    # Create team with memory enhancement if available
    use_memory = os.environ.get("USE_MEMORY", "1") == "1"
    user_id = os.environ.get("USER_ID", "example_user")

    team = create_team(use_memory=use_memory, user_id=user_id)

    # Example: Run the workflow (for demonstration; adapt as needed)
    try:
        result = team.run()
        logger.info("CrewAI workflow completed successfully")
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.error(f"Error running CrewAI workflow: {e}")

# Next steps:
# - Replace example agents, goals, and tasks with project-specific logic.
# - Integrate with application triggers or API endpoints as needed.
# - See agent_team/README.md for setup and usage.
