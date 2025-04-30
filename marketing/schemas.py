"""
Pydantic schemas for the Marketing module.

This module provides Pydantic models for data validation in the Marketing module.
"""

import uuid
from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum


# Enums
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


class SocialMediaPlatform(str, Enum):
    """Enum for social media platforms."""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"


class ContentVisibility(str, Enum):
    """Enum for content visibility settings."""
    PUBLIC = "public"
    PRIVATE = "private"
    FOLLOWERS = "followers"
    CONNECTIONS = "connections"


class PostScheduleType(str, Enum):
    """Enum for post scheduling types."""
    NOW = "now"
    SCHEDULED = "scheduled"
    OPTIMAL = "optimal"
    RECURRING = "recurring"


# Base schemas that don't depend on other schemas
class ConfigSchema(BaseModel):
    """Schema for general configuration settings."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(...)
    description: str = Field(...)
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="allow")


class TimeframeSchema(BaseModel):
    """Schema for timeframe specifications."""
    value: int = Field(..., description="The numeric value of the timeframe", gt=0)
    unit: TimeframeUnit = Field(..., description="The unit of the timeframe")

    model_config = ConfigDict(extra="allow")

    def __str__(self) -> str:
        """Return a string representation of the timeframe."""
        return f"{self.value} {self.unit.value}"


class MetricSchema(BaseModel):
    """Schema for marketing metrics."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(...)
    description: str = Field(...)
    value: float = Field(...)
    unit: str = Field(...)
    target: Optional[float] = Field(default=None)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


class BudgetSchema(BaseModel):
    """Pydantic model for marketing budget."""
    total_amount: float = Field(..., description="Total budget amount")
    timeframe: str = Field(default="monthly", description="Budget timeframe (e.g., 'monthly', 'quarterly', 'annual')")
    allocation_strategy: Optional[str] = Field(default=None, description="Strategy for budget allocation")
    constraints: List[str] = Field(default_factory=list, description="Budget constraints")

    model_config = ConfigDict(extra="allow")


class TargetAudienceSchema(BaseModel):
    """Pydantic model for target audience."""
    demographics: DemographicsSchema = Field(default_factory=DemographicsSchema, description="Demographic information")
    interests: List[str] = Field(default_factory=list, description="Interests of the target audience")
    behaviors: List[str] = Field(default_factory=list, description="Behaviors of the target audience")
    pain_points: List[str] = Field(default_factory=list, description="Pain points of the target audience")
    goals: List[str] = Field(default_factory=list, description="Goals of the target audience")

    model_config = ConfigDict(extra="allow")


# Content-related schemas
class ContentItemSchema(BaseModel):
    """Schema for content calendar items."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(...)
    description: str = Field(...)
    content_type: str = Field(...)
    channel: str = Field(...)
    publish_date: str = Field(...)
    status: str = Field(default="draft")
    assigned_to: Optional[str] = Field(default=None)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    keywords: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="allow")


class ContentCalendarSchema(BaseModel):
    """Schema for content calendars."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(...)
    description: str = Field(...)
    start_date: str = Field(...)
    end_date: str = Field(...)
    items: List[ContentItemSchema] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="allow")


