#!/usr/bin/env python3
"""
Comprehensive tests for the common_utils.tooling module.

This script tests the tool registry and individual tools including
the calculator and text_analyzer tools.
"""

import logging
import re
import ast
import pytest
from typing import Callable, Dict, Any
from unittest.mock import patch

from common_utils.tooling import (
    register_tool,
    get_tool,
    list_tools,
    calculator,
    text_analyzer,
    _TOOL_REGISTRY,
    MAX_EXPONENT_VALUE,
)


@pytest.fixture
def clean_registry():
    """Clean tool registry before and after each test."""
    # Save the original registry
    original_registry = dict(_TOOL_REGISTRY)
    # Clear the registry for testing
    _TOOL_REGISTRY.clear()
    yield
    # Restore the original registry
    _TOOL_REGISTRY.clear()
    _TOOL_REGISTRY.update(original_registry)


class TestToolRegistry:
    """Test cases for the tool registry functionality."""

    def test_register_tool(self, clean_registry):
        """Test register_tool function."""
        # Define a test function
        def test_func(x: int) -> int:
            return x * 2

        # Register the function
        register_tool("test_tool", test_func)

        # Check if the function was registered
        assert "test_tool" in _TOOL_REGISTRY
        assert _TOOL_REGISTRY["test_tool"] is test_func

    def test_get_tool(self, clean_registry):
        """Test get_tool function."""
        # Define a test function
        def test_func(x: int) -> int:
            return x * 2

        # Register the function
        _TOOL_REGISTRY["test_tool"] = test_func

        # Get the function
        func = get_tool("test_tool")

        # Check if the correct function was returned
        assert func is test_func
        assert func(5) == 10

    def test_get_tool_nonexistent(self, clean_registry):
        """Test get_tool with a nonexistent tool."""
        # Try to get a nonexistent tool
        with pytest.raises(KeyError):
            get_tool("nonexistent_tool")

    def test_list_tools(self, clean_registry):
        """Test list_tools function."""
        # Define test functions
        def test_func1(x: int) -> int:
            return x * 2

        def test_func2(x: int) -> int:
            return x * 3

        # Register the functions
        _TOOL_REGISTRY["test_tool1"] = test_func1
        _TOOL_REGISTRY["test_tool2"] = test_func2

        # List the tools
        tools = list_tools()

        # Check if the correct tools were returned
        assert isinstance(tools, dict)
        assert len(tools) == 2
        assert "test_tool1" in tools
        assert "test_tool2" in tools
        assert tools["test_tool1"] is test_func1
        assert tools["test_tool2"] is test_func2

    def test_list_tools_empty(self, clean_registry):
        """Test list_tools function with an empty registry."""
        # List the tools
        tools = list_tools()

        # Check if an empty dict was returned
        assert isinstance(tools, dict)
        assert len(tools) == 0

    def test_register_tool_overwrite(self, clean_registry):
        """Test register_tool function with overwriting an existing tool."""
        # Define test functions
        def test_func1(x: int) -> int:
            return x * 2

        def test_func2(x: int) -> int:
            return x * 3

        # Register the first function
        register_tool("test_tool", test_func1)
        assert _TOOL_REGISTRY["test_tool"] is test_func1

        # Register the second function with the same name
        register_tool("test_tool", test_func2)
        assert _TOOL_REGISTRY["test_tool"] is test_func2

    def test_register_tool_with_lambda(self, clean_registry):
        """Test register_tool function with a lambda function."""
        # Define a lambda function
        lambda_func = lambda x: x * 2

        # Register the lambda function
        register_tool("lambda_tool", lambda_func)

        # Check if the function was registered
        assert "lambda_tool" in _TOOL_REGISTRY
        assert _TOOL_REGISTRY["lambda_tool"] is lambda_func

        # Test the function
        func = get_tool("lambda_tool")
        assert func(5) == 10

    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        def dummy_tool(x: str) -> str:
            return f"processed: {x}"

        register_tool("dummy", dummy_tool)
        retrieved_tool = get_tool("dummy")

        assert retrieved_tool == dummy_tool
        assert retrieved_tool("test") == "processed: test"

    def test_list_tools_contains_defaults(self):
        """Test listing all registered tools includes defaults."""
        tools = list_tools()

        # Should contain at least the default tools
        assert "calculator" in tools
        assert "text_analyzer" in tools

        # Should be a dictionary
        assert isinstance(tools, dict)


