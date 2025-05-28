"""Tests for the ARTIST-style agent wrapper."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from ai_models.artist_agent import ArtistAgent


class TestArtistAgent:
    """Tests for the ArtistAgent class."""

    @patch("common_utils.tooling.list_tools")
    def test_initialization(self, mock_list_tools):
        """Test that the agent initializes correctly."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock(), "search": MagicMock(), "weather": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Verify tools were loaded
        mock_list_tools.assert_called_once()
        assert list(agent.tools.keys()) == ["calculator", "search", "weather"]

    @patch("common_utils.tooling.list_tools")
    def test_decide_tool_calculator(self, mock_list_tools):
        """Test that the agent selects the calculator tool correctly."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock(), "search": MagicMock(), "weather": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Test calculator selection with different prompts
        calculator_prompts = [
            "Calculate 2 + 2",
            "What is 5 * 10?",
            "Can you add 7 and 3?",
            "Subtract 5 from 10",
            "Multiply 6 by 8",
            "Divide 100 by 4",
            "What's 2 + 3 * 4?",
            "Calculate the sum of 5 and 7",
        ]

        for prompt in calculator_prompts:
            assert agent.decide_tool(prompt) == "calculator"

    @patch("common_utils.tooling.list_tools")
    def test_decide_tool_no_match(self, mock_list_tools):
        """Test that the agent returns empty string when no tool matches."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock(), "search": MagicMock(), "weather": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Test prompts that shouldn't match any tool
        no_match_prompts = [
            "Tell me a joke",
            "What's the weather like?",
            "Search for information about AI",
            "How are you today?",
        ]

        for prompt in no_match_prompts:
            assert agent.decide_tool(prompt) == ""

    @patch("common_utils.tooling.list_tools")
    def test_decide_tool_case_insensitive(self, mock_list_tools):
        """Test that the tool selection is case-insensitive."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock(), "search": MagicMock(), "weather": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Test case-insensitive matching
        prompts = [
            "CALCULATE 2 + 2",
            "calculate 5 * 10",
            "Calculate the sum",
            "ADD these numbers",
            "add 5 and 7",
        ]

        for prompt in prompts:
            assert agent.decide_tool(prompt) == "calculator"

    @patch("common_utils.tooling.list_tools")
    def test_extract_relevant_expression_calculator(self, mock_list_tools):
        """Test extracting relevant expression for calculator tool."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Test extraction for calculator
        prompt = "Calculate 2 + 3 * 4"
        result = agent.extract_relevant_expression(prompt, "calculator")
        assert result == prompt

    @patch("common_utils.tooling.list_tools")
    def test_extract_relevant_expression_default(self, mock_list_tools):
        """Test extracting relevant expression for unknown tool."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Test extraction for unknown tool
        prompt = "Tell me a joke"
        result = agent.extract_relevant_expression(prompt, "joke")
        assert result == prompt

    @patch("common_utils.tooling.list_tools")
    def test_run_with_valid_tool(self, mock_list_tools):
        """Test running the agent with a valid tool."""
        # Setup mock calculator function
        mock_calculator = MagicMock(return_value="14")
        mock_list_tools.return_value = {"calculator": mock_calculator}

        # Create agent
        agent = ArtistAgent()

        # Test running with calculator prompt
        result = agent.run("Calculate 2 + 3 * 4")

        # Verify calculator was called
        mock_calculator.assert_called_once_with("Calculate 2 + 3 * 4")
        assert result == "14"

    @patch("common_utils.tooling.list_tools")
    def test_run_with_no_matching_tool(self, mock_list_tools):
        """Test running the agent with no matching tool."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock()}

        # Create agent
        agent = ArtistAgent()

        # Test running with non-calculator prompt
        result = agent.run("Tell me a joke")

        # Verify result is the default message
        assert result == "No suitable tool found for this prompt."

    @patch("common_utils.tooling.list_tools")
    def test_run_with_unknown_tool(self, mock_list_tools):
        """Test running the agent with a tool that doesn't exist."""
        # Setup mock
        mock_list_tools.return_value = {"calculator": MagicMock()}

        # Create agent with a modified decide_tool method
        agent = ArtistAgent()
        agent.decide_tool = MagicMock(return_value="unknown_tool")

        # Test running with unknown tool
        result = agent.run("Some prompt")

        # Verify result is the default message
        assert result == "No suitable tool found for this prompt."
