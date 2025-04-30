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
    'MarketingCampaignError',
    'InvalidTestConfigurationError',
    'TestNotFoundError',
    'ContentNotFoundError',
    'InvalidParameterError',
    'InsufficientDataError',
    'StorageError'
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


class InvalidTestConfigurationError(MarketingError):
    """Error raised when an A/B test configuration is invalid."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the invalid test configuration error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="invalid_test_configuration",
            **kwargs
        )


class TestNotFoundError(MarketingError):
    """Error raised when an A/B test is not found."""

    def __init__(
        self,
        test_id: str,
        **kwargs
    ):
        """
        Initialize the test not found error.

        Args:
            test_id: ID of the test that was not found
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=f"A/B test with ID '{test_id}' not found",
            code="test_not_found",
            **kwargs
        )


class PlatformNotSupportedError(Exception):
    """Exception raised when a social media platform is not supported."""

    def __init__(self, platform: str):
        self.platform = platform
        super().__init__(f"Social media platform '{platform}' is not supported")


class PlatformNotFoundError(Exception):
    """Exception raised when a social media platform connection is not found."""

    def __init__(self, platform_id: str):
        self.platform_id = platform_id
        super().__init__(f"Social media platform with ID '{platform_id}' not found")


class AuthenticationError(Exception):
    """Exception raised when authentication with a social media platform fails."""

    def __init__(self, platform: str, message: str = "Authentication failed"):
        self.platform = platform
        self.message = message
        super().__init__(f"{message} for platform '{platform}'")


class PostNotFoundError(Exception):
    """Exception raised when a social media post is not found."""

    def __init__(self, platform_id: str, post_id: str):
        self.platform_id = platform_id
        self.post_id = post_id
        super().__init__(f"Post with ID '{post_id}' not found on platform '{platform_id}'")


class ContentValidationError(Exception):
    """Exception raised when social media content validation fails."""

    def __init__(self, platform: str, message: str):
        self.platform = platform
        self.message = message
        super().__init__(f"Content validation failed for platform '{platform}': {message}")


class PostingError(Exception):
    """Exception raised when posting to a social media platform fails."""

    def __init__(self, platform: str, message: str):
        self.platform = platform
        self.message = message
        super().__init__(f"Failed to post to platform '{platform}': {message}")


class DeletionError(Exception):
    """Exception raised when deleting a post from a social media platform fails."""

    def __init__(self, platform: str, post_id: str, message: str):
        self.platform = platform
        self.post_id = post_id
        self.message = message
        super().__init__(f"Failed to delete post '{post_id}' from platform '{platform}': {message}")


class SchedulingError(Exception):
    """Exception raised when scheduling a post or campaign fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Failed to schedule content: {message}")


class NotSupportedError(Exception):
    """Exception raised when a feature is not supported by a platform."""

    def __init__(self, platform: str, feature: str):
        self.platform = platform
        self.feature = feature
        super().__init__(f"Feature '{feature}' is not supported by platform '{platform}'")


class ContentNotFoundError(MarketingError):
    """Error raised when content is not found."""

    def __init__(
        self,
        content_id: str,
        **kwargs
    ):
        """
        Initialize the content not found error.

        Args:
            content_id: ID of the content that was not found
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=f"Content with ID '{content_id}' not found",
            code="content_not_found",
            **kwargs
        )


class InvalidParameterError(MarketingError):
    """Error raised when a parameter is invalid."""

    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the invalid parameter error.

        Args:
            message: Human-readable error message
            parameter: Optional name of the invalid parameter
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if parameter:
            details["parameter"] = parameter

        super().__init__(
            message=message,
            code="invalid_parameter",
            details=details,
            **kwargs
        )


class InsufficientDataError(MarketingError):
    """Error raised when there is not enough data for an operation."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the insufficient data error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="insufficient_data",
            **kwargs
        )


class StorageError(MarketingError):
    """Error raised when there is an issue with storage operations."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the storage error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="storage_error",
            **kwargs
        )
