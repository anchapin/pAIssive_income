"""
agent_team public API.
"""

from agent_team.errors import (
    AgentTeamError,
    DependencyNotInstalledError,
    AgentNotFoundError,
    TaskAssignmentError,
)
from agent_team.schemas import (
    AgentProfileSchema,
    TaskSchema,
    TeamConfigSchema,
)
from agent_team.agent_profiles.base import BaseAgent
from agent_team.agent_profiles.developer import DeveloperAgent
from agent_team.agent_profiles.researcher import ResearcherAgent
from agent_team.agent_profiles.monetization import MonetizationAgent
from agent_team.agent_profiles.marketing import MarketingAgent
from agent_team.agent_profiles.feedback import FeedbackAgent
from agent_team.team_config import DEFAULT_TEAM_CONFIG, load_config

# Keep existing exports for CrewAIAgentTeam and MemoryEnhancedCrewAIAgentTeam
try:
    from .crewai_agent_team import CrewAIAgentTeam
except ImportError:
    CrewAIAgentTeam = None

try:
    from .memory_enhanced_crewai_agent_team import MemoryEnhancedCrewAIAgentTeam
except ImportError:
    MemoryEnhancedCrewAIAgentTeam = None

__all__ = [
    "DEFAULT_TEAM_CONFIG",
    "AgentNotFoundError",
    "AgentProfileSchema",
    "AgentTeamError",
    "BaseAgent",
    "CrewAIAgentTeam",
    "DependencyNotInstalledError",
    "DeveloperAgent",
    "FeedbackAgent",
    "MarketingAgent",
    "MemoryEnhancedCrewAIAgentTeam",
    "MonetizationAgent",
    "ResearcherAgent",
    "TaskAssignmentError",
    "TaskSchema",
    "TeamConfigSchema",
    "load_config",
]
