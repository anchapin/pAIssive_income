"""
FeedbackAgent profile.
"""

from agent_team.agent_profiles.base import BaseAgent
from agent_team.schemas import AgentProfileSchema

class FeedbackAgent(BaseAgent):
    """Agent responsible for collecting and analyzing feedback."""

    def __init__(self, goal: str, backstory: str):
        profile = AgentProfileSchema(role="feedback", goal=goal, backstory=backstory)
        super().__init__(profile=profile)

    def collect_feedback(self, product: str) -> dict[str, str]:
        """Return stub feedback for a product."""
        return {
            "product": product,
            "feedback": f"Users find {product} easy to use and effective."
        }

    def analyze_feedback(self, feedback: str) -> str:
        """Return a stub analysis of user feedback."""
        return "Majority of feedback is positive with suggestions for more integrations."
