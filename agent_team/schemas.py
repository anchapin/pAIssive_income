"""
"""
Pydantic schemas for the Agent Team module.
Pydantic schemas for the Agent Team module.


This module provides Pydantic models for data validation in the Agent Team module.
This module provides Pydantic models for data validation in the Agent Team module.
"""
"""


from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import BaseModel, ConfigDict, Field, field_validator




class ModelSettingSchema(BaseModel):
    class ModelSettingSchema(BaseModel):
    """Pydantic model for agent model settings."""

    model: str = Field(..., description="The AI model to use for the agent")
    temperature: float = Field(
    ..., description="Temperature setting for the AI model", ge=0.0, le=1.0
    )

    model_config = ConfigDict(
    extra="allow"
    )  # Allow extra fields for future model-specific parameters


    class ModelSettingsSchema(BaseModel):

    researcher: ModelSettingSchema
    developer: ModelSettingSchema
    monetization: ModelSettingSchema
    marketing: ModelSettingSchema
    feedback: ModelSettingSchema

    model_config = ConfigDict(extra="allow")  # Allow extra fields for future agents


    class WorkflowSettingsSchema(BaseModel):

    auto_progression: bool = Field(
    False, description="Whether to automatically progress through workflow steps"
    )
    review_required: bool = Field(
    True, description="Whether review is required before progressing"
    )

    model_config = ConfigDict(
    extra="allow"
    )  # Allow extra fields for future workflow settings


    class TeamConfigSchema(BaseModel):

    model_settings: ModelSettingsSchema = Field(
    ..., description="Model settings for each agent"
    )
    workflow: WorkflowSettingsSchema = Field(..., description="Workflow settings")

    model_config = ConfigDict(
    extra="allow"
    )  # Allow extra fields for future configuration options


    class AgentProfileSchema(BaseModel):


    name: str = Field(..., description="Name of the agent profile")
    name: str = Field(..., description="Name of the agent profile")
    description: str = Field(..., description="Description of the agent profile")
    description: str = Field(..., description="Description of the agent profile")
    capabilities: List[str] = Field(
    capabilities: List[str] = Field(
    default_factory=list, description="List of agent capabilities"
    default_factory=list, description="List of agent capabilities"
    )
    )
    parameters: Dict[str, Any] = Field(
    parameters: Dict[str, Any] = Field(
    default_factory=dict, description="Dictionary of parameters"
    default_factory=dict, description="Dictionary of parameters"
    )
    )




    class NicheSchema(BaseModel):
    class NicheSchema(BaseModel):


    id: str = Field(..., description="Unique identifier for the niche")
    id: str = Field(..., description="Unique identifier for the niche")
    name: str = Field(..., description="Name of the niche")
    name: str = Field(..., description="Name of the niche")
    market_segment: str = Field(..., description="Market segment of the niche")
    market_segment: str = Field(..., description="Market segment of the niche")
    opportunity_score: float = Field(
    opportunity_score: float = Field(
    ..., description="Opportunity score of the niche", ge=0.0, le=1.0
    ..., description="Opportunity score of the niche", ge=0.0, le=1.0
    )
    )
    description: Optional[str] = Field(None, description="Description of the niche")
    description: Optional[str] = Field(None, description="Description of the niche")
    problems: Optional[List[Dict[str, Any]]] = Field(
    problems: Optional[List[Dict[str, Any]]] = Field(
    None, description="Problems identified in the niche"
    None, description="Problems identified in the niche"
    )
    )
    target_audience: Optional[List[str]] = Field(
    target_audience: Optional[List[str]] = Field(
    None, description="Target audience for the niche"
    None, description="Target audience for the niche"
    )
    )
    competition: Optional[Dict[str, Any]] = Field(
    competition: Optional[Dict[str, Any]] = Field(
    None, description="Competition analysis for the niche"
    None, description="Competition analysis for the niche"
    )
    )


    model_config = ConfigDict(extra="allow")  # Allow extra fields
    model_config = ConfigDict(extra="allow")  # Allow extra fields




    class TechnologyStackSchema(BaseModel):
    class TechnologyStackSchema(BaseModel):


    language: str = Field(..., description="Programming language")
    language: str = Field(..., description="Programming language")
    frameworks: List[str] = Field(..., description="Frameworks used")
    frameworks: List[str] = Field(..., description="Frameworks used")
    apis: Optional[List[str]] = Field(None, description="APIs used")
    apis: Optional[List[str]] = Field(None, description="APIs used")
    databases: Optional[List[str]] = Field(None, description="Databases used")
    databases: Optional[List[str]] = Field(None, description="Databases used")
    hosting: Optional[str] = Field(None, description="Hosting platform")
    hosting: Optional[str] = Field(None, description="Hosting platform")




    class FeatureSchema(BaseModel):
    class FeatureSchema(BaseModel):


    name: str = Field(..., description="Name of the feature")
    name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Description of the feature")
    description: str = Field(..., description="Description of the feature")
    priority: str = Field(
    priority: str = Field(
    ..., description="Priority of the feature (high, medium, low)"
    ..., description="Priority of the feature (high, medium, low)"
    )
    )
    complexity: Optional[str] = Field(None, description="Complexity of the feature")
    complexity: Optional[str] = Field(None, description="Complexity of the feature")


    @field_validator("priority")
    @field_validator("priority")
    @classmethod
    @classmethod
    def validate_priority(cls, v):
    def validate_priority(cls, v):
    """Validate that priority is one of the allowed values."""
    if v.lower() not in ["high", "medium", "low"]:
    raise ValueError("Priority must be one of: high, medium, low")
    return v.lower()


    class SolutionSchema(BaseModel):

    id: str = Field(..., description="Unique identifier for the solution")
    name: str = Field(..., description="Name of the solution")
    description: str = Field(..., description="Description of the solution")
    niche_id: str = Field(..., description="ID of the niche this solution addresses")
    features: List[FeatureSchema] = Field(..., description="Features of the solution")
    tech_stack: TechnologyStackSchema = Field(..., description="Technology stack")
    architecture: Optional[Dict[str, Any]] = Field(
    None, description="Architecture of the solution"
    )
    implementation_plan: Optional[Dict[str, Any]] = Field(
    None, description="Implementation plan for the solution"
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


    class PricingTierSchema(BaseModel):

    name: str = Field(..., description="Name of the pricing tier")
    price: float = Field(..., description="Price of the tier", ge=0.0)
    billing_period: str = Field(..., description="Billing period")
    features: List[str] = Field(..., description="Features included in this tier")

    @field_validator("billing_period")
    @classmethod
    def validate_billing_period(cls, v):
    """Validate that billing period is one of the allowed values."""
    if v.lower() not in ["monthly", "quarterly", "yearly", "one-time"]:
    raise ValueError(
    "Billing period must be one of: monthly, quarterly, yearly, one-time"
    )
    return v.lower()


    class MonetizationStrategySchema(BaseModel):

    id: str = Field(..., description="Unique identifier for the strategy")
    solution_id: str = Field(..., description="ID of the solution")
    model_type: str = Field(..., description="Type of monetization model")
    pricing_tiers: List[PricingTierSchema] = Field(..., description="Pricing tiers")
    target_revenue: Optional[float] = Field(None, description="Target revenue")
    cost_structure: Optional[Dict[str, Any]] = Field(None, description="Cost structure")
    revenue_projections: Optional[Dict[str, Any]] = Field(
    None, description="Revenue projections"
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


    class MarketingChannelSchema(BaseModel):

    name: str = Field(..., description="Name of the marketing channel")
    description: str = Field(..., description="Description of the channel")
    target_audience: List[str] = Field(
    ..., description="Target audience for this channel"
    )
    content_types: List[str] = Field(
    ..., description="Types of content for this channel"
    )
    expected_roi: Optional[float] = Field(None, description="Expected ROI")


    class MarketingPlanSchema(BaseModel):

    id: str = Field(..., description="Unique identifier for the plan")
    solution_id: str = Field(..., description="ID of the solution")
    target_audience: List[str] = Field(..., description="Target audience")
    value_proposition: str = Field(..., description="Value proposition")
    channels: List[MarketingChannelSchema] = Field(
    ..., description="Marketing channels"
    )
    content_strategy: Optional[Dict[str, Any]] = Field(
    None, description="Content strategy"
    )
    launch_plan: Optional[Dict[str, Any]] = Field(None, description="Launch plan")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


    class FeedbackItemSchema(BaseModel):


    id: str = Field(..., description="Unique identifier for the feedback")
    id: str = Field(..., description="Unique identifier for the feedback")
    user_id: str = Field(..., description="ID of the user providing feedback")
    user_id: str = Field(..., description="ID of the user providing feedback")
    solution_id: str = Field(..., description="ID of the solution")
    solution_id: str = Field(..., description="ID of the solution")
    content: str = Field(..., description="Feedback content")
    content: str = Field(..., description="Feedback content")
    rating: Optional[int] = Field(None, description="Numerical rating", ge=1, le=5)
    rating: Optional[int] = Field(None, description="Numerical rating", ge=1, le=5)
    category: Optional[str] = Field(None, description="Feedback category")
    category: Optional[str] = Field(None, description="Feedback category")
    timestamp: str = Field(..., description="Timestamp of the feedback")
    timestamp: str = Field(..., description="Timestamp of the feedback")




    class ProjectStateSchema(BaseModel):
    class ProjectStateSchema(BaseModel):


    id: str = Field(..., description="Unique identifier for the project")
    id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")
    name: str = Field(..., description="Name of the project")
    identified_niches: List[Dict[str, Any]] = Field(
    identified_niches: List[Dict[str, Any]] = Field(
    default_factory=list, description="Identified niches"
    default_factory=list, description="Identified niches"
    )
    )
    selected_niche: Optional[Dict[str, Any]] = Field(None, description="Selected niche")
    selected_niche: Optional[Dict[str, Any]] = Field(None, description="Selected niche")
    user_problems: List[Dict[str, Any]] = Field(
    user_problems: List[Dict[str, Any]] = Field(
    default_factory=list, description="User problems"
    default_factory=list, description="User problems"
    )
    )
    solution_design: Optional[Dict[str, Any]] = Field(
    solution_design: Optional[Dict[str, Any]] = Field(
    None, description="Solution design"
    None, description="Solution design"
    )
    )
    monetization_strategy: Optional[Dict[str, Any]] = Field(
    monetization_strategy: Optional[Dict[str, Any]] = Field(
    None, description="Monetization strategy"
    None, description="Monetization strategy"
    )
    )
    marketing_plan: Optional[Dict[str, Any]] = Field(None, description="Marketing plan")
    marketing_plan: Optional[Dict[str, Any]] = Field(None, description="Marketing plan")
    feedback_data: List[Dict[str, Any]] = Field(
    feedback_data: List[Dict[str, Any]] = Field(
    default_factory=list, description="Feedback data"
    default_factory=list, description="Feedback data"
    )
    )
    created_at: str = Field(..., description="Creation timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


    model_config = ConfigDict(extra="allow")  # Allow extra fields
    model_config = ConfigDict(extra="allow")  # Allow extra fields

