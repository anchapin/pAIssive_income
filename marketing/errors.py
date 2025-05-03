"""
Error handling for the Marketing module.

This module provides custom exceptions and error handling utilities
specific to the Marketing module.
"""

import time


import logging
import os
import sys
from typing import Any, Dict, List, Optional


from errors import MarketingError, ValidationError, handle_exception



# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set up logging
logger = logging.getLogger(__name__)

# Re-export the error classes for convenience
__all__ = [
    "MarketingError",
    "ValidationError",
    "handle_exception",
    "ContentGenerationError",
    "StrategyGenerationError",
    "ChannelStrategyError",
    "ContentTemplateError",
    "ContentOptimizationError",
    "UserPersonaError",
    "MarketingCampaignError",
    "InvalidTestConfigurationError",
    "TestNotFoundError",
    "ContentNotFoundError",
    "InvalidParameterError",
    "InsufficientDataError",
    "StorageError",
    "PlatformNotFoundError",
    "PlatformNotSupportedError",
    "AuthenticationError",
    "ContentValidationError",
    "PostNotFoundError",
    "PostingError",
    "DeletionError",
    "SchedulingError",
    "NotSupportedError",
]


class InvalidTestConfigurationError(MarketingError):
    """Error raised when there's an invalid test configuration."""

def __init__(self, message: str, test_id: Optional[str] = None, **kwargs):
        """
        Initialize the invalid test configuration error.

Args:
            message: Human-readable error message
            test_id: ID of the test with invalid configuration
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if test_id:
            details["test_id"] = test_id

super().__init__(
            message=message,
            code="invalid_test_configuration_error",
            details=details,
            **kwargs,
        )


class TestNotFoundError(MarketingError):
    """Error raised when a test is not found."""

def __init__(self, message: str, test_id: Optional[str] = None, **kwargs):
        """
        Initialize the test not found error.

Args:
            message: Human-readable error message
            test_id: ID of the test that was not found
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if test_id:
            details["test_id"] = test_id

super().__init__(
            message=message, code="test_not_found_error", details=details, **kwargs
        )


class ContentGenerationError(MarketingError):
    """Error raised when there's an issue with content generation."""

def __init__(self, message: str, content_type: Optional[str] = None, **kwargs):
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
            message=message, code="content_generation_error", details=details, **kwargs
        )


class StrategyGenerationError(MarketingError):
    """Error raised when there's an issue with marketing strategy generation."""

def __init__(self, message: str, strategy_type: Optional[str] = None, **kwargs):
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
            message=message, code="strategy_generation_error", details=details, **kwargs
        )


class ChannelStrategyError(MarketingError):
    """Error raised when there's an issue with a marketing channel strategy."""

def __init__(self, message: str, channel: Optional[str] = None, **kwargs):
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
            message=message, code="channel_strategy_error", details=details, **kwargs
        )


class ContentTemplateError(MarketingError):
    """Error raised when there's an issue with a content template."""

def __init__(self, message: str, template_type: Optional[str] = None, **kwargs):
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
        if "code" not in kwargs:
            kwargs["code"] = "content_template_error"

super().__init__(message=message, details=details, **kwargs)


class ContentOptimizationError(MarketingError):
    """Error raised when there's an issue with content optimization."""

def __init__(self, message: str, optimization_type: Optional[str] = None, **kwargs):
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
            **kwargs,
        )


class UserPersonaError(MarketingError):
    """Error raised when there's an issue with user persona creation or analysis."""

def __init__(self, message: str, persona_name: Optional[str] = None, **kwargs):
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
            message=message, code="user_persona_error", details=details, **kwargs
        )


class MarketingCampaignError(MarketingError):
    """Error raised when there's an issue with a marketing campaign."""

def __init__(self, message: str, campaign_id: Optional[str] = None, **kwargs):
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
            message=message, code="marketing_campaign_error", details=details, **kwargs
        )


class InvalidParameterError(MarketingError):
    """Error raised when a parameter is invalid."""

