"""Tests for the ARTIST-style agent wrapper."""

import pytest
from unittest.mock import patch, MagicMock

from ai_models.artist_agent import ArtistAgent


class TestArtistAgent:
    """Tests for the ArtistAgent class."""

    @patch("common_utils.tooling.list_tools")
    def test_initialization(self, mock_list_tools):
        """Test that the agent initializes correctly."""
        # Setup mock
        mock_list_tools.return_value = ["calculator", "search", "weather"]
        
        # Create agent
        agent = ArtistAgent()
        
        # Verify tools were loaded
        mock_list_tools.assert_called_once()
        assert agent.tools == ["calculator", "search", "weather"]

    @patch("common_utils.tooling.list_tools")
    def test_decide_tool_calculator(self, mock_list_tools):
        """Test that the agent selects the calculator tool correctly."""
        # Setup mock
        mock_list_tools.return_value = ["calculator", "search", "weather"]
        
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
        mock_list_tools.return_value = ["calculator", "search", "weather"]
        
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
        mock_list_tools.return_value = ["calculator", "search", "weather"]
        
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
