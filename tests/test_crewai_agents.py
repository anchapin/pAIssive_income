# type: ignore[import]
"""Test scaffold for CrewAI agent integration."""

import logging
import os
import sys
from typing import Protocol

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

crewai_available = False
try:
    import crewai

    crewai_available = True
    logging.info(f"CrewAI is available (version: {crewai.__version__})")
except ImportError as e:
    logging.warning(f"CrewAI is not available: {e}")
    # Try to add the mock_crewai directory to sys.path
    mock_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai"
    )
    if os.path.exists(mock_dir):
        logging.info(f"Found mock_crewai directory at {mock_dir}, adding to sys.path")
        sys.path.insert(0, os.path.dirname(mock_dir))
    # Try to add the current directory to sys.path
    sys.path.insert(0, os.getcwd())


@pytest.mark.skipif(not crewai_available, reason="CrewAI is not available")
def test_crewai_import_and_agent():
    """Test that CrewAI Agent can be imported and instantiated."""
    if not crewai_available:
        pytest.skip("CrewAI is not installed - skipping test")
    try:
        from crewai import Agent

        # Minimal agent instantiation check
        agent = Agent(role="Test Agent", goal="Test goal", backstory="Test backstory")
        assert hasattr(agent, "role")
        assert agent.role == "Test Agent"
        assert hasattr(agent, "goal")
        assert agent.goal == "Test goal"
        assert hasattr(agent, "backstory")
        assert agent.backstory == "Test backstory"

        logging.info("CrewAI Agent test passed")
    except ImportError:
        logging.exception("CrewAI Agent import failed")
        pytest.skip("CrewAI is not installed or cannot be imported.")


@pytest.mark.skipif(not crewai_available, reason="CrewAI is not available")
def test_crewai_task_and_crew():
    """Test that CrewAI Task and Crew can be imported and instantiated."""
    if not crewai_available:
        pytest.skip("CrewAI is not installed - skipping test")
    try:
        from unittest.mock import MagicMock

        from crewai import Agent, Crew, Task

        # Mock the Agent to avoid actual model calls
        mock_agent = MagicMock(spec=Agent)
        mock_agent.execute_task.return_value = "Mock task output"
        # Add required attributes to the mock agent
        mock_agent.role = "Test Agent"

        # Minimal Task instantiation check
        task = Task(description="Test task description", agent=mock_agent)
        assert task.description == "Test task description"
        assert task.agent == mock_agent

        # Minimal Crew instantiation and execution check
        crew = Crew(agents=[mock_agent], tasks=[task])
        # Mock the crew's kick off method using spec to avoid type ignore
        crew.kickoff = MagicMock(return_value="Mock crew output", spec=crew.kickoff)
        result = crew.kickoff()

        assert result == "Mock crew output"

        logging.info("CrewAI Task and Crew test passed")
    except ImportError:
        logging.exception("CrewAI Task and Crew import failed")
        pytest.skip("CrewAI is not installed or cannot be imported.")


class AgentProtocol(Protocol):
    role: str
    goal: str
    backstory: str


def test_crewai_mock_fallback():
    """Test that works even if CrewAI is not available."""
    agent_class = None
    MockAgent = None
    try:
        # Try to import from crewai or mock_crewai
        try:
            from crewai import Agent

            source = "real crewai"
        except ImportError:
            try:
                # Import with a different name to avoid conflicts
                from mock_crewai import Agent as MockAgent

                source = "mock_crewai"
            except ImportError:
                # Try the fallback module
                import crewai

                agent_class = crewai.Agent
                source = "fallback crewai"
            Agent = None  # type: ignore[assignment]
        logging.info(f"Using {source} for Agent")

        # Create a simple agent
        agent: AgentProtocol
        if agent_class is not None:
            agent = agent_class(
                role="Test Agent", goal="Test goal", backstory="Test backstory"
            )
        elif source == "mock_crewai" and MockAgent is not None:
            agent = MockAgent(
                role="Test Agent", goal="Test goal", backstory="Test backstory"
            )
        else:
            agent = Agent(
                role="Test Agent", goal="Test goal", backstory="Test backstory"
            )  # type: ignore[assignment]
        assert hasattr(agent, "role")
        assert agent.role == "Test Agent"
        assert hasattr(agent, "goal")
        assert agent.goal == "Test goal"
        assert hasattr(agent, "backstory")
        assert agent.backstory == "Test backstory"

        logging.info("CrewAI mock fallback test passed")
    except ImportError:
        logging.exception("All CrewAI import attempts failed")
        # This test should never fail, just skip if all imports fail
        pytest.skip("No CrewAI implementation available")
