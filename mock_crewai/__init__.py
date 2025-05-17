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

# Define version first
__version__ = "0.120.0"

# Import classes - using string type annotations in the classes themselves
# to avoid circular imports
from .agent import Agent
from .crew import Crew
from .task import Task

# Define what should be exported
__all__ = ["Agent", "Crew", "Task", "__version__"]
