"""
Agent Team module for pAIssive Income project.
This module contains the AI agent team that collaborates on developing
niche AI tools for passive income generation.
"""

from .team_config import AgentTeam
from .agent_profiles.researcher import ResearchAgent
from .agent_profiles.developer import DeveloperAgent
from .agent_profiles.monetization import MonetizationAgent
from .agent_profiles.marketing import MarketingAgent
from .agent_profiles.feedback import FeedbackAgent

__all__ = [
    'AgentTeam',
    'ResearchAgent',
    'DeveloperAgent',
    'MonetizationAgent',
    'MarketingAgent',
    'FeedbackAgent',
]
