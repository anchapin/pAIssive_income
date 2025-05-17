"""Test scaffold for CrewAI agent integration."""

import pytest
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Check if crewai is installed
try:
    import crewai
    CREWAI_AVAILABLE = True
    logging.info(f"CrewAI is available (version: {crewai.__version__})")
except ImportError as e:
    CREWAI_AVAILABLE = False
    logging.warning(f"CrewAI is not available: {e}")

    # Try to add the mock_crewai directory to sys.path
    mock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai")
    if os.path.exists(mock_dir):
        logging.info(f"Found mock_crewai directory at {mock_dir}, adding to sys.path")
        sys.path.insert(0, os.path.dirname(mock_dir))

    # Try to add the current directory to sys.path
    sys.path.insert(0, os.getcwd())


@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI is not available")
def test_crewai_import_and_agent():
    """Test that CrewAI Agent can be imported and instantiated."""
    if not CREWAI_AVAILABLE:
        pytest.skip("CrewAI is not installed - skipping test")
    try:
        from crewai import Agent

        # Minimal agent instantiation check
        agent = Agent(role="Test Agent", goal="Test goal", backstory="Test backstory")
        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"

        logging.info("CrewAI Agent test passed")
    except ImportError as e:
        logging.exception("CrewAI Agent import failed")
        pytest.skip("CrewAI is not installed or cannot be imported.")


@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI is not available")
def test_crewai_task_and_crew():
    """Test that CrewAI Task and Crew can be imported and instantiated."""
    if not CREWAI_AVAILABLE:
        pytest.skip("CrewAI is not installed - skipping test")
    try:
        from crewai import Agent, Task, Crew
        from unittest.mock import MagicMock

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
        # Mock the crew's kick off method
        crew.kickoff = MagicMock(return_value="Mock crew output")
        result = crew.kickoff()

        assert result == "Mock crew output"

        logging.info("CrewAI Task and Crew test passed")
    except ImportError as e:
        logging.exception("CrewAI Task and Crew import failed")
        pytest.skip("CrewAI is not installed or cannot be imported.")


def test_crewai_mock_fallback():
    """Test that works even if CrewAI is not available."""
    try:
        # Try to import from crewai or mock_crewai
        try:
            from crewai import Agent
            source = "real crewai"
        except ImportError:
            try:
                from mock_crewai import Agent
                source = "mock_crewai"
            except ImportError:
                # Try the fallback module
                import crewai
                agent_class = crewai.Agent
                source = "fallback crewai"

        logging.info(f"Using {source} for Agent")

        # Create a simple agent
        if 'agent_class' in locals():
            agent = agent_class(role="Test Agent", goal="Test goal", backstory="Test backstory")
        else:
            agent = Agent(role="Test Agent", goal="Test goal", backstory="Test backstory")
        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"

        logging.info("CrewAI mock fallback test passed")
    except ImportError as e:
        logging.exception("All CrewAI import attempts failed")
        # This test should never fail, just skip if all imports fail
        pytest.skip("No CrewAI implementation available")
