"""
Channel Strategies module for the pAIssive Income project.
Provides templates for marketing strategies across different channels.
"""

from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import logging

from .errors import (
    ChannelStrategyError, ValidationError, handle_exception
)

# Set up logging
logger = logging.getLogger(__name__)


class ChannelStrategy:
    """
    Base class for all marketing channel strategies.
    This class provides a common interface for all channel-specific strategies.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        channel_type: str = "generic",
        target_audience: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        budget: Optional[float] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a channel strategy.

        Args:
            name: Name of the channel strategy
            description: Description of the channel strategy
            channel_type: Type of channel (e.g., "social_media", "content", "email")
            target_audience: The target audience for this strategy
            goals: List of marketing goals (e.g., "brand awareness", "lead generation")
            budget: Optional budget for this strategy
            timeline: Optional timeline for implementation
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.channel_type = channel_type
        self.target_audience = target_audience or {}
        self.goals = goals or []
        self.budget = budget
        self.timeline = timeline
        self.created_at = datetime.now().isoformat()
        self.tactics = []
        self.metrics = []
        self.resources = []

    def add_tactic(self, name: str, description: str, priority: str = "medium") -> None:
        """
        Add a tactic to the channel strategy.

        Args:
            name: Name of the tactic
            description: Description of the tactic
            priority: Priority level ("high", "medium", "low")
        """
        self.tactics.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "priority": priority
        })

    def add_metric(self, name: str, description: str, target: Optional[str] = None) -> None:
        """
        Add a metric to track for this channel strategy.

        Args:
            name: Name of the metric
            description: Description of the metric
            target: Optional target value for this metric
        """
        self.metrics.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "target": target
        })

    def add_resource(self, name: str, description: str, cost: Optional[float] = None) -> None:
        """
        Add a resource required for this channel strategy.

        Args:
            name: Name of the resource
            description: Description of the resource
            cost: Optional cost of the resource
        """
        self.resources.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "cost": cost
        })

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the channel strategy.

        Returns:
            Dictionary with strategy summary
        """
        return {
            "id": self.id,
            "name": self.name,
            "channel_type": self.channel_type,
            "goals": self.goals,
            "tactics_count": len(self.tactics),
            "metrics_count": len(self.metrics),
            "resources_count": len(self.resources),
            "budget": self.budget,
            "timeline": self.timeline,
            "created_at": self.created_at
        }

    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full channel strategy.

        Returns:
            Dictionary with complete strategy details
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "channel_type": self.channel_type,
            "target_audience": self.target_audience,
            "goals": self.goals,
            "tactics": self.tactics,
            "metrics": self.metrics,
            "resources": self.resources,
            "budget": self.budget,
            "timeline": self.timeline,
            "created_at": self.created_at
        }


