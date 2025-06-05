"""
Unit tests for agentic reasoning and tool use via the ArtistAgent in main_artist_agent.py.

Tests:
- Correct tool selection and use for arithmetic/calculator prompts.
- Behavior when no suitable tool matches the prompt.
- Placeholder for multi-step reasoning/tool chaining.
"""

import sys
import types
from unittest.mock import Mock, patch

import pytest

import main_artist_agent


@pytest.fixture
def mock_calculator_tool():
    """Fixture for a mock calculator tool."""
    tool = Mock()
    tool.name = "calculator"
    tool.description = "A calculator tool for arithmetic operations."
    tool.run = Mock(return_value="14")
    return tool


@pytest.fixture
def artist_agent_with_tools(mock_calculator_tool):
    """Fixture providing ArtistAgent initialized with a calculator tool."""
    # Patch tools as a dict mapping tool name to its callable (mock's run method)
    if hasattr(main_artist_agent, "ArtistAgent"):
        # ArtistAgent doesn't support tools injection, so patch after creation
        agent = main_artist_agent.ArtistAgent()
        agent.tools = {mock_calculator_tool.name: mock_calculator_tool.run}
        return agent
    pytest.skip("ArtistAgent not found in main_artist_agent.py")


def test_artist_agent_uses_calculator_for_arithmetic(
    artist_agent_with_tools, mock_calculator_tool
):
    """Test that ArtistAgent selects and uses the 'calculator' tool for an arithmetic prompt."""
    prompt = "What is 2 + 3 * 4?"
    # ArtistAgent uses the run method
    if hasattr(artist_agent_with_tools, "run"):
        response = artist_agent_with_tools.run(prompt)
    else:
        pytest.skip("ArtistAgent missing 'run' method.")

    # The calculator tool should have been called
    assert mock_calculator_tool.run.called, "Calculator tool was not called"
    assert "14" in str(response), "Agent did not return calculator result"


def test_artist_agent_no_matching_tool():
    """Test that ArtistAgent returns an appropriate message if no tool matches the prompt."""
    dummy_tool = Mock()
    dummy_tool.name = "not_calculator"
    dummy_tool.description = "Not a calculator"
    dummy_tool.run = Mock(return_value="I can't help with that.")

    # Patch ArtistAgent to only have an irrelevant tool
    if hasattr(main_artist_agent, "ArtistAgent"):
        agent = main_artist_agent.ArtistAgent()
        agent.tools = {
            dummy_tool.name: dummy_tool.run
        }  # Override tools with dummy tool
    else:
        pytest.skip("ArtistAgent not found in main_artist_agent.py")

    prompt = "What is 2 + 2?"
    if hasattr(agent, "run"):
        response = agent.run(prompt)
    else:
        pytest.skip("ArtistAgent missing 'run' method.")

    # The dummy tool should not trigger a valid answer
    assert (
        "no tool" in str(response).lower()
        or "no suitable tool" in str(response).lower()
        or "can't help" in str(response).lower()
        or "not available" in str(response).lower()
    ), "Agent did not respond appropriately to missing tool"


def test_artist_agent_multistep_reasoning_placeholder():
    """
    Placeholder test for multi-step reasoning/tool chaining.

    Expand this test when multi-step tool use is implemented in ArtistAgent.
    """
    # NOTE: Implement when ArtistAgent supports multi-step/tool chaining.
