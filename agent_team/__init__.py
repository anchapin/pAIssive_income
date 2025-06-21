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
    from agent_team.crewai_integration import CrewAIAgentTeam, MemoryEnhancedCrewAIAgentTeam
except ImportError:
    # These are optional, only needed for users with CrewAI/mem0 installed.
    CrewAIAgentTeam = None
    MemoryEnhancedCrewAIAgentTeam = None

__all__ = [
    "AgentTeamError", "DependencyNotInstalledError", "AgentNotFoundError", "TaskAssignmentError",
    "AgentProfileSchema", "TaskSchema", "TeamConfigSchema",
    "BaseAgent", "DeveloperAgent", "ResearcherAgent", "MonetizationAgent",
    "MarketingAgent", "FeedbackAgent",
    "DEFAULT_TEAM_CONFIG", "load_config",
    "CrewAIAgentTeam", "MemoryEnhancedCrewAIAgentTeam",
]