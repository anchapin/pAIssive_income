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
from typing import Any

# Import CrewAI components
try:
    from crewai import Agent, Crew, Task

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Use placeholder classes from crewai_agents.py

# Import mem0 components
try:
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None  # type: ignore[assignment]

# Import base CrewAI agent team
from agent_team.crewai_agents import CrewAIAgentTeam

# Configure logging
logger = logging.getLogger(__name__)


class MemoryEnhancedCrewAIAgentTeam(CrewAIAgentTeam):
    """
    CrewAI Agent Team with mem0 memory enhancement.

    This class extends the CrewAIAgentTeam with persistent memory capabilities
    using mem0. It adds memory hooks to key lifecycle points:
    - Agent initialization
    - Task assignment
    - Team execution
    """

    def __init__(self, llm_provider: object = None, user_id: str | None = None) -> None:
        """
        Initialize a memory-enhanced CrewAI Agent Team.

        Args:
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

    def add_agent(self, role: str, goal: str, backstory: str) -> object:
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
        agent = super().add_agent(role, goal, backstory)

        # Store agent information in memory
        self._store_memory(
            f"Agent '{role}' added to team with goal: {goal}",
            metadata={"agent_role": role, "agent_goal": goal},
        )

        return agent

    def add_task(self, description: str, agent: object) -> object:
        """
        Add a task to the team with memory enhancement.

        Args:
            description: The task description
            agent: The agent assigned to the task

        Returns:
            The created task

        """
        # Create the task using the parent method
        task = super().add_task(description, agent)

        # Get agent role for metadata
        agent_role = getattr(agent, "role", "unknown")

        # Store task information in memory
        self._store_memory(
            f"Task assigned to agent '{agent_role}': {description}",
            metadata={"task_description": description, "agent_role": agent_role},
        )

        return task

    def run(self) -> object:
        """
        Run the agent team workflow with memory enhancement.

        This method:
        1. Retrieves relevant memories before running
        2. Enhances context with memories
        3. Runs the team workflow
        4. Stores the results in memory

        Returns:
            The result of the workflow

        """
        if not CREWAI_AVAILABLE:
            error_msg = "CrewAI is not installed. Install with: pip install '.[agents]'"
            raise ImportError(error_msg)

        # Retrieve relevant memories for context enhancement
        context_query = f"Information about team with {len(self.agents)} agents and {len(self.tasks)} tasks"
        memories = self._retrieve_relevant_memories(query=context_query)
        logger.info(
            f"Retrieved {len(memories)} relevant memories for context enhancement"
        )

        # Log the start of the workflow
        workflow_description = f"Starting memory-enhanced workflow with {len(self.agents)} agents and {len(self.tasks)} tasks"
        logger.info(workflow_description)
        self._store_memory(workflow_description)

        # Create and run the crew
        crew = self._create_crew()

        # Enhance context with memories if possible
        # Note: This is a placeholder for future CrewAI integration
        # Currently, CrewAI doesn't provide a direct way to inject context
        # into all agents, but we can use this for future extensions
        enhanced_context = self._enhance_context_with_memories(workflow_description)
        logger.debug(f"Enhanced context: {enhanced_context[:100]}...")

        # Run the workflow
        result = crew.kickoff()  # type: ignore[attr-defined]

        # Store the result in memory
        if isinstance(result, str):
            self._store_memory(
                f"Workflow completed with result: {result[:100]}...",  # Store truncated result
                metadata={"workflow_result": "success"},
            )
        else:
            self._store_memory(
                "Workflow completed with non-string result",
                metadata={"workflow_result": "success"},
            )

        return result

    def _store_memory(
        self, content: str | list[dict[str, str]], metadata: dict[str, str] | None = None
    ) -> None:
        """
        Store a memory using mem0.

        Args:
            content: The content to store (string or conversation messages)
            metadata: Optional metadata for the memory

        """
        if self.memory is None:
            return

        try:
            self.memory.add(content, user_id=self.user_id, metadata=metadata or {})
            logger.debug(
                f"Memory stored: {content[:50]}..."
                if isinstance(content, str)
                else "Conversation stored"
            )
        except Exception:
            logger.exception("Error storing memory:")

    def _retrieve_relevant_memories(
        self, query: str | None = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant memories for the current context.

        Args:
            query: Optional query string (defaults to team and agent information)
            limit: Maximum number of memories to retrieve

        Returns:
            List of relevant memories

        """
        if self.memory is None:
            return []

        # If no query provided, create one based on team information
        if query is None:
            agent_roles = [getattr(agent, "role", "unknown") for agent in self.agents]
            query = f"Information about agents with roles: {', '.join(agent_roles)}"

        try:
            # Search for relevant memories
            memories = self.memory.search(
                query=query, user_id=self.user_id, limit=limit
            )
            return memories
        except Exception:
            logger.exception("Error retrieving memories:")
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
        enhanced_context = f"""
Relevant memories:
{memory_text}

Original context:
{context}
"""

        return enhanced_context


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
        # Create a memory-enhanced agent team
        team = MemoryEnhancedCrewAIAgentTeam(user_id="example_user")

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
        research_task = team.add_task(
            description="Research the latest trends in AI memory systems",
            agent=researcher,
        )

        writing_task = team.add_task(
            description="Write a summary of the research findings", agent=writer
        )

        # Run the team
        try:
            result = team.run()
            logger.info(f"Workflow result: {result}")
        except Exception:
            logger.exception("Error running workflow:")
