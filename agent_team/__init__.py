"""
Agent Team module for the pAIssive Income project.

This module provides functionality for managing a team of specialized AI agents
that collaborate on developing and monetizing niche AI tools for passive income.
"""

from .team_config import AgentTeam
from .schemas import (
    TeamConfigSchema,
    ModelSettingsSchema,
    WorkflowSettingsSchema,
    AgentProfileSchema,
    NicheSchema,
    SolutionSchema,
    MonetizationStrategySchema,
    MarketingPlanSchema,
    FeedbackItemSchema,
    ProjectStateSchema,
)
from .agent_profiles import (
    AgentProfile,
    ResearchAgent,
    DeveloperAgent,
    MonetizationAgent,
    MarketingAgent,
    FeedbackAgent,
)

__all__ = [
    # Team configuration
    "AgentTeam",
    "TeamConfigSchema",
    "ModelSettingsSchema",
    "WorkflowSettingsSchema",
    # Agent profiles
    "AgentProfile",
    "ResearchAgent",
    "DeveloperAgent",
    "MonetizationAgent",
    "MarketingAgent",
    "FeedbackAgent",
    # Project schemas
    "AgentProfileSchema",
    "NicheSchema",
    "SolutionSchema",
    "MonetizationStrategySchema",
    "MarketingPlanSchema",
    "FeedbackItemSchema",
    "ProjectStateSchema",
]
