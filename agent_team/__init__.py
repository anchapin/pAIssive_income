"""
"""
Agent Team module for the pAIssive Income project.
Agent Team module for the pAIssive Income project.


This module provides functionality for managing a team of specialized AI agents
This module provides functionality for managing a team of specialized AI agents
that collaborate on developing and monetizing niche AI tools for passive income.
that collaborate on developing and monetizing niche AI tools for passive income.
"""
"""


from .agent_profiles import (AgentProfile, DeveloperAgent, FeedbackAgent,
from .agent_profiles import (AgentProfile, DeveloperAgent, FeedbackAgent,
MarketingAgent, MonetizationAgent, ResearchAgent)
MarketingAgent, MonetizationAgent, ResearchAgent)
from .schemas import (AgentProfileSchema, FeedbackItemSchema,
from .schemas import (AgentProfileSchema, FeedbackItemSchema,
MarketingPlanSchema, ModelSettingsSchema,
MarketingPlanSchema, ModelSettingsSchema,
MonetizationStrategySchema, NicheSchema,
MonetizationStrategySchema, NicheSchema,
ProjectStateSchema, SolutionSchema, TeamConfigSchema,
ProjectStateSchema, SolutionSchema, TeamConfigSchema,
WorkflowSettingsSchema)
WorkflowSettingsSchema)
from .team_config import AgentTeam
from .team_config import AgentTeam


__all__ = [
__all__ = [
# Team configuration
# Team configuration
"AgentTeam",
"AgentTeam",
"TeamConfigSchema",
"TeamConfigSchema",
"ModelSettingsSchema",
"ModelSettingsSchema",
"WorkflowSettingsSchema",
"WorkflowSettingsSchema",
# Agent profiles
# Agent profiles
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
# Project schemas
# Project schemas
"AgentProfileSchema",
"AgentProfileSchema",
"NicheSchema",
"NicheSchema",
"SolutionSchema",
"SolutionSchema",
"MonetizationStrategySchema",
"MonetizationStrategySchema",
"MarketingPlanSchema",
"MarketingPlanSchema",
"FeedbackItemSchema",
"FeedbackItemSchema",
"ProjectStateSchema",
"ProjectStateSchema",
]
]

