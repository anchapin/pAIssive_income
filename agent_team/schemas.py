"""Pydantic schemas for agent team data validation.

This module provides Pydantic models for data validation in the Agent Team module.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelSettingSchema(BaseModel):
    """Pydantic model for agent model settings."""
    model: str = Field(..., description="The AI model to use for the agent")
    temperature: float = Field(
        ...,
        description="Temperature setting for the AI model",
        ge=0.0,
        le=1.0
    )
    max_tokens: int = Field(2000, description="Maximum tokens per response")

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields for future model-specific parameters
        protected_namespaces=()  # Disable protected namespace warnings
    )


class ModelSettingsSchema(BaseModel):
    """Pydantic model for all agents' model settings."""
    researcher: ModelSettingSchema
    developer: ModelSettingSchema
    monetization: ModelSettingSchema
    marketing: ModelSettingSchema
    feedback: ModelSettingSchema

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class WorkflowSettingsSchema(BaseModel):
    """Schema for workflow configuration settings."""
    auto_progression: bool = Field(
        False,
        description="Whether to auto-progress through workflow steps"
    )
    review_required: bool = Field(
        True,
        description="Whether human review is required between steps"
    )

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class TeamConfigSchema(BaseModel):
    """Configuration schema for the agent team."""
    project_name: str = Field(default="unnamed")
    model_settings: ModelSettingsSchema = Field(
        ...,
        description="Model settings for each agent"
    )
    workflow: WorkflowSettingsSchema = Field(
        ...,
        description="Workflow settings"
    )

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class NicheSchema(BaseModel):
    """Pydantic model for a niche."""
    id: str = Field(..., description="Unique identifier for the niche")
    name: str = Field(..., description="Name of the niche")
    market_segment: str = Field(..., description="Market segment of the niche")
    opportunity_score: float = Field(
        ...,
        description="Opportunity score of the niche",
        ge=0.0,
        le=1.0
    )
    description: str = Field(..., description="Description of the niche")
    market_size: float = Field(..., description="Market size estimate")
    competition_level: str = Field(..., description="Level of competition")
    growth_potential: float = Field(..., description="Growth potential score")
    barriers_to_entry: List[str] = Field(..., description="Barriers to entry")
    target_audience: List[str] = Field(..., description="Target audience segments")
    problems: List[Dict[str, Any]] = Field(..., description="Problems identified in the niche")
    opportunities: List[Dict[str, Any]] = Field(..., description="Opportunities in the niche")
    competition: Dict[str, Any] = Field(..., description="Competition analysis")

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class TechnologyStackSchema(BaseModel):
    """Pydantic model for a solution's technology stack."""
    language: str = Field(..., description="Programming language")
    frameworks: List[str] = Field(..., description="Frameworks used")
    apis: Optional[List[str]] = Field(None, description="APIs used")
    databases: Optional[List[str]] = Field(None, description="Databases used")
    hosting: Optional[str] = Field(None, description="Hosting platform")


