"""
Schema definitions for marketing tools.
"""


import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from marketing.enums import BusinessSize, BusinessType, PriorityLevel, TimeframeUnit
from marketing.schemas.budget import BudgetSchema
from marketing.schemas.demographics import DemographicsSchema
from marketing.schemas.strategy import MarketingStrategySchema
from marketing.schemas.target_audience import TargetAudienceSchema


class TimeframeSchema

(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    """Schema for timeframe specifications."""
    value: int = Field(..., description="The numeric value of the timeframe", gt=0)
    unit: TimeframeUnit = Field(..., description="The unit of the timeframe")

    model_config = ConfigDict(extra="allow")

    def __str__(self) -> str:
        """Return a string representation of the timeframe."""
        return f"{self.value} {self.unit.value}"


class ConfigSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for general configuration settings."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the config",
    )
    name: str = Field(..., description="Name of the configuration")
    description: str = Field(..., description="Description of the configuration")
    settings: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration settings"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp",
    )
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class MetricSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for marketing metrics."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the metric",
    )
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of the metric")
    value: float = Field(..., description="Value of the metric")
    unit: str = Field(..., description="Unit of the metric")
    target: Optional[float] = Field(
        default=None, description="Target value of the metric"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(), description="Timestamp"
    )

    model_config = ConfigDict(extra="allow")


class ContentItemSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for content calendar items."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the content item",
    )
    title: str = Field(..., description="Title of the content item")
    description: str = Field(..., description="Description of the content item")
    content_type: str = Field(
        ..., description="Type of content (e.g., blog post, social media post)"
    )
    channel: str = Field(..., description="Distribution channel")
    publish_date: str = Field(..., description="Publication date")
    status: str = Field(default="draft", description="Status of the content item")
    assigned_to: Optional[str] = Field(
        default=None, description="Assignee of the content item"
    )
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM, description="Priority of the content item"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Keywords for the content item"
    )
    notes: Optional[str] = Field(default=None, description="Notes for the content item")

    model_config = ConfigDict(extra="allow")


class ContentCalendarSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for content calendars."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the calendar",
    )
    name: str = Field(..., description="Name of the calendar")
    description: str = Field(..., description="Description of the calendar")
    start_date: str = Field(..., description="Start date of the calendar")
    end_date: str = Field(..., description="End date of the calendar")
    items: List[ContentItemSchema] = Field(
        default_factory=list, description="Content items in the calendar"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp",
    )
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class PersonaSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for user personas."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the persona",
    )
    name: str = Field(..., description="Name of the persona")
    description: str = Field(..., description="Description of the persona")
    demographics: DemographicsSchema = Field(
        default_factory=DemographicsSchema, description="Demographics of the persona"
    )
    goals: List[str] = Field(..., description="Goals of the persona")
    pain_points: List[str] = Field(..., description="Pain points of the persona")
    behaviors: List[str] = Field(..., description="Behaviors of the persona")
    motivations: List[str] = Field(..., description="Motivations of the persona")
    preferences: Dict[str, Any] = Field(
        default_factory=dict, description="Preferences of the persona"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp",
    )
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class ChannelAnalysisSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for channel analysis."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the analysis",
    )
    channel_name: str = Field(..., description="Name of the channel")
    metrics: List[MetricSchema] = Field(
        default_factory=list, description="Metrics for the channel"
    )
    strengths: List[str] = Field(
        default_factory=list, description="Strengths of the channel"
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Weaknesses of the channel"
    )
    opportunities: List[str] = Field(
        default_factory=list, description="Opportunities for the channel"
    )
    threats: List[str] = Field(
        default_factory=list, description="Threats for the channel"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for the channel"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Analysis timestamp",
    )

    model_config = ConfigDict(extra="allow")


class MarketingPlanSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for marketing plans."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the plan",
    )
    name: str = Field(..., description="Name of the plan")
    description: str = Field(..., description="Description of the plan")
    start_date: str = Field(..., description="Start date of the plan")
    end_date: str = Field(..., description="End date of the plan")
    goals: List[str] = Field(..., description="Goals of the plan")
    strategies: List[MarketingStrategySchema] = Field(
        default_factory=list, description="Strategies for the plan"
    )
    budget: BudgetSchema = Field(..., description="Budget for the plan")
    metrics: List[MetricSchema] = Field(
        default_factory=list, description="Metrics for the plan"
    )
    content_calendar: Optional[ContentCalendarSchema] = Field(
        default=None, description="Content calendar for the plan"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp",
    )
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class MarketingStrategyInputSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for marketing strategy inputs."""
    business_type: BusinessType = Field(..., description="Type of business")
    business_size: BusinessSize = Field(..., description="Size of business")
    business_goals: List[str] = Field(..., description="Business goals")
    target_audience: TargetAudienceSchema = Field(..., description="Target audience")
    budget: BudgetSchema = Field(..., description="Marketing budget")
    timeframe: TimeframeSchema = Field(..., description="Strategy timeframe")
    current_channels: Optional[List[str]] = Field(
        default=None, description="Current marketing channels"
    )
    industry: str = Field(..., description="Business industry")
    location: Optional[str] = Field(default=None, description="Business location")
    unique_selling_points: List[str] = Field(..., description="Unique selling points")
    competitors: Optional[List[str]] = Field(
        default=None, description="Competitor names"
    )

    model_config = ConfigDict(extra="allow")


class MarketingStrategyResultsSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for marketing strategy results."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the results",
    )
    strategy_id: str = Field(..., description="ID of the strategy")
    metrics: List[MetricSchema] = Field(
        default_factory=list, description="Results metrics"
    )
    roi: float = Field(..., description="Return on investment")
    achievements: List[str] = Field(default_factory=list, description="Achievements")
    challenges: List[str] = Field(default_factory=list, description="Challenges faced")
    lessons_learned: List[str] = Field(
        default_factory=list, description="Lessons learned"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for future"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Results timestamp",
    )

    model_config = ConfigDict(extra="allow")


class AudienceAnalysisSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for audience analysis."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the analysis",
    )
    segment_name: str = Field(..., description="Name of the audience segment")
    demographics: DemographicsSchema = Field(
        ..., description="Demographics of the audience"
    )
    size: Optional[int] = Field(default=None, description="Size of the audience")
    interests: List[str] = Field(
        default_factory=list, description="Interests of the audience"
    )
    behaviors: List[str] = Field(
        default_factory=list, description="Behaviors of the audience"
    )
    pain_points: List[str] = Field(
        default_factory=list, description="Pain points of the audience"
    )
    goals: List[str] = Field(default_factory=list, description="Goals of the audience")
    channels: List[str] = Field(
        default_factory=list, description="Preferred channels of the audience"
    )
    engagement_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Engagement metrics"
    )
    conversion_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Conversion metrics"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for this audience"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Analysis timestamp",
    )

    model_config = ConfigDict(extra="allow")


class BusinessAnalysisSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for business analysis."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the analysis",
    )
    business_name: str = Field(..., description="Name of the business")
    business_type: BusinessType = Field(..., description="Type of business")
    business_size: BusinessSize = Field(..., description="Size of business")
    industry: str = Field(..., description="Business industry")
    location: Optional[str] = Field(default=None, description="Business location")
    strengths: List[str] = Field(default_factory=list, description="Business strengths")
    weaknesses: List[str] = Field(
        default_factory=list, description="Business weaknesses"
    )
    opportunities: List[str] = Field(
        default_factory=list, description="Business opportunities"
    )
    threats: List[str] = Field(default_factory=list, description="Business threats")
    unique_selling_points: List[str] = Field(
        default_factory=list, description="Unique selling points"
    )
    competitors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Competitor analysis"
    )
    market_position: Dict[str, Any] = Field(
        default_factory=dict, description="Market position analysis"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for the business"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Analysis timestamp",
    )

    model_config = ConfigDict(extra="allow")