class TestCalculatorTool:
    """Test cases for the calculator tool."""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        assert calculator("2 + 3") == 5
        assert calculator("10 - 4") == 6
        assert calculator("3 * 4") == 12
        assert calculator("15 / 3") == 5.0

    def test_complex_expressions(self):
        """Test more complex mathematical expressions."""
        assert calculator("2 + 3 * 4") == 14
        assert calculator("(2 + 3) * 4") == 20
        assert calculator("10 % 3") == 1

    def test_calculator_with_parentheses(self):
        """Test calculator function with parentheses."""
        result = calculator("(2 + 3) * 4")
        assert result == 20

    def test_calculator_with_float_numbers(self):
        """Test calculator function with float numbers."""
        result = calculator("2.5 + 3.5")
        assert result == 6.0

    def test_calculator_with_modulo(self):
        """Test calculator function with modulo operation."""
        result = calculator("10 % 3")
        assert result == 1

    def test_calculator_with_exponentiation(self):
        """Test calculator function with exponentiation."""
        # This should be allowed since the values are small
        result = calculator("2 ** 3")
        assert result == 8

    def test_calculator_with_large_exponentiation(self):
        """Test calculator function with large exponentiation values."""
        # This should be rejected due to the MAX_EXPONENT_VALUE limit
        result = calculator(f"{MAX_EXPONENT_VALUE + 1} ** 2")
        assert isinstance(result, str)
        assert "Error:" in result
        assert str(MAX_EXPONENT_VALUE) in result

    def test_calculator_error(self):
        """Test calculator function with an invalid expression."""
        result = calculator("2 + / 3")
        assert isinstance(result, str)
        assert result.startswith("Error:")

    def test_calculator_security(self):
        """Test calculator function security (no access to builtins)."""
        result = calculator("__import__('os').system('echo security_breach')")
        assert isinstance(result, str)
        assert result.startswith("Error:")

    def test_calculator_with_invalid_characters(self):
        """Test calculator function with invalid characters."""
        result = calculator("2 + 3; import os")
        assert isinstance(result, str)
        assert "Error:" in result
        assert "Invalid characters" in result

    def test_calculator_with_empty_expression(self):
        """Test calculator function with an empty expression."""
        result = calculator("")
        assert isinstance(result, str)
        assert "Error:" in result

    def test_calculator_with_whitespace_only(self):
        """Test calculator function with whitespace only."""
        result = calculator("   ")
        assert isinstance(result, str)
        assert "Error:" in result

    def test_invalid_expressions(self):
        """Test handling of invalid expressions."""
        result = calculator("invalid expression")
        assert "Error" in str(result)

        result = calculator("2 + abc")
        assert "Error" in str(result)

    def test_calculator_registered(self, clean_registry):
        """Test that calculator is registered as a tool."""
        # Register the calculator tool explicitly for this test
        register_tool("calculator", calculator)

        # Now check if it's registered
        tools = list_tools()
        assert "calculator" in tools
        assert tools["calculator"] is calculator


class TestTextAnalyzerTool:
    """Test cases for the text_analyzer tool."""

    def test_positive_sentiment(self):
        """Test positive sentiment analysis."""
        result = text_analyzer("This is a fantastic development!")
        assert "Sentiment: positive" in result
        assert "Positive indicators: 1" in result
        assert "Negative indicators: 0" in result

    def test_negative_sentiment(self):
        """Test negative sentiment analysis."""
        result = text_analyzer("This is terrible and awful!")
        assert "Sentiment: negative" in result
        assert "Positive indicators: 0" in result
        assert "Negative indicators: 2" in result

    def test_neutral_sentiment(self):
        """Test neutral sentiment analysis."""
        result = text_analyzer("This is a regular statement.")
        assert "Sentiment: neutral" in result
        assert "Positive indicators: 0" in result
        assert "Negative indicators: 0" in result

    def test_mixed_sentiment(self):
        """Test mixed sentiment with equal positive and negative indicators."""
        result = text_analyzer("I love this but I also hate that part.")
        assert "Sentiment: neutral" in result  # Equal positive and negative
        assert "Positive indicators: 1" in result
        assert "Negative indicators: 1" in result

    def test_word_and_character_count(self):
        """Test word and character counting functionality."""
        result = text_analyzer("Hello world")
        assert "Words: 2" in result
        assert "Characters: 11" in result

    def test_empty_text(self):
        """Test handling of empty text."""
        result = text_analyzer("")
        assert "Sentiment: neutral" in result
        assert "Words: 0" in result
        assert "Characters: 0" in result

    def test_case_insensitive_analysis(self):
        """Test that sentiment analysis is case insensitive."""
        result_lower = text_analyzer("this is great")
        result_upper = text_analyzer("THIS IS GREAT")
        result_mixed = text_analyzer("This Is Great")

        # All should detect positive sentiment
        assert "Sentiment: positive" in result_lower
        assert "Sentiment: positive" in result_upper
        assert "Sentiment: positive" in result_mixed

    def test_multiple_sentiment_words(self):
        """Test text with multiple sentiment indicators."""
        result = text_analyzer("This is excellent, wonderful, and amazing!")
        assert "Sentiment: positive" in result
        assert "Positive indicators: 3" in result

    def test_error_handling(self):
        """Test error handling in text analyzer."""
        # Mock an exception to test error handling
        with patch('common_utils.tooling.len', side_effect=Exception("Test error")):
            result = text_analyzer("test text")
            assert "Error analyzing text" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
