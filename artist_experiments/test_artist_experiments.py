"""
Tests for ARTIST experiments.

This module contains tests for the ARTIST experiments.
"""

from __future__ import annotations

import json
import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

from artist_experiments import math_problem_solving, multi_api_orchestration

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestMathProblemSolving(unittest.TestCase):
    """Tests for the mathematical problem-solving experiment."""

    def test_solve_equation(self) -> None:
        """Test solving an equation."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.solve_equation("x = 2 + 3")
        assert result == "5"  # nosec # noqa: S101

    def test_factor_expression(self) -> None:
        """Test factoring an expression."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.factor_expression("x**2 - 5*x + 6")
        assert result == "(x - 2)*(x - 3)"  # nosec # noqa: S101

    def test_expand_expression(self) -> None:
        """Test expanding an expression."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.expand_expression("(x + 2)*(x - 3)")
        assert result == "x**2 - x - 6"  # nosec # noqa: S101

    @patch("ai_models.artist_agent.ArtistAgent.run")
    def test_run_experiment(self, mock_run: MagicMock) -> None:
        """Test running the experiment."""
        mock_run.return_value = "5"
        result = math_problem_solving.run_experiment("Solve 2 + 3")
        assert result == "5"  # nosec # noqa: S101
        mock_run.assert_called_once_with("Solve 2 + 3")


class TestMultiAPIOrchestration(unittest.TestCase):
    """Tests for the multi-API orchestration experiment."""

    def test_search_products(self) -> None:
        """Test searching for products."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.search_products("test", 2)
        result_dict = json.loads(result)
        assert len(result_dict["results"]) == 2  # noqa: PLR2004  # nosec # noqa: S101
        assert result_dict["results"][0]["name"] == "test Product 1"  # nosec # noqa: S101

    def test_get_market_trends(self) -> None:
        """Test getting market trends."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.get_market_trends("electronics")
        result_dict = json.loads(result)
        assert result_dict["category"] == "electronics"  # nosec # noqa: S101
        assert "growth_rate" in result_dict  # nosec # noqa: S101

    def test_analyze_competitors(self) -> None:
        """Test analyzing competitors."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.analyze_competitors("Test Company")
        result_dict = json.loads(result)
        assert result_dict["company"] == "Test Company"  # nosec # noqa: S101
        assert "direct_competitors" in result_dict  # nosec # noqa: S101

    @patch("ai_models.artist_agent.ArtistAgent.run")
    def test_run_experiment(self, mock_run: MagicMock) -> None:
        """Test running the experiment."""
        mock_result = json.dumps({"results": [{"name": "test Product 1"}]})
        mock_run.return_value = mock_result
        result = multi_api_orchestration.run_experiment("Search for test products")
        assert result == mock_result  # nosec # noqa: S101
        mock_run.assert_called_once_with("Search for test products")


if __name__ == "__main__":
    unittest.main()
