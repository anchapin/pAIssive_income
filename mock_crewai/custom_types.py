"""Type definitions for mock_crewai package to avoid circular imports."""

from __future__ import annotations

from typing import Any, Dict, TypeVar

# Define type variables for forward references
AgentType = TypeVar("AgentType", bound="Agent")
TaskType = TypeVar("TaskType", bound="Task")
CrewType = TypeVar("CrewType", bound="Crew")

# Define type aliases
AgentDict = Dict[str, Any]
TaskDict = Dict[str, Any]
CrewDict = Dict[str, Any]


# These empty class definitions are just for type checking
# and will be replaced by the actual implementations
class Agent:
    """Type stub for Agent class."""


class Task:
    """Type stub for Task class."""


class Crew:
    """Type stub for Crew class."""