class ContentTemplateSchema(BaseModel):
    """Base schema for content templates."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(...)
    description: str = Field(...)
    target_persona: Dict[str, Any] = Field(...)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="allow")


class BlogPostTemplateSchema(ContentTemplateSchema):
    """Schema for blog post templates."""
    key_points: List[str] = Field(..., description="Key points to cover in the blog post")
    seo_keywords: List[str] = Field(..., description="SEO keywords for the blog post")
    call_to_action: Optional[str] = Field(default=None, description="Call to action for the blog post")
    estimated_reading_time: Optional[int] = Field(default=None, description="Estimated reading time in minutes")
    target_word_count: Optional[int] = Field(default=None, description="Target word count for the blog post")
    topics: List[str] = Field(..., description="Topics covered in the blog post")
    target_reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")

    model_config = ConfigDict(extra="allow")


class SocialMediaTemplateSchema(ContentTemplateSchema):
    """Schema for social media templates."""
    platform: str = Field(..., description="Social media platform")
    key_messages: List[str] = Field(..., description="Key messages for the social media post")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags for the social media post")
    include_image: bool = Field(default=True, description="Whether to include an image")
    include_link: bool = Field(default=True, description="Whether to include a link")
    character_limit: Optional[int] = Field(default=None, description="Character limit for the post")

    model_config = ConfigDict(extra="allow")


class EmailNewsletterTemplateSchema(ContentTemplateSchema):
    """Schema for email newsletter templates."""
    sections: List[Dict[str, Any]] = Field(..., description="Sections of the email newsletter")
    subject_line_options: List[str] = Field(..., description="Subject line options for the email")
    preview_text_options: List[str] = Field(..., description="Preview text options for the email")
    include_header: bool = Field(default=True, description="Whether to include a header")
    include_footer: bool = Field(default=True, description="Whether to include a footer")
    include_social_links: bool = Field(default=True, description="Whether to include social links")
    include_call_to_action: bool = Field(default=True, description="Whether to include a call to action")

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


class MarketingChannelSchema(BaseModel):
    """Pydantic model for marketing channel."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the channel")
    name: str = Field(..., description="Name of the channel")
    category: ChannelCategory = Field(default=ChannelCategory.OTHER, description="Category of the channel")
    description: str = Field(..., description="Description of the channel")
    cost_structure: Dict[str, Any] = Field(default_factory=dict, description="Cost structure information")
    audience_demographics: Dict[str, Any] = Field(default_factory=dict, description="Typical audience demographics")
    typical_roi: Optional[Dict[str, Any]] = Field(None, description="Typical ROI information")
    best_practices: List[str] = Field(default_factory=list, description="Best practices for this channel")
    metrics: List[str] = Field(default_factory=list, description="Key metrics for this channel")
    implementation_difficulty: DifficultyLevel = Field(DifficultyLevel.MEDIUM, description="Difficulty level of implementation")
    time_to_results: str = Field(default="medium-term", description="Typical time to see results")
    scalability: float = Field(default=0.5, description="Scalability score (0.0 to 1.0)", ge=0.0, le=1.0)
    required_resources: List[str] = Field(default_factory=list, description="Required resources for implementation")
    platforms: List[str] = Field(default_factory=list, description="Platforms within this channel")
    relevance_score: float = Field(default=0.5, description="Relevance score for this channel (0.0 to 1.0)", ge=0.0, le=1.0)

    model_config = ConfigDict(extra="allow")


class MarketingTacticSchema(BaseModel):
    """Pydantic model for marketing tactic."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the tactic")
    name: str = Field(..., description="Name of the tactic")
    channel_name: str = Field(..., description="Name of the channel this tactic belongs to")
    description: str = Field(..., description="Description of the tactic")
    expected_impact: float = Field(default=0.5, description="Expected impact score (0.0 to 1.0)", ge=0.0, le=1.0)
    timeframe: str = Field(default="medium-term", description="Timeframe for results")
    resources_required: List[str] = Field(default_factory=list, description="Resources required for implementation")
    estimated_cost: float = Field(default=0.0, description="Estimated cost for implementation")

    model_config = ConfigDict(extra="allow")


class MarketingMetricSchema(BaseModel):
    """Pydantic model for marketing metric."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the metric")
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of the metric")
    target_value: float = Field(..., description="Target value for the metric")
    current_value: float = Field(default=0.0, description="Current value of the metric")
    unit: str = Field(..., description="Unit of measurement")

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


