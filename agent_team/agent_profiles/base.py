"""
Base agent profile class for agent_team.
"""

from dataclasses import dataclass
from typing import Any
from agent_team.schemas import AgentProfileSchema

@dataclass
class BaseAgent:
    """Base class for agent profiles."""
    profile: AgentProfileSchema

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation of the agent profile."""
        return self.profile.model_dump()

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"role={self.profile.role!r}, "
                f"goal={self.profile.goal!r}, "
                f"backstory={self.profile.backstory!r})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseAgent):
            return False
        return self.profile == other.profile
