"""
MonetizationAgent profile.
"""

from agent_team.agent_profiles.base import BaseAgent
from agent_team.schemas import AgentProfileSchema

class MonetizationAgent(BaseAgent):
    """Agent responsible for monetization strategies."""

    DEFAULT_MONTHLY_REVENUE_ESTIMATE = 1000

    def __init__(self, goal: str, backstory: str):
        profile = AgentProfileSchema(role="monetization", goal=goal, backstory=backstory)
        super().__init__(profile=profile)

    def build_plan(self, solution: str) -> dict[str, str]:
        """Return a deterministic monetization plan based on solution."""
        return {
            "solution": solution,
            "plan": f"Basic subscription model for '{solution}'."
        }

    def estimate_revenue(self, months: int = 6) -> int:
        """Return a stubbed revenue estimate."""
        return months * self.DEFAULT_MONTHLY_REVENUE_ESTIMATE  # Uses class constant.
