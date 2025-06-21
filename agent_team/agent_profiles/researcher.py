"""
ResearcherAgent profile.
"""

from agent_team.agent_profiles.base import BaseAgent
from agent_team.schemas import AgentProfileSchema

class ResearcherAgent(BaseAgent):
    """Agent responsible for research tasks."""

    def __init__(self, goal: str, backstory: str):
        profile = AgentProfileSchema(role="researcher", goal=goal, backstory=backstory)
        super().__init__(profile=profile)

    def identify_niche(self, keywords: str) -> dict[str, str]:
        """Return a deterministic 'niche' based on keywords, robust to empty/whitespace input."""
        parts = keywords.strip().split()
        first_word = parts[0].capitalize() if parts else "General"
        return {
            "niche": f"AI-powered {first_word} Platform"
        }

    def summarize_findings(self, topic: str) -> str:
        """Return a stubbed summary of research findings for a topic."""
        return f"Research summary for {topic}: The topic is promising for MVP."
