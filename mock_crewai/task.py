"""Mock implementation of CrewAI Task class for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union

# Only import Agent for type checking to avoid circular imports at runtime
if TYPE_CHECKING:
    from .agent import Agent

T = TypeVar("T")


class Task:
    """Mock implementation of CrewAI Task class."""

    def __init__(
        self,
        description: str = "",
        agent: Optional[
            Union[Agent, None]
        ] = None,  # Use string literal for forward reference
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Initialize a mock Task.

        Args:
            description: The description of the task
            agent: The agent assigned to the task
            kwargs: Additional keyword arguments

        """
        self.description = description
        self.agent = agent
        self.kwargs = kwargs
