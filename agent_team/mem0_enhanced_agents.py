"""
mem0-Enhanced Agents for pAIssive_income.

This module provides memory-enhanced versions of the agent classes using mem0.
It extends the CrewAI agent implementation with persistent memory capabilities.

Usage:
    from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam

    # Create a memory-enhanced agent team
    team = MemoryEnhancedCrewAIAgentTeam(user_id="user123")

    # Add agents with memory capabilities
    researcher = team.add_agent(
        role="Researcher",
        goal="Find relevant information",
        backstory="Expert at gathering data"
    )

    # Run the team with memory enhancement
    result = team.run()

Requirements:
    - mem0ai package: pip install mem0ai
"""

from __future__ import annotations

import logging
from typing import Any, Generic, Optional, Protocol, TypeVar, Union, runtime_checkable

# Import base CrewAI agent team
from agent_team.crewai_agents import CrewAIAgentTeam

# Define type variables for better type hints
AgentType = TypeVar("AgentType")
TaskType = TypeVar("TaskType")
ResultType = TypeVar("ResultType")

# Import CrewAI components
try:
    from crewai import Agent, Task

    CREWAI_AVAILABLE = True

    # Define type variables with proper naming convention
    AgentType_co = TypeVar("AgentType_co", bound=Agent, covariant=True)
    TaskType_co = TypeVar("TaskType_co", bound=Task, covariant=True)
    ResultType_co = TypeVar("ResultType_co", covariant=True)

    @runtime_checkable
    class TeamResult(Protocol[ResultType_co]):
        """Protocol for team execution results."""

        def __str__(self) -> str:
            """Convert result to string representation."""
            ...

except ImportError:
    CREWAI_AVAILABLE = False
    AgentType_co = TypeVar("AgentType_co", covariant=True)
    TaskType_co = TypeVar("TaskType_co", covariant=True)
    ResultType_co = TypeVar("ResultType_co", covariant=True)

    @runtime_checkable
    class TeamResult(Protocol[ResultType_co]):
        """Protocol for team execution results."""

        def __str__(self) -> str:
            """Convert result to string representation."""
            ...


# Import mem0 components
try:
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None  # type: ignore[assignment]

# Configure logging
logger = logging.getLogger(__name__)


