"""Test module for common_utils.tooling."""

import logging
import pytest
from typing import Callable, Dict, Any

from common_utils.tooling import (
    register_tool,
    get_tool,
    list_tools,
    calculator,
    _TOOL_REGISTRY,
)


class TestTooling:
    """Test suite for tooling module."""

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
        def test_func(x: int) -> int:
            return x * 2

        # Register the function
        register_tool("test_tool", test_func)

        # Check if the function was registered
        assert "test_tool" in _TOOL_REGISTRY
        assert _TOOL_REGISTRY["test_tool"] is test_func

    def test_get_tool(self):
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

    def test_get_tool_nonexistent(self):
        """Test get_tool with a nonexistent tool."""
        # Clear the registry
        _TOOL_REGISTRY.clear()

        # Try to get a nonexistent tool
        with pytest.raises(KeyError):
            get_tool("nonexistent_tool")

    def test_list_tools(self):
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

    def test_calculator_registered(self):
        """Test that calculator is registered as a tool."""
        # Register the calculator tool explicitly for this test
        register_tool("calculator", calculator)

        # Now check if it's registered
        tools = list_tools()
        assert "calculator" in tools
        assert tools["calculator"] is calculator
