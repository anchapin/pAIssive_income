"""
Example script demonstrating the use of mem0-enhanced agents.

This script shows how to use the memory-enhanced agent team implementation
to create and run a team of agents with persistent memory capabilities.

Requirements:
    - mem0ai package: uv pip install mem0ai
    - crewai package: uv pip install crewai

Usage:
    python examples/mem0_enhanced_agents_example.py
"""

from __future__ import annotations

import logging
import os

# Import the memory-enhanced agent team
from agent_team.mem0_enhanced_agents import (
    MEM0_AVAILABLE,
    MemoryEnhancedCrewAIAgentTeam,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_dependencies() -> bool:
    """
    Check if required dependencies are installed.

    Returns:
        bool: True if all dependencies are available, False otherwise

    """
    try:
        from crewai import Agent, Crew  # noqa: F401
    except ImportError:
        logger.error("CrewAI is not installed. Install with: uv pip install crewai")
        return False

    if not MEM0_AVAILABLE:
        logger.error("mem0 is not installed. Install with: uv pip install mem0ai")
        return False

    # Check for OpenAI API key (required by mem0)
    if "OPENAI_API_KEY" not in os.environ:
        logger.warning("OPENAI_API_KEY environment variable not set.")
        logger.warning("mem0 requires an OpenAI API key to function properly.")
        logger.warning("Set it with: export OPENAI_API_KEY='your-api-key'")
        return False

    return True


def create_research_team(user_id: str) -> MemoryEnhancedCrewAIAgentTeam:
    """
    Create a research team with memory-enhanced agents.

    Args:
        user_id: The user ID for memory storage and retrieval

    Returns:
        A memory-enhanced agent team

    """
    # Create a memory-enhanced agent team
    team = MemoryEnhancedCrewAIAgentTeam(user_id=user_id)

    # Add agents
    researcher = team.add_agent(
        role="Market Researcher",
        goal="Identify profitable niches for AI tools",
        backstory="Expert at analyzing market trends and identifying opportunities",
    )

    developer = team.add_agent(
        role="AI Developer",
        goal="Design and develop AI solutions for identified niches",
        backstory="Skilled AI engineer with expertise in building practical tools",
    )

    monetization = team.add_agent(
        role="Monetization Specialist",
        goal="Create effective monetization strategies",
        backstory="Expert at developing subscription models and pricing strategies",
    )

    # Add tasks
    team.add_task(
        description="Research the market for AI-powered productivity tools",
        agent=researcher,
    )

    team.add_task(
        description="Design an AI tool based on the market research", agent=developer
    )

    team.add_task(
        description="Create a monetization strategy for the AI tool", agent=monetization
    )

    return team


def run_example() -> None:
    """Run the example workflow with memory-enhanced agents."""
    # Check dependencies
    if not check_dependencies():
        return

    # Create a unique user ID (in a real application, this would be the actual user ID)
    user_id = "example_user_123"

    # Create the research team
    logger.info("Creating research team with memory-enhanced agents")
    team = create_research_team(user_id)

    # Run the team
    logger.info("Running the research team workflow")
    try:
        result = team.run()
        logger.info("Workflow completed successfully")
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.error(f"Error running workflow: {e}")

    # Demonstrate memory retrieval
    if team.memory is not None:
        logger.info("Retrieving memories from the workflow")
        try:
            memories = team.memory.search(
                query="What agents were involved in the workflow?",
                user_id=user_id,
                limit=5,
            )

            logger.info(f"Retrieved {len(memories)} memories:")
            for i, memory in enumerate(memories):
                logger.info(
                    "Memory %d: %s...", i + 1, memory.get("text", "No text")[:100]
                )
        except Exception:
            logger.exception("Error retrieving memories")

    # --- New: Demonstrate retrieval using KnowledgeIntegrationLayer ---
    logger.info(
        "=== Using KnowledgeIntegrationLayer for unified knowledge querying ==="
    )
    try:
        # Import the integration layer and sources
        from interfaces.knowledge_interfaces import (
            KnowledgeIntegrationLayer,
            KnowledgeStrategy,
            Mem0KnowledgeSource,
            VectorRAGKnowledgeSource,
        )

        # Stub/mock clients for demonstration (replace with real clients as needed)
        class DummyMem0Client:
            def search(
                self, query: str, _user_id: str, **_kwargs: object
            ) -> list[dict[str, str]]:
                return [{"source": "mem0", "content": f"dummy mem0 for '{query}'"}]

            def add(
                self, content: str, _user_id: str, **_kwargs: object
            ) -> dict[str, str]:
                return {"status": "added", "content": content}

        class DummyVectorClient:
            def query(
                self, query: str, _user_id: str, **_kwargs: object
            ) -> list[dict[str, str]]:
                return [
                    {"source": "vector_rag", "content": f"dummy vector for '{query}'"}
                ]

            def add(
                self, content: str, _user_id: str, **_kwargs: object
            ) -> dict[str, str]:
                return {"status": "added", "content": content}

        mem0_source = Mem0KnowledgeSource(DummyMem0Client())
        vector_rag_source = VectorRAGKnowledgeSource(DummyVectorClient())

        # Example: fallback strategy (will return from mem0 if available)
        integration_fallback = KnowledgeIntegrationLayer(
            sources=[mem0_source, vector_rag_source],
            strategy=KnowledgeStrategy.FALLBACK,
        )
        query = "What agents were involved in the workflow?"
        results_fallback = integration_fallback.search(query, user_id=user_id)
        logger.info("Fallback strategy results: %s", results_fallback)

        # Example: aggregation strategy (combines results from all sources)
        integration_aggregate = KnowledgeIntegrationLayer(
            sources=[mem0_source, vector_rag_source],
            strategy=KnowledgeStrategy.AGGREGATE,
        )
        results_aggregate = integration_aggregate.search(query, user_id=user_id)
        logger.info("Aggregation strategy results: %s", results_aggregate)

        # This is the new recommended pattern for agent/team knowledge retrieval:
        # Use KnowledgeIntegrationLayer as a unified, extensible interface to search across all sources.
    except Exception:
        logger.exception("Error using KnowledgeIntegrationLayer")


def main() -> None:
    """Run the mem0-enhanced agents example."""
    logger.info("Starting mem0-enhanced agents example")
    run_example()
    logger.info("Example completed")


if __name__ == "__main__":
    main()
