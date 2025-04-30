"""
Concrete implementation of the StrategyGenerator class.

This module provides a concrete implementation of the StrategyGenerator class
that implements all the required abstract methods from IMarketingStrategy.
"""

from typing import Dict, List, Any, Optional, Tuple
import uuid
from datetime import datetime
from marketing.strategy_generator import StrategyGenerator
from marketing.schemas import TargetAudienceSchema, BudgetSchema, BusinessType
from interfaces.agent_interfaces import IAgentTeam


class DefaultStrategyGenerator(StrategyGenerator):
    """
    Concrete implementation of the StrategyGenerator class.

    This class implements all the required abstract methods from IMarketingStrategy.
    """

    # Valid business types
    BUSINESS_TYPES = {
        "saas": {
            "name": "SaaS",
            "description": "Software as a Service",
            "typical_channels": [
                "content_marketing",
                "email_marketing",
                "social_media",
                "seo",
                "ppc",
            ],
            "typical_goals": [
                "lead_generation",
                "customer_acquisition",
                "retention",
                "brand_awareness",
            ],
        },
        "ecommerce": {
            "name": "E-commerce",
            "description": "Online retail",
            "typical_channels": [
                "social_media",
                "email_marketing",
                "ppc",
                "affiliate_marketing",
                "influencer_marketing",
            ],
            "typical_goals": [
                "sales",
                "conversion_rate",
                "average_order_value",
                "customer_acquisition",
            ],
        },
        "service": {
            "name": "Service",
            "description": "Professional services",
            "typical_channels": [
                "content_marketing",
                "email_marketing",
                "social_media",
                "seo",
                "referral_marketing",
            ],
            "typical_goals": [
                "lead_generation",
                "brand_awareness",
                "thought_leadership",
                "customer_acquisition",
            ],
        },
        "content_creator": {
            "name": "Content Creator",
            "description": "Content creation and monetization",
            "typical_channels": [
                "social_media",
                "content_marketing",
                "email_marketing",
                "influencer_marketing",
            ],
            "typical_goals": [
                "audience_growth",
                "engagement",
                "monetization",
                "brand_awareness",
            ],
        },
        "local_business": {
            "name": "Local Business",
            "description": "Brick and mortar business",
            "typical_channels": [
                "local_seo",
                "social_media",
                "email_marketing",
                "direct_mail",
                "events",
            ],
            "typical_goals": [
                "foot_traffic",
                "local_awareness",
                "customer_acquisition",
                "loyalty",
            ],
        },
    }

    # Valid marketing goals
    MARKETING_GOALS = {
        "brand_awareness": {
            "name": "Brand Awareness",
            "description": "Increase awareness of the brand",
            "recommended_channels": [
                "social_media",
                "content_marketing",
                "influencer_marketing",
                "pr",
            ],
            "typical_metrics": [
                "reach",
                "impressions",
                "brand_mentions",
                "social_media_followers",
            ],
        },
        "lead_generation": {
            "name": "Lead Generation",
            "description": "Generate new leads",
            "recommended_channels": [
                "content_marketing",
                "email_marketing",
                "ppc",
                "social_media",
            ],
            "typical_metrics": [
                "leads_generated",
                "conversion_rate",
                "cost_per_lead",
                "lead_quality",
            ],
        },
        "customer_acquisition": {
            "name": "Customer Acquisition",
            "description": "Acquire new customers",
            "recommended_channels": [
                "ppc",
                "email_marketing",
                "content_marketing",
                "social_media",
            ],
            "typical_metrics": [
                "new_customers",
                "customer_acquisition_cost",
                "conversion_rate",
            ],
        },
        "retention": {
            "name": "Retention",
            "description": "Retain existing customers",
            "recommended_channels": [
                "email_marketing",
                "content_marketing",
                "social_media",
                "customer_service",
            ],
            "typical_metrics": [
                "retention_rate",
                "churn_rate",
                "customer_lifetime_value",
            ],
        },
        "sales": {
            "name": "Sales",
            "description": "Increase sales",
            "recommended_channels": [
                "ppc",
                "email_marketing",
                "social_media",
                "affiliate_marketing",
            ],
            "typical_metrics": [
                "revenue",
                "conversion_rate",
                "average_order_value",
                "return_on_ad_spend",
            ],
        },
        "engagement": {
            "name": "Engagement",
            "description": "Increase engagement with the brand",
            "recommended_channels": [
                "social_media",
                "content_marketing",
                "email_marketing",
                "events",
            ],
            "typical_metrics": [
                "engagement_rate",
                "time_on_site",
                "comments",
                "shares",
            ],
        },
        "thought_leadership": {
            "name": "Thought Leadership",
            "description": "Establish thought leadership in the industry",
            "recommended_channels": [
                "content_marketing",
                "social_media",
                "pr",
                "speaking_engagements",
            ],
            "typical_metrics": [
                "content_shares",
                "speaking_engagements",
                "media_mentions",
                "industry_recognition",
            ],
        },
        "audience_growth": {
            "name": "Audience Growth",
            "description": "Grow the audience",
            "recommended_channels": [
                "social_media",
                "content_marketing",
                "influencer_marketing",
                "collaborations",
            ],
            "typical_metrics": [
                "followers",
                "subscribers",
                "audience_growth_rate",
                "reach",
            ],
        },
        "monetization": {
            "name": "Monetization",
            "description": "Monetize content or audience",
            "recommended_channels": [
                "affiliate_marketing",
                "sponsored_content",
                "product_sales",
                "memberships",
            ],
            "typical_metrics": [
                "revenue",
                "revenue_per_user",
                "conversion_rate",
                "average_order_value",
            ],
        },
    }

    # Marketing channels data
    MARKETING_CHANNELS = {
        "content_marketing": {
            "name": "Content Marketing",
            "description": "Creating and sharing valuable content to attract and engage a target audience",
            "formats": [
                "blog_posts",
                "videos",
                "podcasts",
                "infographics",
                "ebooks",
                "webinars",
            ],
            "metrics": [
                "traffic",
                "engagement",
                "leads",
                "conversions",
                "time_on_page",
            ],
            "difficulty": "medium",
            "time_investment": "high",
            "cost_range": "low_to_medium",
            "best_for": ["brand_awareness", "lead_generation", "thought_leadership"],
        },
        "social_media": {
            "name": "Social Media Marketing",
            "description": "Using social media platforms to connect with the audience and build the brand",
            "formats": [
                "posts",
                "stories",
                "reels",
                "live_videos",
                "groups",
                "communities",
            ],
            "metrics": ["followers", "engagement", "reach", "clicks", "conversions"],
            "difficulty": "medium",
            "time_investment": "high",
            "cost_range": "low_to_high",
            "best_for": ["brand_awareness", "engagement", "community_building"],
        },
        "email_marketing": {
            "name": "Email Marketing",
            "description": "Sending targeted emails to prospects and customers",
            "formats": [
                "newsletters",
                "promotional_emails",
                "automated_sequences",
                "transactional_emails",
            ],
            "metrics": [
                "open_rate",
                "click_rate",
                "conversion_rate",
                "unsubscribe_rate",
                "revenue",
            ],
            "difficulty": "medium",
            "time_investment": "medium",
            "cost_range": "low_to_medium",
            "best_for": ["lead_nurturing", "customer_retention", "sales"],
        },
        "seo": {
            "name": "Search Engine Optimization",
            "description": "Optimizing website content to rank higher in search engine results",
            "formats": ["on_page_seo", "off_page_seo", "technical_seo", "local_seo"],
            "metrics": [
                "rankings",
                "organic_traffic",
                "backlinks",
                "domain_authority",
                "conversions",
            ],
            "difficulty": "high",
            "time_investment": "high",
            "cost_range": "medium_to_high",
            "best_for": ["organic_traffic", "brand_visibility", "lead_generation"],
        },
        "ppc": {
            "name": "Pay-Per-Click Advertising",
            "description": "Paying for ads on search engines and other platforms",
            "formats": ["search_ads", "display_ads", "social_media_ads", "remarketing"],
            "metrics": ["clicks", "impressions", "ctr", "cpc", "conversions", "roas"],
            "difficulty": "medium",
            "time_investment": "medium",
            "cost_range": "medium_to_high",
            "best_for": ["immediate_traffic", "lead_generation", "sales"],
        },
        "influencer_marketing": {
            "name": "Influencer Marketing",
            "description": "Partnering with influencers to promote products or services",
            "formats": ["sponsored_posts", "reviews", "collaborations", "takeovers"],
            "metrics": [
                "reach",
                "engagement",
                "conversions",
                "brand_mentions",
                "user_generated_content",
            ],
            "difficulty": "medium",
            "time_investment": "medium",
            "cost_range": "medium_to_high",
            "best_for": ["brand_awareness", "credibility", "reaching_new_audiences"],
        },
        "affiliate_marketing": {
            "name": "Affiliate Marketing",
            "description": "Partnering with affiliates who promote products for a commission",
            "formats": ["affiliate_links", "coupon_codes", "co_branded_content"],
            "metrics": ["clicks", "conversions", "revenue", "commission_paid", "roas"],
            "difficulty": "medium",
            "time_investment": "medium",
            "cost_range": "low_to_medium",
            "best_for": [
                "sales",
                "reaching_new_audiences",
                "performance_based_marketing",
            ],
        },
        "pr": {
            "name": "Public Relations",
            "description": "Managing the spread of information between an organization and the public",
            "formats": ["press_releases", "media_outreach", "interviews", "events"],
            "metrics": [
                "media_mentions",
                "reach",
                "sentiment",
                "website_traffic",
                "backlinks",
            ],
            "difficulty": "high",
            "time_investment": "high",
            "cost_range": "medium_to_high",
            "best_for": ["brand_awareness", "credibility", "reputation_management"],
        },
        "events": {
            "name": "Event Marketing",
            "description": "Creating or participating in events to promote products or services",
            "formats": [
                "conferences",
                "webinars",
                "workshops",
                "trade_shows",
                "meetups",
            ],
            "metrics": ["attendees", "leads", "engagement", "conversions", "feedback"],
            "difficulty": "high",
            "time_investment": "high",
            "cost_range": "medium_to_high",
            "best_for": ["networking", "lead_generation", "brand_experience"],
        },
        "direct_mail": {
            "name": "Direct Mail",
            "description": "Sending physical mail to prospects and customers",
            "formats": ["postcards", "letters", "catalogs", "brochures", "samples"],
            "metrics": [
                "response_rate",
                "conversion_rate",
                "cost_per_acquisition",
                "roi",
            ],
            "difficulty": "medium",
            "time_investment": "medium",
            "cost_range": "medium_to_high",
            "best_for": [
                "local_businesses",
                "high_value_products",
                "personalized_outreach",
            ],
        },
    }

    def __init__(
        self,
        business_type: Optional[str] = None,
        business_size: Optional[str] = None,
        goals: Optional[List[str]] = None,
        target_audience: Optional[TargetAudienceSchema] = None,
        budget: Optional[BudgetSchema] = None,
        agent_team: Optional[IAgentTeam] = None,
        name: str = "Default Marketing Strategy",
        description: str = "A comprehensive marketing strategy for your business",
        channel_type: str = "multi_channel",
        timeframe: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize a DefaultStrategyGenerator.

        Args:
            business_type: Type of business (e.g., "SaaS", "E-commerce")
            business_size: Size of business (e.g., "Startup", "Small", "Medium", "Enterprise")
            goals: List of marketing goals
            target_audience: Target audience details
            budget: Budget details
            agent_team: Optional agent team for strategy generation assistance
            name: Name of the strategy
            description: Description of the strategy
            channel_type: Type of channel (e.g., "multi_channel", "social_media", "content")
            timeframe: Optional timeframe for the strategy
            kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(
            business_type=business_type,
            business_size=business_size,
            goals=goals,
            target_audience=target_audience,
            budget=budget,
            agent_team=agent_team,
            **kwargs,
        )
        self._name = name
        self._description = description
        self._channel_type = channel_type

    @property
    def name(self) -> str:
        """Get the strategy name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the strategy description."""
        return self._description

    @property
    def channel_type(self) -> str:
        """Get the channel type."""
        return self._channel_type

    def create_strategy(
        self, target_persona: Dict[str, Any], goals: List[str]
    ) -> Dict[str, Any]:
        """
        Create a marketing strategy.

        Args:
            target_persona: Target user persona
            goals: List of marketing goals

        Returns:
            Marketing strategy dictionary
        """
        # Update the target audience and goals
        if target_persona:
            self.target_audience = TargetAudienceSchema(**target_persona)

        if goals:
            self.goals = goals

        # Generate the strategy
        strategy = self.generate_strategy()

        # Convert to dictionary
        return strategy.model_dump()

    def get_tactics(self) -> List[Dict[str, Any]]:
        """
        Get marketing tactics.

        Returns:
            List of marketing tactic dictionaries
        """
        # If we have strategies, return tactics from the most recent one
        if self.strategies:
            latest_strategy = self.strategies[-1]
            return [tactic.model_dump() for tactic in latest_strategy.tactics]

        # Otherwise, generate a new strategy and return its tactics
        strategy = self.generate_strategy()
        return [tactic.model_dump() for tactic in strategy.tactics]

    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get marketing metrics.

        Returns:
            List of marketing metric dictionaries
        """
        # If we have strategies, return metrics from the most recent one
        if self.strategies:
            latest_strategy = self.strategies[-1]
            return [metric.model_dump() for metric in latest_strategy.metrics]

        # Otherwise, generate a new strategy and return its metrics
        strategy = self.generate_strategy()
        return [metric.model_dump() for metric in strategy.metrics]

    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full marketing strategy.

        Returns:
            Dictionary with complete strategy details
        """
        # If we have strategies, return the most recent one
        if self.strategies:
            latest_strategy = self.strategies[-1]
            return latest_strategy.model_dump()

        # Otherwise, generate a new strategy and return it
        strategy = self.generate_strategy()
        return strategy.model_dump()

    def validate_business_type(self) -> Tuple[bool, List[str]]:
        """
        Validate the business type.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if business type is set
        if not self.business_type:
            errors.append("Business type is required")
            return False, errors

        # Check if business type is valid
        if self.business_type.lower() not in self.BUSINESS_TYPES:
            errors.append(
                f"Invalid business type: {self.business_type}. Must be one of: {', '.join(self.BUSINESS_TYPES.keys())}"
            )
            return False, errors

        return True, errors

    def validate_goals(self) -> Tuple[bool, List[str]]:
        """
        Validate the marketing goals.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if goals are set
        if not self.goals:
            errors.append("At least one marketing goal is required")
            return False, errors

        # Check if each goal is valid
        invalid_goals = [
            goal for goal in self.goals if goal.lower() not in self.MARKETING_GOALS
        ]
        if invalid_goals:
            errors.append(
                f"Invalid goals: {', '.join(invalid_goals)}. Valid goals are: {', '.join(self.MARKETING_GOALS.keys())}"
            )
            return False, errors

        return True, errors

    def analyze_channels(self) -> Dict[str, Any]:
        """
        Analyze marketing channels for the business.

        Returns:
            Dictionary with channel analysis results
        """
        # Get channel effectiveness analysis
        channel_effectiveness = self._analyze_channel_effectiveness()

        # Get audience fit analysis
        audience_fit = self._analyze_channel_audience_fit()

        # Get goal alignment analysis
        goal_alignment = self._analyze_channel_goal_alignment()

        # Get budget fit analysis
        budget_fit = self._analyze_channel_budget_fit()

        # Get ROI analysis
        roi_analysis = self._analyze_channel_roi()

        # Prioritize channels
        prioritized_channels = self._prioritize_channels(
            channel_effectiveness,
            audience_fit,
            goal_alignment,
            budget_fit,
            roi_analysis,
        )

        # Generate channel recommendations
        channel_recommendations = self._generate_channel_recommendations(
            prioritized_channels
        )

        # Return the complete analysis
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "channel_effectiveness": channel_effectiveness,
            "audience_fit": audience_fit,
            "goal_alignment": goal_alignment,
            "budget_fit": budget_fit,
            "roi_analysis": roi_analysis,
            "prioritized_channels": prioritized_channels,
            "channel_recommendations": channel_recommendations,
        }

    def _analyze_channel_effectiveness(self) -> Dict[str, Any]:
        """
        Analyze the effectiveness of marketing channels for the business.

        Returns:
            Dictionary with channel effectiveness analysis
        """
        effectiveness_scores = {}

        for channel, channel_data in self.MARKETING_CHANNELS.items():
            # Calculate base score
            base_score = self._calculate_channel_base_score(channel)

            # Calculate business alignment
            business_alignment = self._calculate_channel_business_alignment(channel)

            # Calculate goal alignment
            goal_alignment = self._calculate_channel_goal_alignment_score(channel)

            # Calculate difficulty adjustment
            difficulty_adjustment = self._calculate_difficulty_adjustment(
                channel_data.get("difficulty", "medium")
            )

            # Calculate time adjustment
            time_adjustment = self._calculate_time_adjustment(
                channel_data.get("time_investment", "medium")
            )

            # Calculate metrics effectiveness
            metrics_effectiveness = self._analyze_channel_metrics_effectiveness(channel)

            # Calculate overall score
            overall_score = (
                base_score * 0.2
                + business_alignment * 0.3
                + goal_alignment * 0.3
                + difficulty_adjustment * 0.1
                + time_adjustment * 0.1
            ) * metrics_effectiveness["avg_effectiveness"]

            # Determine effectiveness level
            if overall_score >= 0.7:
                effectiveness_level = "high"
            elif overall_score >= 0.4:
                effectiveness_level = "medium"
            else:
                effectiveness_level = "low"

            # Store the results
            effectiveness_scores[channel] = {
                "channel": channel_data["name"],
                "description": channel_data["description"],
                "base_score": base_score,
                "business_alignment": business_alignment,
                "goal_alignment": goal_alignment,
                "difficulty_adjustment": difficulty_adjustment,
                "time_adjustment": time_adjustment,
                "metrics_effectiveness": metrics_effectiveness["avg_effectiveness"],
                "overall_score": overall_score,
                "effectiveness_level": effectiveness_level,
                "best_for": channel_data.get("best_for", []),
                "formats": channel_data.get("formats", []),
                "metrics": channel_data.get("metrics", []),
            }

        # Sort channels by overall score
        sorted_channels = sorted(
            [{"channel": k, **v} for k, v in effectiveness_scores.items()],
            key=lambda x: x["overall_score"],
            reverse=True,
        )

        # Get top channels
        top_channels = [channel["channel"] for channel in sorted_channels[:5]]

        # Get highly effective channels
        highly_effective = [
            channel
            for channel, data in effectiveness_scores.items()
            if data["effectiveness_level"] == "high"
        ]

        # Get moderately effective channels
        moderately_effective = [
            channel
            for channel, data in effectiveness_scores.items()
            if data["effectiveness_level"] == "medium"
        ]

        return {
            "effectiveness_scores": effectiveness_scores,
            "sorted_channels": sorted_channels,
            "top_channels": top_channels,
            "highly_effective": highly_effective,
            "moderately_effective": moderately_effective,
        }

    def _analyze_channel_metrics_effectiveness(self, channel: str) -> Dict[str, Any]:
        """
        Analyze the effectiveness of a channel for different metrics.

        Args:
            channel: The channel to analyze

        Returns:
            Dictionary with metrics effectiveness analysis
        """
        # Define base metrics
        metrics = {
            "awareness": 0.7,
            "engagement": 0.6,
            "conversion": 0.5,
            "retention": 0.4,
            "reach": 0.8,
            "cost_efficiency": 0.6,
        }

        # Adjust metrics based on business type
        metrics = self._adjust_metrics_for_business_type(metrics, channel)

        # Adjust metrics based on goals
        metrics = self._adjust_metrics_for_goals(metrics, channel)

        # Calculate average effectiveness
        avg_effectiveness = sum(metrics.values()) / len(metrics)

        # Identify top metrics
        top_metrics = [metric for metric, value in metrics.items() if value >= 0.7]

        # Identify weak metrics
        weak_metrics = [metric for metric, value in metrics.items() if value < 0.5]

        return {
            "metrics": metrics,
            "avg_effectiveness": avg_effectiveness,
            "top_metrics": top_metrics,
            "weak_metrics": weak_metrics,
        }

    def _calculate_channel_base_score(self, channel: str) -> float:
        """
        Calculate the base score for a channel.

        Args:
            channel: The channel to calculate the base score for

        Returns:
            Base score between 0 and 1
        """
        # For simplicity, return a default score
        # In a real implementation, this would be more sophisticated
        return 0.7

    def _calculate_channel_business_alignment(self, channel: str) -> float:
        """
        Calculate how well a channel aligns with the business type.

        Args:
            channel: The channel to calculate alignment for

        Returns:
            Alignment score between 0 and 1
        """
        if not self.business_type:
            return 0.5

        business_type_data = self.BUSINESS_TYPES.get(self.business_type.lower(), {})
        typical_channels = business_type_data.get("typical_channels", [])

        if channel in typical_channels:
            return 1.0

        # If not a typical channel, return a lower score
        return 0.5

    def _calculate_channel_goal_alignment_score(self, channel: str) -> float:
        """
        Calculate how well a channel aligns with the marketing goals.

        Args:
            channel: The channel to calculate alignment for

        Returns:
            Alignment score between 0 and 1
        """
        if not self.goals:
            return 0.5

        alignment_scores = []

        for goal in self.goals:
            goal_data = self.MARKETING_GOALS.get(goal.lower(), {})
            recommended_channels = goal_data.get("recommended_channels", [])

            if channel in recommended_channels:
                alignment_scores.append(1.0)
            else:
                alignment_scores.append(0.3)

        # Average the alignment scores
        return (
            sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.5
        )

    def _calculate_difficulty_adjustment(self, difficulty: str) -> float:
        """
        Calculate an adjustment factor based on channel difficulty.

        Args:
            difficulty: The difficulty level of the channel

        Returns:
            Adjustment factor between 0 and 1
        """
        if difficulty == "low":
            return 1.0
        elif difficulty == "medium":
            return 0.8
        elif difficulty == "high":
            return 0.6
        else:
            return 0.8  # Default to medium

    def _calculate_time_adjustment(self, time_investment: str) -> float:
        """
        Calculate an adjustment factor based on channel time investment.

        Args:
            time_investment: The time investment level of the channel

        Returns:
            Adjustment factor between 0 and 1
        """
        if time_investment == "low":
            return 1.0
        elif time_investment == "medium":
            return 0.8
        elif time_investment == "high":
            return 0.6
        else:
            return 0.8  # Default to medium

    def _adjust_metrics_for_business_type(
        self, metrics: Dict[str, float], channel: str
    ) -> Dict[str, float]:
        """
        Adjust metrics based on business type.

        Args:
            metrics: The metrics to adjust
            channel: The channel the metrics are for

        Returns:
            Adjusted metrics
        """
        if not self.business_type:
            return metrics

        adjusted_metrics = metrics.copy()

        # Adjust metrics based on business type
        if self.business_type.lower() == "saas":
            if channel == "content_marketing":
                adjusted_metrics["conversion"] *= 1.2
                adjusted_metrics["retention"] *= 1.2
            elif channel == "email_marketing":
                adjusted_metrics["retention"] *= 1.3
                adjusted_metrics["engagement"] *= 1.2
        elif self.business_type.lower() == "ecommerce":
            if channel == "social_media":
                adjusted_metrics["awareness"] *= 1.2
                adjusted_metrics["reach"] *= 1.2
            elif channel == "ppc":
                adjusted_metrics["conversion"] *= 1.3
                adjusted_metrics["cost_efficiency"] *= 1.1

        # Ensure no metric exceeds 1.0
        for metric in adjusted_metrics:
            adjusted_metrics[metric] = min(adjusted_metrics[metric], 1.0)

        return adjusted_metrics

    def _adjust_metrics_for_goals(
        self, metrics: Dict[str, float], channel: str
    ) -> Dict[str, float]:
        """
        Adjust metrics based on marketing goals.

        Args:
            metrics: The metrics to adjust
            channel: The channel the metrics are for

        Returns:
            Adjusted metrics
        """
        if not self.goals:
            return metrics

        adjusted_metrics = metrics.copy()

        # Adjust metrics based on goals
        for goal in self.goals:
            if goal.lower() == "brand_awareness":
                adjusted_metrics["awareness"] *= 1.2
                adjusted_metrics["reach"] *= 1.2
            elif goal.lower() == "lead_generation":
                adjusted_metrics["conversion"] *= 1.2
                adjusted_metrics["cost_efficiency"] *= 1.1
            elif goal.lower() == "customer_acquisition":
                adjusted_metrics["conversion"] *= 1.3
                adjusted_metrics["cost_efficiency"] *= 1.2
            elif goal.lower() == "retention":
                adjusted_metrics["retention"] *= 1.3
                adjusted_metrics["engagement"] *= 1.2

        # Ensure no metric exceeds 1.0
        for metric in adjusted_metrics:
            adjusted_metrics[metric] = min(adjusted_metrics[metric], 1.0)

        return adjusted_metrics

    def _analyze_channel_audience_fit(self) -> Dict[str, Any]:
        """
        Analyze how well each channel fits the target audience.

        Returns:
            Dictionary with audience fit analysis
        """
        audience_fit_scores = {}

        for channel, channel_data in self.MARKETING_CHANNELS.items():
            # Calculate demographic fit
            demographic_fit = 0.7  # Default value

            # Calculate interest fit
            interest_fit = 0.7  # Default value

            # Calculate behavior fit
            behavior_fit = 0.7  # Default value

            # Calculate overall fit
            overall_fit = (demographic_fit + interest_fit + behavior_fit) / 3

            # Determine fit level
            if overall_fit >= 0.7:
                fit_level = "high"
            elif overall_fit >= 0.4:
                fit_level = "medium"
            else:
                fit_level = "low"

            # Store the results
            audience_fit_scores[channel] = {
                "channel": channel_data["name"],
                "demographic_fit": demographic_fit,
                "interest_fit": interest_fit,
                "behavior_fit": behavior_fit,
                "overall_fit": overall_fit,
                "fit_level": fit_level,
            }

        # Sort channels by overall fit
        sorted_channels = sorted(
            [{"channel": k, **v} for k, v in audience_fit_scores.items()],
            key=lambda x: x["overall_fit"],
            reverse=True,
        )

        # Get top channels
        top_channels = [channel["channel"] for channel in sorted_channels[:5]]

        # Get high fit channels
        high_fit_channels = [
            channel
            for channel, data in audience_fit_scores.items()
            if data["fit_level"] == "high"
        ]

        # Get medium fit channels
        medium_fit_channels = [
            channel
            for channel, data in audience_fit_scores.items()
            if data["fit_level"] == "medium"
        ]

        return {
            "audience_fit_scores": audience_fit_scores,
            "sorted_channels": sorted_channels,
            "top_channels": top_channels,
            "high_fit_channels": high_fit_channels,
            "medium_fit_channels": medium_fit_channels,
        }

    def _analyze_channel_goal_alignment(self) -> Dict[str, Any]:
        """
        Analyze how well each channel aligns with the marketing goals.

        Returns:
            Dictionary with goal alignment analysis
        """
        goal_alignment_scores = {}

        for goal in self.goals:
            goal_data = self.MARKETING_GOALS.get(goal.lower(), {})
            recommended_channels = goal_data.get("recommended_channels", [])

            channel_scores = {}

            for channel, channel_data in self.MARKETING_CHANNELS.items():
                # Calculate alignment score
                if channel in recommended_channels:
                    alignment_score = 1.0
                else:
                    alignment_score = 0.3

                # Determine alignment level
                if alignment_score >= 0.7:
                    alignment_level = "high"
                elif alignment_score >= 0.4:
                    alignment_level = "medium"
                else:
                    alignment_level = "low"

                # Store the results
                channel_scores[channel] = {
                    "channel": channel_data["name"],
                    "alignment_score": alignment_score,
                    "alignment_level": alignment_level,
                }

            # Sort channels by alignment score
            sorted_channels = sorted(
                [{"channel": k, **v} for k, v in channel_scores.items()],
                key=lambda x: x["alignment_score"],
                reverse=True,
            )

            # Get top channels
            top_channels = [channel["channel"] for channel in sorted_channels[:5]]

            # Store the results for this goal
            goal_alignment_scores[goal] = {
                "goal": goal_data.get("name", goal),
                "description": goal_data.get("description", ""),
                "channel_scores": channel_scores,
                "top_channels": top_channels,
            }

        # Calculate overall alignment for each channel
        overall_alignment = {}

        for channel, channel_data in self.MARKETING_CHANNELS.items():
            goal_scores = {}

            for goal, goal_score in goal_alignment_scores.items():
                goal_scores[goal] = goal_score["channel_scores"][channel][
                    "alignment_score"
                ]

            # Calculate average alignment
            avg_alignment = (
                sum(goal_scores.values()) / len(goal_scores) if goal_scores else 0
            )

            # Determine alignment level
            if avg_alignment >= 0.7:
                alignment_level = "high"
            elif avg_alignment >= 0.4:
                alignment_level = "medium"
            else:
                alignment_level = "low"

            # Store the results
            overall_alignment[channel] = {
                "channel": channel_data["name"],
                "avg_alignment": avg_alignment,
                "goal_scores": goal_scores,
                "alignment_level": alignment_level,
            }

        # Sort channels by average alignment
        sorted_channels = sorted(
            [{"channel": k, **v} for k, v in overall_alignment.items()],
            key=lambda x: x["avg_alignment"],
            reverse=True,
        )

        # Get top channels
        top_channels = [channel["channel"] for channel in sorted_channels[:5]]

        return {
            "goal_alignment_scores": goal_alignment_scores,
            "overall_alignment": overall_alignment,
            "top_channels_overall": top_channels,
        }

    def _analyze_channel_budget_fit(self) -> Dict[str, Any]:
        """
        Analyze how well each channel fits the budget.

        Returns:
            Dictionary with budget fit analysis
        """
        budget_fit_scores = {}

        # Get total budget
        if self.budget:
            if isinstance(self.budget, dict):
                total_budget = self.budget.get("amount", 5000)
            else:
                total_budget = getattr(self.budget, "total_amount", 5000)
        else:
            total_budget = 5000

        for channel, channel_data in self.MARKETING_CHANNELS.items():
            # Estimate channel cost
            cost_range = channel_data.get("cost_range", "medium")

            if cost_range == "low":
                estimated_cost = total_budget * 0.1
            elif cost_range == "low_to_medium":
                estimated_cost = total_budget * 0.2
            elif cost_range == "medium":
                estimated_cost = total_budget * 0.3
            elif cost_range == "medium_to_high":
                estimated_cost = total_budget * 0.4
            elif cost_range == "high":
                estimated_cost = total_budget * 0.5
            else:
                estimated_cost = total_budget * 0.3  # Default to medium

            # Calculate budget percentage
            budget_percentage = estimated_cost / total_budget

            # Calculate budget fit
            if budget_percentage <= 0.2:
                budget_fit = 1.0
                affordability = "affordable"
            elif budget_percentage <= 0.4:
                budget_fit = 0.7
                affordability = "moderate"
            else:
                budget_fit = 0.4
                affordability = "expensive"

            # Store the results
            budget_fit_scores[channel] = {
                "channel": channel_data["name"],
                "estimated_cost": estimated_cost,
                "budget_percentage": budget_percentage,
                "budget_fit": budget_fit,
                "affordability": affordability,
            }

        # Sort channels by budget fit
        sorted_channels = sorted(
            [{"channel": k, **v} for k, v in budget_fit_scores.items()],
            key=lambda x: x["budget_fit"],
            reverse=True,
        )

        # Get top channels
        top_channels = [channel["channel"] for channel in sorted_channels[:5]]

        # Get affordable channels
        affordable_channels = [
            channel
            for channel, data in budget_fit_scores.items()
            if data["affordability"] == "affordable"
        ]

        # Get moderate channels
        moderate_channels = [
            channel
            for channel, data in budget_fit_scores.items()
            if data["affordability"] == "moderate"
        ]

        # Get expensive channels
        expensive_channels = [
            channel
            for channel, data in budget_fit_scores.items()
            if data["affordability"] == "expensive"
        ]

        return {
            "budget_fit_scores": budget_fit_scores,
            "sorted_channels": sorted_channels,
            "top_channels": top_channels,
            "affordable_channels": affordable_channels,
            "moderate_channels": moderate_channels,
            "expensive_channels": expensive_channels,
        }

    def _analyze_channel_roi(self) -> Dict[str, Any]:
        """
        Analyze the potential ROI of each channel.

        Returns:
            Dictionary with ROI analysis
        """
        # For simplicity, create a basic implementation
        roi_scores = {}

        for channel, channel_data in self.MARKETING_CHANNELS.items():
            # Calculate a simple ROI score
            roi_score = 0.7  # Default value

            # Determine ROI level
            if roi_score >= 0.7:
                roi_level = "high"
            elif roi_score >= 0.4:
                roi_level = "medium"
            else:
                roi_level = "low"

            # Store the results
            roi_scores[channel] = {
                "channel": channel_data["name"],
                "roi_score": roi_score,
                "roi_level": roi_level,
                "estimated_return": 2.5,  # Placeholder value
                "estimated_cost": 1000.0,  # Placeholder value
                "potential_revenue": 2500.0,  # Placeholder value
                "roi": 2.5,  # Placeholder value
                "confidence": 0.6,  # Placeholder value
            }

        # Sort channels by ROI score
        sorted_channels = sorted(
            [{"channel": k, **v} for k, v in roi_scores.items()],
            key=lambda x: x["roi_score"],
            reverse=True,
        )

        # Get top channels
        top_channels = [channel["channel"] for channel in sorted_channels[:5]]

        # Get high ROI channels
        high_roi_channels = [
            channel
            for channel, data in roi_scores.items()
            if data["roi_level"] == "high"
        ]

        # Get medium ROI channels
        medium_roi_channels = [
            channel
            for channel, data in roi_scores.items()
            if data["roi_level"] == "medium"
        ]

        return {
            "roi_scores": roi_scores,
            "sorted_channels": sorted_channels,
            "top_channels": top_channels,
            "high_roi_channels": high_roi_channels,
            "medium_roi_channels": medium_roi_channels,
        }

    def _prioritize_channels(
        self,
        channel_effectiveness: Dict[str, Any],
        audience_fit: Dict[str, Any],
        goal_alignment: Dict[str, Any],
        budget_fit: Dict[str, Any],
        roi_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prioritize channels based on multiple factors.

        Args:
            channel_effectiveness: Channel effectiveness analysis
            audience_fit: Audience fit analysis
            goal_alignment: Goal alignment analysis
            budget_fit: Budget fit analysis
            roi_analysis: ROI analysis

        Returns:
            Dictionary with prioritized channels
        """
        # Calculate priority scores
        priority_scores = {}

        for channel, channel_data in self.MARKETING_CHANNELS.items():
            # Get scores from each analysis
            effectiveness_score = channel_effectiveness["effectiveness_scores"][
                channel
            ]["overall_score"]
            audience_fit_score = audience_fit["audience_fit_scores"][channel][
                "overall_fit"
            ]
            goal_alignment_score = goal_alignment["overall_alignment"][channel][
                "avg_alignment"
            ]
            budget_fit_score = budget_fit["budget_fit_scores"][channel]["budget_fit"]
            roi_score = roi_analysis["roi_scores"][channel]["roi_score"]

            # Calculate weighted priority score
            priority_score = (
                effectiveness_score * 0.3
                + audience_fit_score * 0.2
                + goal_alignment_score * 0.3
                + budget_fit_score * 0.2
            )

            # Determine priority level
            if priority_score >= 0.7:
                priority_level = "high"
            elif priority_score >= 0.4:
                priority_level = "medium"
            else:
                priority_level = "low"

            # Store the results
            priority_scores[channel] = {
                "channel": channel_data["name"],
                "overall_score": priority_score,
                "effectiveness_score": effectiveness_score,
                "audience_fit_score": audience_fit_score,
                "goal_alignment_score": goal_alignment_score,
                "budget_fit_score": budget_fit_score,
                "roi_score": roi_score,
                "priority_level": priority_level,
            }

        # Sort channels by priority score
        sorted_channels = sorted(
            [{"channel": k, **v} for k, v in priority_scores.items()],
            key=lambda x: x["overall_score"],
            reverse=True,
        )

        # Categorize channels
        high_priority_channels = [
            channel["channel"]
            for channel in sorted_channels
            if channel["overall_score"] >= 0.7
        ]

        medium_priority_channels = [
            channel["channel"]
            for channel in sorted_channels
            if 0.4 <= channel["overall_score"] < 0.7
        ]

        low_priority_channels = [
            channel["channel"]
            for channel in sorted_channels
            if channel["overall_score"] < 0.4
        ]

        return {
            "priority_scores": priority_scores,
            "sorted_channels": sorted_channels,
            "high_priority_channels": high_priority_channels,
            "medium_priority_channels": medium_priority_channels,
            "low_priority_channels": low_priority_channels,
            "prioritization_method": "weighted_score",
        }

    def _generate_channel_recommendations(
        self, prioritized_channels: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate recommendations for channel selection and implementation.

        Args:
            prioritized_channels: Prioritized channels analysis

        Returns:
            Dictionary with channel recommendations
        """
        recommendations = {}

        # Get high priority channels
        high_priority_channels = prioritized_channels["high_priority_channels"]

        # Get medium priority channels
        medium_priority_channels = prioritized_channels["medium_priority_channels"]

        # Generate recommendations for each high priority channel
        for channel in high_priority_channels:
            # Find the channel in MARKETING_CHANNELS
            # First try direct match
            if channel in self.MARKETING_CHANNELS:
                channel_data = self.MARKETING_CHANNELS[channel]
            else:
                # Try to find a matching channel by name
                channel_key = None
                for key, data in self.MARKETING_CHANNELS.items():
                    if data["name"] == channel:
                        channel_key = key
                        break

                # If we found a matching channel, use it
                if channel_key:
                    channel_data = self.MARKETING_CHANNELS[channel_key]
                else:
                    # If we can't find a matching channel, use a default
                    channel_data = {
                        "name": channel,
                        "description": "Marketing channel",
                        "formats": ["content", "ads", "social"],
                        "metrics": ["engagement", "conversion", "roi"],
                        "best_for": ["brand_awareness", "lead_generation"],
                    }

            # Generate recommendation
            recommendation = {
                "channel": channel_data["name"],
                "description": channel_data["description"],
                "priority": "high",
                "recommended_formats": channel_data.get("formats", [])[:3],
                "key_metrics": channel_data.get("metrics", [])[:3],
                "implementation_tips": [
                    f"Focus on {channel_data.get('best_for', [''])[0]} to maximize effectiveness",
                    f"Allocate at least 20% of your budget to this channel",
                    f"Measure {', '.join(channel_data.get('metrics', [])[:2])} to track performance",
                ],
            }

            # Add business-specific recommendations
            if self.business_type and self.business_type.lower() in self.BUSINESS_TYPES:
                business_type_data = self.BUSINESS_TYPES[self.business_type.lower()]
                if channel in business_type_data.get("typical_channels", []):
                    recommendation["implementation_tips"].append(
                        f"This channel is particularly effective for {business_type_data['name']} businesses"
                    )

            # Add goal-specific recommendations
            for goal in self.goals:
                if goal.lower() in self.MARKETING_GOALS:
                    goal_data = self.MARKETING_GOALS[goal.lower()]
                    if channel in goal_data.get("recommended_channels", []):
                        recommendation["implementation_tips"].append(
                            f"This channel is highly effective for {goal_data['name']}"
                        )

            # Store the recommendation
            recommendations[channel] = recommendation

        # Generate recommendations for each medium priority channel
        for channel in medium_priority_channels[
            :3
        ]:  # Limit to top 3 medium priority channels
            # Find the channel in MARKETING_CHANNELS
            # First try direct match
            if channel in self.MARKETING_CHANNELS:
                channel_data = self.MARKETING_CHANNELS[channel]
            else:
                # Try to find a matching channel by name
                channel_key = None
                for key, data in self.MARKETING_CHANNELS.items():
                    if data["name"] == channel:
                        channel_key = key
                        break

                # If we found a matching channel, use it
                if channel_key:
                    channel_data = self.MARKETING_CHANNELS[channel_key]
                else:
                    # If we can't find a matching channel, use a default
                    channel_data = {
                        "name": channel,
                        "description": "Marketing channel",
                        "formats": ["content", "ads", "social"],
                        "metrics": ["engagement", "conversion", "roi"],
                        "best_for": ["brand_awareness", "lead_generation"],
                    }

            # Generate recommendation
            recommendation = {
                "channel": channel_data["name"],
                "description": channel_data["description"],
                "priority": "medium",
                "recommended_formats": channel_data.get("formats", [])[:2],
                "key_metrics": channel_data.get("metrics", [])[:2],
                "implementation_tips": [
                    f"Consider this channel as a secondary focus",
                    f"Allocate around 10% of your budget to this channel",
                    f"Measure {', '.join(channel_data.get('metrics', [])[:1])} to track performance",
                ],
            }

            # Store the recommendation
            recommendations[channel] = recommendation

        return recommendations


class ContentMarketingStrategyGenerator(DefaultStrategyGenerator):
    """
    Strategy generator for content marketing.
    """

    def __init__(
        self,
        business_type: Optional[str] = None,
        business_size: Optional[str] = None,
        goals: Optional[List[str]] = None,
        target_audience: Optional[TargetAudienceSchema] = None,
        budget: Optional[BudgetSchema] = None,
        agent_team: Optional[IAgentTeam] = None,
        platforms: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        frequency: str = "weekly",
        timeframe: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize a ContentMarketingStrategyGenerator.

        Args:
            business_type: Type of business (e.g., "SaaS", "E-commerce")
            business_size: Size of business (e.g., "Startup", "Small", "Medium", "Enterprise")
            goals: List of marketing goals
            target_audience: Target audience details
            budget: Budget details
            agent_team: Optional agent team for strategy generation assistance
            platforms: List of platforms for content distribution
            content_types: List of content types to create
            frequency: How often to publish content
        """
        super().__init__(
            business_type=business_type,
            business_size=business_size,
            goals=goals,
            target_audience=target_audience,
            budget=budget,
            agent_team=agent_team,
            name="Content Marketing Strategy",
            description="A strategy focused on creating and distributing valuable content",
            channel_type="content_marketing",
            timeframe=timeframe,
            **kwargs,
        )
        self.platforms = platforms or ["blog", "social_media", "email"]
        self.content_types = content_types or ["blog_posts", "videos", "infographics"]
        self.frequency = frequency


class SocialMediaStrategyGenerator(DefaultStrategyGenerator):
    """
    Strategy generator for social media marketing.
    """

    def __init__(
        self,
        business_type: Optional[str] = None,
        business_size: Optional[str] = None,
        goals: Optional[List[str]] = None,
        target_audience: Optional[TargetAudienceSchema] = None,
        budget: Optional[BudgetSchema] = None,
        agent_team: Optional[IAgentTeam] = None,
        platforms: Optional[List[str]] = None,
        post_frequency: str = "daily",
        content_mix: Optional[Dict[str, int]] = None,
        timeframe: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize a SocialMediaStrategyGenerator.

        Args:
            business_type: Type of business (e.g., "SaaS", "E-commerce")
            business_size: Size of business (e.g., "Startup", "Small", "Medium", "Enterprise")
            goals: List of marketing goals
            target_audience: Target audience details
            budget: Budget details
            agent_team: Optional agent team for strategy generation assistance
            platforms: List of social media platforms
            post_frequency: How often to post on each platform
            content_mix: Dictionary mapping content types to percentage
        """
        super().__init__(
            business_type=business_type,
            business_size=business_size,
            goals=goals,
            target_audience=target_audience,
            budget=budget,
            agent_team=agent_team,
            name="Social Media Marketing Strategy",
            description="A strategy focused on social media marketing",
            channel_type="social_media",
            timeframe=timeframe,
            **kwargs,
        )
        self.platforms = platforms or ["instagram", "twitter", "facebook", "linkedin"]
        self.post_frequency = post_frequency
        self.content_mix = content_mix or {
            "educational": 40,
            "promotional": 20,
            "entertaining": 40,
        }


class EmailMarketingStrategyGenerator(DefaultStrategyGenerator):
    """
    Strategy generator for email marketing.
    """

    def __init__(
        self,
        business_type: Optional[str] = None,
        business_size: Optional[str] = None,
        goals: Optional[List[str]] = None,
        target_audience: Optional[TargetAudienceSchema] = None,
        budget: Optional[BudgetSchema] = None,
        agent_team: Optional[IAgentTeam] = None,
        email_types: Optional[List[str]] = None,
        frequency: str = "weekly",
        list_building_tactics: Optional[List[str]] = None,
        timeframe: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize an EmailMarketingStrategyGenerator.

        Args:
            business_type: Type of business (e.g., "SaaS", "E-commerce")
            business_size: Size of business (e.g., "Startup", "Small", "Medium", "Enterprise")
            goals: List of marketing goals
            target_audience: Target audience details
            budget: Budget details
            agent_team: Optional agent team for strategy generation assistance
            email_types: List of email types to send
            frequency: How often to send emails
            list_building_tactics: List of tactics for building your email list
        """
        super().__init__(
            business_type=business_type,
            business_size=business_size,
            goals=goals,
            target_audience=target_audience,
            budget=budget,
            agent_team=agent_team,
            name="Email Marketing Strategy",
            description="A strategy focused on email marketing",
            channel_type="email_marketing",
            timeframe=timeframe,
            **kwargs,
        )
        self.email_types = email_types or [
            "newsletter",
            "promotional",
            "onboarding",
            "retention",
        ]
        self.frequency = frequency
        self.list_building_tactics = list_building_tactics or [
            "content upgrades",
            "lead magnets",
            "webinars",
            "free trials",
        ]
