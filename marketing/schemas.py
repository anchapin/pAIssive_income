"""
Pydantic schemas for the Marketing module.

This module provides Pydantic models for data validation in the Marketing module.
"""

import uuid
from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum


class BusinessType(str, Enum):
    """Enum for business types."""
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    SERVICE = "service"
    CONTENT_CREATOR = "content_creator"
    LOCAL_BUSINESS = "local_business"


class BusinessSize(str, Enum):
    """Enum for business sizes."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class BillingPeriod(str, Enum):
    """Enum for billing periods."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class TimeframeUnit(str, Enum):
    """Enum for timeframe units."""
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    QUARTERS = "quarters"
    YEARS = "years"


class ChannelType(str, Enum):
    """Enum for channel types."""
    SINGLE_CHANNEL = "single-channel"
    MULTI_CHANNEL = "multi-channel"
    OMNI_CHANNEL = "omni-channel"


class DifficultyLevel(str, Enum):
    """Enum for difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class ChannelCategory(str, Enum):
    """Enum for marketing channel categories."""
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    CONTENT = "content"
    SEO = "seo"
    PPC = "ppc"
    DISPLAY = "display"
    AFFILIATE = "affiliate"
    INFLUENCER = "influencer"
    PR = "pr"
    EVENTS = "events"
    DIRECT_MAIL = "direct_mail"
    SMS = "sms"
    PODCAST = "podcast"
    VIDEO = "video"
    TRADITIONAL = "traditional"
    OTHER = "other"


class MarketingChannelSchema(BaseModel):
    """Pydantic model for marketing channel."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the channel")
    name: str = Field(..., description="Name of the channel")
    category: ChannelCategory = Field(default=ChannelCategory.OTHER, description="Category of the channel")
    description: str = Field(..., description="Description of the channel")
    cost_structure: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cost structure information"
    )
    audience_demographics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Typical audience demographics"
    )
    typical_roi: Optional[Dict[str, Any]] = Field(
        None,
        description="Typical ROI information"
    )
    best_practices: List[str] = Field(
        default_factory=list,
        description="Best practices for this channel"
    )
    metrics: List[str] = Field(
        default_factory=list,
        description="Key metrics for this channel"
    )
    implementation_difficulty: DifficultyLevel = Field(
        DifficultyLevel.MEDIUM,
        description="Difficulty level of implementation"
    )
    time_to_results: str = Field(
        default="medium-term",
        description="Typical time to see results"
    )
    scalability: float = Field(
        default=0.5,
        description="Scalability score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    required_resources: List[str] = Field(
        default_factory=list,
        description="Required resources for implementation"
    )
    # Additional fields used in strategy_generator.py
    platforms: List[str] = Field(
        default_factory=list,
        description="Platforms within this channel"
    )
    relevance_score: float = Field(
        default=0.5,
        description="Relevance score for this channel (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingTacticSchema(BaseModel):
    """Pydantic model for marketing tactic."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the tactic")
    name: str = Field(..., description="Name of the tactic")
    channel_name: str = Field(..., description="Name of the channel this tactic belongs to")
    description: str = Field(..., description="Description of the tactic")
    expected_impact: float = Field(
        default=0.5,
        description="Expected impact score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    timeframe: str = Field(
        default="medium-term",
        description="Timeframe for results (e.g., 'short-term', 'medium-term', 'long-term')"
    )
    resources_required: List[str] = Field(
        default_factory=list,
        description="Resources required for implementation"
    )
    estimated_cost: float = Field(
        default=0.0,
        description="Estimated cost for implementation"
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingMetricSchema(BaseModel):
    """Pydantic model for marketing metric."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the metric")
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of the metric")
    target_value: float = Field(..., description="Target value for the metric")
    current_value: float = Field(default=0.0, description="Current value of the metric")
    unit: str = Field(..., description="Unit of measurement (e.g., 'percentage', 'USD', 'visitors/month')")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class DemographicsSchema(BaseModel):
    """Pydantic model for target audience demographics."""
    age_range: Optional[str] = Field(
        None,
        description="Age range (e.g., 18-24, 25-34)"
    )
    gender: Optional[str] = Field(
        None,
        description="Gender (e.g., male, female, mixed)"
    )
    location: Optional[str] = Field(
        None,
        description="Location (e.g., urban, rural, global)"
    )
    income: Optional[str] = Field(
        None,
        description="Income level (e.g., low, middle, high)"
    )
    education: Optional[str] = Field(
        None,
        description="Education level (e.g., high school, college, graduate)"
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class TargetAudienceSchema(BaseModel):
    """Pydantic model for target audience."""
    demographics: DemographicsSchema = Field(default_factory=DemographicsSchema, description="Demographic information")
    interests: List[str] = Field(default_factory=list, description="Interests of the target audience")
    behaviors: List[str] = Field(default_factory=list, description="Behaviors of the target audience")
    pain_points: List[str] = Field(default_factory=list, description="Pain points of the target audience")
    goals: List[str] = Field(default_factory=list, description="Goals of the target audience")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class BudgetSchema(BaseModel):
    """Pydantic model for marketing budget."""
    total_amount: float = Field(..., description="Total budget amount")
    timeframe: str = Field(default="monthly", description="Budget timeframe (e.g., 'monthly', 'quarterly', 'annual')")
    allocation_strategy: Optional[str] = Field(default=None, description="Strategy for budget allocation")
    constraints: List[str] = Field(default_factory=list, description="Budget constraints")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingStrategySchema(BaseModel):
    """Pydantic model for marketing strategy."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the strategy")
    name: str = Field(..., description="Name of the strategy")
    business_type: str = Field(..., description="Type of business")
    business_size: str = Field(..., description="Size of business")
    goals: List[str] = Field(..., description="Marketing goals")
    target_audience: TargetAudienceSchema = Field(default_factory=TargetAudienceSchema, description="Target audience")
    budget: BudgetSchema = Field(..., description="Marketing budget")
    channels: List[MarketingChannelSchema] = Field(default_factory=list, description="Marketing channels")
    tactics: List[MarketingTacticSchema] = Field(default_factory=list, description="Marketing tactics")
    allocated_budget: Dict[str, float] = Field(default_factory=dict, description="Budget allocation by channel")
    metrics: List[MarketingMetricSchema] = Field(default_factory=list, description="Marketing metrics")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    previous_version_id: Optional[str] = Field(default=None, description="ID of the previous version")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class PriorityLevel(str, Enum):
    """Enum for priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


class ReadingLevel(str, Enum):
    """Enum for reading levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ContentFormat(str, Enum):
    """Enum for content formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    RICH_TEXT = "rich_text"


class ContentTemplateSchema(BaseModel):
    """Base schema for content templates."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the template")
    title: str = Field(..., description="Title of the template")
    description: str = Field(..., description="Description of the template")
    target_persona: Dict[str, Any] = Field(..., description="Target persona for the content")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class BlogPostTemplateSchema(ContentTemplateSchema):
    """Schema for blog post templates."""
    key_points: List[str] = Field(..., description="Key points to cover in the blog post")
    seo_keywords: List[str] = Field(..., description="SEO keywords for the blog post")
    call_to_action: Optional[str] = Field(default=None, description="Call to action for the blog post")
    estimated_reading_time: Optional[int] = Field(default=None, description="Estimated reading time in minutes")
    target_word_count: Optional[int] = Field(default=None, description="Target word count for the blog post")
    topics: List[str] = Field(..., description="Topics covered in the blog post")
    target_reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class SocialMediaTemplateSchema(ContentTemplateSchema):
    """Schema for social media templates."""
    platform: str = Field(..., description="Social media platform")
    key_messages: List[str] = Field(..., description="Key messages for the social media post")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags for the social media post")
    include_image: bool = Field(default=True, description="Whether to include an image")
    include_link: bool = Field(default=True, description="Whether to include a link")
    character_limit: Optional[int] = Field(default=None, description="Character limit for the post")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class EmailNewsletterTemplateSchema(ContentTemplateSchema):
    """Schema for email newsletter templates."""
    sections: List[Dict[str, Any]] = Field(..., description="Sections of the email newsletter")
    subject_line_options: List[str] = Field(..., description="Subject line options for the email")
    preview_text_options: List[str] = Field(..., description="Preview text options for the email")
    include_header: bool = Field(default=True, description="Whether to include a header")
    include_footer: bool = Field(default=True, description="Whether to include a footer")
    include_social_links: bool = Field(default=True, description="Whether to include social links")
    include_call_to_action: bool = Field(default=True, description="Whether to include a call to action")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class GeneratedBlogPostSchema(BaseModel):
    """Schema for generated blog posts."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the blog post")
    template_id: str = Field(..., description="ID of the template used to generate the blog post")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Generation timestamp")
    title: str = Field(..., description="Title of the blog post")
    meta_description: str = Field(..., description="Meta description for SEO")
    introduction: str = Field(..., description="Introduction paragraph")
    sections: List[Dict[str, Any]] = Field(..., description="Sections of the blog post")
    conclusion: str = Field(..., description="Conclusion paragraph")
    call_to_action: str = Field(..., description="Call to action")
    tags: List[str] = Field(..., description="Tags for the blog post")
    categories: List[str] = Field(..., description="Categories for the blog post")
    featured_image: Dict[str, Any] = Field(..., description="Featured image information")
    seo_data: Dict[str, Any] = Field(..., description="SEO data for the blog post")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class GeneratedSocialMediaPostSchema(BaseModel):
    """Schema for generated social media posts."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the post")
    template_id: str = Field(..., description="ID of the template used to generate the post")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Generation timestamp")
    platform: str = Field(..., description="Social media platform")
    content: str = Field(..., description="Content of the post")
    hashtags: List[str] = Field(..., description="Hashtags for the post")
    image_suggestions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Image suggestions")
    link: Optional[str] = Field(default=None, description="Link to include in the post")
    call_to_action: Optional[str] = Field(default=None, description="Call to action")
    optimal_posting_times: Optional[List[str]] = Field(default=None, description="Optimal posting times")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class GeneratedEmailNewsletterSchema(BaseModel):
    """Schema for generated email newsletters."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the newsletter")
    template_id: str = Field(..., description="ID of the template used to generate the newsletter")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Generation timestamp")
    subject_line: str = Field(..., description="Subject line of the email")
    preview_text: str = Field(..., description="Preview text of the email")
    content_sections: List[Dict[str, Any]] = Field(..., description="Content sections of the email")
    header: Optional[Dict[str, Any]] = Field(default=None, description="Header of the email")
    footer: Dict[str, Any] = Field(..., description="Footer of the email")
    call_to_action: Dict[str, Any] = Field(..., description="Call to action")
    images: Optional[List[Dict[str, Any]]] = Field(default=None, description="Images to include in the email")
    links: Optional[List[Dict[str, Any]]] = Field(default=None, description="Links to include in the email")
    spam_score: Optional[float] = Field(default=None, description="Spam score of the email")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ContentGeneratorConfigSchema(BaseModel):
    """Schema for content generator configuration."""
    creativity_level: float = Field(default=0.7, description="Creativity level (0.0 to 1.0)", ge=0.0, le=1.0)
    tone_consistency: float = Field(default=0.8, description="Tone consistency (0.0 to 1.0)", ge=0.0, le=1.0)
    max_length: int = Field(default=2000, description="Maximum content length")
    min_length: int = Field(default=500, description="Minimum content length")
    include_images: bool = Field(default=True, description="Whether to include images")
    include_links: bool = Field(default=True, description="Whether to include links")
    seo_optimization: bool = Field(default=True, description="Whether to optimize for SEO")
    target_reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")
    language: str = Field(default="en-US", description="Content language")
    content_format: ContentFormat = Field(default=ContentFormat.MARKDOWN, description="Content format")
    include_metadata: bool = Field(default=True, description="Whether to include metadata")
    use_ai_enhancement: bool = Field(default=True, description="Whether to use AI enhancement")
    ai_enhancement_level: float = Field(default=0.5, description="AI enhancement level (0.0 to 1.0)", ge=0.0, le=1.0)
    include_analytics_tags: bool = Field(default=False, description="Whether to include analytics tags")
    include_call_to_action: bool = Field(default=True, description="Whether to include a call to action")
    call_to_action_strength: float = Field(default=0.7, description="Call to action strength (0.0 to 1.0)", ge=0.0, le=1.0)
    personalization_level: float = Field(default=0.5, description="Personalization level (0.0 to 1.0)", ge=0.0, le=1.0)
    content_freshness: float = Field(default=0.8, description="Content freshness (0.0 to 1.0)", ge=0.0, le=1.0)
    content_uniqueness: float = Field(default=0.9, description="Content uniqueness (0.0 to 1.0)", ge=0.0, le=1.0)
    content_relevance: float = Field(default=0.9, description="Content relevance (0.0 to 1.0)", ge=0.0, le=1.0)
    content_engagement: float = Field(default=0.8, description="Content engagement (0.0 to 1.0)", ge=0.0, le=1.0)
    content_conversion: float = Field(default=0.7, description="Content conversion (0.0 to 1.0)", ge=0.0, le=1.0)
    content_authority: float = Field(default=0.6, description="Content authority (0.0 to 1.0)", ge=0.0, le=1.0)
    content_trustworthiness: float = Field(default=0.9, description="Content trustworthiness (0.0 to 1.0)", ge=0.0, le=1.0)
    content_expertise: float = Field(default=0.8, description="Content expertise (0.0 to 1.0)", ge=0.0, le=1.0)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Configuration timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fieldsclass TimeframeSchema(BaseModel):
    """Schema for timeframe specifications."""
    value: int = Field(..., description="The numeric value of the timeframe", gt=0)
    unit: TimeframeUnit = Field(..., description="The unit of the timeframe")
    
    model_config = ConfigDict(extra="allow")
    
    def __str__(self) -> str:
        """Return a string representation of the timeframe."""
        return f"{self.value} {self.unit.value}"