class MarketingStrategyInputSchema(BaseModel):
    """Schema for marketing strategy inputs."""
    business_type: BusinessType = Field(..., description="Type of business")
    business_size: BusinessSize = Field(..., description="Size of business")
    business_goals: List[str] = Field(..., description="Business goals")
    target_audience: TargetAudienceSchema = Field(..., description="Target audience")
    budget: BudgetSchema = Field(..., description="Marketing budget")
    timeframe: TimeframeSchema = Field(..., description="Strategy timeframe")
    current_channels: Optional[List[str]] = Field(default=None, description="Current marketing channels")
    industry: str = Field(..., description="Business industry")
    location: Optional[str] = Field(default=None, description="Business location")
    unique_selling_points: List[str] = Field(..., description="Unique selling points")
    competitors: Optional[List[str]] = Field(default=None, description="Competitor names")

    model_config = ConfigDict(extra="allow")


class MarketingStrategyResultsSchema(BaseModel):
    """Schema for marketing strategy results."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the results")
    strategy_id: str = Field(..., description="ID of the strategy")
    metrics: List[MetricSchema] = Field(default_factory=list, description="Results metrics")
    roi: float = Field(..., description="Return on investment")
    achievements: List[str] = Field(default_factory=list, description="Achievements")
    challenges: List[str] = Field(default_factory=list, description="Challenges faced")
    lessons_learned: List[str] = Field(default_factory=list, description="Lessons learned")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for future")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Results timestamp")

    model_config = ConfigDict(extra="allow")


class MarketingPlanSchema(BaseModel):
    """Schema for marketing plans."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the plan")
    name: str = Field(..., description="Name of the plan")
    description: str = Field(..., description="Description of the plan")
    start_date: str = Field(..., description="Start date of the plan")
    end_date: str = Field(..., description="End date of the plan")
    goals: List[str] = Field(..., description="Goals of the plan")
    strategies: List[MarketingStrategySchema] = Field(default_factory=list, description="Strategies for the plan")
    budget: BudgetSchema = Field(..., description="Budget for the plan")
    metrics: List[MetricSchema] = Field(default_factory=list, description="Metrics for the plan")
    content_calendar: Optional[ContentCalendarSchema] = Field(default=None, description="Content calendar for the plan")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class PersonaSchema(BaseModel):
    """Schema for user personas."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the persona")
    name: str = Field(..., description="Name of the persona")
    description: str = Field(..., description="Description of the persona")
    demographics: DemographicsSchema = Field(default_factory=DemographicsSchema, description="Demographics of the persona")
    goals: List[str] = Field(..., description="Goals of the persona")
    pain_points: List[str] = Field(..., description="Pain points of the persona")
    behaviors: List[str] = Field(..., description="Behaviors of the persona")
    motivations: List[str] = Field(..., description="Motivations of the persona")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Preferences of the persona")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class ChannelAnalysisSchema(BaseModel):
    """Schema for channel analysis."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the analysis")
    channel_name: str = Field(..., description="Name of the channel")
    metrics: List[MetricSchema] = Field(default_factory=list, description="Metrics for the channel")
    strengths: List[str] = Field(default_factory=list, description="Strengths of the channel")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses of the channel")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities for the channel")
    threats: List[str] = Field(default_factory=list, description="Threats for the channel")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for the channel")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Analysis timestamp")

    model_config = ConfigDict(extra="allow")


