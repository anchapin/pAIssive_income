"""
Agent profiles for the pAIssive Income project.
This package contains the specialized AI agents that make up the agent team.
"""

from .base import AgentProfile
from .researcher import ResearchAgent
from .developer import DeveloperAgent
from .monetization import MonetizationAgent
from .marketing import MarketingAgent
from .feedback import FeedbackAgent

__all__ = [
    'AgentProfile',
    'ResearchAgent',
    'DeveloperAgent',
    'MonetizationAgent',
    'MarketingAgent',
    'FeedbackAgent',
]