class MarketingStrategy:
    """
    Base class for all marketing channel strategies.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a marketing strategy.

        Args:
            name: Name of the marketing strategy
            description: Description of the marketing strategy
            target_persona: The target user persona for this strategy
            goals: List of marketing goals (e.g., "brand awareness", "lead generation")
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.target_persona = target_persona or {}
        self.goals = goals or []
        self.budget = budget
        self.timeline = timeline
        self.created_at = datetime.now().isoformat()
        self.channel_type = "generic"
        self.tactics = []
        self.content_recommendations = []
        self.engagement_strategies = []
        self.metrics = []
        self.budget_allocation = {}

    def add_tactic(self, tactic: str, description: str, priority: str = "medium") -> None:
        """
        Add a tactic to the marketing strategy.

        Args:
            tactic: Name of the tactic
            description: Description of the tactic
            priority: Priority level ("high", "medium", "low")
        """
        self.tactics.append({
            "id": str(uuid.uuid4()),
            "name": tactic,
            "description": description,
            "priority": priority
        })

    def add_content_recommendation(self, content_type: str, description: str, frequency: str) -> None:
        """
        Add a content recommendation to the marketing strategy.

        Args:
            content_type: Type of content (e.g., "blog post", "video")
            description: Description of the content
            frequency: How often to publish this content
        """
        self.content_recommendations.append({
            "id": str(uuid.uuid4()),
            "content_type": content_type,
            "description": description,
            "frequency": frequency
        })

    def add_engagement_strategy(self, name: str, description: str) -> None:
        """
        Add an engagement strategy to the marketing strategy.

        Args:
            name: Name of the engagement strategy
            description: Description of the engagement strategy
        """
        self.engagement_strategies.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description
        })

    def add_metric(self, name: str, description: str, target: Optional[str] = None) -> None:
        """
        Add a metric to track for this marketing strategy.

        Args:
            name: Name of the metric
            description: Description of the metric
            target: Optional target value for this metric
        """
        self.metrics.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "target": target
        })

    def set_budget_allocation(self, allocations: Dict[str, str]) -> None:
        """
        Set budget allocations for different aspects of the strategy.

        Args:
            allocations: Dictionary mapping categories to percentage allocations
        """
        self.budget_allocation = allocations

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the marketing strategy.

        Returns:
            Dictionary with strategy summary
        """
        return {
            "id": self.id,
            "channel_type": self.channel_type,
            "target_persona": self.target_persona["name"],
            "goals": self.goals,
            "tactics_count": len(self.tactics),
            "content_recommendations_count": len(self.content_recommendations),
            "engagement_strategies_count": len(self.engagement_strategies),
            "metrics_count": len(self.metrics),
            "budget": self.budget,
            "timeline": self.timeline,
            "created_at": self.created_at
        }

    def create_plan(
        self,
        niche: str,
        target_audience: str,
        budget: float,
        timeline: str
    ) -> Dict[str, Any]:
        """
        Create a marketing plan for a specific niche and target audience.

        Args:
            niche: The niche market to target
            target_audience: Description of the target audience
            budget: Budget for the marketing plan
            timeline: Timeline for the marketing plan

        Returns:
            Marketing plan dictionary
        """
        # Create a unique ID for the plan
        plan_id = str(uuid.uuid4())

        # Generate default channels based on the niche
        channels = [
            {"name": "Content Marketing", "description": "Create valuable content to attract and engage the target audience"},
            {"name": "Social Media", "description": "Use social media to promote content and engage with the audience"},
            {"name": "Email Marketing", "description": "Build an email list and nurture leads through email campaigns"}
        ]

        # Generate default goals
        goals = [
            "Build brand awareness",
            "Generate leads",
            "Increase website traffic",
            "Establish authority in the niche"
        ]

        # Generate default metrics
        metrics = [
            {"name": "Website Traffic", "description": "Number of visitors to the website", "target": "1000 visitors per month"},
            {"name": "Lead Generation", "description": "Number of new leads generated", "target": "100 leads per month"},
            {"name": "Conversion Rate", "description": "Percentage of visitors who become leads", "target": "10%"},
            {"name": "Customer Acquisition Cost", "description": "Cost to acquire a new customer", "target": "$50 per customer"}
        ]

        # Create the plan
        plan = {
            "id": plan_id,
            "name": f"Marketing Plan for {niche}",
            "description": f"A marketing plan targeting {target_audience} in the {niche} niche",
            "niche": niche,
            "target_audience": target_audience,
            "budget": budget,
            "timeline": timeline,
            "channels": channels,
            "goals": goals,
            "metrics": metrics,
            "created_at": datetime.now().isoformat()
        }

        return plan

    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full marketing strategy.

        Returns:
            Dictionary with complete strategy details

        Raises:
            ChannelStrategyError: If there's an issue getting the strategy
        """
        try:
            strategy = {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "channel_type": self.channel_type,
                "target_persona": self.target_persona,
                "goals": self.goals,
                "tactics": self.tactics,
                "content_recommendations": self.content_recommendations,
                "engagement_strategies": self.engagement_strategies,
                "metrics": self.metrics,
                "budget": self.budget,
                "budget_allocation": self.budget_allocation,
                "timeline": self.timeline,
                "created_at": self.created_at
            }

            logger.info(f"Retrieved full strategy for: {self.name}")
            return strategy

        except Exception as e:
            # Handle unexpected errors
            error = handle_exception(
                e,
                error_class=ChannelStrategyError,
                message=f"Failed to get full strategy for: {self.name}",
                channel=self.channel_type,
                reraise=True,
                log_level=logging.ERROR
            )
            return {}  # This line won't be reached due to reraise=True


class ContentMarketingStrategy(MarketingStrategy):
    """
    Strategy for content marketing across different platforms.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        frequency: str = "weekly",
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a content marketing strategy.

        Args:
            name: Name of the content marketing strategy
            description: Description of the content marketing strategy
            target_persona: The target user persona for this strategy
            goals: List of marketing goals
            platforms: List of platforms for content distribution
            content_types: List of content types to create
            frequency: How often to publish content
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        super().__init__(name, description, target_persona, goals, budget, timeline)
        self.channel_type = "content_marketing"
        self.platforms = platforms or ["blog", "social_media", "email"]
        self.content_types = content_types or ["blog_posts", "videos", "infographics"]
        self.frequency = frequency

        # Add default tactics based on platforms
        self._add_default_tactics()

        # Add default content recommendations based on content types
        self._add_default_content_recommendations()

        # Add default engagement strategies
        self._add_default_engagement_strategies()

        # Add default metrics
        self._add_default_metrics()

        # Set default budget allocation
        self._set_default_budget_allocation()

    def _add_default_tactics(self) -> None:
        """Add default tactics based on selected platforms."""
        platform_tactics = {
            "blog": {
                "name": "SEO-Optimized Blog Content",
                "description": "Create SEO-optimized blog content targeting relevant keywords",
                "priority": "high"
            },
            "youtube": {
                "name": "YouTube Video Series",
                "description": "Create a series of educational videos for YouTube",
                "priority": "high"
            },
            "medium": {
                "name": "Medium Publication",
                "description": "Publish articles on Medium to reach a wider audience",
                "priority": "medium"
            },
            "podcast": {
                "name": "Podcast Episodes",
                "description": "Create podcast episodes discussing industry topics",
                "priority": "medium"
            },
            "linkedin": {
                "name": "LinkedIn Articles",
                "description": "Publish thought leadership articles on LinkedIn",
                "priority": "medium"
            }
        }

        for platform in self.platforms:
            if platform in platform_tactics:
                tactic = platform_tactics[platform]
                self.add_tactic(tactic["name"], tactic["description"], tactic["priority"])

    def _add_default_content_recommendations(self) -> None:
        """Add default content recommendations based on selected content types."""
        content_recommendations = {
            "tutorials": {
                "description": "Step-by-step tutorials solving specific problems",
                "frequency": self.frequency
            },
            "case studies": {
                "description": "Case studies showcasing successful implementations",
                "frequency": self.frequency
            },
            "how-to guides": {
                "description": "Comprehensive guides on specific topics",
                "frequency": self.frequency
            },
            "industry reports": {
                "description": "Reports on industry trends and insights",
                "frequency": "monthly"
            },
            "interviews": {
                "description": "Interviews with industry experts",
                "frequency": "monthly"
            }
        }

        for content_type in self.content_types:
            if content_type in content_recommendations:
                rec = content_recommendations[content_type]
                self.add_content_recommendation(content_type, rec["description"], rec["frequency"])

    def _add_default_engagement_strategies(self) -> None:
        """Add default engagement strategies."""
        self.add_engagement_strategy(
            "Comment Engagement",
            "Actively respond to comments on all content within 24 hours"
        )
        self.add_engagement_strategy(
            "Content Promotion",
            "Share content across social media platforms and relevant communities"
        )
        self.add_engagement_strategy(
            "Email Distribution",
            "Send new content to email subscribers with personalized notes"
        )

    def _add_default_metrics(self) -> None:
        """Add default metrics to track."""
        self.add_metric(
            "Traffic",
            "Website traffic from content marketing efforts",
            "Increase by 20% quarter-over-quarter"
        )
        self.add_metric(
            "Engagement",
            "Likes, comments, shares, and other engagement metrics",
            "Increase by 15% quarter-over-quarter"
        )
        self.add_metric(
            "Lead Generation",
            "Leads generated from content marketing efforts",
            "Generate 50 qualified leads per month"
        )
        self.add_metric(
            "Conversion Rate",
            "Percentage of content consumers who convert to customers",
            "2-5% conversion rate"
        )

    def _set_default_budget_allocation(self) -> None:
        """Set default budget allocation."""
        self.set_budget_allocation({
            "content_creation": "50%",
            "content_promotion": "20%",
            "tools_and_software": "15%",
            "freelancers_and_contractors": "15%"
        })

    def create_content_plan(
        self,
        niche: str,
        target_audience: str,
        content_types: List[str],
        frequency: str,
        distribution_channels: List[str]
    ) -> Dict[str, Any]:
        """
        Create a content marketing plan for a specific niche and target audience.

        Args:
            niche: The niche market to target
            target_audience: Description of the target audience
            content_types: Types of content to create
            frequency: How often to publish content
            distribution_channels: Channels to distribute content

        Returns:
            Content marketing plan dictionary
        """
        # Create a unique ID for the plan
        plan_id = str(uuid.uuid4())

        # Generate a content calendar
        content_calendar = []

        # Add sample content ideas based on content types
        for content_type in content_types:
            if content_type == "blog_posts":
                content_calendar.append({
                    "title": f"Top 10 {niche} Tips for {target_audience}",
                    "type": "blog_post",
                    "channel": "blog",
                    "publish_date": "Week 1"
                })
                content_calendar.append({
                    "title": f"How to Solve Common {niche} Problems",
                    "type": "blog_post",
                    "channel": "blog",
                    "publish_date": "Week 3"
                })
            elif content_type == "videos":
                content_calendar.append({
                    "title": f"{niche} Tutorial for {target_audience}",
                    "type": "video",
                    "channel": "youtube",
                    "publish_date": "Week 2"
                })
            elif content_type == "infographics":
                content_calendar.append({
                    "title": f"{niche} Statistics and Trends",
                    "type": "infographic",
                    "channel": "blog",
                    "publish_date": "Week 4"
                })

        # Create the plan
        plan = {
            "id": plan_id,
            "name": f"Content Marketing Plan for {niche}",
            "niche": niche,
            "target_audience": target_audience,
            "content_types": content_types,
            "frequency": frequency,
            "distribution_channels": distribution_channels,
            "content_calendar": content_calendar,
            "created_at": datetime.now().isoformat()
        }

        return plan

    def get_content_calendar(self, months: int = 3) -> List[Dict[str, Any]]:
        """
        Generate a content calendar for the specified number of months.

        Args:
            months: Number of months to generate calendar for

        Returns:
            List of content calendar items
        """
        calendar = []

        # Determine publishing frequency
        if self.frequency == "weekly":
            items_per_month = 4
        elif self.frequency == "bi-weekly":
            items_per_month = 2
        elif self.frequency == "monthly":
            items_per_month = 1
        elif self.frequency == "daily":
            items_per_month = 20  # Assuming 20 business days per month
        else:
            items_per_month = 2  # Default to bi-weekly

        # Generate calendar items
        for month in range(1, months + 1):
            for item in range(1, items_per_month + 1):
                # Rotate through content types
                content_type_index = (month * item - 1) % len(self.content_types)
                content_type = self.content_types[content_type_index]

                # Rotate through platforms
                platform_index = (month * item - 1) % len(self.platforms)
                platform = self.platforms[platform_index]

                calendar.append({
                    "id": str(uuid.uuid4()),
                    "month": month,
                    "week": item,
                    "content_type": content_type,
                    "platform": platform,
                    "title": f"{content_type.title()} for {self.target_persona['name']}s - Part {month * item}",
                    "description": f"Create a {content_type} about {self.target_persona['pain_points'][item % len(self.target_persona['pain_points'])]} for {platform}",
                    "status": "planned"
                })

        return calendar


