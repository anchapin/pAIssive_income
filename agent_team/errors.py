"""
Error definitions for agent_team package.
"""

from typing import Optional


class AgentTeamError(Exception):
    """Base exception for agent_team errors."""


class DependencyNotInstalledError(AgentTeamError):
    """Raised when an optional dependency is not installed."""

    def __init__(self, dependency: str, extra: Optional[str] = None):
        msg = f"Required dependency '{dependency}' is not installed."
        if extra:
            msg += f" {extra}"
        super().__init__(msg)


class AgentNotFoundError(AgentTeamError):
    """Raised when an agent with a given role or name cannot be found."""


class TaskAssignmentError(AgentTeamError):
    """Raised when a task cannot be assigned to an agent."""