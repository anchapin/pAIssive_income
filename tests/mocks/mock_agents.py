"""
Mock agent classes for testing.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock


class MockResearchAgent:
    """Mock Research Agent for testing."""

    def __init__(self, team=None, **kwargs):
        """Initialize the mock Research Agent."""
        self.team = team
        self._name = "Mock Research Agent"
        self._description = "Mock agent for testing"
        self.model_settings = {}
        self.is_configured = MagicMock(return_value=True)
        self.analyze_market_segments = MagicMock(return_value=[])

    @property
    def name(self) -> str:
        """Get the agent name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the agent description."""
        return self._description


class MockDeveloperAgent:
    """Mock Developer Agent for testing."""

    def __init__(self, team=None, **kwargs):
        """Initialize the mock Developer Agent."""
        self.team = team
        self.name = "Mock Developer Agent"
        self.description = "Mock agent for testing"
        self.model_settings = {}
        self.is_configured = MagicMock(return_value=True)
        self.design_solution = MagicMock(return_value={})


class MockMonetizationAgent:
    """Mock Monetization Agent for testing."""

    def __init__(self, team=None, **kwargs):
        """Initialize the mock Monetization Agent."""
        self.team = team
        self.name = "Mock Monetization Agent"
        self.description = "Mock agent for testing"
        self.model_settings = {}
        self.is_configured = MagicMock(return_value=True)
        self.create_strategy = MagicMock(return_value={})


class MockMarketingAgent:
    """Mock Marketing Agent for testing."""

    def __init__(self, team=None, **kwargs):
        """Initialize the mock Marketing Agent."""
        self.team = team
        self.name = "Mock Marketing Agent"
        self.description = "Mock agent for testing"
        self.model_settings = {}
        self.is_configured = MagicMock(return_value=True)
        self.create_plan = MagicMock(return_value={})


class MockFeedbackAgent:
    """Mock Feedback Agent for testing."""

    def __init__(self, team=None, **kwargs):
        """Initialize the mock Feedback Agent."""
        self.team = team
        self.name = "Mock Feedback Agent"
        self.description = "Mock agent for testing"
        self.model_settings = {}
        self.is_configured = MagicMock(return_value=True)
        self.analyze_feedback = MagicMock(return_value={})
