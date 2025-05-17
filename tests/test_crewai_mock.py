"""Test module for mock_crewai module."""

import os
import sys
import importlib
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the mock_crewai module directly
mock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai")
if os.path.exists(mock_dir):
    sys.path.insert(0, os.path.dirname(mock_dir))

import mock_crewai as crewai


class TestCrewAIMock:
    """Test suite for mock_crewai module."""

    def test_version_attribute(self):
        """Test that the __version__ attribute is defined."""
        assert hasattr(crewai, "__version__")
        assert isinstance(crewai.__version__, str)
        assert crewai.__version__ == "0.120.0"
        
    def test_version_attribute_in_init(self):
        """Test that the __version__ attribute is defined in __init__.py."""
        # Import the module directly to check its attributes
        import mock_crewai
        assert hasattr(mock_crewai, "__version__")
        assert isinstance(mock_crewai.__version__, str)
        assert mock_crewai.__version__ == "0.120.0"
        
    def test_version_attribute_import(self):
        """Test that the __version__ attribute can be imported directly."""
        # Test direct import of __version__
        from mock_crewai import __version__
        assert __version__ == "0.120.0"

    def test_agent_class(self):
        """Test the Agent class."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            verbose=True,
            allow_delegation=False,
        )

        # Verify the agent attributes
        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"
        assert "verbose" in agent.kwargs
        assert agent.kwargs["verbose"] is True
        assert "allow_delegation" in agent.kwargs
        assert agent.kwargs["allow_delegation"] is False
        
    def test_agent_str_representation(self):
        """Test the string representation of the Agent class."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )
        
        # Verify the string representation
        assert str(agent) == "Agent(role='Test Agent')"
        assert repr(agent) == "Aegnt(role='Test Agent', goal='Test goal', backstory='Test backstory')"

    def test_agent_execute_task(self):
        """Test the Agent.execute_task method."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Create a task
        task = crewai.Task(
            description="Test task",
            agent=agent,
        )

        # Execute the task
        result = agent.execute_task(task)

        # Verify the result
        assert result == "Executed task: Test task"
        
    def test_agent_execute_task_with_context(self):
        """Test the Agent.execute_task method with context."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Create a task
        task = crewai.Task(
            description="Test task",
            agent=agent,
        )

        # Execute the task with context
        context = "Additional context"
        result = agent.execute_task(task, context=context)

        # Verify the result includes the context
        assert result == f"Executed task: Test task with context: {context}"