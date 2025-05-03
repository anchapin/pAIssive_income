"""
Agent Team module for the pAIssive Income project.

This module provides functionality for managing a team of specialized AI agents
that collaborate on developing and monetizing niche AI tools for passive income.
"""

from .agent_profiles import (
    AgentProfile,
    DeveloperAgent,
    FeedbackAgent,
    MarketingAgent,
    MonetizationAgent,
    ResearchAgent,
)
from .schemas import (
    AgentProfileSchema,
    FeedbackItemSchema,
    MarketingPlanSchema,
    ModelSettingsSchema,
    MonetizationStrategySchema,
    NicheSchema,
    ProjectStateSchema,
    SolutionSchema,
    TeamConfigSchema,
    WorkflowSettingsSchema,
)
from .team_config import AgentTeam

__all__ = [
    # Team configuration
    'AgentTeam',
    'TeamConfigSchema',
    'ModelSettingsSchema',
    'WorkflowSettingsSchema',

    # Agent profiles
    'AgentProfile',
    'ResearchAgent',
    'DeveloperAgent',
    'MonetizationAgent',
    'MarketingAgent',
    'FeedbackAgent',

    # Project schemas
    'AgentProfileSchema',
    'NicheSchema',
    'SolutionSchema',
    'MonetizationStrategySchema',
    'MarketingPlanSchema',
    'FeedbackItemSchema',
    'ProjectStateSchema'
]
