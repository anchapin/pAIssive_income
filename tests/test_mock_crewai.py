"""test_mock_crewai - Test for mock_crewai module."""

# Standard library imports
import unittest

# Third-party imports
import pytest

# Local imports
import mock_crewai
from mock_crewai import Agent, Crew, Task, __version__


def test_mock_crewai_version():
    """Test that the mock_crewai version is correct."""
    assert mock_crewai.__version__ == "0.120.0"


def test_version_import():
    """Test that __version__ is imported correctly."""
    assert __version__ == "0.120.0"


def test_agent_class():
    """Test that Agent class is available."""
    assert hasattr(mock_crewai, "Agent")
    assert Agent.__name__ == "MockAgent"


def test_crew_class():
    """Test that Crew class is available."""
    assert hasattr(mock_crewai, "Crew")
    assert Crew.__name__ == "MockCrew"


def test_task_class():
    """Test that Task class is available."""
    assert hasattr(mock_crewai, "Task")
    assert Task.__name__ == "MockTask"


def test_agent_creation():
    """Test that Agent can be created."""
    agent = Agent(name="Test Agent", role="Test Role")
    assert agent.name == "Test Agent"
    assert agent.role == "Test Role"


def test_task_creation():
    """Test that Task can be created."""
    task = Task(description="Test Task")
    assert task.description == "Test Task"


def test_crew_creation():
    """Test that Crew can be created."""
    agent = Agent(name="Test Agent", role="Test Role")
    task = Task(description="Test Task")
    crew = Crew(agents=[agent], tasks=[task])
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1
