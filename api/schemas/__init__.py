"""
Schemas for the API server.

This module provides Pydantic models for API request and response validation.
"""

from .niche_analysis import *
from .monetization import *
from .marketing import *
from .ai_models import *
from .agent_team import *
from .user import *
from .dashboard import *
from .common import *

__all__ = [
    # Common schemas
    'ErrorResponse',
    'SuccessResponse',
    'PaginatedResponse',
    'IdResponse',
    
    # Niche Analysis schemas
    'NicheAnalysisRequest',
    'NicheAnalysisResponse',
    'NicheResponse',
    'MarketSegmentResponse',
    'ProblemResponse',
    'OpportunityResponse',
    
    # Monetization schemas
    'SubscriptionModelRequest',
    'SubscriptionModelResponse',
    'PricingTierResponse',
    'FeatureResponse',
    'RevenueProjectionRequest',
    'RevenueProjectionResponse',
    
    # Marketing schemas
    'MarketingStrategyRequest',
    'MarketingStrategyResponse',
    'PersonaResponse',
    'ChannelResponse',
    'ContentTemplateResponse',
    'ContentCalendarResponse',
    
    # AI Models schemas
    'ModelInfoResponse',
    'ModelDownloadRequest',
    'ModelDownloadResponse',
    'InferenceRequest',
    'InferenceResponse',
    
    # Agent Team schemas
    'AgentTeamRequest',
    'AgentTeamResponse',
    'AgentResponse',
    'WorkflowResponse',
    
    # User schemas
    'UserRequest',
    'UserResponse',
    'LoginRequest',
    'LoginResponse',
    'RegisterRequest',
    'RegisterResponse',
    
    # Dashboard schemas
    'DashboardOverviewResponse',
    'RevenueStatsResponse',
    'SubscriberStatsResponse',
]