class FeatureSchema(BaseModel):
    """Pydantic model for a solution feature."""
    name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Description of the feature")
    priority: str = Field(..., description="Priority of the feature (high, medium, low)")
    complexity: Optional[str] = Field(None, description="Complexity of the feature")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate that priority is one of the allowed values."""
        if v.lower() not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v.lower()


class SolutionSchema(BaseModel):
    """Pydantic model for a solution."""
    id: str = Field(..., description="Unique identifier for the solution")
    name: str = Field(..., description="Name of the solution")
    description: str = Field(..., description="Description of the solution")
    niche_id: str = Field(..., description="ID of the niche this solution addresses")
    features: List[FeatureSchema] = Field(..., description="Features of the solution")
    tech_stack: TechnologyStackSchema = Field(..., description="Technology stack")
    architecture: Dict[str, Any] = Field(..., description="Architecture of the solution")
    development_roadmap: List[Dict[str, Any]] = Field(..., description="Development roadmap")
    resource_requirements: Dict[str, Any] = Field(..., description="Resource requirements")
    implementation_plan: Optional[Dict[str, Any]] = Field(
        None,
        description="Implementation plan for the solution"
    )

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class PricingTierSchema(BaseModel):
    """Pydantic model for a pricing tier."""
    name: str = Field(..., description="Name of the pricing tier")
    price: float = Field(..., description="Price of the tier", ge=0.0)
    billing_period: str = Field(..., description="Billing period")
    features: List[str] = Field(..., description="Features included in this tier")
    limits: Optional[Dict[str, Any]] = Field(None, description="Usage limits for this tier")

    @field_validator('billing_period')
    @classmethod
    def validate_billing_period(cls, v):
        """Validate that billing period is one of the allowed values."""
        if v.lower() not in ["monthly", "quarterly", "yearly", "one-time"]:
            raise ValueError("Billing period must be one of: monthly, quarterly, yearly, one-time")
        return v.lower()


class MonetizationStrategySchema(BaseModel):
    """Pydantic model for a monetization strategy."""
    id: str = Field(..., description="Unique identifier for the strategy")
    solution_id: str = Field(..., description="ID of the solution")
    model_type: str = Field(..., description="Type of monetization model")
    pricing_tiers: List[PricingTierSchema] = Field(..., description="Pricing tiers")
    target_revenue: float = Field(..., description="Target revenue")
    cost_structure: Dict[str, Any] = Field(..., description="Cost structure")
    revenue_projections: Dict[str, Any] = Field(..., description="Revenue projections")
    break_even_analysis: Dict[str, Any] = Field(..., description="Break-even analysis")

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class MarketingChannelSchema(BaseModel):
    """Pydantic model for a marketing channel."""
    name: str = Field(..., description="Name of the marketing channel")
    description: str = Field(..., description="Description of the channel")
    type: str = Field(..., description="Type of marketing channel")
    target_audience: List[str] = Field(..., description="Target audience for this channel")
    content_types: List[str] = Field(..., description="Types of content for this channel")
    content_strategy: Dict[str, Any] = Field(..., description="Content strategy for this channel")
    budget_allocation: float = Field(..., description="Budget allocation for this channel")
    success_metrics: Dict[str, Any] = Field(..., description="Success metrics for this channel")
    expected_roi: Optional[float] = Field(None, description="Expected ROI")


class MarketingPlanSchema(BaseModel):
    """Pydantic model for a marketing plan."""
    id: str = Field(..., description="Unique identifier for the plan")
    solution_id: str = Field(..., description="ID of the solution")
    target_audience: List[str] = Field(..., description="Target audience segments")
    value_proposition: str = Field(..., description="Value proposition")
    channels: List[MarketingChannelSchema] = Field(..., description="Marketing channels")
    content_strategy: Dict[str, Any] = Field(..., description="Content strategy")
    budget_allocation: Dict[str, Any] = Field(..., description="Budget allocation")
    campaign_schedule: List[Dict[str, Any]] = Field(..., description="Campaign schedule")
    launch_plan: Optional[Dict[str, Any]] = Field(None, description="Launch plan")

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )


class FeedbackType(str, Enum):
    """Enumeration of feedback types."""
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    USABILITY = "usability"
    PERFORMANCE = "performance"
    PRICING = "pricing"
    OTHER = "other"


class FeedbackItemSchema(BaseModel):
    """Schema for user feedback."""
    user_id: str = Field(..., description="ID of the user providing feedback")
    timestamp: datetime = Field(..., description="Timestamp of the feedback")
    category: FeedbackType = Field(..., description="Category of the feedback")
    content: str = Field(..., description="Feedback content")
    rating: Optional[int] = Field(None, description="Optional rating")
    sentiment: Optional[str] = Field(None, description="Optional sentiment analysis")


class ProjectStateSchema(BaseModel):
    """Pydantic model for the project state."""
    id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")
    identified_niches: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Identified niches"
    )
    selected_niche: Optional[Dict[str, Any]] = Field(
        None,
        description="Selected niche"
    )
    user_problems: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="User problems"
    )
    solution_design: Optional[Dict[str, Any]] = Field(
        None,
        description="Solution design"
    )
    monetization_strategy: Optional[Dict[str, Any]] = Field(
        None,
        description="Monetization strategy"
    )
    marketing_plan: Optional[Dict[str, Any]] = Field(
        None,
        description="Marketing plan"
    )
    feedback_data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Feedback data"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    @field_validator("updated_at", "created_at")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Invalid timestamp format")
        return v

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=()  # Disable protected namespace warnings
    )
