"""Type definitions for mock_crewai package to avoid circular imports."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, TypeVar

# Define type variables for forward references
AgentVar = TypeVar("AgentVar", bound="Agent")
TaskVar = TypeVar("TaskVar", bound="Task")
CrewVar = TypeVar("CrewVar", bound="Crew")

# Define type aliases
AgentDict = Dict[str, Any]
TaskDict = Dict[str, Any]
CrewDict = Dict[str, Any]

# Define enums for agent, task, and crew types
class AgentType(Enum):
    """Enum for agent types."""
    DEFAULT = "default"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"

class TaskType(Enum):
    """Enum for task types."""
    DEFAULT = "default"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CUSTOM = "custom"

class CrewType(Enum):
    """Enum for crew types."""
    DEFAULT = "default"
    HIERARCHICAL = "hierarchical"
    CUSTOM = "custom"

# These empty class definitions are just for type checking
# and will be replaced by the actual implementations
class Agent:
    """Type stub for Agent class."""


class Task:
    """Type stub for Task class."""


class Crew:
    """Type stub for Crew class."""