class SocialMediaStrategy(MarketingStrategy):
    """
    Strategy for social media marketing across different platforms.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        post_frequency: str = "daily",
        content_mix: Optional[Dict[str, int]] = None,
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a social media marketing strategy.

        Args:
            name: Name of the social media strategy
            description: Description of the social media strategy
            target_persona: The target user persona for this strategy
            goals: List of marketing goals
            platforms: List of social media platforms
            post_frequency: How often to post on each platform
            content_mix: Dictionary mapping content types to percentage (e.g., {"educational": 40, "promotional": 20})
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        super().__init__(name, description, target_persona, goals, budget, timeline)
        self.channel_type = "social_media"
        self.platforms = platforms or ["instagram", "twitter", "facebook", "linkedin"]
        self.post_frequency = post_frequency
        self.content_mix = content_mix or {"educational": 40, "promotional": 20, "entertaining": 40}

        # Add default tactics based on platforms
        self._add_default_tactics()

        # Add default content recommendations
        self._add_default_content_recommendations()

        # Add default engagement strategies
        self._add_default_engagement_strategies()

        # Add default metrics
        self._add_default_metrics()

        # Set default budget allocation
        self._set_default_budget_allocation()

    def _add_default_tactics(self) -> None:
        """Add default tactics based on selected platforms."""
        platform_tactics = {
            "twitter": {
                "name": "Twitter Engagement",
                "description": "Regular posting and engagement on Twitter",
                "priority": "high"
            },
            "linkedin": {
                "name": "LinkedIn Networking",
                "description": "Professional networking and content sharing on LinkedIn",
                "priority": "high"
            },
            "facebook": {
                "name": "Facebook Community",
                "description": "Build and nurture a Facebook community or group",
                "priority": "medium"
            },
            "instagram": {
                "name": "Instagram Visual Content",
                "description": "Share visual content and stories on Instagram",
                "priority": "medium"
            },
            "tiktok": {
                "name": "TikTok Short-Form Videos",
                "description": "Create engaging short-form videos for TikTok",
                "priority": "medium"
            },
            "reddit": {
                "name": "Reddit Community Engagement",
                "description": "Participate in relevant subreddits and discussions",
                "priority": "medium"
            },
            "discord": {
                "name": "Discord Community",
                "description": "Build and manage a Discord server for your community",
                "priority": "medium"
            }
        }

        for platform in self.platforms:
            if platform in platform_tactics:
                tactic = platform_tactics[platform]
                self.add_tactic(tactic["name"], tactic["description"], tactic["priority"])

    def _add_default_content_recommendations(self) -> None:
        """Add default content recommendations based on content mix."""
        for content_type, percentage in self.content_mix.items():
            if content_type == "educational":
                self.add_content_recommendation(
                    "Educational Posts",
                    "Posts that educate your audience about topics related to your niche",
                    self.post_frequency
                )
            elif content_type == "promotional":
                self.add_content_recommendation(
                    "Promotional Posts",
                    "Posts that promote your product or service",
                    self.post_frequency
                )
            elif content_type == "entertaining":
                self.add_content_recommendation(
                    "Entertaining Posts",
                    "Fun, engaging posts that entertain your audience",
                    self.post_frequency
                )
            elif content_type == "inspirational":
                self.add_content_recommendation(
                    "Inspirational Posts",
                    "Posts that inspire your audience",
                    self.post_frequency
                )
            elif content_type == "user-generated":
                self.add_content_recommendation(
                    "User-Generated Content",
                    "Sharing and highlighting content created by your users",
                    self.post_frequency
                )

    def _add_default_engagement_strategies(self) -> None:
        """Add default engagement strategies."""
        self.add_engagement_strategy(
            "Consistent Posting",
            f"Post consistently according to your {self.post_frequency} schedule"
        )
        self.add_engagement_strategy(
            "Community Engagement",
            "Respond to comments and messages within 24 hours"
        )
        self.add_engagement_strategy(
            "Hashtag Strategy",
            "Use relevant hashtags to increase visibility"
        )
        self.add_engagement_strategy(
            "Cross-Promotion",
            "Cross-promote content across different social media platforms"
        )

    def _add_default_metrics(self) -> None:
        """Add default metrics to track."""
        self.add_metric(
            "Follower Growth",
            "Growth in followers across all platforms",
            "10% month-over-month growth"
        )
        self.add_metric(
            "Engagement Rate",
            "Likes, comments, shares, and other engagement metrics",
            "3-5% engagement rate"
        )
        self.add_metric(
            "Click-Through Rate",
            "Percentage of people who click on links in your posts",
            "1-3% click-through rate"
        )
        self.add_metric(
            "Conversion Rate",
            "Percentage of social media visitors who convert to customers",
            "1-2% conversion rate"
        )

    def _set_default_budget_allocation(self) -> None:
        """Set default budget allocation."""
        self.set_budget_allocation({
            "content_creation": "40%",
            "paid_promotion": "30%",
            "tools_and_software": "15%",
            "community_management": "15%"
        })

    def create_platform_plan(
        self,
        platform: str,
        target_audience: str,
        content_types: List[str],
        posting_frequency: str,
        engagement_tactics: List[str]
    ) -> Dict[str, Any]:
        """
        Create a social media platform plan.

        Args:
            platform: The social media platform
            target_audience: Description of the target audience
            content_types: Types of content to create
            posting_frequency: How often to post
            engagement_tactics: Tactics for engaging with the audience

        Returns:
            Platform plan dictionary
        """
        # Create a unique ID for the plan
        plan_id = str(uuid.uuid4())

        # Generate content ideas based on platform and content types
        content_ideas = []

        if platform == "instagram":
            content_ideas.extend([
                "Behind-the-scenes photos",
                "Product showcases",
                "User-generated content",
                "Instagram Stories polls",
                "IGTV tutorials"
            ])
        elif platform == "twitter":
            content_ideas.extend([
                "Industry news and updates",
                "Quick tips and tricks",
                "Polls and questions",
                "Retweets of relevant content",
                "Twitter chats"
            ])
        elif platform == "facebook":
            content_ideas.extend([
                "Longer-form content",
                "Live videos",
                "Community discussions",
                "Event promotions",
                "Facebook Groups engagement"
            ])
        elif platform == "linkedin":
            content_ideas.extend([
                "Industry insights",
                "Professional tips",
                "Company updates",
                "Thought leadership articles",
                "Job postings"
            ])
        else:
            content_ideas.extend([
                "Platform-specific content",
                "Engaging visuals",
                "Educational content",
                "Promotional content",
                "Interactive content"
            ])

        # Generate metrics based on platform
        metrics = []

        if platform == "instagram":
            metrics.extend([
                {"name": "Followers", "description": "Number of followers", "target": "1000 new followers per month"},
                {"name": "Engagement Rate", "description": "Likes and comments per post", "target": "3-5%"},
                {"name": "Story Views", "description": "Number of story views", "target": "500 views per story"}
            ])
        elif platform == "twitter":
            metrics.extend([
                {"name": "Followers", "description": "Number of followers", "target": "500 new followers per month"},
                {"name": "Retweets", "description": "Number of retweets", "target": "10 retweets per post"},
                {"name": "Click-through Rate", "description": "Percentage of clicks on links", "target": "1-2%"}
            ])
        else:
            metrics.extend([
                {"name": "Followers/Connections", "description": "Number of followers or connections", "target": "Increase by 10% per month"},
                {"name": "Engagement Rate", "description": "Interactions per post", "target": "2-4%"},
                {"name": "Reach", "description": "Number of people who see your content", "target": "Increase by 15% per month"}
            ])

        # Create the plan
        plan = {
            "id": plan_id,
            "platform": platform,
            "target_audience": target_audience,
            "content_types": content_types,
            "posting_frequency": posting_frequency,
            "engagement_tactics": engagement_tactics,
            "content_ideas": content_ideas,
            "metrics": metrics,
            "created_at": datetime.now().isoformat()
        }

        return plan

    def get_posting_schedule(self, weeks: int = 4) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a posting schedule for the specified number of weeks.

        Args:
            weeks: Number of weeks to generate schedule for

        Returns:
            Dictionary mapping platforms to lists of post ideas
        """
        schedule = {platform: [] for platform in self.platforms}

        # Determine posts per week based on frequency
        if self.post_frequency == "daily":
            posts_per_week = 7
        elif self.post_frequency == "weekdays":
            posts_per_week = 5
        elif self.post_frequency == "3x_week":
            posts_per_week = 3
        elif self.post_frequency == "2x_week":
            posts_per_week = 2
        elif self.post_frequency == "weekly":
            posts_per_week = 1
        else:
            posts_per_week = 3  # Default to 3x per week

        # Generate post ideas for each platform
        for platform in self.platforms:
            for week in range(1, weeks + 1):
                for post in range(1, posts_per_week + 1):
                    # Determine content type based on content mix
                    content_types = []
                    for content_type, percentage in self.content_mix.items():
                        content_types.extend([content_type] * percentage)

                    content_type_index = (week * post - 1) % len(content_types)
                    content_type = content_types[content_type_index]

                    # Generate post idea based on content type and platform
                    post_idea = self._generate_post_idea(platform, content_type, week, post)

                    schedule[platform].append({
                        "id": str(uuid.uuid4()),
                        "week": week,
                        "day": post,
                        "content_type": content_type,
                        "title": post_idea["title"],
                        "description": post_idea["description"],
                        "hashtags": post_idea["hashtags"],
                        "status": "planned"
                    })

        return schedule

    def _generate_post_idea(self, platform: str, content_type: str, week: int, post: int) -> Dict[str, Any]:
        """
        Generate a post idea based on platform and content type.

        Args:
            platform: Social media platform
            content_type: Type of content
            week: Week number
            post: Post number within the week

        Returns:
            Dictionary with post idea details
        """
        # Get a pain point to focus on
        pain_point_index = (week * post - 1) % len(self.target_persona["pain_points"])
        pain_point = self.target_persona["pain_points"][pain_point_index]

        # Generate post idea based on content type
        if content_type == "educational":
            return {
                "title": f"How to solve {pain_point}",
                "description": f"Educational post about solving {pain_point} for {self.target_persona['name']}s",
                "hashtags": ["#tips", "#howto", f"#{platform}tips"]
            }
        elif content_type == "promotional":
            return {
                "title": f"Introducing our solution for {pain_point}",
                "description": f"Promotional post highlighting how our product solves {pain_point}",
                "hashtags": ["#product", "#solution", "#productivity"]
            }
        elif content_type == "entertaining":
            return {
                "title": f"The struggle with {pain_point} is real",
                "description": f"Entertaining post about the challenges of {pain_point}",
                "hashtags": ["#relatable", "#thestruggleisreal", "#funny"]
            }
        elif content_type == "inspirational":
            return {
                "title": f"Overcoming {pain_point} - Success Story",
                "description": f"Inspirational post about overcoming {pain_point}",
                "hashtags": ["#success", "#motivation", "#overcome"]
            }
        elif content_type == "user-generated":
            return {
                "title": f"How our users are solving {pain_point}",
                "description": f"Sharing user-generated content about solving {pain_point}",
                "hashtags": ["#userstories", "#community", "#testimonial"]
            }
        else:
            return {
                "title": f"Tips for {pain_point}",
                "description": f"General post about {pain_point}",
                "hashtags": ["#tips", "#advice", f"#{platform}"]
            }


