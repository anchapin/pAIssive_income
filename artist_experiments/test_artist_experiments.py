"""
Tests for ARTIST experiments.

This module contains tests for the ARTIST experiments.
"""

import json
import unittest
from unittest.mock import patch

from artist_experiments import math_problem_solving, multi_api_orchestration


class TestMathProblemSolving(unittest.TestCase):
    """Tests for the mathematical problem-solving experiment."""

    def test_solve_equation(self):
        """Test solving an equation."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.solve_equation("x = 2 + 3")
        self.assertEqual(result, "5")

    def test_factor_expression(self):
        """Test factoring an expression."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.factor_expression("x**2 - 5*x + 6")
        self.assertEqual(result, "(x - 2)*(x - 3)")

    def test_expand_expression(self):
        """Test expanding an expression."""
        math_tool = math_problem_solving.MathTool()
        result = math_tool.expand_expression("(x + 2)*(x - 3)")
        self.assertEqual(result, "x**2 - x - 6")

    @patch("ai_models.artist_agent.ArtistAgent.run")
    def test_run_experiment(self, mock_run):
        """Test running the experiment."""
        mock_run.return_value = "5"
        result = math_problem_solving.run_experiment("Solve 2 + 3")
        self.assertEqual(result, "5")
        mock_run.assert_called_once_with("Solve 2 + 3")


class TestMultiAPIOrchestration(unittest.TestCase):
    """Tests for the multi-API orchestration experiment."""

    def test_search_products(self):
        """Test searching for products."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.search_products("test", 2)
        result_dict = json.loads(result)
        self.assertEqual(len(result_dict["results"]), 2)
        self.assertEqual(result_dict["results"][0]["name"], "test Product 1")

    def test_get_market_trends(self):
        """Test getting market trends."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.get_market_trends("electronics")
        result_dict = json.loads(result)
        self.assertEqual(result_dict["category"], "electronics")
        self.assertIn("growth_rate", result_dict)

    def test_analyze_competitors(self):
        """Test analyzing competitors."""
        api_tool = multi_api_orchestration.APITool()
        result = api_tool.analyze_competitors("Test Company")
        result_dict = json.loads(result)
        self.assertEqual(result_dict["company"], "Test Company")
        self.assertIn("direct_competitors", result_dict)

    @patch("ai_models.artist_agent.ArtistAgent.run")
    def test_run_experiment(self, mock_run):
        """Test running the experiment."""
        mock_result = json.dumps({"results": [{"name": "test Product 1"}]})
        mock_run.return_value = mock_result
        result = multi_api_orchestration.run_experiment("Search for test products")
        self.assertEqual(result, mock_result)
        mock_run.assert_called_once_with("Search for test products")


if __name__ == "__main__":
    unittest.main()
