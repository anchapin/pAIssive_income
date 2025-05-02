"""
Agent profiles for the pAIssive Income project.
This package contains the specialized AI agents that make up the agent team.
"""

from .base import AgentProfile
from .developer import DeveloperAgent
from .feedback import FeedbackAgent
from .marketing import MarketingAgent
from .monetization import MonetizationAgent
from .researcher import ResearchAgent

__all__ = [
    "AgentProfile",
    "ResearchAgent",
    "DeveloperAgent",
    "MonetizationAgent",
    "MarketingAgent",
    "FeedbackAgent",
]
