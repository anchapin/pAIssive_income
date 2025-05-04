"""
"""
Agent profiles for the pAIssive Income project.
Agent profiles for the pAIssive Income project.
This package contains the specialized AI agents that make up the agent team.
This package contains the specialized AI agents that make up the agent team.
"""
"""


from .base import AgentProfile
from .base import AgentProfile
from .developer import DeveloperAgent
from .developer import DeveloperAgent
from .feedback import FeedbackAgent
from .feedback import FeedbackAgent
from .marketing import MarketingAgent
from .marketing import MarketingAgent
from .monetization import MonetizationAgent
from .monetization import MonetizationAgent
from .researcher import ResearchAgent
from .researcher import ResearchAgent


__all__ = [
__all__ = [
"AgentProfile",
"AgentProfile",
"ResearchAgent",
"ResearchAgent",
"DeveloperAgent",
"DeveloperAgent",
"MonetizationAgent",
"MonetizationAgent",
"MarketingAgent",
"MarketingAgent",
"FeedbackAgent",
"FeedbackAgent",
]
]

