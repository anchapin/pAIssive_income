# Mock mock_crewai module for CI
__version__ = "0.120.0"

from enum import Enum

# Import types from submodules
from . import tools, types

# Import main classes
from .agent import Agent
from .crew import Crew
from .task import Task
from .types import AgentType, CrewType, TaskType

# Mock attributes
role = "mock_value"
goal = "mock_value"
backstory = "mock_value"
verbose = "mock_value"
allow_delegation = "mock_value"

class Process:
    """Mock Process class."""


# Export all the classes and types
__all__ = [
    "Agent",
    "AgentType",
    "Crew",
    "CrewType",
    "Process",
    "Task",
    "TaskType",
    "tools",
    "types"
]
