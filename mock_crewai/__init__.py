"""
Mock CrewAI package for testing without requiring the actual CrewAI package.

This package provides mock implementations of the core CrewAI classes:
- Agent: Mock implementation of CrewAI Agent
- Crew: Mock implementation of CrewAI Crew
- Task: Mock implementation of CrewAI Task

These mocks allow tests to run without requiring the actual CrewAI package
to be installed, which can be useful in CI environments or for users who
don't need the full CrewAI functionality.
"""

# Define version first at the module level
__version__ = "0.120.0"

# Import types first to avoid circular imports
from . import tools

# Import classes in a specific order to avoid circular imports
from .agent import Agent
from .crew import Crew
from .task import Task
from .types import AgentType, CrewType, TaskType

# Define what should be exported
__all__ = ["Agent", "AgentType", "Crew", "CrewType", "Task", "TaskType", "__version__", "tools"]

# Ensure __version__ is accessible when importing the module
# This is needed for compatibility with different import styles
import sys

sys.modules[__name__].__version__ = __version__

# Mock CrewAI module for CI environments
class MockAgent:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, task):
        return "mock result"

class MockCrew:
    def __init__(self, *args, **kwargs):
        pass

    def kickoff(self):
        return "mock crew result"

class MockTask:
    def __init__(self, *args, **kwargs):
        pass

# Mock the main CrewAI classes
Agent = MockAgent
Crew = MockCrew
Task = MockTask
