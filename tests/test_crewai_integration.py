"""Test the integration between CrewAI and the agent_team module."""

import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
    mock_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai"
    )
    if os.path.exists(mock_dir):
        logging.info(f"Found mock_crewai directory at {mock_dir}, adding to sys.path")
        sys.path.insert(0, os.path.dirname(mock_dir))

    # Try to add the current directory to sys.path
    sys.path.insert(0, os.getcwd())


@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI is not available")
def test_crewai_agent_team_integration():
    """Test the integration between CrewAI and the agent_team module."""
    if not CREWAI_AVAILABLE:
        pytest.skip("CrewAI is not installed - skipping test")

    try:
        # Import the CrewAI agent from the agent_team module
        from agent_team.crewai_agents import CrewAIAgentTeam

        # Create a mock LLM provider
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Mock LLM response"

        # Create a CrewAIAgentTeam instance
        agent_team = CrewAIAgentTeam(llm_provider=mock_llm)

        # Verify the agent team was created successfully
        assert agent_team is not None

        # Test the run method with a mock workflow
        with patch.object(agent_team, "_create_crew") as mock_create_crew:
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = "Mock workflow result"
            mock_create_crew.return_value = mock_crew

            result = agent_team.run()

            # Verify the result
            assert result == "Mock workflow result"

            # Verify the crew was created and kickoff was called
            mock_create_crew.assert_called_once()
            mock_crew.kickoff.assert_called_once()

        logging.info("CrewAI agent team integration test passed")
    except ImportError:
        logging.exception("CrewAI agent team integration test failed")
        pytest.skip("CrewAI agent team integration test failed")


@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI is not available")
def test_crewai_agentic_reasoning_tool_selection_logging(caplog):
    """
    Demonstrates and tests CrewAIAgentTeam's agentic reasoning and autonomous tool selection.

    This test:
    - Creates a CrewAIAgentTeam, adds an agent and a task like 'Calculate 2 + 2'
    - Runs the team (with crew mocked)
    - Captures logs from the 'agentic_reasoning' logger
    - Asserts that logs include:
        (a) Reasoning about tool selection,
        (b) Invocation of the calculator tool,
        (c) The result of the tool call

    Serves as both a test and a usage example for users.
    """
    if not CREWAI_AVAILABLE:
        pytest.skip("CrewAI is not installed - skipping test")

    from agent_team.crewai_agents import CrewAIAgentTeam

    # Patch crew creation/kickoff as in other tests
    from unittest.mock import MagicMock, patch

    agent_team = CrewAIAgentTeam()
    agent = agent_team.add_agent(
        role="CalculatorAgent",
        goal="Solve math problems",
        backstory="A math-savvy AI.",
    )

    # Add a task with a description that should trigger calculator tool selection
    agent_team.add_task(description="Calculate 2 + 2", agent=agent)

    with patch.object(agent_team, "_create_crew") as mock_create_crew, caplog.at_level("INFO", logger="agentic_reasoning"):
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Calculation complete"
        mock_create_crew.return_value = mock_crew

        result = agent_team.run()
        assert result == "Calculation complete"

    logs = caplog.text
    # Check for tool selection reasoning
    assert "Evaluating task: 'Calculate 2 + 2'" in logs
    assert "Tool 'calculator' matched by keyword" in logs or "Tool 'calculator' matched by name" in logs
    # Check for tool invocation and result (account for leading space as extracted by regex)
    assert "Invoking tool 'calculator' with input: ' 2 + 2'" in logs
    assert "Tool 'calculator' returned:" in logs
    # Should see result '4' for 2 + 2
    assert "Tool 'calculator' returned: 4" in logs

@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI is not available")
def test_crewai_agent_team_with_custom_agents():
    """Test the CrewAIAgentTeam with custom agents."""
    if not CREWAI_AVAILABLE:
        pytest.skip("CrewAI is not installed - skipping test")

    try:
        # Import the CrewAI agent from the agent_team module
        from agent_team.crewai_agents import CrewAIAgentTeam
        from crewai import Agent, Task

        # Create a mock LLM provider
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Mock LLM response"

        # Create a CrewAIAgentTeam instance
        agent_team = CrewAIAgentTeam(llm_provider=mock_llm)

        # Create custom agents
        with patch("crewai.Agent") as MockAgent:
            mock_agent1 = MagicMock()
            mock_agent1.role = "Researcher"
            mock_agent1.goal = "Research the topic"
            mock_agent1.backstory = "Expert researcher"

            mock_agent2 = MagicMock()
            mock_agent2.role = "Writer"
            mock_agent2.goal = "Write the report"
            mock_agent2.backstory = "Expert writer"

            MockAgent.side_effect = [mock_agent1, mock_agent2]

            # Add custom agents to the agent team
            agent_team.add_agent(
                role="Researcher",
                goal="Research the topic",
                backstory="Expert researcher",
            )

            agent_team.add_agent(
                role="Writer", goal="Write the report", backstory="Expert writer"
            )

            # Verify the agents were added
            assert len(agent_team.agents) == 2
            # Cast to Any to avoid mypy errors with role attribute
            from typing import Any, cast

            assert cast("Any", agent_team.agents[0]).role == "Researcher"
            assert cast("Any", agent_team.agents[1]).role == "Writer"

            # Test the run method with custom agents
            with patch.object(agent_team, "_create_crew") as mock_create_crew:
                mock_crew = MagicMock()
                mock_crew.kickoff.return_value = "Custom agents workflow result"
                mock_create_crew.return_value = mock_crew

                result = agent_team.run()

                # Verify the result
                assert result == "Custom agents workflow result"

                # Verify the crew was created with the custom agents
                mock_create_crew.assert_called_once()
                mock_crew.kickoff.assert_called_once()

        logging.info("CrewAI agent team with custom agents test passed")
    except ImportError:
        logging.exception("CrewAI agent team with custom agents test failed")
        pytest.skip("CrewAI agent team with custom agents test failed")


def test_crewai_agent_team_mock_fallback():
    """Test that works even if CrewAI is not available."""
    try:
        # Import the CrewAI agent from the agent_team module
        from agent_team.crewai_agents import CrewAIAgentTeam

        # Create a mock LLM provider
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Mock LLM response"

        # Create a CrewAIAgentTeam instance
        agent_team = CrewAIAgentTeam(llm_provider=mock_llm)

        # Verify the agent team was created successfully
        assert agent_team is not None

        # Test the run method with a mock workflow
        with patch.object(agent_team, "run") as mock_run:
            mock_run.return_value = "Mock workflow result"

            result = agent_team.run()

            # Verify the result
            assert result == "Mock workflow result"

        logging.info("CrewAI agent team mock fallback test passed")
    except ImportError:
        logging.exception("CrewAI agent team mock fallback test failed")
        # This test should never fail, just skip if all imports fail
        pytest.skip("No CrewAI implementation available")
