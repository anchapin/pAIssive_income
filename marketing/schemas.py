"""
Pydantic schemas for the Marketing module.

This module provides Pydantic models for data validation in the Marketing module.
"""

from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
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


class PriorityLevel(str, Enum):
    """Enum for priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DifficultyLevel(str, Enum):
    """Enum for difficulty levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


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


class BudgetSchema(BaseModel):
    """Pydantic model for marketing budget."""
    amount: float = Field(..., description="Budget amount", ge=0)
    period: BillingPeriod = Field(
        BillingPeriod.MONTHLY, 
        description="Budget period (monthly, quarterly, annually)"
    )
    currency: str = Field(
        "USD", 
        description="Currency code (e.g., USD, EUR)"
    )

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class TimeframeSchema(BaseModel):
    """Pydantic model for marketing timeframe."""
    duration: float = Field(..., description="Timeframe duration", ge=0)
    unit: TimeframeUnit = Field(
        TimeframeUnit.MONTHS,
        description="Timeframe unit (days, weeks, months, quarters, years)"
    )

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


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

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class TargetAudienceSchema(BaseModel):
    """Pydantic model for target audience."""
    demographics: DemographicsSchema = Field(
        ..., 
        description="Audience demographics"
    )
    interests: List[str] = Field(
        ..., 
        description="Audience interests"
    )
    pain_points: List[str] = Field(
        ..., 
        description="Audience pain points"
    )
    goals: List[str] = Field(
        ..., 
        description="Audience goals"
    )

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class ConfigSchema(BaseModel):
    """Pydantic model for marketing strategy configuration."""
    max_channels: int = Field(
        5, 
        description="Maximum number of channels to recommend", 
        ge=1, 
        le=10
    )
    min_channel_score: float = Field(
        0.6, 
        description="Minimum score for recommended channels", 
        ge=0.0, 
        le=1.0
    )
    prioritize_by: str = Field(
        "roi", 
        description="Metric to prioritize channels by (roi, effectiveness, audience_fit)"
    )
    include_experimental: bool = Field(
        False, 
        description="Whether to include experimental channels"
    )
    detail_level: str = Field(
        "medium", 
        description="Level of detail in recommendations (low, medium, high)"
    )
    timestamp: str = Field(
        ..., 
        description="Timestamp of configuration"
    )

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class MarketingTacticSchema(BaseModel):
    """Pydantic model for marketing tactic."""
    id: str = Field(..., description="Unique identifier for the tactic")
    name: str = Field(..., description="Name of the tactic")
    channel: str = Field(..., description="Marketing channel")
    description: str = Field(..., description="Description of the tactic")
    priority: PriorityLevel = Field(
        ..., 
        description="Priority level (high, medium, low)"
    )
    difficulty: DifficultyLevel = Field(
        DifficultyLevel.MEDIUM, 
        description="Difficulty level (high, medium, low)"
    )
    timeline: str = Field(..., description="Implementation timeline")
    cost_estimate: Optional[Dict[str, Any]] = Field(
        None, 
        description="Cost estimate"
    )
    roi_estimate: Optional[Dict[str, Any]] = Field(
        None, 
        description="ROI estimate"
    )
    resources_needed: Optional[List[str]] = Field(
        None, 
        description="Resources needed"
    )
    steps: List[str] = Field(..., description="Implementation steps")
    metrics: List[str] = Field(..., description="Success metrics")
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class MetricSchema(BaseModel):
    """Pydantic model for marketing metric."""
    id: str = Field(..., description="Unique identifier for the metric")
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of the metric")
    category: str = Field(..., description="Metric category")
    formula: Optional[str] = Field(
        None, 
        description="Formula for calculating the metric"
    )
    unit: Optional[str] = Field(
        None, 
        description="Unit of measurement"
    )
    target: Optional[Dict[str, Any]] = Field(
        None, 
        description="Target value(s)"
    )
    benchmarks: Optional[Dict[str, Any]] = Field(
        None, 
        description="Industry benchmarks"
    )
    tracking_frequency: str = Field(
        ..., 
        description="How often to track the metric"
    )
    data_source: Optional[str] = Field(
        None, 
        description="Source of data for the metric"
    )

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class ContentItemSchema(BaseModel):
    """Pydantic model for content item."""
    id: str = Field(..., description="Unique identifier for the content item")
    title: str = Field(..., description="Title of the content item")
    description: str = Field(..., description="Description of the content item")
    type: str = Field(..., description="Type of content (e.g., blog post, video)")
    channel: str = Field(..., description="Marketing channel")
    target_audience: str = Field(..., description="Target audience segment")
    goal: str = Field(..., description="Marketing goal for this content")
    keywords: List[str] = Field(
        ..., 
        description="Target keywords"
    )
    estimated_effort: str = Field(
        ..., 
        description="Estimated effort required"
    )
    expected_impact: str = Field(
        ..., 
        description="Expected impact"
    )
    timeline: str = Field(..., description="Production timeline")
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class ContentCalendarSchema(BaseModel):
    """Pydantic model for content calendar."""
    id: str = Field(..., description="Unique identifier for the calendar")
    name: str = Field(..., description="Name of the content calendar")
    description: str = Field(..., description="Description of the content calendar")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    channels: List[str] = Field(..., description="Marketing channels included")
    content_items: List[Dict[str, Any]] = Field(
        ..., 
        description="Content items in the calendar"
    )
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class PersonaSchema(BaseModel):
    """Pydantic model for user persona."""
    id: str = Field(..., description="Unique identifier for the persona")
    name: str = Field(..., description="Name of the persona")
    age: Optional[int] = Field(None, description="Age of the persona")
    gender: Optional[str] = Field(None, description="Gender of the persona")
    job_title: Optional[str] = Field(None, description="Job title of the persona")
    company_size: Optional[str] = Field(None, description="Company size")
    industry: Optional[str] = Field(None, description="Industry")
    education: Optional[str] = Field(None, description="Education level")
    income: Optional[str] = Field(None, description="Income level")
    location: Optional[str] = Field(None, description="Location")
    goals: List[str] = Field(..., description="Goals of the persona")
    challenges: List[str] = Field(..., description="Challenges faced by the persona")
    motivations: List[str] = Field(..., description="Motivations of the persona")
    preferred_channels: List[str] = Field(
        ..., 
        description="Preferred communication channels"
    )
    decision_factors: List[str] = Field(
        ..., 
        description="Decision-making factors"
    )
    bio: Optional[str] = Field(None, description="Brief biography of the persona")
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class ChannelAnalysisSchema(BaseModel):
    """Pydantic model for channel analysis."""
    id: str = Field(..., description="Unique identifier for the analysis")
    channel: str = Field(..., description="Marketing channel")
    effectiveness_score: float = Field(
        ..., 
        description="Overall effectiveness score", 
        ge=0.0, 
        le=1.0
    )
    audience_fit_score: float = Field(
        ..., 
        description="Audience fit score", 
        ge=0.0, 
        le=1.0
    )
    goal_alignment_score: float = Field(
        ..., 
        description="Goal alignment score", 
        ge=0.0, 
        le=1.0
    )
    budget_fit_score: float = Field(
        ..., 
        description="Budget fit score", 
        ge=0.0, 
        le=1.0
    )
    roi_score: float = Field(
        ..., 
        description="ROI score", 
        ge=0.0, 
        le=1.0
    )
    recommended_budget: Dict[str, Any] = Field(
        ..., 
        description="Recommended budget allocation"
    )
    recommendation_details: Dict[str, Any] = Field(
        ..., 
        description="Detailed recommendations"
    )
    implementation_timeline: Dict[str, Any] = Field(
        ..., 
        description="Implementation timeline"
    )
    metrics_to_track: List[str] = Field(
        ..., 
        description="Metrics to track for this channel"
    )
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class MarketingPlanSchema(BaseModel):
    """Pydantic model for marketing plan."""
    id: str = Field(..., description="Unique identifier for the marketing plan")
    name: str = Field(..., description="Name of the marketing plan")
    business_type: BusinessType = Field(
        ..., 
        description="Type of business"
    )
    business_size: BusinessSize = Field(
        BusinessSize.SMALL, 
        description="Size of business"
    )
    goals: List[str] = Field(..., description="Marketing goals")
    target_audience: TargetAudienceSchema = Field(
        ..., 
        description="Target audience"
    )
    budget: BudgetSchema = Field(..., description="Marketing budget")
    timeframe: TimeframeSchema = Field(..., description="Marketing timeframe")
    channels: List[str] = Field(..., description="Selected marketing channels")
    tactics: List[Dict[str, Any]] = Field(
        ..., 
        description="Marketing tactics"
    )
    metrics: List[Dict[str, Any]] = Field(..., description="Marketing metrics")
    content_calendar: Optional[Dict[str, Any]] = Field(
        None, 
        description="Content calendar"
    )
    implementation_plan: Dict[str, Any] = Field(
        ..., 
        description="Implementation plan"
    )
    resource_requirements: Dict[str, Any] = Field(
        ..., 
        description="Resource requirements"
    )
    expected_results: Dict[str, Any] = Field(
        ..., 
        description="Expected results"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class MarketingStrategyInputSchema(BaseModel):
    """Pydantic model for marketing strategy input."""
    business_type: BusinessType = Field(
        ..., 
        description="Type of business"
    )
    business_size: BusinessSize = Field(
        BusinessSize.SMALL, 
        description="Size of business"
    )
    goals: List[str] = Field(..., description="Marketing goals")
    target_audience: TargetAudienceSchema = Field(
        ..., 
        description="Target audience"
    )
    budget: BudgetSchema = Field(..., description="Marketing budget")
    timeframe: TimeframeSchema = Field(..., description="Marketing timeframe")
    config: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional configuration"
    )

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class MarketingStrategyResultsSchema(BaseModel):
    """Pydantic model for marketing strategy results."""
    id: str = Field(..., description="Unique identifier for the results")
    business_type: BusinessType = Field(
        ..., 
        description="Type of business"
    )
    goals: List[str] = Field(..., description="Marketing goals")
    tactics: List[Dict[str, Any]] = Field(
        ..., 
        description="Marketing tactics"
    )
    metrics: List[Dict[str, Any]] = Field(..., description="Marketing metrics")
    channels: List[Dict[str, Any]] = Field(
        ..., 
        description="Channel analysis and recommendations"
    )
    audience_analysis: Optional[Dict[str, Any]] = Field(
        None, 
        description="Target audience analysis"
    )
    business_analysis: Optional[Dict[str, Any]] = Field(
        None, 
        description="Business analysis"
    )
    content_plan: Optional[Dict[str, Any]] = Field(
        None, 
        description="Content marketing plan"
    )
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class AudienceAnalysisSchema(BaseModel):
    """Pydantic model for audience analysis."""
    id: str = Field(..., description="Unique identifier for the analysis")
    demographic_analysis: Dict[str, Any] = Field(
        ..., 
        description="Demographic analysis"
    )
    interest_analysis: Dict[str, Any] = Field(
        ..., 
        description="Interest analysis"
    )
    pain_point_analysis: Dict[str, Any] = Field(
        ..., 
        description="Pain point analysis"
    )
    goal_analysis: Dict[str, Any] = Field(
        ..., 
        description="Goal analysis"
    )
    audience_segments: List[Dict[str, Any]] = Field(
        ..., 
        description="Audience segments"
    )
    audience_size_estimate: Optional[Dict[str, Any]] = Field(
        None, 
        description="Audience size estimate"
    )
    audience_growth_potential: Optional[Dict[str, Any]] = Field(
        None, 
        description="Audience growth potential"
    )
    audience_value_estimate: Optional[Dict[str, Any]] = Field(
        None, 
        description="Audience value estimate"
    )
    timestamp: str = Field(..., description="Timestamp of analysis")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class BusinessAnalysisSchema(BaseModel):
    """Pydantic model for business analysis."""
    id: str = Field(..., description="Unique identifier for the analysis")
    business_type: Dict[str, Any] = Field(
        ..., 
        description="Business type information"
    )
    goal_analysis: Dict[str, Any] = Field(
        ..., 
        description="Goal analysis"
    )
    competitive_analysis: Dict[str, Any] = Field(
        ..., 
        description="Competitive analysis"
    )
    strengths: List[str] = Field(..., description="Business strengths")
    weaknesses: List[str] = Field(..., description="Business weaknesses")
    opportunities: List[str] = Field(..., description="Business opportunities")
    threats: List[str] = Field(..., description="Business threats")
    timestamp: str = Field(..., description="Timestamp of analysis")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class ContentGeneratorConfigSchema(BaseModel):
    """Pydantic model for content generator configuration."""
    creativity_level: float = Field(
        0.7, 
        description="Level of creativity in generated content",
        ge=0.0,
        le=1.0
    )
    tone_consistency: float = Field(
        0.8, 
        description="Consistency of tone in generated content",
        ge=0.0,
        le=1.0
    )
    max_length: int = Field(
        2000, 
        description="Maximum length of generated content",
        ge=1
    )
    min_length: int = Field(
        500, 
        description="Minimum length of generated content",
        ge=1
    )
    include_images: bool = Field(
        True, 
        description="Whether to include images in generated content"
    )
    include_links: bool = Field(
        True, 
        description="Whether to include links in generated content"
    )
    seo_optimization: bool = Field(
        True, 
        description="Whether to optimize generated content for SEO"
    )
    target_reading_level: ReadingLevel = Field(
        ReadingLevel.INTERMEDIATE,
        description="Target reading level for generated content"
    )
    language: str = Field(
        "en-US", 
        description="Language of generated content"
    )
    content_format: ContentFormat = Field(
        ContentFormat.MARKDOWN,
        description="Format of generated content"
    )
    include_metadata: bool = Field(
        True, 
        description="Whether to include metadata in generated content"
    )
    use_ai_enhancement: bool = Field(
        True, 
        description="Whether to use AI enhancement for generated content"
    )
    ai_enhancement_level: float = Field(
        0.5, 
        description="Level of AI enhancement for generated content",
        ge=0.0,
        le=1.0
    )
    include_analytics_tags: bool = Field(
        False, 
        description="Whether to include analytics tags in generated content"
    )
    include_call_to_action: bool = Field(
        True, 
        description="Whether to include call to action in generated content"
    )
    call_to_action_strength: float = Field(
        0.7, 
        description="Strength of call to action in generated content",
        ge=0.0,
        le=1.0
    )
    personalization_level: float = Field(
        0.5, 
        description="Level of personalization in generated content",
        ge=0.0,
        le=1.0
    )
    content_freshness: float = Field(
        0.8, 
        description="Freshness of generated content",
        ge=0.0,
        le=1.0
    )
    content_uniqueness: float = Field(
        0.9, 
        description="Uniqueness of generated content",
        ge=0.0,
        le=1.0
    )
    content_relevance: float = Field(
        0.9, 
        description="Relevance of generated content",
        ge=0.0,
        le=1.0
    )
    content_engagement: float = Field(
        0.8, 
        description="Engagement level of generated content",
        ge=0.0,
        le=1.0
    )
    content_conversion: float = Field(
        0.7, 
        description="Conversion potential of generated content",
        ge=0.0,
        le=1.0
    )
    content_authority: float = Field(
        0.6, 
        description="Authority level of generated content",
        ge=0.0,
        le=1.0
    )
    content_trustworthiness: float = Field(
        0.9, 
        description="Trustworthiness of generated content",
        ge=0.0,
        le=1.0
    )
    content_expertise: float = Field(
        0.8, 
        description="Expertise level of generated content",
        ge=0.0,
        le=1.0
    )
    timestamp: str = Field(
        ..., 
        description="Timestamp when the configuration was created/updated"
    )
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields for template-specific configurations


