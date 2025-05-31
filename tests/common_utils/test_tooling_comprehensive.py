"""Comprehensive tests for the common_utils.tooling module."""

import ast
import operator
import re
from unittest.mock import MagicMock, patch

import pytest

from common_utils.tooling import (
    _TOOL_REGISTRY,
    MAX_EXPONENT_VALUE,
    calculator,
    get_tool,
    list_tools,
    register_tool,
)


class TestToolingComprehensive:
    """Comprehensive test suite for the tooling module."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Save the original registry
        self.original_registry = dict(_TOOL_REGISTRY)
        # Clear the registry for testing
        _TOOL_REGISTRY.clear()

    def teardown_method(self):
        """Clean up after each test."""
        # Restore the original registry
        _TOOL_REGISTRY.clear()
        _TOOL_REGISTRY.update(self.original_registry)

    def test_register_tool(self):
        """Test register_tool function."""
        # Define a test function
        def test_func(x):
            return x * 2

        # Register the function
        register_tool("test_tool", test_func)

        # Check if the function was registered
        assert "test_tool" in _TOOL_REGISTRY
        assert _TOOL_REGISTRY["test_tool"] is test_func

    def test_get_tool(self):
        """Test get_tool function."""
        # Define a test function
        def test_func(x):
            return x * 2

        # Register the function
        _TOOL_REGISTRY["test_tool"] = test_func

        # Get the function
        func = get_tool("test_tool")

        # Check if the correct function was returned
        assert func is test_func
        assert func(5) == 10

    def test_get_tool_nonexistent(self):
        """Test get_tool with a nonexistent tool."""
        # Try to get a nonexistent tool
        with pytest.raises(KeyError):
            get_tool("nonexistent_tool")

    def test_list_tools(self):
        """Test list_tools function."""
        # Define test functions
        def test_func1(x):
            return x * 2

        def test_func2(x):
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

    def test_list_tools_empty(self):
        """Test list_tools with an empty registry."""
        # Clear the registry
        _TOOL_REGISTRY.clear()

        # List the tools
        tools = list_tools()

        # Check if an empty dict was returned
        assert isinstance(tools, dict)
        assert len(tools) == 0

    def test_calculator_addition(self):
        """Test calculator function with addition."""
        result = calculator("2 + 3")
        assert result == 5

    def test_calculator_subtraction(self):
        """Test calculator function with subtraction."""
        result = calculator("5 - 3")
        assert result == 2

    def test_calculator_multiplication(self):
        """Test calculator function with multiplication."""
        result = calculator("2 * 3")
        assert result == 6

    def test_calculator_division(self):
        """Test calculator function with division."""
        result = calculator("6 / 3")
        assert result == 2

    def test_calculator_complex_expression(self):
        """Test calculator function with a complex expression."""
        result = calculator("2 + 3 * 4")
        assert result == 14

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
        result = calculator("2 ** 3")
        assert result == 8

    def test_calculator_with_large_exponentiation(self):
        """Test calculator function with large exponentiation values."""
        # This should be rejected due to the MAX_EXPONENT_VALUE limit
        result = calculator(f"{MAX_EXPONENT_VALUE + 1} ** 2")
        assert isinstance(result, str)
        assert "Error:" in result
        assert str(MAX_EXPONENT_VALUE) in result

    def test_calculator_with_invalid_characters(self):
        """Test calculator function with invalid characters."""
        result = calculator("2 + 3; import os")
        assert isinstance(result, str)
        assert "Error:" in result
        assert "Invalid characters" in result

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

    def test_calculator_registered(self):
        """Test that calculator is registered as a tool."""
        # Register the calculator tool explicitly for this test
        register_tool("calculator", calculator)

        # Now check if it's registered
        tools = list_tools()
        assert "calculator" in tools
        assert tools["calculator"] is calculator

    def test_calculator_with_literal_eval(self):
        """Test calculator function with ast.literal_eval."""
        # This should be handled by ast.literal_eval
        result = calculator("123")
        assert result == 123

    def test_calculator_with_zero_division(self):
        """Test calculator function with division by zero."""
        result = calculator("5 / 0")
        assert isinstance(result, str)
        assert "Error:" in result
        assert "division by zero" in str(result).lower()

    def test_calculator_with_overflow(self):
        """Test calculator function with overflow."""
        # This should cause an OverflowError
        result = calculator("2 ** 1000")
        assert isinstance(result, str)
        assert "Error:" in result

    @patch("ast.literal_eval")
    def test_calculator_with_syntax_error(self, mock_literal_eval):
        """Test calculator function with a syntax error."""
        # Mock ast.literal_eval to raise a SyntaxError
        mock_literal_eval.side_effect = SyntaxError("invalid syntax")

        # This should be handled by the SafeExpressionEvaluator
        result = calculator("2 + 3")
        assert result == 5

    @patch("ast.literal_eval")
    @patch.object(ast, "parse")
    def test_calculator_with_unsupported_node(self, mock_parse, mock_literal_eval):
        """Test calculator function with an unsupported node type."""
        # Mock ast.literal_eval to raise a ValueError
        mock_literal_eval.side_effect = ValueError("malformed node or string")

        # Create a mock AST node that will be unsupported
        mock_node = MagicMock(spec=ast.AST)
        mock_node.__class__.__name__ = "UnsupportedNode"

        # Create a mock expression with the unsupported node
        mock_expr = MagicMock(spec=ast.Expression)
        mock_expr.body = mock_node

        # Mock ast.parse to return the mock expression
        mock_parse.return_value = mock_expr

        # Override the regex check to allow the expression through
        with patch("re.match") as mock_match:
            mock_match.return_value = True  # Make the regex check pass

            # This should raise an error in the SafeExpressionEvaluator
            result = calculator("unsupported_expression")
            assert isinstance(result, str)
            assert "Error:" in result
            # The error message might vary, so we'll check for a more general condition
            assert "Error" in result

    def test_register_tool_overwrite(self):
        """Test register_tool function with overwriting an existing tool."""
        # Define test functions
        def test_func1(x):
            return x * 2

        def test_func2(x):
            return x * 3

        # Register the first function
        register_tool("test_tool", test_func1)
        assert _TOOL_REGISTRY["test_tool"] is test_func1

        # Register the second function with the same name
        register_tool("test_tool", test_func2)
        assert _TOOL_REGISTRY["test_tool"] is test_func2

    def test_register_tool_with_lambda(self):
        """Test register_tool function with a lambda function."""
        # Define a lambda function
        def lambda_func(x):
            return x * 2

        # Register the lambda function
        register_tool("lambda_tool", lambda_func)

        # Check if the function was registered
        assert "lambda_tool" in _TOOL_REGISTRY
        assert _TOOL_REGISTRY["lambda_tool"] is lambda_func

        # Test the function
        func = get_tool("lambda_tool")
        assert func(5) == 10
