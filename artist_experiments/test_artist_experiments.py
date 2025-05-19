"""
Tests for ARTIST experiments.

This module contains tests for the ARTIST experiments.
"""

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from artist_experiments import math_problem_solving, multi_api_orchestration


class TestMathProblemSolving:
    """Tests for the mathematical problem-solving experiment."""

    # Constants for test values
    EQUATION_INPUT = "x = 2 + 3"
    EQUATION_RESULT = "5"
    FACTOR_INPUT = "x**2 - 5*x + 6"
    FACTOR_RESULT = "(x - 2)*(x - 3)"
    EXPAND_INPUT = "(x + 2)*(x - 3)"
    EXPAND_RESULT = "x**2 - x - 6"

    def test_solve_equation(self) -> None:
        """Test solving an equation."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.solve_equation(self.EQUATION_INPUT)
        assert result == self.EQUATION_RESULT

    def test_factor_expression(self) -> None:
        """Test factoring an expression."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.factor_expression(self.FACTOR_INPUT)
        assert result == self.FACTOR_RESULT

    def test_expand_expression(self) -> None:
        """Test expanding an expression."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.expand_expression(self.EXPAND_INPUT)
        assert result == self.EXPAND_RESULT

    # Constants for test values
    EXPECTED_RESULT = "5"
    TEST_PROMPT = "Solve 2 + 3"

    @patch("ai_models.artist_agent.ArtistAgent.run")
    def test_run_experiment(self, mock_run: MagicMock) -> None:
        """Test running the experiment."""
        mock_run.return_value = self.EXPECTED_RESULT
        result = math_problem_solving.run_experiment(self.TEST_PROMPT)
        assert result == self.EXPECTED_RESULT
        mock_run.assert_called_once_with(self.TEST_PROMPT)


class TestMultiAPIOrchestration:
    """Tests for the multi-API orchestration experiment."""

    # Constants for test values
    SEARCH_QUERY = "test"
    SEARCH_LIMIT = 2
    EXPECTED_PRODUCT_NAME = "test Product 1"
    MARKET_CATEGORY = "electronics"
    COMPANY_NAME = "Test Company"

    def test_search_products(self) -> None:
        """Test searching for products."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.search_products(self.SEARCH_QUERY, self.SEARCH_LIMIT)
        result_dict = json.loads(result)
        assert len(result_dict["results"]) == self.SEARCH_LIMIT
        assert result_dict["results"][0]["name"] == self.EXPECTED_PRODUCT_NAME

    def test_get_market_trends(self) -> None:
        """Test getting market trends."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.get_market_trends(self.MARKET_CATEGORY)
        result_dict = json.loads(result)
        assert result_dict["category"] == self.MARKET_CATEGORY
        assert "growth_rate" in result_dict

    def test_analyze_competitors(self) -> None:
        """Test analyzing competitors."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.analyze_competitors(self.COMPANY_NAME)
        result_dict = json.loads(result)
        assert result_dict["company"] == self.COMPANY_NAME
        assert "direct_competitors" in result_dict

    # Constants for test values
    MOCK_RESULT = json.dumps({"results": [{"name": "test Product 1"}]})
    TEST_PROMPT = "Search for test products"

    @patch("ai_models.artist_agent.ArtistAgent.run")
    def test_run_experiment(self, mock_run: MagicMock) -> None:
        """Test running the experiment."""
        mock_run.return_value = self.MOCK_RESULT
        result = multi_api_orchestration.run_experiment(self.TEST_PROMPT)
        assert result == self.MOCK_RESULT
        mock_run.assert_called_once_with(self.TEST_PROMPT)


if __name__ == "__main__":
    pytest.main()
