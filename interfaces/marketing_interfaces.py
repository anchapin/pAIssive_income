"""
Interfaces for the Marketing module.

This module provides interfaces for the marketing components to enable dependency injection
and improve testability and maintainability.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class IPersonaCreator(ABC):
    """Interface for persona creator."""

    @abstractmethod
    def create_persona(
        self,
        name: str,
        description: str,
        demographics: Dict[str, Any],
        pain_points: List[str],
        goals: List[str],
    ) -> Dict[str, Any]:
        """
        Create a user persona.

        Args:
            name: Persona name
            description: Persona description
            demographics: Demographic information
            pain_points: List of pain points
            goals: List of goals

        Returns:
            User persona dictionary
        """
        pass

    @abstractmethod
    def analyze_persona(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a user persona.

        Args:
            persona: User persona dictionary

        Returns:
            Persona analysis dictionary
        """
        pass

    @abstractmethod
    def get_persona_categories(self) -> List[str]:
        """
        Get a list of persona categories.

        Returns:
            List of persona categories
        """
        pass


class IMarketingStrategy(ABC):
    """Interface for marketing strategy."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the strategy name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get the strategy description."""
        pass

    @property
    @abstractmethod
    def channel_type(self) -> str:
        """Get the channel type."""
        pass

    @abstractmethod
    def create_strategy(self, target_persona: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """
        Create a marketing strategy.

        Args:
            target_persona: Target user persona
            goals: List of marketing goals

        Returns:
            Marketing strategy dictionary
        """
        pass

    @abstractmethod
    def get_tactics(self) -> List[Dict[str, Any]]:
        """
        Get marketing tactics.

        Returns:
            List of marketing tactic dictionaries
        """
        pass

    @abstractmethod
    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get marketing metrics.

        Returns:
            List of marketing metric dictionaries
        """
        pass

    @abstractmethod
    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full marketing strategy.

        Returns:
            Dictionary with complete strategy details
        """
        pass


class IContentTemplate(ABC):
    """Interface for content template."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Get the template ID."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the template name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get the template description."""
        pass

    @property
    @abstractmethod
    def content_type(self) -> str:
        """Get the content type."""
        pass

    @abstractmethod
    def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the content.

        Returns:
            Dictionary with outline details
        """
        pass

    @abstractmethod
    def generate_content(
        self,
        topic: str = "",
        target_audience: str = "",
        tone: str = "",
        keywords: List[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate content based on the template.

        Args:
            topic: Topic of the content
            target_audience: Target audience for the content
            tone: Tone of the content
            keywords: Keywords for the content
            **kwargs: Additional keyword arguments

        Returns:
            Dictionary with generated content
        """
        pass

    @abstractmethod
    def add_section(
        self,
        name: str = "",
        description: str = "",
        content_type: str = "text",
        placeholder: str = "",
        required: bool = False,
        section_type: str = "",
        title: str = "",
        content: str = "",
    ) -> Dict[str, Any]:
        """
        Add a section to the content template.

        Args:
            name: Name of the section
            description: Description of the section
            content_type: Type of content
            placeholder: Placeholder text for the section
            required: Whether the section is required
            section_type: Type of section
            title: Title of the section
            content: Optional content for the section

        Returns:
            Dictionary with section details
        """
        pass

    @abstractmethod
    def get_seo_recommendations(self) -> Dict[str, Any]:
        """
        Get SEO recommendations for the content.

        Returns:
            Dictionary with SEO recommendations
        """
        pass


class IABTesting(ABC):
    """Interface for A/B testing."""

    @abstractmethod
    def create_test(
        self,
        name: str,
        description: str,
        content_type: str,
        test_type: str,
        variants: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create an A/B test.

        Args:
            name: Test name
            description: Test description
            content_type: Type of content being tested (email, landing_page, ad, etc.)
            test_type: Type of test (a_b, split, multivariate)
            variants: List of test variants including control

        Returns:
            A/B test dictionary
        """
        pass

    @abstractmethod
    def get_variants(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get variants for an A/B test.

        Args:
            test_id: ID of the A/B test

        Returns:
            List of variant dictionaries
        """
        pass

    @abstractmethod
    def record_interaction(
        self,
        test_id: str,
        variant_id: str,
        interaction_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record an interaction with a variant.

        Args:
            test_id: ID of the A/B test
            variant_id: ID of the variant
            interaction_type: Type of interaction (impression, click, conversion, etc.)
            user_id: Optional ID of the user
            metadata: Optional metadata about the interaction

        Returns:
            Interaction dictionary
        """
        pass

    @abstractmethod
    def get_results(self, test_id: str) -> Dict[str, Any]:
        """
        Get results for an A/B test.

        Args:
            test_id: ID of the A/B test

        Returns:
            Dictionary with test results
        """
        pass

    @abstractmethod
    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """
        Analyze an A/B test for statistical significance.

        Args:
            test_id: ID of the A/B test

        Returns:
            Dictionary with test analysis
        """
        pass

    @abstractmethod
    def end_test(self, test_id: str, winning_variant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End an A/B test and optionally select a winning variant.

        Args:
            test_id: ID of the A/B test
            winning_variant_id: Optional ID of the winning variant

        Returns:
            Dictionary with test results and winner
        """
        pass


class ICampaignTracker(ABC):
    """Interface for campaign tracking."""

    @abstractmethod
    def create_campaign(
        self,
        name: str,
        description: str,
        channels: List[str],
        goals: List[Dict[str, Any]],
        target_metrics: Dict[str, float],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        budget: Optional[float] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new campaign for tracking.

        Args:
            name: Campaign name
            description: Campaign description
            channels: Marketing channels used (e.g., "email", "social_media", "content")
            goals: List of campaign goals with metrics and targets
            target_metrics: Dictionary mapping metric names to target values
            start_date: Optional start date for the campaign, defaults to current time
            end_date: Optional end date for the campaign
            budget: Optional campaign budget
            tags: Optional tags for categorizing the campaign
            metadata: Optional additional data about the campaign

        Returns:
            Dictionary containing the created campaign data
        """
        pass

    @abstractmethod
    def update_campaign(self, campaign_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a campaign's details.

        Args:
            campaign_id: ID of the campaign to update
            **kwargs: Campaign attributes to update

        Returns:
            Updated campaign dictionary
        """
        pass

    @abstractmethod
    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign details.

        Args:
            campaign_id: ID of the campaign to retrieve

        Returns:
            Campaign dictionary
        """
        pass

    @abstractmethod
    def list_campaigns(
        self,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        tag: Optional[str] = None,
        start_date_after: Optional[datetime] = None,
        start_date_before: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        List campaigns with optional filtering.

        Args:
            status: Optional filter for campaign status
            channel: Optional filter for campaigns using a specific channel
            tag: Optional filter for campaigns with a specific tag
            start_date_after: Optional filter for campaigns starting after a date
            start_date_before: Optional filter for campaigns starting before a date

        Returns:
            List of campaign dictionaries matching the filters
        """
        pass

    @abstractmethod
    def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a campaign and its associated metrics.

        Args:
            campaign_id: ID of the campaign to delete

        Returns:
            True if the campaign was deleted, False otherwise
        """
        pass

    @abstractmethod
    def record_metric(
        self,
        campaign_id: str,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None,
        channel: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a metric value for a campaign.

        Args:
            campaign_id: ID of the campaign
            metric_name: Name of the metric to record
            value: Value of the metric
            timestamp: Optional timestamp for the metric, defaults to current time
            channel: Optional channel to associate with the metric
            metadata: Optional additional data about the metric

        Returns:
            Dictionary containing the recorded metric
        """
        pass

    @abstractmethod
    def get_metrics(
        self,
        campaign_id: str,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[str] = None,
        group_by: Optional[str] = None,
        aggregation: str = "sum",
    ) -> Dict[str, Any]:
        """
        Get metrics for a campaign with optional filtering and aggregation.

        Args:
            campaign_id: ID of the campaign
            metric_name: Optional name of a specific metric to retrieve
            start_time: Optional start time to filter metrics
            end_time: Optional end time to filter metrics
            channel: Optional channel to filter metrics
            group_by: Optional grouping ("channel", "daily", "weekly", "monthly")
            aggregation: Aggregation method ("sum", "avg", "min", "max", "count")

        Returns:
            Dictionary containing the campaign metrics data
        """
        pass

    @abstractmethod
    def analyze_performance(
        self,
        campaign_id: str,
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance against target metrics.

        Args:
            campaign_id: ID of the campaign
            metrics: Optional list of metrics to include in the analysis

        Returns:
            Dictionary containing the performance analysis
        """
        pass

    @abstractmethod
    def compare_campaigns(
        self, campaign_ids: List[str], metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare performance of multiple campaigns.

        Args:
            campaign_ids: List of campaign IDs to compare
            metrics: Optional list of metrics to include in the comparison

        Returns:
            Dictionary containing the campaign comparison
        """
        pass

    @abstractmethod
    def generate_report(
        self,
        campaign_id: str,
        report_type: str = "summary",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a campaign performance report.

        Args:
            campaign_id: ID of the campaign
            report_type: Type of report to generate ("summary", "detailed", "goals")
            start_date: Optional start date for report data
            end_date: Optional end date for report data

        Returns:
            Dictionary containing the report data
        """
        pass


class IROIAnalyzer(ABC):
    """Interface for marketing ROI analysis."""

    @abstractmethod
    def calculate_roi(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        time_period: Optional[Tuple[datetime, datetime]] = None,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate ROI for a marketing campaign.

        Args:
            campaign_id: ID of the campaign to analyze
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            include_details: Whether to include detailed breakdown in results

        Returns:
            Dictionary containing ROI analysis results
        """
        pass

    @abstractmethod
    def calculate_cumulative_roi(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        start_date: datetime,
        end_date: datetime,
        interval: str = "daily",
    ) -> Dict[str, Any]:
        """
        Calculate cumulative ROI over time for a campaign.

        Args:
            campaign_id: ID of the campaign to analyze
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            start_date: Start date for analysis
            end_date: End date for analysis
            interval: Time interval for ROI points ("daily", "weekly", "monthly")

        Returns:
            Dictionary containing cumulative ROI analysis
        """
        pass

    @abstractmethod
    def compare_campaign_roi(
        self,
        campaign_ids: List[str],
        costs: Dict[str, Dict[str, float]],
        revenue_metrics: Dict[str, Union[str, List[str]]],
        time_periods: Optional[Dict[str, Tuple[datetime, datetime]]] = None,
    ) -> Dict[str, Any]:
        """
        Compare ROI across multiple campaigns.

        Args:
            campaign_ids: List of campaign IDs to compare
            costs: Dictionary mapping campaign IDs to their cost dictionaries
            revenue_metrics: Dictionary mapping campaign IDs to their revenue metrics
            time_periods: Optional dictionary mapping campaign IDs to time period tuples

        Returns:
            Dictionary containing comparative ROI analysis
        """
        pass

    @abstractmethod
    def forecast_roi(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        forecast_period: int,
        forecast_unit: str = "days",
        historical_period: Optional[Tuple[datetime, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Forecast future ROI based on historical data.

        Args:
            campaign_id: ID of the campaign to forecast
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            forecast_period: Number of time units to forecast
            forecast_unit: Unit for forecast period ("days", "weeks", "months")
            historical_period: Optional tuple of (start_date, end_date) for historical data

        Returns:
            Dictionary containing ROI forecast results
        """
        pass

    @abstractmethod
    def calculate_channel_roi(
        self,
        campaign_id: str,
        channel_costs: Dict[str, float],
        channel_revenue_metrics: Dict[str, Union[str, List[str]]],
        time_period: Optional[Tuple[datetime, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate ROI for each channel in a campaign.

        Args:
            campaign_id: ID of the campaign to analyze
            channel_costs: Dictionary mapping channel names to costs
            channel_revenue_metrics: Dictionary mapping channels to revenue metrics
            time_period: Optional tuple of (start_date, end_date) to limit analysis

        Returns:
            Dictionary containing channel ROI analysis
        """
        pass

    @abstractmethod
    def optimize_budget_allocation(
        self,
        campaign_id: str,
        total_budget: float,
        channel_costs: Dict[str, float],
        channel_revenue_metrics: Dict[str, Union[str, List[str]]],
        constraints: Optional[Dict[str, Any]] = None,
        time_period: Optional[Tuple[datetime, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize budget allocation across channels to maximize ROI.

        Args:
            campaign_id: ID of the campaign to optimize
            total_budget: Total budget to allocate
            channel_costs: Dictionary mapping channel names to costs
            channel_revenue_metrics: Dictionary mapping channels to revenue metrics
            constraints: Optional constraints for optimization
            time_period: Optional tuple of (start_date, end_date) for historical data

        Returns:
            Dictionary containing optimized budget allocation
        """
        pass

    @abstractmethod
    def generate_roi_report(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        time_period: Optional[Tuple[datetime, datetime]] = None,
        include_forecast: bool = False,
        forecast_period: int = 30,
        report_type: str = "summary",
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive ROI report for a campaign.

        Args:
            campaign_id: ID of the campaign to analyze
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            include_forecast: Whether to include ROI forecast
            forecast_period: Number of days to forecast if include_forecast is True
            report_type: Type of report to generate ("summary", "detailed", "executive")

        Returns:
            Dictionary containing ROI report data
        """
        pass


class IContentPerformanceAnalyzer(ABC):
    """Interface for content performance analytics."""

    @abstractmethod
    def track_content(
        self,
        content_id: str,
        content_type: str,
        title: str,
        channels: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register content for performance tracking.

        Args:
            content_id: Unique identifier for the content
            content_type: Type of content (blog_post, social_media, email, etc.)
            title: Title or headline of the content
            channels: List of channels where the content is published
            metadata: Optional additional data about the content

        Returns:
            Dictionary containing the registered content data
        """
        pass

    @abstractmethod
    def record_engagement(
        self,
        content_id: str,
        engagement_type: str,
        channel: str,
        count: int = 1,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record an engagement with content.

        Args:
            content_id: ID of the content
            engagement_type: Type of engagement (view, click, comment, share, conversion, etc.)
            channel: Channel where the engagement occurred
            count: Number of engagements to record (default 1)
            timestamp: Optional timestamp for the engagement, defaults to current time
            metadata: Optional additional data about the engagement

        Returns:
            Dictionary containing the recorded engagement
        """
        pass

    @abstractmethod
    def get_content(self, content_id: str) -> Dict[str, Any]:
        """
        Get content details.

        Args:
            content_id: ID of the content to retrieve

        Returns:
            Content dictionary
        """
        pass

    @abstractmethod
    def list_content(
        self,
        content_type: Optional[str] = None,
        channel: Optional[str] = None,
        date_published_after: Optional[datetime] = None,
        date_published_before: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List content with optional filtering.

        Args:
            content_type: Optional filter for content type
            channel: Optional filter for content published on a specific channel
            date_published_after: Optional filter for content published after a date
            date_published_before: Optional filter for content published before a date
            tags: Optional filter for content with specific tags

        Returns:
            List of content dictionaries matching the filters
        """
        pass

    @abstractmethod
    def get_engagement_metrics(
        self,
        content_id: str,
        engagement_types: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        group_by: Optional[str] = None,
        aggregation: str = "sum",
    ) -> Dict[str, Any]:
        """
        Get engagement metrics for content with optional filtering and aggregation.

        Args:
            content_id: ID of the content
            engagement_types: Optional list of engagement types to include
            channels: Optional list of channels to include
            start_time: Optional start time to filter engagements
            end_time: Optional end time to filter engagements
            group_by: Optional grouping ("channel", "engagement_type", "daily", "weekly", "monthly")
            aggregation: Aggregation method ("sum", "avg", "min", "max", "count")

        Returns:
            Dictionary containing the engagement metrics
        """
        pass

    @abstractmethod
    def analyze_performance(
        self, content_id: str, benchmark_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze content performance against benchmarks or averages.

        Args:
            content_id: ID of the content
            benchmark_metrics: Optional dictionary of benchmark metrics for comparison

        Returns:
            Dictionary containing the performance analysis
        """
        pass

    @abstractmethod
    def compare_content(
        self, content_ids: List[str], metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare performance of multiple content items.

        Args:
            content_ids: List of content IDs to compare
            metrics: Optional list of metrics to include in the comparison

        Returns:
            Dictionary containing the content comparison
        """
        pass

    @abstractmethod
    def identify_top_performing_content(
        self,
        content_type: Optional[str] = None,
        channel: Optional[str] = None,
        engagement_metric: str = "views",
        time_period: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Identify top-performing content based on engagement metrics.

        Args:
            content_type: Optional filter for content type
            channel: Optional filter for a specific channel
            engagement_metric: Metric to use for ranking
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            limit: Maximum number of items to return

        Returns:
            List of top-performing content items with metrics
        """
        pass

    @abstractmethod
    def generate_content_report(
        self,
        content_id: str,
        report_type: str = "summary",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a content performance report.

        Args:
            content_id: ID of the content
            report_type: Type of report to generate ("summary", "detailed", "channel")
            start_date: Optional start date for report data
            end_date: Optional end date for report data

        Returns:
            Dictionary containing the report data
        """
        pass


class ISocialMediaIntegration(ABC):
    """Interface for social media platform integration."""

    @abstractmethod
    def connect_platform(
        self, platform: str, credentials: Dict[str, Any], settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Connect to a social media platform with provided credentials.

        Args:
            platform: Social media platform name (e.g., "twitter", "facebook", "linkedin")
            credentials: Platform-specific authentication credentials
            settings: Optional platform-specific settings

        Returns:
            Dictionary containing the connection details

        Raises:
            PlatformNotSupportedError: If the platform is not supported
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def disconnect_platform(self, platform_id: str) -> bool:
        """
        Disconnect from a connected social media platform.

        Args:
            platform_id: ID of the connected platform

        Returns:
            True if disconnected successfully, False otherwise

        Raises:
            PlatformNotFoundError: If the platform ID is not found
        """
        pass

    @abstractmethod
    def get_connected_platforms(self) -> List[Dict[str, Any]]:
        """
        Get a list of connected social media platforms.

        Returns:
            List of dictionaries containing connected platform details
        """
        pass

    @abstractmethod
    def post_content(
        self,
        platform_id: str,
        content: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        visibility: str = "public",
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Post content to a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            content: Content to post (text, media, etc.)
            schedule_time: Optional time to schedule the post for
            visibility: Visibility setting (public, private, etc.)
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the post details and ID

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            ContentValidationError: If the content is invalid
            PostingError: If posting fails
        """
        pass

    @abstractmethod
    def get_post(self, platform_id: str, post_id: str) -> Dict[str, Any]:
        """
        Get details of a specific post.

        Args:
            platform_id: ID of the connected platform
            post_id: ID of the post to retrieve

        Returns:
            Dictionary containing the post details

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            PostNotFoundError: If the post ID is not found
        """
        pass

    @abstractmethod
    def delete_post(self, platform_id: str, post_id: str) -> bool:
        """
        Delete a post from a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            post_id: ID of the post to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            PostNotFoundError: If the post ID is not found
            DeletionError: If deletion fails
        """
        pass

    @abstractmethod
    def get_analytics(
        self,
        platform_id: str,
        post_id: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "day",
    ) -> Dict[str, Any]:
        """
        Get analytics for posts on a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            post_id: Optional ID of a specific post to get analytics for
            metrics: Optional list of specific metrics to retrieve
            start_date: Optional start date for analytics data
            end_date: Optional end date for analytics data
            granularity: Time granularity for data (day, week, month)

        Returns:
            Dictionary containing analytics data

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            PostNotFoundError: If the post ID is not found
            InvalidParameterError: If parameters are invalid
        """
        pass

    @abstractmethod
    def schedule_campaign(
        self,
        platform_ids: List[str],
        campaign_name: str,
        content_items: List[Dict[str, Any]],
        schedule_settings: Dict[str, Any],
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a social media campaign with multiple content items.

        Args:
            platform_ids: List of connected platform IDs
            campaign_name: Name of the campaign
            content_items: List of content items to post
            schedule_settings: Settings for content scheduling
            targeting: Optional audience targeting parameters

        Returns:
            Dictionary containing the campaign details and scheduled post IDs

        Raises:
            PlatformNotFoundError: If a platform ID is not found
            ContentValidationError: If content validation fails
            SchedulingError: If scheduling fails
        """
        pass

    @abstractmethod
    def get_audience_insights(
        self,
        platform_id: str,
        metrics: Optional[List[str]] = None,
        segment: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get audience insights from a connected social media platform.

        Args:
            platform_id: ID of the connected platform
            metrics: Optional list of specific metrics to retrieve
            segment: Optional audience segment parameters

        Returns:
            Dictionary containing audience insights data

        Raises:
            PlatformNotFoundError: If the platform ID is not found
            InvalidParameterError: If parameters are invalid
            NotSupportedError: If the platform doesn't support audience insights
        """
        pass
