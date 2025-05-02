"""Pydantic schemas for agent team data validation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseSchema(BaseModel):
    """Base schema for all agent team schemas."""



class AgentProfileSchema(BaseModel):
    """Schema for agent profile configuration."""

    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role/responsibility")
    model_name: str = Field(..., description="Name of the AI model to use")
    temperature: float = Field(0.7, description="Model temperature parameter")
    max_tokens: int = Field(2000, description="Maximum tokens per response")


class ModelSettingsSchema(BaseModel):
    """Schema for model configuration settings."""

    model: str = Field(..., description="Model identifier/name")
    temperature: float = Field(0.7, description="Model temperature parameter")
    max_tokens: Optional[int] = Field(2000, description="Maximum tokens per response")


class WorkflowSettingsSchema(BaseModel):
    """Schema for workflow configuration settings."""

    auto_progression: bool = Field(
        False, description="Whether to auto-progress through workflow steps"
    )
    review_required: bool = Field(
        True, description="Whether human review is required between steps"
    )


class TeamConfigSchema(BaseModel):
    """Configuration schema for the agent team."""

    project_name: str = Field(default="unnamed")
    model_settings: Dict[str, Any] = Field(default_factory=dict)
    workflow: Dict[str, Any] = Field(default_factory=dict)


class NicheSchema(BaseModel):
    """Schema for niche market data."""

    name: str
    description: str
    market_size: float
    competition_level: str
    growth_potential: float
    barriers_to_entry: List[str]
    target_audience: Dict[str, Any]
    problems: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]


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

    @field_validator("priority")
    def validate_priority(cls, v):
        """Validate that priority is one of the allowed values."""
        if v.lower() not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v.lower()


class SolutionComponentSchema(BaseModel):
    """Schema for solution component specification."""

    name: str
    description: str
    type: str
    features: List[str]
    technology_stack: List[str]
    dependencies: Optional[List[str]] = None
    api_spec: Optional[Dict[str, Any]] = None


class SolutionSchema(BaseModel):
    """Schema for AI solution design."""

    name: str
    description: str
    features: List[Dict[str, Any]]
    architecture: Dict[str, Any]
    technology_stack: List[str]
    development_roadmap: List[Dict[str, Any]]
    resource_requirements: Dict[str, Any]


class PricingTierSchema(BaseModel):
    """Pydantic model for a pricing tier."""

    name: str = Field(..., description="Name of the pricing tier")
    price: float = Field(..., description="Price of the tier", ge=0.0)
    billing_period: str = Field(..., description="Billing period")
    features: List[str] = Field(..., description="Features included in this tier")
    limits: Optional[Dict[str, Any]] = None

    @field_validator("billing_period")
    def validate_billing_period(cls, v):
        """Validate that billing period is one of the allowed values."""
        if v.lower() not in ["monthly", "quarterly", "yearly", "one-time"]:
            raise ValueError("Billing period must be one of: monthly, quarterly, yearly, one-time")
        return v.lower()


class MonetizationStrategySchema(BaseModel):
    """Schema for monetization strategy."""

    model_type: str
    pricing_tiers: List[Dict[str, Any]]
    revenue_projections: Dict[str, Any]
    cost_structure: Dict[str, Any]
    break_even_analysis: Dict[str, Any]


class MarketingChannelSchema(BaseModel):
    """Pydantic model for a marketing channel."""

    name: str = Field(..., description="Name of the marketing channel")
    description: str = Field(..., description="Description of the channel")
    target_audience: List[str] = Field(..., description="Target audience for this channel")
    content_types: List[str] = Field(..., description="Types of content for this channel")
    expected_roi: Optional[float] = Field(None, description="Expected ROI")
    type: str
    content_strategy: Dict[str, Any]
    budget_allocation: float
    success_metrics: Dict[str, Any]


class MarketingPlanSchema(BaseModel):
    """Schema for marketing plan."""

    target_segments: List[Dict[str, Any]]
    channels: List[Dict[str, Any]]
    content_strategy: Dict[str, Any]
    budget_allocation: Dict[str, Any]
    campaign_schedule: List[Dict[str, Any]]


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

    user_id: str
    timestamp: datetime
    category: str
    content: str
    rating: Optional[int] = None
    sentiment: Optional[str] = None


class ProjectStateSchema(BaseModel):
    """Schema for project state tracking."""

    identified_niches: List[Dict[str, Any]] = Field(default_factory=list)
    selected_niche: Optional[Dict[str, Any]] = None
    solution_design: Optional[Dict[str, Any]] = None
    monetization_strategy: Optional[Dict[str, Any]] = None
    marketing_plan: Optional[Dict[str, Any]] = None
    feedback_data: List[Dict[str, Any]] = Field(default_factory=list)
    updated_at: Optional[str] = None

    @field_validator("updated_at")
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid timestamp format")
        return v

    model_config = {
        "extra": "allow"  # Allow extra fields
    }
