"""
Pydantic schemas for the Marketing module.

This module provides Pydantic models for data validation in the Marketing module.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
        description="Budget period (monthly, quarterly, annually)",
    )
    currency: str = Field("USD", description="Currency code (e.g., USD, EUR)")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class TimeframeSchema(BaseModel):
    """Pydantic model for marketing timeframe."""

    duration: float = Field(..., description="Timeframe duration", ge=0)
    unit: TimeframeUnit = Field(
        TimeframeUnit.MONTHS,
        description="Timeframe unit (days, weeks, months, quarters, years)",
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class DemographicsSchema(BaseModel):
    """Pydantic model for target audience demographics."""

    age_range: Optional[str] = Field(None, description="Age range (e.g., 18-24, 25-34)")
    gender: Optional[str] = Field(None, description="Gender (e.g., male, female, mixed)")
    location: Optional[str] = Field(None, description="Location (e.g., urban, rural, global)")
    income: Optional[str] = Field(None, description="Income level (e.g., low, middle, high)")
    education: Optional[str] = Field(
        None, description="Education level (e.g., high school, college, graduate)"
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class TargetAudienceSchema(BaseModel):
    """Pydantic model for target audience."""

    demographics: DemographicsSchema = Field(..., description="Audience demographics")
    interests: List[str] = Field(..., description="Audience interests")
    pain_points: List[str] = Field(..., description="Audience pain points")
    goals: List[str] = Field(..., description="Audience goals")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ConfigSchema(BaseModel):
    """Pydantic model for marketing strategy configuration."""

    max_channels: int = Field(5, description="Maximum number of channels to recommend", ge=1, le=10)
    min_channel_score: float = Field(
        0.6, description="Minimum score for recommended channels", ge=0.0, le=1.0
    )
    prioritize_by: str = Field(
        "roi",
        description="Metric to prioritize channels by (roi, effectiveness, audience_fit)",
    )
    include_experimental: bool = Field(
        False, description="Whether to include experimental channels"
    )
    detail_level: str = Field(
        "medium", description="Level of detail in recommendations (low, medium, high)"
    )
    timestamp: str = Field(..., description="Timestamp of configuration")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingTacticSchema(BaseModel):
    """Pydantic model for marketing tactic."""

    id: str = Field(..., description="Unique identifier for the tactic")
    name: str = Field(..., description="Name of the tactic")
    channel: str = Field(..., description="Marketing channel")
    description: str = Field(..., description="Description of the tactic")
    priority: PriorityLevel = Field(..., description="Priority level (high, medium, low)")
    difficulty: DifficultyLevel = Field(
        DifficultyLevel.MEDIUM, description="Difficulty level (high, medium, low)"
    )
    timeline: str = Field(..., description="Implementation timeline")
    cost_estimate: Optional[Dict[str, Any]] = Field(None, description="Cost estimate")
    roi_estimate: Optional[Dict[str, Any]] = Field(None, description="ROI estimate")
    resources_needed: Optional[List[str]] = Field(None, description="Resources needed")
    steps: List[str] = Field(..., description="Implementation steps")
    metrics: List[str] = Field(..., description="Success metrics")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MetricSchema(BaseModel):
    """Pydantic model for marketing metric."""

    id: str = Field(..., description="Unique identifier for the metric")
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of the metric")
    category: str = Field(..., description="Metric category")
    formula: Optional[str] = Field(None, description="Formula for calculating the metric")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    target: Optional[Dict[str, Any]] = Field(None, description="Target value(s)")
    benchmarks: Optional[Dict[str, Any]] = Field(None, description="Industry benchmarks")
    tracking_frequency: str = Field(..., description="How often to track the metric")
    data_source: Optional[str] = Field(None, description="Source of data for the metric")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingMetricSchema(BaseModel):
    """Pydantic model for marketing metric with additional fields."""

    id: str = Field(..., description="Unique identifier for the metric")
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of the metric")
    category: str = Field(..., description="Metric category")
    formula: Optional[str] = Field(None, description="Formula for calculating the metric")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    target: Optional[Dict[str, Any]] = Field(None, description="Target value(s)")
    benchmarks: Optional[Dict[str, Any]] = Field(None, description="Industry benchmarks")
    tracking_frequency: str = Field(..., description="How often to track the metric")
    data_source: Optional[str] = Field(None, description="Source of data for the metric")
    baseline_value: Optional[float] = Field(None, description="Baseline value for the metric")
    current_value: Optional[float] = Field(None, description="Current value of the metric")
    goal_value: Optional[float] = Field(None, description="Goal value for the metric")
    trend: Optional[str] = Field(None, description="Trend direction (up, down, stable)")
    importance: Optional[str] = Field(None, description="Importance level (high, medium, low)")
    visualization_type: Optional[str] = Field(None, description="Type of visualization for the metric")
    related_metrics: Optional[List[str]] = Field(None, description="Related metrics")
    notes: Optional[str] = Field(None, description="Additional notes about the metric")
    last_updated: Optional[str] = Field(None, description="Last updated timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ContentItemSchema(BaseModel):
    """Pydantic model for content item."""

    id: str = Field(..., description="Unique identifier for the content item")
    title: str = Field(..., description="Title of the content item")
    description: str = Field(..., description="Description of the content item")
    type: str = Field(..., description="Type of content (e.g., blog post, video)")
    channel: str = Field(..., description="Marketing channel")
    target_audience: str = Field(..., description="Target audience segment")
    goal: str = Field(..., description="Marketing goal for this content")
    keywords: List[str] = Field(..., description="Target keywords")
    estimated_effort: str = Field(..., description="Estimated effort required")
    expected_impact: str = Field(..., description="Expected impact")
    timeline: str = Field(..., description="Production timeline")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ContentCalendarSchema(BaseModel):
    """Pydantic model for content calendar."""

    id: str = Field(..., description="Unique identifier for the calendar")
    name: str = Field(..., description="Name of the content calendar")
    description: str = Field(..., description="Description of the content calendar")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    channels: List[str] = Field(..., description="Marketing channels included")
    content_items: List[Dict[str, Any]] = Field(..., description="Content items in the calendar")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


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
    preferred_channels: List[str] = Field(..., description="Preferred communication channels")
    decision_factors: List[str] = Field(..., description="Decision-making factors")
    bio: Optional[str] = Field(None, description="Brief biography of the persona")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingChannelSchema(BaseModel):
    """Pydantic model for marketing channel."""

    id: str = Field(..., description="Unique identifier for the channel")
    name: str = Field(..., description="Name of the channel")
    description: str = Field(..., description="Description of the channel")
    type: str = Field(..., description="Type of channel (e.g., social media, email, content)")
    audience_fit: Dict[str, Any] = Field(..., description="Audience fit information")
    cost_structure: Dict[str, Any] = Field(..., description="Cost structure information")
    effectiveness_metrics: Dict[str, Any] = Field(..., description="Effectiveness metrics")
    implementation_difficulty: DifficultyLevel = Field(
        DifficultyLevel.MEDIUM, description="Implementation difficulty"
    )
    time_to_results: str = Field(..., description="Estimated time to see results")
    best_practices: List[str] = Field(..., description="Best practices for this channel")
    common_pitfalls: List[str] = Field(..., description="Common pitfalls to avoid")
    integration_points: List[str] = Field(..., description="Integration points with other channels")
    tools_and_resources: List[Dict[str, Any]] = Field(..., description="Tools and resources")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ChannelAnalysisSchema(BaseModel):
    """Pydantic model for channel analysis."""

    id: str = Field(..., description="Unique identifier for the analysis")
    channel: str = Field(..., description="Marketing channel")
    effectiveness_score: float = Field(
        ..., description="Overall effectiveness score", ge=0.0, le=1.0
    )
    audience_fit_score: float = Field(..., description="Audience fit score", ge=0.0, le=1.0)
    goal_alignment_score: float = Field(..., description="Goal alignment score", ge=0.0, le=1.0)
    budget_fit_score: float = Field(..., description="Budget fit score", ge=0.0, le=1.0)
    roi_score: float = Field(..., description="ROI score", ge=0.0, le=1.0)
    recommended_budget: Dict[str, Any] = Field(..., description="Recommended budget allocation")
    recommendation_details: Dict[str, Any] = Field(..., description="Detailed recommendations")
    implementation_timeline: Dict[str, Any] = Field(..., description="Implementation timeline")
    metrics_to_track: List[str] = Field(..., description="Metrics to track for this channel")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingPlanSchema(BaseModel):
    """Pydantic model for marketing plan."""

    id: str = Field(..., description="Unique identifier for the marketing plan")
    name: str = Field(..., description="Name of the marketing plan")
    business_type: BusinessType = Field(..., description="Type of business")
    business_size: BusinessSize = Field(BusinessSize.SMALL, description="Size of business")
    goals: List[str] = Field(..., description="Marketing goals")
    target_audience: TargetAudienceSchema = Field(..., description="Target audience")
    budget: BudgetSchema = Field(..., description="Marketing budget")
    timeframe: TimeframeSchema = Field(..., description="Marketing timeframe")
    channels: List[str] = Field(..., description="Selected marketing channels")
    tactics: List[Dict[str, Any]] = Field(..., description="Marketing tactics")
    metrics: List[Dict[str, Any]] = Field(..., description="Marketing metrics")
    content_calendar: Optional[Dict[str, Any]] = Field(None, description="Content calendar")
    implementation_plan: Dict[str, Any] = Field(..., description="Implementation plan")
    resource_requirements: Dict[str, Any] = Field(..., description="Resource requirements")
    expected_results: Dict[str, Any] = Field(..., description="Expected results")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingStrategyInputSchema(BaseModel):
    """Pydantic model for marketing strategy input."""

    business_type: BusinessType = Field(..., description="Type of business")
    business_size: BusinessSize = Field(BusinessSize.SMALL, description="Size of business")
    goals: List[str] = Field(..., description="Marketing goals")
    target_audience: TargetAudienceSchema = Field(..., description="Target audience")
    budget: BudgetSchema = Field(..., description="Marketing budget")
    timeframe: TimeframeSchema = Field(..., description="Marketing timeframe")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional configuration")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingStrategyResultsSchema(BaseModel):
    """Pydantic model for marketing strategy results."""

    id: str = Field(..., description="Unique identifier for the results")
    business_type: BusinessType = Field(..., description="Type of business")
    goals: List[str] = Field(..., description="Marketing goals")
    tactics: List[Dict[str, Any]] = Field(..., description="Marketing tactics")
    metrics: List[Dict[str, Any]] = Field(..., description="Marketing metrics")
    channels: List[Dict[str, Any]] = Field(..., description="Channel analysis and recommendations")
    audience_analysis: Optional[Dict[str, Any]] = Field(
        None, description="Target audience analysis"
    )
    business_analysis: Optional[Dict[str, Any]] = Field(None, description="Business analysis")
    content_plan: Optional[Dict[str, Any]] = Field(None, description="Content marketing plan")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class AudienceAnalysisSchema(BaseModel):
    """Pydantic model for audience analysis."""

    id: str = Field(..., description="Unique identifier for the analysis")
    demographic_analysis: Dict[str, Any] = Field(..., description="Demographic analysis")
    interest_analysis: Dict[str, Any] = Field(..., description="Interest analysis")
    pain_point_analysis: Dict[str, Any] = Field(..., description="Pain point analysis")
    goal_analysis: Dict[str, Any] = Field(..., description="Goal analysis")
    audience_segments: List[Dict[str, Any]] = Field(..., description="Audience segments")
    audience_size_estimate: Optional[Dict[str, Any]] = Field(
        None, description="Audience size estimate"
    )
    audience_growth_potential: Optional[Dict[str, Any]] = Field(
        None, description="Audience growth potential"
    )
    audience_value_estimate: Optional[Dict[str, Any]] = Field(
        None, description="Audience value estimate"
    )
    timestamp: str = Field(..., description="Timestamp of analysis")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class BusinessAnalysisSchema(BaseModel):
    """Pydantic model for business analysis."""

    id: str = Field(..., description="Unique identifier for the analysis")
    business_type: Dict[str, Any] = Field(..., description="Business type information")
    goal_analysis: Dict[str, Any] = Field(..., description="Goal analysis")
    competitive_analysis: Dict[str, Any] = Field(..., description="Competitive analysis")
    strengths: List[str] = Field(..., description="Business strengths")
    weaknesses: List[str] = Field(..., description="Business weaknesses")
    opportunities: List[str] = Field(..., description="Business opportunities")
    threats: List[str] = Field(..., description="Business threats")
    timestamp: str = Field(..., description="Timestamp of analysis")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ContentGeneratorConfigSchema(BaseModel):
    """Pydantic model for content generator configuration."""

    creativity_level: float = Field(
        0.7, description="Level of creativity in generated content", ge=0.0, le=1.0
    )
    tone_consistency: float = Field(
        0.8, description="Consistency of tone in generated content", ge=0.0, le=1.0
    )
    max_length: int = Field(2000, description="Maximum length of generated content", ge=1)
    min_length: int = Field(500, description="Minimum length of generated content", ge=1)
    include_images: bool = Field(True, description="Whether to include images in generated content")
    include_links: bool = Field(True, description="Whether to include links in generated content")
    seo_optimization: bool = Field(
        True, description="Whether to optimize generated content for SEO"
    )
    target_reading_level: ReadingLevel = Field(
        ReadingLevel.INTERMEDIATE,
        description="Target reading level for generated content",
    )
    language: str = Field("en-US", description="Language of generated content")
    content_format: ContentFormat = Field(
        ContentFormat.MARKDOWN, description="Format of generated content"
    )
    include_metadata: bool = Field(
        True, description="Whether to include metadata in generated content"
    )
    use_ai_enhancement: bool = Field(
        True, description="Whether to use AI enhancement for generated content"
    )
    ai_enhancement_level: float = Field(
        0.5, description="Level of AI enhancement for generated content", ge=0.0, le=1.0
    )
    include_analytics_tags: bool = Field(
        False, description="Whether to include analytics tags in generated content"
    )
    include_call_to_action: bool = Field(
        True, description="Whether to include call to action in generated content"
    )
    call_to_action_strength: float = Field(
        0.7,
        description="Strength of call to action in generated content",
        ge=0.0,
        le=1.0,
    )
    personalization_level: float = Field(
        0.5, description="Level of personalization in generated content", ge=0.0, le=1.0
    )
    content_freshness: float = Field(
        0.8, description="Freshness of generated content", ge=0.0, le=1.0
    )
    content_uniqueness: float = Field(
        0.9, description="Uniqueness of generated content", ge=0.0, le=1.0
    )
    content_relevance: float = Field(
        0.9, description="Relevance of generated content", ge=0.0, le=1.0
    )
    content_engagement: float = Field(
        0.8, description="Engagement level of generated content", ge=0.0, le=1.0
    )
    content_conversion: float = Field(
        0.7, description="Conversion potential of generated content", ge=0.0, le=1.0
    )
    content_authority: float = Field(
        0.6, description="Authority level of generated content", ge=0.0, le=1.0
    )
    content_trustworthiness: float = Field(
        0.9, description="Trustworthiness of generated content", ge=0.0, le=1.0
    )
    content_expertise: float = Field(
        0.8, description="Expertise level of generated content", ge=0.0, le=1.0
    )
    timestamp: str = Field(..., description="Timestamp when the configuration was created/updated")

    model_config = ConfigDict(extra="allow")  # Allow extra fields for template-specific configurations


class ContentTemplateSchema(BaseModel):
    """Base Pydantic model for content templates."""

    id: str = Field(..., description="Unique identifier for the template")
    title: str = Field(..., description="Title of the template")
    description: str = Field(..., description="Description of the template")
    target_persona: Dict[str, Any] = Field(..., description="Target persona information")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class BlogPostTemplateSchema(ContentTemplateSchema):
    """Pydantic model for blog post templates."""

    key_points: List[str] = Field(..., description="Key points to cover")
    seo_keywords: List[str] = Field(..., description="Target SEO keywords")
    call_to_action: Optional[str] = Field(None, description="Call to action")
    estimated_reading_time: Optional[int] = Field(
        None, description="Estimated reading time in minutes", ge=1
    )
    target_word_count: Optional[int] = Field(None, description="Target word count", ge=200)
    topics: List[str] = Field(..., description="Topics covered")
    target_reading_level: ReadingLevel = Field(
        ReadingLevel.INTERMEDIATE, description="Target reading level"
    )


class SocialMediaTemplateSchema(ContentTemplateSchema):
    """Pydantic model for social media templates."""

    platform: str = Field(..., description="Social media platform")
    key_messages: List[str] = Field(..., description="Key messages to convey")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags to include")
    include_image: bool = Field(True, description="Whether to include an image")
    include_link: bool = Field(True, description="Whether to include a link")
    character_limit: Optional[int] = Field(None, description="Character limit", ge=1)


class EmailNewsletterTemplateSchema(ContentTemplateSchema):
    """Pydantic model for email newsletter templates."""

    sections: List[Dict[str, Any]] = Field(..., description="Content sections")
    subject_line_options: List[str] = Field(..., description="Subject line options")
    preview_text_options: List[str] = Field(..., description="Preview text options")
    include_header: bool = Field(True, description="Whether to include a header")
    include_footer: bool = Field(True, description="Whether to include a footer")
    include_social_links: bool = Field(True, description="Whether to include social links")
    include_call_to_action: bool = Field(True, description="Whether to include a call to action")


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

    platform: str = Field(..., description="Social media platform (e.g., Twitter, LinkedIn)")
    post_text: str = Field(..., description="Text content of the post")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags to include")
    include_media: bool = Field(False, description="Whether to include media")
    media_urls: Optional[List[str]] = Field(None, description="URLs to media files")
    call_to_action: Optional[str] = Field(None, description="Call to action for the post")
    post_time: Optional[str] = Field(None, description="Suggested posting time")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class AdCopySchema(BaseModel):
    """Pydantic model for advertising copy."""

    platform: str = Field(..., description="Advertising platform")
    headline: str = Field(..., description="Ad headline")
    description: str = Field(..., description="Ad description")
    call_to_action: str = Field(..., description="Call to action text")
    display_url: Optional[str] = Field(None, description="Display URL")
    destination_url: str = Field(..., description="Destination URL")
    ad_format: str = Field(..., description="Format of the ad")
    character_count: Optional[Dict[str, int]] = Field(None, description="Character count limits")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class PressReleaseSchema(BaseModel):
    """Pydantic model for press release content."""

    headline: str = Field(..., description="Press release headline")
    subheadline: Optional[str] = Field(None, description="Press release subheadline")
    dateline: str = Field(..., description="Dateline (city, state, date)")
    intro_paragraph: str = Field(..., description="Introductory paragraph")
    body_content: str = Field(..., description="Main content")
    quote: Optional[str] = Field(None, description="Quote from company representative")
    quote_attribution: Optional[str] = Field(None, description="Attribution for the quote")
    boilerplate: str = Field(..., description="Company boilerplate")
    contact_info: Dict[str, str] = Field(..., description="Contact information")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class WhitePaperSchema(BaseModel):
    """Pydantic model for whitepaper content."""

    title: str = Field(..., description="Whitepaper title")
    abstract: str = Field(..., description="Abstract/executive summary")
    sections: List[Dict[str, Any]] = Field(..., description="Content sections")
    author: str = Field(..., description="Author name")
    publication_date: str = Field(..., description="Publication date")
    references: Optional[List[Dict[str, str]]] = Field(None, description="References/citations")
    figures: Optional[List[Dict[str, Any]]] = Field(None, description="Figures and tables")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ContentGeneratorInputSchema(BaseModel):
    """Pydantic model for content generator input."""

    content_type: str = Field(..., description="Type of content to generate")
    target_audience: Dict[str, Any] = Field(..., description="Target audience information")
    key_messages: List[str] = Field(..., description="Key messages to include")
    tone: str = Field(..., description="Desired tone of the content")
    style: str = Field(..., description="Desired style of the content")
    purpose: str = Field(..., description="Purpose of the content")
    length: Optional[Dict[str, Any]] = Field(None, description="Desired length parameters")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    competitor_analysis: Optional[Dict[str, Any]] = Field(None, description="Competitor analysis")
    brand_guidelines: Optional[Dict[str, Any]] = Field(None, description="Brand guidelines")
    config: Optional[ContentGeneratorConfigSchema] = Field(
        None, description="Generator configuration"
    )

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class ContentGeneratorOutputSchema(BaseModel):
    """Pydantic model for content generator output."""

    content_type: str = Field(..., description="Type of content generated")
    content: Dict[str, Any] = Field(..., description="Generated content")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Content metrics")
    recommendations: Optional[List[str]] = Field(None, description="Content recommendations")
    timestamp: str = Field(..., description="Generation timestamp")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class MarketingStrategySchema(BaseModel):
    """Pydantic model for marketing strategy."""

    id: str = Field(..., description="Unique identifier for the strategy")
    name: str = Field(..., description="Name of the strategy")
    business_type: str = Field(..., description="Type of business")
    business_size: Optional[str] = Field(None, description="Size of business")
    goals: List[str] = Field(..., description="Marketing goals")
    target_audience: TargetAudienceSchema = Field(..., description="Target audience")
    budget: BudgetSchema = Field(..., description="Marketing budget")
    channels: List[MarketingChannelSchema] = Field(..., description="Marketing channels")
    tactics: List[MarketingTacticSchema] = Field(..., description="Marketing tactics")
    allocated_budget: Dict[str, float] = Field(..., description="Budget allocation by channel")
    metrics: List[MarketingMetricSchema] = Field(..., description="Marketing metrics")
    created_at: str = Field(..., description="Creation timestamp")
    previous_version_id: Optional[str] = Field(None, description="ID of the previous version")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class GeneratedBlogPostSchema(BaseModel):
    """Pydantic model for generated blog post."""

    id: str = Field(..., description="Unique identifier for the content")
    template_id: str = Field(..., description="ID of the template used")
    timestamp: str = Field(..., description="Generation timestamp")
    title: str = Field(..., description="Blog post title")
    meta_description: str = Field(..., description="Meta description for SEO")
    introduction: str = Field(..., description="Blog post introduction")
    sections: List[Dict[str, Any]] = Field(..., description="Blog post sections")
    conclusion: str = Field(..., description="Blog post conclusion")
    call_to_action: str = Field(..., description="Call to action")
    tags: List[str] = Field(..., description="Blog post tags")
    categories: List[str] = Field(..., description="Blog post categories")
    featured_image: Dict[str, Any] = Field(..., description="Featured image information")
    seo_data: Dict[str, Any] = Field(..., description="SEO data")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class GeneratedSocialMediaPostSchema(BaseModel):
    """Pydantic model for generated social media post."""

    id: str = Field(..., description="Unique identifier for the content")
    template_id: str = Field(..., description="ID of the template used")
    timestamp: str = Field(..., description="Generation timestamp")
    platform: str = Field(..., description="Social media platform")
    content: str = Field(..., description="Post content")
    hashtags: List[str] = Field(..., description="Hashtags")
    image_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="Image suggestions")
    link: Optional[str] = Field(None, description="Link to include")
    call_to_action: Optional[str] = Field(None, description="Call to action")
    optimal_posting_times: Optional[List[str]] = Field(None, description="Optimal posting times")

    model_config = ConfigDict(extra="allow")  # Allow extra fields


class GeneratedEmailNewsletterSchema(BaseModel):
    """Pydantic model for generated email newsletter."""

    id: str = Field(..., description="Unique identifier for the content")
    template_id: str = Field(..., description="ID of the template used")
    timestamp: str = Field(..., description="Generation timestamp")
    subject_line: str = Field(..., description="Email subject line")
    preview_text: str = Field(..., description="Email preview text")
    content_sections: List[Dict[str, Any]] = Field(..., description="Email content sections")
    header: Optional[Dict[str, Any]] = Field(None, description="Email header")
    footer: Dict[str, Any] = Field(..., description="Email footer")
    call_to_action: Dict[str, Any] = Field(..., description="Call to action")
    images: Optional[List[Dict[str, Any]]] = Field(None, description="Images to include")
    links: Optional[List[Dict[str, Any]]] = Field(None, description="Links to include")
    spam_score: Optional[float] = Field(None, description="Spam score", ge=0.0, le=1.0)

    model_config = ConfigDict(extra="allow")  # Allow extra fields
