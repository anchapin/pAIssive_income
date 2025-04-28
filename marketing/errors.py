"""
Error handling for the Marketing module.

This module provides custom exceptions and error handling utilities
specific to the Marketing module.
"""

import sys
import os
from typing import Dict, Any, Optional, List, Type, Union
import logging

# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from errors import (
    MarketingError, ValidationError, handle_exception
)

# Set up logging
logger = logging.getLogger(__name__)

# Re-export the error classes for convenience
__all__ = [
    'MarketingError',
    'ValidationError',
    'handle_exception',
    'ContentGenerationError',
    'StrategyGenerationError',
    'ChannelStrategyError',
    'ContentTemplateError',
    'ContentOptimizationError',
    'UserPersonaError',
    'MarketingCampaignError'
]


class ContentGenerationError(MarketingError):
    """Error raised when there's an issue with content generation."""

    def __init__(
        self,
        message: str,
        content_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the content generation error.

        Args:
            message: Human-readable error message
            content_type: Type of content that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if content_type:
            details["content_type"] = content_type

        super().__init__(
            message=message,
            code="content_generation_error",
            details=details,
            **kwargs
        )


class StrategyGenerationError(MarketingError):
    """Error raised when there's an issue with marketing strategy generation."""

    def __init__(
        self,
        message: str,
        strategy_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the strategy generation error.

        Args:
            message: Human-readable error message
            strategy_type: Type of strategy that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if strategy_type:
            details["strategy_type"] = strategy_type

        super().__init__(
            message=message,
            code="strategy_generation_error",
            details=details,
            **kwargs
        )


class ChannelStrategyError(MarketingError):
    """Error raised when there's an issue with a marketing channel strategy."""

    def __init__(
        self,
        message: str,
        channel: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the channel strategy error.

        Args:
            message: Human-readable error message
            channel: Marketing channel that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if channel:
            details["channel"] = channel

        super().__init__(
            message=message,
            code="channel_strategy_error",
            details=details,
            **kwargs
        )


class ContentTemplateError(MarketingError):
    """Error raised when there's an issue with a content template."""

    def __init__(
        self,
        message: str,
        template_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the content template error.

        Args:
            message: Human-readable error message
            template_type: Type of template that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if template_type:
            details["template_type"] = template_type

        # Only set code if it's not already provided in kwargs
        if 'code' not in kwargs:
            kwargs['code'] = "content_template_error"

        super().__init__(
            message=message,
            details=details,
            **kwargs
        )


class ContentOptimizationError(MarketingError):
    """Error raised when there's an issue with content optimization."""

    def __init__(
        self,
        message: str,
        optimization_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the content optimization error.

        Args:
            message: Human-readable error message
            optimization_type: Type of optimization that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if optimization_type:
            details["optimization_type"] = optimization_type

        super().__init__(
            message=message,
            code="content_optimization_error",
            details=details,
            **kwargs
        )


class UserPersonaError(MarketingError):
    """Error raised when there's an issue with user persona creation or analysis."""

    def __init__(
        self,
        message: str,
        persona_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the user persona error.

        Args:
            message: Human-readable error message
            persona_name: Name of the persona that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if persona_name:
            details["persona_name"] = persona_name

        super().__init__(
            message=message,
            code="user_persona_error",
            details=details,
            **kwargs
        )


class MarketingCampaignError(MarketingError):
    """Error raised when there's an issue with a marketing campaign."""

    def __init__(
        self,
        message: str,
        campaign_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the marketing campaign error.

        Args:
            message: Human-readable error message
            campaign_id: ID of the campaign that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if campaign_id:
            details["campaign_id"] = campaign_id

        super().__init__(
            message=message,
            code="marketing_campaign_error",
            details=details,
            **kwargs
        )
