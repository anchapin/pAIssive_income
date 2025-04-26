"""
Channel Strategies module for the pAIssive Income project.
Provides templates for marketing strategies across different channels.
"""

from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime


class MarketingStrategy:
    """
    Base class for all marketing channel strategies.
    """

    def __init__(
        self,
        target_persona: Dict[str, Any],
        goals: List[str],
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a marketing strategy.

        Args:
            target_persona: The target user persona for this strategy
            goals: List of marketing goals (e.g., "brand awareness", "lead generation")
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        self.id = str(uuid.uuid4())
        self.target_persona = target_persona
        self.goals = goals
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

    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full marketing strategy.

        Returns:
            Dictionary with complete strategy details
        """
        return {
            "id": self.id,
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


class ContentMarketingStrategy(MarketingStrategy):
    """
    Strategy for content marketing across different platforms.
    """

    def __init__(
        self,
        target_persona: Dict[str, Any],
        goals: List[str],
        platforms: List[str],
        content_types: List[str],
        frequency: str,
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a content marketing strategy.

        Args:
            target_persona: The target user persona for this strategy
            goals: List of marketing goals
            platforms: List of platforms for content distribution
            content_types: List of content types to create
            frequency: How often to publish content
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        super().__init__(target_persona, goals, budget, timeline)
        self.channel_type = "content_marketing"
        self.platforms = platforms
        self.content_types = content_types
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
        target_persona: Dict[str, Any],
        goals: List[str],
        platforms: List[str],
        post_frequency: str,
        content_mix: Dict[str, int],
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize a social media marketing strategy.

        Args:
            target_persona: The target user persona for this strategy
            goals: List of marketing goals
            platforms: List of social media platforms
            post_frequency: How often to post on each platform
            content_mix: Dictionary mapping content types to percentage (e.g., {"educational": 40, "promotional": 20})
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        super().__init__(target_persona, goals, budget, timeline)
        self.channel_type = "social_media"
        self.platforms = platforms
        self.post_frequency = post_frequency
        self.content_mix = content_mix

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
        target_persona: Dict[str, Any],
        goals: List[str],
        email_types: List[str],
        frequency: str,
        list_building_tactics: List[str],
        budget: Optional[str] = None,
        timeline: Optional[str] = None,
    ):
        """
        Initialize an email marketing strategy.

        Args:
            target_persona: The target user persona for this strategy
            goals: List of marketing goals
            email_types: List of email types to send (e.g., "newsletter", "promotional")
            frequency: How often to send emails
            list_building_tactics: List of tactics for building your email list
            budget: Optional budget range for this strategy
            timeline: Optional timeline for implementation
        """
        super().__init__(target_persona, goals, budget, timeline)
        self.channel_type = "email_marketing"
        self.email_types = email_types
        self.frequency = frequency
        self.list_building_tactics = list_building_tactics

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
            "subject": f"Welcome to our {self.target_persona['name']} community!",
            "content_summary": "Welcome email introducing your brand and what to expect",
            "cta": "Explore our resources"
        })
        welcome_sequence.append({
            "id": str(uuid.uuid4()),
            "sequence_position": 2,
            "days_after_trigger": 2,
            "subject": f"How to solve {self.target_persona['pain_points'][0]}",
            "content_summary": f"Educational content about solving {self.target_persona['pain_points'][0]}",
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
                    subject = f"Newsletter #{month * email}: Tips for {self.target_persona['name']}s"
                    content = f"Monthly newsletter with tips, news, and resources for {self.target_persona['name']}s"
                elif email_type == "promotional":
                    subject = f"Special offer for {self.target_persona['name']}s"
                    content = "Promotional email with special offer or discount"
                elif email_type == "educational":
                    pain_point_index = (month * email - 1) % len(self.target_persona["pain_points"])
                    pain_point = self.target_persona["pain_points"][pain_point_index]
                    subject = f"How to solve {pain_point}"
                    content = f"Educational email about solving {pain_point}"
                else:
                    subject = f"Updates for {self.target_persona['name']}s"
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