class ContentTemplateSchema(BaseModel):
    """Base Pydantic model for content templates."""
    id: str = Field(..., description="Unique identifier for the template")
    title: str = Field(..., description="Title of the template")
    description: str = Field(..., description="Description of the template")
    target_persona: Dict[str, Any] = Field(
        ..., 
        description="Target persona information"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class BlogPostTemplateSchema(ContentTemplateSchema):
    """Pydantic model for blog post templates."""
    key_points: List[str] = Field(..., description="Key points to cover")
    seo_keywords: List[str] = Field(..., description="Target SEO keywords")
    call_to_action: Optional[str] = Field(None, description="Call to action")
    estimated_reading_time: Optional[int] = Field(
        None, 
        description="Estimated reading time in minutes",
        ge=1
    )
    target_word_count: Optional[int] = Field(
        None, 
        description="Target word count",
        ge=200
    )
    topics: List[str] = Field(..., description="Topics covered")
    target_reading_level: ReadingLevel = Field(
        ReadingLevel.INTERMEDIATE, 
        description="Target reading level"
    )


class SocialMediaTemplateSchema(ContentTemplateSchema):
    """Pydantic model for social media templates."""
    platform: str = Field(..., description="Social media platform")
    key_messages: List[str] = Field(..., description="Key messages to convey")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags to include")
    include_image: bool = Field(True, description="Whether to include an image")
    include_link: bool = Field(True, description="Whether to include a link")
    character_limit: Optional[int] = Field(
        None, 
        description="Character limit",
        ge=1
    )


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
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


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
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields for platform-specific post parameters


class SocialMediaAnalyticsMetricSchema(BaseModel):
    """Pydantic model for social media analytics metric."""
    name: str = Field(..., description="Metric name")
    value: Union[int, float, str] = Field(..., description="Metric value")
    timestamp: datetime = Field(..., description="Timestamp when metric was recorded")
    change_percent: Optional[float] = Field(None, description="Percent change from previous period")
    benchmark: Optional[Union[int, float, str]] = Field(None, description="Benchmark value for comparison")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


class SocialMediaAnalyticsSchema(BaseModel):
    """Pydantic model for social media analytics data."""
    platform_id: str = Field(..., description="ID of the connected platform")
    post_id: Optional[str] = Field(None, description="ID of the specific post (if applicable)")
    time_period: Dict[str, datetime] = Field(..., description="Time period for the analytics data")
    granularity: str = Field("day", description="Data granularity (day, week, month)")
    metrics: Dict[str, List[SocialMediaAnalyticsMetricSchema]] = Field(..., description="Metrics data")
    aggregates: Dict[str, Union[int, float, str]] = Field(..., description="Aggregate values for metrics")
    insights: List[Dict[str, Any]] = Field(default_factory=list, description="Insights derived from analytics")

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


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
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


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
    
    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


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

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields for platform-specific auth details


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

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields


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

    class Config:
        """Configuration for the model."""
        extra = "allow"  # Allow extra fields