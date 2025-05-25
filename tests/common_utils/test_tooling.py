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

        self.assertEqual(retrieved_tool, dummy_tool)
        self.assertEqual(retrieved_tool("test"), "processed: test")

    def test_list_tools(self) -> None:
        """Test listing all registered tools."""
        tools = tooling.list_tools()

        # Should contain at least the default tools
        self.assertIn("calculator", tools)
        self.assertIn("text_analyzer", tools)

        # Should be a dictionary
        self.assertIsInstance(tools, dict)


class TestCalculatorTool(unittest.TestCase):
    """Test cases for the calculator tool."""

    def test_basic_arithmetic(self) -> None:
        """Test basic arithmetic operations."""
        calculator = tooling.get_tool("calculator")

        self.assertEqual(calculator("2 + 3"), 5)
        self.assertEqual(calculator("10 - 4"), 6)
        self.assertEqual(calculator("3 * 4"), 12)
        self.assertEqual(calculator("15 / 3"), 5.0)

    def test_complex_expressions(self) -> None:
        """Test more complex mathematical expressions."""
        calculator = tooling.get_tool("calculator")

        self.assertEqual(calculator("2 + 3 * 4"), 14)
        self.assertEqual(calculator("(2 + 3) * 4"), 20)
        self.assertEqual(calculator("10 % 3"), 1)

    def test_invalid_expressions(self) -> None:
        """Test handling of invalid expressions."""
        calculator = tooling.get_tool("calculator")

        result = calculator("invalid expression")
        self.assertIn("Error", str(result))

        result = calculator("2 + abc")
        self.assertIn("Error", str(result))


class TestTextAnalyzerTool(unittest.TestCase):
    """Test cases for the text_analyzer tool."""

    def test_positive_sentiment(self) -> None:
        """Test positive sentiment analysis."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is a fantastic development!")
        self.assertIn("Sentiment: positive", result)
        self.assertIn("Positive indicators: 1", result)
        self.assertIn("Negative indicators: 0", result)

    def test_negative_sentiment(self) -> None:
        """Test negative sentiment analysis."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is terrible and awful!")
        self.assertIn("Sentiment: negative", result)
        self.assertIn("Positive indicators: 0", result)
        self.assertIn("Negative indicators: 2", result)

    def test_neutral_sentiment(self) -> None:
        """Test neutral sentiment analysis."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is a regular statement.")
        self.assertIn("Sentiment: neutral", result)
        self.assertIn("Positive indicators: 0", result)
        self.assertIn("Negative indicators: 0", result)

    def test_mixed_sentiment(self) -> None:
        """Test mixed sentiment with equal positive and negative indicators."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("I love this but I also hate that part.")
        self.assertIn("Sentiment: neutral", result)  # Equal positive and negative
        self.assertIn("Positive indicators: 1", result)
        self.assertIn("Negative indicators: 1", result)

    def test_word_and_character_count(self) -> None:
        """Test word and character counting functionality."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("Hello world")
        self.assertIn("Words: 2", result)
        self.assertIn("Characters: 11", result)

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("")
        self.assertIn("Sentiment: neutral", result)
        self.assertIn("Words: 0", result)
        self.assertIn("Characters: 0", result)

    def test_case_insensitive_analysis(self) -> None:
        """Test that sentiment analysis is case insensitive."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result_lower = text_analyzer("this is great")
        result_upper = text_analyzer("THIS IS GREAT")
        result_mixed = text_analyzer("This Is Great")

        # All should detect positive sentiment
        self.assertIn("Sentiment: positive", result_lower)
        self.assertIn("Sentiment: positive", result_upper)
        self.assertIn("Sentiment: positive", result_mixed)

    def test_multiple_sentiment_words(self) -> None:
        """Test text with multiple sentiment indicators."""
        text_analyzer = tooling.get_tool("text_analyzer")

        result = text_analyzer("This is excellent, wonderful, and amazing!")
        self.assertIn("Sentiment: positive", result)
        self.assertIn("Positive indicators: 3", result)

    def test_error_handling(self) -> None:
        """Test error handling in text analyzer."""
        text_analyzer = tooling.get_tool("text_analyzer")

        # Mock an exception to test error handling
        with patch('common_utils.tooling.len', side_effect=Exception("Test error")):
            result = text_analyzer("test text")
            self.assertIn("Error analyzing text", result)


if __name__ == "__main__":
    unittest.main()