class MemoryEnhancedCrewAIAgentTeam(
    CrewAIAgentTeam, Generic[AgentType_co, TaskType_co, ResultType_co]
):
    """
    CrewAI Agent Team with mem0 memory enhancement.

    This class extends the CrewAIAgentTeam with persistent memory capabilities
    using mem0. It adds memory hooks to key lifecycle points:
    - Agent initialization
    - Task assignment
    - Team execution
    """

    def __init__(
        self, llm_provider: Optional[object] = None, user_id: Optional[str] = None
    ) -> None:
        """
        Initialize a memory-enhanced CrewAI Agent Team.

        Args:
            llm_provider: Optional language model provider for the agent team.
            user_id: Optional user identifier for memory persistence.
            llm_provider: The LLM provider to use for agent interactions
            user_id: The user ID for memory storage and retrieval

        """
        super().__init__(llm_provider)

        # Initialize mem0 memory if available
        if MEM0_AVAILABLE:
            self.memory = Memory()
            logger.info("mem0 memory initialized")
        else:
            self.memory = None
            logger.warning("mem0 not available. Install with: pip install mem0ai")

        # Set user ID for memory operations
        self.user_id = user_id or "default_user"

        # Store team creation in memory
        self._store_memory(f"Agent team created with user ID: {self.user_id}")

    def add_agent(self, role: str, goal: str, backstory: str) -> AgentType:
        """
        Add an agent to the team with memory enhancement.

        Args:
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent

        Returns:
            The created agent

        """
        # Create the agent using the parent method
        agent = super().add_agent(role, goal, backstory)  # type: ignore[return-value]

        # Store agent information in memory
        self._store_memory(
            f"Agent '{role}' added to team with goal: {goal}",
            metadata={"agent_role": role, "agent_goal": goal},
        )

        return agent  # type: ignore[return-value]

    def add_task(self, description: str, agent: AgentType) -> TaskType:
        """
        Add a task to the team with memory enhancement.

        Args:
            description: The task description
            agent: The agent assigned to the task

        Returns:
            The created task

        """
        # Create the task using the parent method
        task = super().add_task(description, agent)  # type: ignore[return-value]

        # Get agent role for metadata
        agent_role = getattr(agent, "role", "unknown")

        # Store task information in memory
        self._store_memory(
            f"Task assigned to agent '{agent_role}': {description}",
            metadata={"task_description": description, "agent_role": agent_role},
        )

        return task  # type: ignore[return-value]

    def run(self) -> ResultType:
        """
        Run the agent team workflow with memory enhancement.

        This method:
        1. Retrieves relevant memories before running
        2. Enhances context with memories
        3. Runs the team workflow
        4. Stores the results in memory

        Returns:
            The result of the workflow

        Raises:
            ImportError: If CrewAI is not installed
            RuntimeError: If the workflow fails to execute

        """
        if not CREWAI_AVAILABLE:
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

        # Retrieve relevant memories for context enhancement
        context_query = f"Information about team with {len(self.agents)} agents and {len(self.tasks)} tasks"
        memories: list[dict[str, Any]] = self._retrieve_relevant_memories(
            query=context_query
        )
        logger.info(
            "Retrieved %d relevant memories for context enhancement", len(memories)
        )

        # Log the start of the workflow
        workflow_description = f"Starting memory-enhanced workflow with {len(self.agents)} agents and {len(self.tasks)} tasks"
        logger.info(workflow_description)
        self._store_memory(workflow_description)

        crew = self._create_crew()
        enhanced_context = self._enhance_context_with_memories(workflow_description)
        logger.debug("Enhanced context: %.100s...", enhanced_context)

        try:
            result: ResultType = crew.kickoff()  # type: ignore[attr-defined]
        except Exception as e:
            error_msg = f"Workflow failed: {e!s}"
            logger.exception(error_msg)
            self._store_memory(
                error_msg,
                metadata={
                    "workflow_result": "error",
                    "error_type": e.__class__.__name__,
                },
            )
            raise RuntimeError(error_msg) from e

        # Store success result in memory
        if isinstance(result, str):
            self._store_memory(
                f"Workflow completed with result: {result[:100]}...",
                metadata={"workflow_result": "success"},
            )
        else:
            self._store_memory(
                "Workflow completed with non-string result",
                metadata={"workflow_result": "success"},
            )

        return result

    def _store_memory(
        self,
        content: Union[str, list[dict[str, str]]],
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Store a memory using mem0."""
        if self.memory is None:
            return

        try:
            self.memory.add(content, user_id=self.user_id, metadata=metadata or {})
            if isinstance(content, str):
                logger.debug("Memory stored: %.50s...", content)
            else:
                logger.debug("Conversation stored")
        except (OSError, ValueError):
            logger.exception("Error storing memory")

    def _retrieve_relevant_memories(
        self, query: Optional[str] = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Retrieve relevant memories."""
        if self.memory is None:
            return []

        # If no query provided, create one based on team information
        if query is None:
            agent_roles = [getattr(agent, "role", "unknown") for agent in self.agents]
            query = "Information about agents with roles: " + ", ".join(agent_roles)

        try:
            # Search for relevant memories
            return self.memory.search(query=query, user_id=self.user_id, limit=limit)
        except (OSError, ValueError):
            logger.exception("Error retrieving memories")
            return []

    def _enhance_context_with_memories(self, context: str) -> str:
        """
        Enhance a context string with relevant memories.

        This method retrieves relevant memories based on the context
        and adds them to the context string to provide additional
        information for the agents.

        Args:
            context: The original context string

        Returns:
            The enhanced context with memories included

        """
        if self.memory is None:
            return context

        # Retrieve relevant memories for the context
        memories = self._retrieve_relevant_memories(query=context)

        if not memories:
            return context

        # Format memories as a string
        memory_text = "\n".join(
            [
                f"- {memory.get('text', memory.get('memory', str(memory)))}"
                for memory in memories
            ]
        )

        # Combine memories with original context
        return f"""
Relevant memories:
{memory_text}

Original context:
{context}
"""


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Check if dependencies are available
    if not CREWAI_AVAILABLE:
        logger.error("CrewAI is not installed. Install with: pip install '.[agents]'")
    elif not MEM0_AVAILABLE:
        logger.error("mem0 is not installed. Install with: pip install mem0ai")
    else:
        # Create a memory-enhanced agent team with type hints
        team: MemoryEnhancedCrewAIAgentTeam[AgentType, TaskType, str] = (
            MemoryEnhancedCrewAIAgentTeam(user_id="example_user")
        )

        # Add agents
        researcher = team.add_agent(
            role="Researcher",
            goal="Find relevant information about the topic",
            backstory="Expert at gathering and analyzing data from various sources",
        )

        writer = team.add_agent(
            role="Writer",
            goal="Create engaging content based on research",
            backstory="Skilled content creator with expertise in clear communication",
        )

        # Add tasks
        team.add_task(
            description="Research the latest trends in AI memory systems",
            agent=researcher,
        )

        team.add_task(
            description="Write a summary of the research findings", agent=writer
        )

        # Run the team
        try:
            result = team.run()
            logger.info("Result: %s", result)
        except Exception:
            logger.exception("Error running workflow")