class EmailMarketingStrategy(MarketingStrategy):
    """
    Strategy for email marketing campaigns.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        email_types: Optional[List[str]] = None,
        frequency: str = "weekly",
        list_building_tactics: Optional[List[str]] = None,
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize an email marketing strategy.

        Args:
            name: Name of the email marketing strategy
            description: Description of the email marketing strategy
            target_persona: The target user persona for this strategy
            goals: List of marketing goals
            email_types: List of email types to send (e.g., "newsletter", "promotional")
            frequency: How often to send emails
            list_building_tactics: List of tactics for building your email list
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        super().__init__(name, description, target_persona, goals, budget, timeline)
        self.channel_type = "email_marketing"
        self.email_types = email_types or ["newsletter", "promotional", "onboarding", "retention"]
        self.frequency = frequency
        self.list_building_tactics = list_building_tactics or [
            "Lead magnets",
            "Content upgrades",
            "Webinars and events",
            "Social media promotion",
            "Website opt-in forms"
        ]

        # Add default tactics
        self._add_default_tactics()

        # Add default content recommendations
        self._add_default_content_recommendations()

        # Add default engagement strategies
        self._add_default_engagement_strategies()

        # Add default metrics
        self._add_default_metrics()

        # Set default budget allocation
        self._set_default_budget_allocation()

        # Add email sequences
        self.email_sequences = self._create_default_email_sequences()

    def _add_default_tactics(self) -> None:
        """Add default tactics."""
        for tactic in self.list_building_tactics:
            if tactic == "lead_magnet":
                self.add_tactic(
                    "Lead Magnet",
                    "Create a valuable lead magnet to attract subscribers",
                    "high"
                )
            elif tactic == "content_upgrade":
                self.add_tactic(
                    "Content Upgrades",
                    "Create content upgrades for your blog posts",
                    "medium"
                )
            elif tactic == "webinar":
                self.add_tactic(
                    "Webinar Registration",
                    "Host webinars and collect email addresses during registration",
                    "high"
                )
            elif tactic == "social_media":
                self.add_tactic(
                    "Social Media Promotion",
                    "Promote your newsletter on social media",
                    "medium"
                )
            elif tactic == "referral":
                self.add_tactic(
                    "Referral Program",
                    "Create a referral program to encourage subscribers to refer others",
                    "medium"
                )

    def _add_default_content_recommendations(self) -> None:
        """Add default content recommendations based on email types."""
        for email_type in self.email_types:
            if email_type == "newsletter":
                self.add_content_recommendation(
                    "Newsletter",
                    "Regular newsletter with valuable content for your subscribers",
                    self.frequency
                )
            elif email_type == "promotional":
                self.add_content_recommendation(
                    "Promotional Emails",
                    "Emails promoting your product or service",
                    "monthly"
                )
            elif email_type == "educational":
                self.add_content_recommendation(
                    "Educational Emails",
                    "Emails that educate your subscribers about topics related to your niche",
                    self.frequency
                )
            elif email_type == "onboarding":
                self.add_content_recommendation(
                    "Onboarding Sequence",
                    "Sequence of emails to onboard new subscribers or customers",
                    "triggered"
                )
            elif email_type == "re-engagement":
                self.add_content_recommendation(
                    "Re-engagement Campaign",
                    "Campaign to re-engage inactive subscribers",
                    "quarterly"
                )

    def _add_default_engagement_strategies(self) -> None:
        """Add default engagement strategies."""
        self.add_engagement_strategy(
            "Personalization",
            "Personalize emails with subscriber name and relevant content"
        )
        self.add_engagement_strategy(
            "Segmentation",
            "Segment your email list based on subscriber behavior and preferences"
        )
        self.add_engagement_strategy(
            "A/B Testing",
            "Test different subject lines, content, and CTAs to optimize performance"
        )
        self.add_engagement_strategy(
            "Clear CTAs",
            "Include clear and compelling calls-to-action in every email"
        )

    def _add_default_metrics(self) -> None:
        """Add default metrics to track."""
        self.add_metric(
            "Open Rate",
            "Percentage of subscribers who open your emails",
            "20-30% open rate"
        )
        self.add_metric(
            "Click-Through Rate",
            "Percentage of subscribers who click on links in your emails",
            "2-5% click-through rate"
        )
        self.add_metric(
            "Conversion Rate",
            "Percentage of email clicks that result in a desired action",
            "1-3% conversion rate"
        )
        self.add_metric(
            "List Growth Rate",
            "Rate at which your email list is growing",
            "5-10% month-over-month growth"
        )
        self.add_metric(
            "Unsubscribe Rate",
            "Percentage of subscribers who unsubscribe",
            "Less than 1% unsubscribe rate"
        )

    def _set_default_budget_allocation(self) -> None:
        """Set default budget allocation."""
        self.set_budget_allocation({
            "email_marketing_platform": "30%",
            "content_creation": "40%",
            "lead_generation": "20%",
            "testing_and_optimization": "10%"
        })

    def _create_default_email_sequences(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create default email sequences.

        Returns:
            Dictionary mapping sequence types to lists of emails
        """
        sequences = {}

        # Welcome sequence
        welcome_sequence = []
        welcome_sequence.append({
            "id": str(uuid.uuid4()),
            "sequence_position": 1,
            "days_after_trigger": 0,
            "subject": "Welcome to our community!",
            "content_summary": "Welcome email introducing your brand and what to expect",
            "cta": "Explore our resources"
        })
        welcome_sequence.append({
            "id": str(uuid.uuid4()),
            "sequence_position": 2,
            "days_after_trigger": 2,
            "subject": "How to solve common problems",
            "content_summary": "Educational content about solving common problems",
            "cta": "Learn more"
        })
        welcome_sequence.append({
            "id": str(uuid.uuid4()),
            "sequence_position": 3,
            "days_after_trigger": 5,
            "subject": "Our story and mission",
            "content_summary": "Share your brand story and mission to connect with subscribers",
            "cta": "Connect with us"
        })
        welcome_sequence.append({
            "id": str(uuid.uuid4()),
            "sequence_position": 4,
            "days_after_trigger": 7,
            "subject": "Exclusive resources for you",
            "content_summary": "Share exclusive resources and tools for subscribers",
            "cta": "Access resources"
        })
        sequences["welcome"] = welcome_sequence

        # Onboarding sequence
        if "onboarding" in self.email_types:
            onboarding_sequence = []
            onboarding_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 1,
                "days_after_trigger": 0,
                "subject": "Getting started with our product",
                "content_summary": "Introduction to the product and first steps",
                "cta": "Get started"
            })
            onboarding_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 2,
                "days_after_trigger": 2,
                "subject": "Key features you should know about",
                "content_summary": "Overview of key features and how to use them",
                "cta": "Explore features"
            })
            onboarding_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 3,
                "days_after_trigger": 4,
                "subject": "Tips and tricks for success",
                "content_summary": "Advanced tips and tricks for getting the most out of the product",
                "cta": "Learn more"
            })
            onboarding_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 4,
                "days_after_trigger": 7,
                "subject": "How are you doing?",
                "content_summary": "Check-in email to see how the user is doing and offer help",
                "cta": "Get help"
            })
            sequences["onboarding"] = onboarding_sequence

        # Promotional sequence
        if "promotional" in self.email_types:
            promotional_sequence = []
            promotional_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 1,
                "days_after_trigger": 0,
                "subject": "Introducing our new product",
                "content_summary": "Introduction to the new product and its benefits",
                "cta": "Learn more"
            })
            promotional_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 2,
                "days_after_trigger": 2,
                "subject": "How our product solves your problems",
                "content_summary": "Detailed explanation of how the product solves specific problems",
                "cta": "See how it works"
            })
            promotional_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 3,
                "days_after_trigger": 4,
                "subject": "What our customers are saying",
                "content_summary": "Testimonials and case studies from satisfied customers",
                "cta": "Read testimonials"
            })
            promotional_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 4,
                "days_after_trigger": 6,
                "subject": "Special offer ending soon",
                "content_summary": "Limited-time offer with clear deadline",
                "cta": "Get the offer"
            })
            promotional_sequence.append({
                "id": str(uuid.uuid4()),
                "sequence_position": 5,
                "days_after_trigger": 7,
                "subject": "Last chance: Offer ends today",
                "content_summary": "Final reminder about the offer ending",
                "cta": "Get the offer now"
            })
            sequences["promotional"] = promotional_sequence

        return sequences

    def create_campaign(
        self,
        name: str,
        target_audience: str,
        email_sequence: List[str],
        frequency: str,
        goals: List[str]
    ) -> Dict[str, Any]:
        """
        Create an email marketing campaign.

        Args:
            name: Name of the campaign
            target_audience: Description of the target audience
            email_sequence: Sequence of email types to send
            frequency: How often to send emails
            goals: Goals of the campaign

        Returns:
            Campaign dictionary
        """
        # Create a unique ID for the campaign
        campaign_id = str(uuid.uuid4())

        # Generate metrics based on goals
        metrics = []

        if "build_relationship" in goals:
            metrics.append({
                "name": "Open Rate",
                "description": "Percentage of subscribers who open your emails",
                "target": "25-30%"
            })
            metrics.append({
                "name": "Unsubscribe Rate",
                "description": "Percentage of subscribers who unsubscribe",
                "target": "Less than 1%"
            })

        if "introduce_product" in goals:
            metrics.append({
                "name": "Click-Through Rate",
                "description": "Percentage of subscribers who click on links in your emails",
                "target": "3-5%"
            })
            metrics.append({
                "name": "Website Visit Duration",
                "description": "How long subscribers stay on your website after clicking",
                "target": "2+ minutes"
            })

        if "convert" in goals:
            metrics.append({
                "name": "Conversion Rate",
                "description": "Percentage of email clicks that result in a conversion",
                "target": "2-3%"
            })
            metrics.append({
                "name": "Revenue per Email",
                "description": "Average revenue generated per email sent",
                "target": "$0.10-$0.20"
            })

        # Add default metrics if none were added
        if not metrics:
            metrics.extend([
                {
                    "name": "Open Rate",
                    "description": "Percentage of subscribers who open your emails",
                    "target": "20-25%"
                },
                {
                    "name": "Click-Through Rate",
                    "description": "Percentage of subscribers who click on links in your emails",
                    "target": "2-4%"
                },
                {
                    "name": "Conversion Rate",
                    "description": "Percentage of email clicks that result in a conversion",
                    "target": "1-2%"
                }
            ])

        # Create the campaign
        campaign = {
            "id": campaign_id,
            "name": name,
            "target_audience": target_audience,
            "email_sequence": email_sequence,
            "frequency": frequency,
            "goals": goals,
            "metrics": metrics,
            "created_at": datetime.now().isoformat()
        }

        return campaign

    def get_email_calendar(self, months: int = 3) -> List[Dict[str, Any]]:
        """
        Generate an email calendar for the specified number of months.

        Args:
            months: Number of months to generate calendar for

        Returns:
            List of email calendar items
        """
        calendar = []

        # Determine emails per month based on frequency
        if self.frequency == "weekly":
            emails_per_month = 4
        elif self.frequency == "bi-weekly":
            emails_per_month = 2
        elif self.frequency == "monthly":
            emails_per_month = 1
        elif self.frequency == "daily":
            emails_per_month = 20  # Assuming 20 business days per month
        else:
            emails_per_month = 2  # Default to bi-weekly

        # Generate calendar items
        for month in range(1, months + 1):
            for email in range(1, emails_per_month + 1):
                # Rotate through email types
                email_type_index = (month * email - 1) % len(self.email_types)
                email_type = self.email_types[email_type_index]

                # Generate email idea based on type
                if email_type == "newsletter":
                    subject = f"Newsletter #{month * email}: Tips and Updates"
                    content = "Monthly newsletter with tips, news, and resources"
                elif email_type == "promotional":
                    subject = "Special offer for our subscribers"
                    content = "Promotional email with special offer or discount"
                elif email_type == "educational":
                    subject = "How to solve common problems"
                    content = "Educational email about solving common problems"
                else:
                    subject = "Updates from our team"
                    content = "General update email"

                calendar.append({
                    "id": str(uuid.uuid4()),
                    "month": month,
                    "email_number": email,
                    "email_type": email_type,
                    "subject": subject,
                    "content_summary": content,
                    "status": "planned"
                })

        return calendar