class AudienceAnalysisSchema(BaseModel):
    """Schema for audience analysis."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the analysis")
    segment_name: str = Field(..., description="Name of the audience segment")
    demographics: DemographicsSchema = Field(..., description="Demographics of the audience")
    size: Optional[int] = Field(default=None, description="Size of the audience")
    interests: List[str] = Field(default_factory=list, description="Interests of the audience")
    behaviors: List[str] = Field(default_factory=list, description="Behaviors of the audience")
    pain_points: List[str] = Field(default_factory=list, description="Pain points of the audience")
    goals: List[str] = Field(default_factory=list, description="Goals of the audience")
    channels: List[str] = Field(default_factory=list, description="Preferred channels of the audience")
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict, description="Engagement metrics")
    conversion_metrics: Dict[str, Any] = Field(default_factory=dict, description="Conversion metrics")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for this audience")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Analysis timestamp")

    model_config = ConfigDict(extra="allow")


class BusinessAnalysisSchema(BaseModel):
    """Schema for business analysis."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the analysis")
    business_name: str = Field(..., description="Name of the business")
    business_type: BusinessType = Field(..., description="Type of business")
    business_size: BusinessSize = Field(..., description="Size of business")
    industry: str = Field(..., description="Business industry")
    location: Optional[str] = Field(default=None, description="Business location")
    strengths: List[str] = Field(default_factory=list, description="Business strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Business weaknesses")
    opportunities: List[str] = Field(default_factory=list, description="Business opportunities")
    threats: List[str] = Field(default_factory=list, description="Business threats")
    unique_selling_points: List[str] = Field(default_factory=list, description="Unique selling points")
    competitors: List[Dict[str, Any]] = Field(default_factory=list, description="Competitor analysis")
    market_position: Dict[str, Any] = Field(default_factory=dict, description="Market position analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for the business")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Analysis timestamp")

    model_config = ConfigDict(extra="allow")

class EmailContentSchema(BaseModel):
    """Pydantic model for email content."""
    subject: str = Field(..., description="Email subject line")
    preview_text: Optional[str] = Field(None, description="Email preview text")
    body_content: str = Field(..., description="Main content of the email")
    sender_name: str = Field(..., description="Name of the sender")
    sender_email: str = Field(..., description="Email address of the sender")
    reply_to: Optional[str] = Field(None, description="Reply-to email address")
    include_unsubscribe: bool = Field(True, description="Whether to include unsubscribe link")
    footer_text: Optional[str] = Field(None, description="Text for the email footer")
    template_id: Optional[str] = Field(None, description="ID of the email template to use")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class SocialMediaPostSchema(BaseModel):
    """Pydantic model for social media post content."""
    platform_id: str = Field(..., description="ID of the connected platform")
    content_text: str = Field(..., description="Text content of the post")
    media_urls: List[str] = Field(default_factory=list, description="URLs of media attachments")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags to include")
    mentions: List[str] = Field(default_factory=list, description="Accounts to mention")
    links: List[str] = Field(default_factory=list, description="URLs to include")
    location: Optional[Dict[str, Any]] = Field(None, description="Location data")
    visibility: ContentVisibility = Field(ContentVisibility.PUBLIC, description="Post visibility setting")
    schedule_type: PostScheduleType = Field(PostScheduleType.NOW, description="Posting schedule type")
    schedule_time: Optional[datetime] = Field(None, description="Scheduled posting time")
    targeting: Optional[Dict[str, Any]] = Field(None, description="Audience targeting parameters")

    model_config = ConfigDict(extra="allow")  # Allow extra fields for platform-specific post parameters


