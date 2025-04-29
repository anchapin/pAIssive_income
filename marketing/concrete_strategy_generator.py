"""
Concrete implementation of the StrategyGenerator class.

This module provides a concrete implementation of the StrategyGenerator class
that implements all the required abstract methods from IMarketingStrategy.
"""

from typing import Dict, List, Any, Optional
from marketing.strategy_generator import StrategyGenerator
from marketing.schemas import TargetAudienceSchema, BudgetSchema
from interfaces.agent_interfaces import IAgentTeam


class DefaultStrategyGenerator(StrategyGenerator):
    """
    Concrete implementation of the StrategyGenerator class.

    This class implements all the required abstract methods from IMarketingStrategy.
    """

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
        **kwargs
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
            **kwargs
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

    def create_strategy(self, target_persona: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
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
        **kwargs
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
            **kwargs
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
        **kwargs
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
            **kwargs
        )
        self.platforms = platforms or ["instagram", "twitter", "facebook", "linkedin"]
        self.post_frequency = post_frequency
        self.content_mix = content_mix or {"educational": 40, "promotional": 20, "entertaining": 40}


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
        **kwargs
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
            **kwargs
        )
        self.email_types = email_types or ["newsletter", "promotional", "onboarding", "retention"]
        self.frequency = frequency
        self.list_building_tactics = list_building_tactics or [
            "content upgrades",
            "lead magnets",
            "webinars",
            "free trials"
        ]
