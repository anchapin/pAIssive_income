#!/usr/bin/env python3
"""
Test script for common_utils/tooling.py.

This script tests the tool registry and individual tools including
the text_analyzer tool as requested in the code review.
"""

import unittest
from unittest.mock import patch

from common_utils import tooling


class TestToolRegistry(unittest.TestCase):
    """Test cases for the tool registry functionality."""

    def test_register_and_get_tool(self) -> None:
        """Test registering and retrieving a tool."""
        def dummy_tool(x: str) -> str:
            return f"processed: {x}"

        tooling.register_tool("dummy", dummy_tool)
        retrieved_tool = tooling.get_tool("dummy")

        assert retrieved_tool == dummy_tool
        assert retrieved_tool("test") == "processed: test"

    def test_list_tools(self) -> None:
        """Test listing all registered tools."""
        tools = tooling.list_tools()

        # Should contain at least the default tools
        assert "calculator" in tools
        assert "text_analyzer" in tools

        # Should be a dictionary
        assert isinstance(tools, dict)


class TestCalculatorTool(unittest.TestCase):
    """Test cases for the calculator tool."""

    def test_basic_arithmetic(self) -> None:
        """Test basic arithmetic operations."""
        calculator = tooling.get_tool("calculator")

        assert calculator("2 + 3") == 5
        assert calculator("10 - 4") == 6
        assert calculator("3 * 4") == 12
        assert calculator("15 / 3") == 5.0

    def test_complex_expressions(self) -> None:
        """Test more complex mathematical expressions."""
        calculator = tooling.get_tool("calculator")

        assert calculator("2 + 3 * 4") == 14
        assert calculator("(2 + 3) * 4") == 20
        assert calculator("10 % 3") == 1

    def test_invalid_expressions(self) -> None:
        """Test handling of invalid expressions."""
        calculator = tooling.get_tool("calculator")

        result = calculator("invalid expression")
        assert "Error" in str(result)

        result = calculator("2 + abc")
        assert "Error" in str(result)


class TestTextAnalyzerTool(unittest.TestCase):
    """Test cases for the text_analyzer tool."""

    def test_positive_sentiment(self) -> None:
        """Test positive sentiment analysis."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is a fantastic development!")
        assert "Sentiment: positive" in result
        assert "Positive indicators: 1" in result
        assert "Negative indicators: 0" in result

    def test_negative_sentiment(self) -> None:
        """Test negative sentiment analysis."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is terrible and awful!")
        assert "Sentiment: negative" in result
        assert "Positive indicators: 0" in result
        assert "Negative indicators: 2" in result

    def test_neutral_sentiment(self) -> None:
        """Test neutral sentiment analysis."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is a regular statement.")
        assert "Sentiment: neutral" in result
        assert "Positive indicators: 0" in result
        assert "Negative indicators: 0" in result

    def test_mixed_sentiment(self) -> None:
        """Test mixed sentiment with equal positive and negative indicators."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("I love this but I also hate that part.")
        assert "Sentiment: neutral" in result  # Equal positive and negative
        assert "Positive indicators: 1" in result
        assert "Negative indicators: 1" in result

    def test_word_and_character_count(self) -> None:
        """Test word and character counting functionality."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("Hello world")
        assert "Words: 2" in result
        assert "Characters: 11" in result

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("")
        assert "Sentiment: neutral" in result
        assert "Words: 0" in result
        assert "Characters: 0" in result

    def test_case_insensitive_analysis(self) -> None:
        """Test that sentiment analysis is case insensitive."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result_lower = text_analyzer("this is great")
        result_upper = text_analyzer("THIS IS GREAT")
        result_mixed = text_analyzer("This Is Great")

        # All should detect positive sentiment
        assert "Sentiment: positive" in result_lower
        assert "Sentiment: positive" in result_upper
        assert "Sentiment: positive" in result_mixed

    def test_multiple_sentiment_words(self) -> None:
        """Test text with multiple sentiment indicators."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is excellent, wonderful, and amazing!")
        assert "Sentiment: positive" in result
        assert "Positive indicators: 3" in result

    def test_error_handling(self) -> None:
        """Test error handling in text analyzer."""
        text_analyzer = tooling.get_tool("text_analyzer")

        # Mock an exception to test error handling
        with patch("common_utils.tooling.len", side_effect=Exception("Test error")):
            result = text_analyzer("test text")
            assert "Error analyzing text" in result


if __name__ == "__main__":
    unittest.main()