class SocialMediaAnalyticsMetricSchema(BaseModel):
    """Pydantic model for social media analytics metric."""
    name: str = Field(..., description="Metric name")
    value: Union[int, float, str] = Field(..., description="Metric value")
    timestamp: datetime = Field(..., description="Timestamp when metric was recorded")
    change_percent: Optional[float] = Field(None, description="Percent change from previous period")
    benchmark: Optional[Union[int, float, str]] = Field(None, description="Benchmark value for comparison")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class SocialMediaAnalyticsSchema(BaseModel):
    """Pydantic model for social media analytics data."""
    platform_id: str = Field(..., description="ID of the connected platform")
    post_id: Optional[str] = Field(None, description="ID of the specific post (if applicable)")
    time_period: Dict[str, datetime] = Field(..., description="Time period for the analytics data")
    granularity: str = Field("day", description="Data granularity (day, week, month)")
    metrics: Dict[str, List[SocialMediaAnalyticsMetricSchema]] = Field(..., description="Metrics data")
    aggregates: Dict[str, Union[int, float, str]] = Field(..., description="Aggregate values for metrics")
    insights: List[Dict[str, Any]] = Field(default_factory=list, description="Insights derived from analytics")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class SocialMediaCampaignSchema(BaseModel):
    """Pydantic model for social media campaign."""
    id: str = Field(..., description="Unique identifier for the campaign")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    platform_ids: List[str] = Field(..., description="IDs of connected platforms")
    content_items: List[Dict[str, Any]] = Field(..., description="Content items in the campaign")
    schedule_settings: Dict[str, Any] = Field(..., description="Schedule settings")
    targeting: Optional[Dict[str, Any]] = Field(None, description="Audience targeting parameters")
    start_date: datetime = Field(..., description="Campaign start date")
    end_date: Optional[datetime] = Field(None, description="Campaign end date")
    status: str = Field("draft", description="Campaign status")
    scheduled_posts: Dict[str, List[str]] = Field(default_factory=dict, description="Scheduled post IDs by platform")
    tags: List[str] = Field(default_factory=list, description="Campaign tags")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class AudienceInsightSchema(BaseModel):
    """Pydantic model for social media audience insights."""
    platform_id: str = Field(..., description="ID of the connected platform")
    segment: Optional[Dict[str, Any]] = Field(None, description="Audience segment parameters")
    demographics: Optional[Dict[str, Any]] = Field(None, description="Demographic breakdown")
    interests: Optional[Dict[str, Any]] = Field(None, description="Interest categories")
    behaviors: Optional[Dict[str, Any]] = Field(None, description="Audience behaviors")
    engagement_metrics: Optional[Dict[str, Any]] = Field(None, description="Engagement metrics")
    active_times: Optional[Dict[str, Any]] = Field(None, description="Active times data")
    insights: List[Dict[str, Any]] = Field(default_factory=list, description="Insights derived from audience data")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class SocialMediaAuthSchema(BaseModel):
    """Pydantic model for social media authentication."""
    platform: SocialMediaPlatform
    api_key: Optional[str] = Field(None, description="API key for the platform")
    api_secret: Optional[str] = Field(None, description="API secret for the platform")
    access_token: Optional[str] = Field(None, description="Access token for the platform")
    access_token_secret: Optional[str] = Field(None, description="Access token secret for the platform")
    refresh_token: Optional[str] = Field(None, description="Refresh token for the platform")
    expires_at: Optional[datetime] = Field(None, description="Token expiration timestamp")
    oauth_verifier: Optional[str] = Field(None, description="OAuth verifier for the platform")
    user_id: Optional[str] = Field(None, description="User ID on the platform")

    model_config = ConfigDict(extra="allow")  # Allow extra fields for platform-specific auth details


class SocialMediaConnectionSchema(BaseModel):
    """Pydantic model for social media connection."""
    id: str = Field(..., description="Unique identifier for the connection")
    platform: SocialMediaPlatform = Field(..., description="Social media platform")
    account_name: str = Field(..., description="Account name on the platform")
    account_id: str = Field(..., description="Account ID on the platform")
    profile_url: Optional[str] = Field(None, description="URL to the profile on the platform")
    connected_at: datetime = Field(..., description="Connection timestamp")
    last_synced_at: Optional[datetime] = Field(None, description="Last sync timestamp")
    status: str = Field("active", description="Connection status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific settings")
    capabilities: List[str] = Field(..., description="Supported capabilities for this connection")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingChannelSchema(BaseModel):
    """Pydantic model for marketing channel."""
    id: str = Field(..., description="Unique identifier for the channel")
    name: str = Field(..., description="Channel name")
    type: str = Field(..., description="Channel type")
    description: str = Field(..., description="Channel description")
    audience_reach: Optional[int] = Field(None, description="Estimated audience reach")
    cost_per_engagement: Optional[float] = Field(None, description="Average cost per engagement")
    effectiveness_score: Optional[float] = Field(None, description="Effectiveness score (0-1)")
    metrics: List[str] = Field(default_factory=list, description="Metrics tracked for this channel")
    best_practices: List[str] = Field(default_factory=list, description="Best practices for this channel")

    model_config = ConfigDict(extra="allow")  # Allow extra fields
