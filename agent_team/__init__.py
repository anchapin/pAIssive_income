"""
Agent Team module for pAIssive Income project.
This module contains the AI agent team that collaborates on developing
niche AI tools for passive income generation.
"""

from .team_config import AgentTeam
from .agent_profiles import (
    AgentProfile,
    ResearchAgent,
    DeveloperAgent,
    MonetizationAgent,
    MarketingAgent,
    FeedbackAgent
)

__all__ = [
    'AgentTeam',
    'AgentProfile',
    'ResearchAgent',
    'DeveloperAgent',
    'MonetizationAgent',
    'MarketingAgent',
    'FeedbackAgent',
]