def __init__(self, message: str, parameter_name: Optional[str] = None, **kwargs):
        """
        Initialize the invalid parameter error.

Args:
            message: Human-readable error message
            parameter_name: Name of the parameter that is invalid
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if parameter_name:
            details["parameter_name"] = parameter_name

super().__init__(
            message=message, code="invalid_parameter_error", details=details, **kwargs
        )


class ContentNotFoundError(MarketingError):
    """Error raised when specific content is not found."""

def __init__(
        self,
        message: str,
        content_id: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the content not found error.

Args:
            message: Human-readable error message
            content_id: ID of the content that was not found
            content_type: Type of content that was not found
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if content_id:
            details["content_id"] = content_id
        if content_type:
            details["content_type"] = content_type

super().__init__(
            message=message, code="content_not_found_error", details=details, **kwargs
        )


class StorageError(MarketingError):
    """Error raised when there is an issue with data storage or retrieval."""

def __init__(
        self,
        message: str,
        storage_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the storage error.

Args:
            message: Human-readable error message
            storage_type: Type of storage that encountered the error
            operation: Operation that was being performed
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if storage_type:
            details["storage_type"] = storage_type
        if operation:
            details["operation"] = operation

super().__init__(
            message=message, code="storage_error", details=details, **kwargs
        )


class InsufficientDataError(MarketingError):
    """Error raised when there is insufficient data for analysis."""

def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        min_required: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize the insufficient data error.

Args:
            message: Human-readable error message
            data_type: Type of data that is insufficient
            min_required: Minimum amount of data required
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if data_type:
            details["data_type"] = data_type
        if min_required is not None:
            details["min_required"] = min_required

super().__init__(
            message=message, code="insufficient_data_error", details=details, **kwargs
        )


class ContentValidationError(MarketingError):
    """Error raised when content validation fails."""

def __init__(
        self,
        message: str,
        content_type: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Initialize the content validation error.

Args:
            message: Human-readable error message
            content_type: Type of content that failed validation
            validation_errors: List of specific validation errors
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if content_type:
            details["content_type"] = content_type
        if validation_errors:
            details["validation_errors"] = validation_errors

super().__init__(
            message=message, code="content_validation_error", details=details, **kwargs
        )


class PlatformNotFoundError(MarketingError):
    """Error raised when a social media platform connection is not found."""

def __init__(self, platform_id: str, message: Optional[str] = None, **kwargs):
        """
        Initialize the platform not found error.

Args:
            platform_id: ID of the platform that was not found
            message: Optional custom message
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        details["platform_id"] = platform_id

if message is None:
            message = f"Social media platform with ID '{platform_id}' not found"

super().__init__(
            message=message, code="platform_not_found_error", details=details, **kwargs
        )


class AuthenticationError(MarketingError):
    """Error raised when there's an authentication issue with a third-party service."""

def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        """
        Initialize the authentication error.

Args:
            message: Human-readable error message
            service_name: Name of the service that failed authentication
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if service_name:
            details["service_name"] = service_name

super().__init__(
            message=message, code="authentication_error", details=details, **kwargs
        )


class PostNotFoundError(MarketingError):
    """Error raised when a social media post is not found."""

def __init__(
        self,
        message: str,
        post_id: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the post not found error.

Args:
            message: Human-readable error message
            post_id: ID of the post that was not found
            platform: Social media platform where the post should exist
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if post_id:
            details["post_id"] = post_id
        if platform:
            details["platform"] = platform

super().__init__(
            message=message, code="post_not_found_error", details=details, **kwargs
        )


class PostingError(MarketingError):
    """Error raised when there's an error posting content to a platform."""

def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        content_id: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize the posting error.

Args:
            message: Human-readable error message
            platform: The platform where the posting failed
            content_id: ID of the content that failed to post
            error_details: Additional details about the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if platform:
            details["platform"] = platform
        if content_id:
            details["content_id"] = content_id
        if error_details:
            details["error_details"] = error_details

super().__init__(
            message=message, code="posting_error", details=details, **kwargs
        )


class DeletionError(MarketingError):
    """Error raised when content or entity deletion fails."""

def __init__(
        self,
        message: str,
        content_type: Optional[str] = None,
        content_id: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the deletion error.

Args:
            message: Human-readable error message
            content_type: Type of content that failed to delete
            content_id: ID of the content that failed to delete
            platform: The platform where deletion failed
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if content_type:
            details["content_type"] = content_type
        if content_id:
            details["content_id"] = content_id
        if platform:
            details["platform"] = platform

super().__init__(
            message=message, code="deletion_error", details=details, **kwargs
        )


class SchedulingError(MarketingError):
    """Error raised when there's an issue with scheduling content."""

def __init__(
        self,
        message: str,
        content_id: Optional[str] = None,
        schedule_time: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the scheduling error.

Args:
            message: Human-readable error message
            content_id: ID of the content that failed to schedule
            schedule_time: The time when the content was supposed to be scheduled
            platform: The platform where scheduling failed
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if content_id:
            details["content_id"] = content_id
        if schedule_time:
            details["schedule_time"] = schedule_time
        if platform:
            details["platform"] = platform

super().__init__(
            message=message, code="scheduling_error", details=details, **kwargs
        )


class NotSupportedError(MarketingError):
    """Error raised when a feature or operation is not supported."""

def __init__(
        self,
        message: str,
        feature: Optional[str] = None,
        platform: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the not supported error.

Args:
            message: Human-readable error message
            feature: The feature that is not supported
            platform: The platform or context where the feature is not supported
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if feature:
            details["feature"] = feature
        if platform:
            details["platform"] = platform

super().__init__(
            message=message, code="not_supported_error", details=details, **kwargs
        )


class PlatformNotSupportedError(Exception):
    """Exception raised when a feature is not supported by a platform."""

def __init__(self, platform: str, feature: str):
        self.platform = platform
        self.feature = feature
        super().__init__(
            f"Feature '{feature}' is not supported by platform '{platform}'"
        )