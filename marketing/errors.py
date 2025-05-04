"""
"""
Error handling for the Marketing module.
Error handling for the Marketing module.


This module provides custom exceptions and error handling utilities
This module provides custom exceptions and error handling utilities
specific to the Marketing module.
specific to the Marketing module.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from errors import MarketingError, ValidationError, handle_exception
from errors import MarketingError, ValidationError, handle_exception


# Add the project root to the Python path to import the errors module
# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Re-export the error classes for convenience
# Re-export the error classes for convenience
__all__ = [
__all__ = [
"MarketingError",
"MarketingError",
"ValidationError",
"ValidationError",
"handle_exception",
"handle_exception",
"ContentGenerationError",
"ContentGenerationError",
"StrategyGenerationError",
"StrategyGenerationError",
"ChannelStrategyError",
"ChannelStrategyError",
"ContentTemplateError",
"ContentTemplateError",
"ContentOptimizationError",
"ContentOptimizationError",
"UserPersonaError",
"UserPersonaError",
"MarketingCampaignError",
"MarketingCampaignError",
"InvalidTestConfigurationError",
"InvalidTestConfigurationError",
"TestNotFoundError",
"TestNotFoundError",
"ContentNotFoundError",
"ContentNotFoundError",
"InvalidParameterError",
"InvalidParameterError",
"InsufficientDataError",
"InsufficientDataError",
"StorageError",
"StorageError",
"PlatformNotFoundError",
"PlatformNotFoundError",
"PlatformNotSupportedError",
"PlatformNotSupportedError",
"AuthenticationError",
"AuthenticationError",
"ContentValidationError",
"ContentValidationError",
"PostNotFoundError",
"PostNotFoundError",
"PostingError",
"PostingError",
"DeletionError",
"DeletionError",
"SchedulingError",
"SchedulingError",
"NotSupportedError",
"NotSupportedError",
]
]




class InvalidTestConfigurationError(MarketingError):
    class InvalidTestConfigurationError(MarketingError):
    """Error raised when there's an invalid test configuration."""


    def __init__(self, message: str, test_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the invalid test configuration error.
    Initialize the invalid test configuration error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    test_id: ID of the test with invalid configuration
    test_id: ID of the test with invalid configuration
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if test_id:
    if test_id:
    details["test_id"] = test_id
    details["test_id"] = test_id




    super().__init__(
    super().__init__(
    message=message,
    message=message,
    code="invalid_test_configuration_error",
    code="invalid_test_configuration_error",
    details=details,
    details=details,
    **kwargs,
    **kwargs,
    )
    )




    class TestNotFoundError(MarketingError):
    class TestNotFoundError(MarketingError):
    """Error raised when a test is not found."""


    def __init__(self, message: str, test_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the test not found error.
    Initialize the test not found error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    test_id: ID of the test that was not found
    test_id: ID of the test that was not found
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if test_id:
    if test_id:
    details["test_id"] = test_id
    details["test_id"] = test_id




    super().__init__(
    super().__init__(
    message=message, code="test_not_found_error", details=details, **kwargs
    message=message, code="test_not_found_error", details=details, **kwargs
    )
    )




    class ContentGenerationError(MarketingError):
    class ContentGenerationError(MarketingError):
    """Error raised when there's an issue with content generation."""


    def __init__(self, message: str, content_type: Optional[str] = None, **kwargs):
    """
    """
    Initialize the content generation error.
    Initialize the content generation error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    content_type: Type of content that caused the error
    content_type: Type of content that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if content_type:
    if content_type:
    details["content_type"] = content_type
    details["content_type"] = content_type




    super().__init__(
    super().__init__(
    message=message, code="content_generation_error", details=details, **kwargs
    message=message, code="content_generation_error", details=details, **kwargs
    )
    )




    class StrategyGenerationError(MarketingError):
    class StrategyGenerationError(MarketingError):
    """Error raised when there's an issue with marketing strategy generation."""


    def __init__(self, message: str, strategy_type: Optional[str] = None, **kwargs):
    """
    """
    Initialize the strategy generation error.
    Initialize the strategy generation error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    strategy_type: Type of strategy that caused the error
    strategy_type: Type of strategy that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if strategy_type:
    if strategy_type:
    details["strategy_type"] = strategy_type
    details["strategy_type"] = strategy_type




    super().__init__(
    super().__init__(
    message=message, code="strategy_generation_error", details=details, **kwargs
    message=message, code="strategy_generation_error", details=details, **kwargs
    )
    )




    class ChannelStrategyError(MarketingError):
    class ChannelStrategyError(MarketingError):
    """Error raised when there's an issue with a marketing channel strategy."""


    def __init__(self, message: str, channel: Optional[str] = None, **kwargs):
    """
    """
    Initialize the channel strategy error.
    Initialize the channel strategy error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    channel: Marketing channel that caused the error
    channel: Marketing channel that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if channel:
    if channel:
    details["channel"] = channel
    details["channel"] = channel




    super().__init__(
    super().__init__(
    message=message, code="channel_strategy_error", details=details, **kwargs
    message=message, code="channel_strategy_error", details=details, **kwargs
    )
    )




    class ContentTemplateError(MarketingError):
    class ContentTemplateError(MarketingError):
    """Error raised when there's an issue with a content template."""


    def __init__(self, message: str, template_type: Optional[str] = None, **kwargs):
    """
    """
    Initialize the content template error.
    Initialize the content template error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    template_type: Type of template that caused the error
    template_type: Type of template that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if template_type:
    if template_type:
    details["template_type"] = template_type
    details["template_type"] = template_type


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "content_template_error"
    kwargs["code"] = "content_template_error"




    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    class ContentOptimizationError(MarketingError):
    class ContentOptimizationError(MarketingError):
    """Error raised when there's an issue with content optimization."""


    def __init__(self, message: str, optimization_type: Optional[str] = None, **kwargs):
    """
    """
    Initialize the content optimization error.
    Initialize the content optimization error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    optimization_type: Type of optimization that caused the error
    optimization_type: Type of optimization that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if optimization_type:
    if optimization_type:
    details["optimization_type"] = optimization_type
    details["optimization_type"] = optimization_type




    super().__init__(
    super().__init__(
    message=message,
    message=message,
    code="content_optimization_error",
    code="content_optimization_error",
    details=details,
    details=details,
    **kwargs,
    **kwargs,
    )
    )




    class UserPersonaError(MarketingError):
    class UserPersonaError(MarketingError):
    """Error raised when there's an issue with user persona creation or analysis."""


    def __init__(self, message: str, persona_name: Optional[str] = None, **kwargs):
    """
    """
    Initialize the user persona error.
    Initialize the user persona error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    persona_name: Name of the persona that caused the error
    persona_name: Name of the persona that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if persona_name:
    if persona_name:
    details["persona_name"] = persona_name
    details["persona_name"] = persona_name




    super().__init__(message=message, code="user_persona_error", details=details, **kwargs)
    super().__init__(message=message, code="user_persona_error", details=details, **kwargs)




    class MarketingCampaignError(MarketingError):
    class MarketingCampaignError(MarketingError):
    """Error raised when there's an issue with a marketing campaign."""


    def __init__(self, message: str, campaign_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the marketing campaign error.
    Initialize the marketing campaign error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    campaign_id: ID of the campaign that caused the error
    campaign_id: ID of the campaign that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if campaign_id:
    if campaign_id:
    details["campaign_id"] = campaign_id
    details["campaign_id"] = campaign_id




    super().__init__(
    super().__init__(
    message=message, code="marketing_campaign_error", details=details, **kwargs
    message=message, code="marketing_campaign_error", details=details, **kwargs
    )
    )




    class InvalidParameterError(MarketingError):
    class InvalidParameterError(MarketingError):
    """Error raised when a parameter is invalid."""


    def __init__(self, message: str, parameter_name: Optional[str] = None, **kwargs):
    """
    """
    Initialize the invalid parameter error.
    Initialize the invalid parameter error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    parameter_name: Name of the parameter that is invalid
    parameter_name: Name of the parameter that is invalid
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if parameter_name:
    if parameter_name:
    details["parameter_name"] = parameter_name
    details["parameter_name"] = parameter_name




    super().__init__(
    super().__init__(
    message=message, code="invalid_parameter_error", details=details, **kwargs
    message=message, code="invalid_parameter_error", details=details, **kwargs
    )
    )




    class ContentNotFoundError(MarketingError):
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
    """
    Initialize the content not found error.
    Initialize the content not found error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    content_id: ID of the content that was not found
    content_id: ID of the content that was not found
    content_type: Type of content that was not found
    content_type: Type of content that was not found
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if content_id:
    if content_id:
    details["content_id"] = content_id
    details["content_id"] = content_id
    if content_type:
    if content_type:
    details["content_type"] = content_type
    details["content_type"] = content_type




    super().__init__(
    super().__init__(
    message=message, code="content_not_found_error", details=details, **kwargs
    message=message, code="content_not_found_error", details=details, **kwargs
    )
    )




    class StorageError(MarketingError):
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
    """
    Initialize the storage error.
    Initialize the storage error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    storage_type: Type of storage that encountered the error
    storage_type: Type of storage that encountered the error
    operation: Operation that was being performed
    operation: Operation that was being performed
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if storage_type:
    if storage_type:
    details["storage_type"] = storage_type
    details["storage_type"] = storage_type
    if operation:
    if operation:
    details["operation"] = operation
    details["operation"] = operation




    super().__init__(message=message, code="storage_error", details=details, **kwargs)
    super().__init__(message=message, code="storage_error", details=details, **kwargs)




    class InsufficientDataError(MarketingError):
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
    """
    Initialize the insufficient data error.
    Initialize the insufficient data error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    data_type: Type of data that is insufficient
    data_type: Type of data that is insufficient
    min_required: Minimum amount of data required
    min_required: Minimum amount of data required
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if data_type:
    if data_type:
    details["data_type"] = data_type
    details["data_type"] = data_type
    if min_required is not None:
    if min_required is not None:
    details["min_required"] = min_required
    details["min_required"] = min_required




    super().__init__(
    super().__init__(
    message=message, code="insufficient_data_error", details=details, **kwargs
    message=message, code="insufficient_data_error", details=details, **kwargs
    )
    )




    class ContentValidationError(MarketingError):
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
    """
    Initialize the content validation error.
    Initialize the content validation error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    content_type: Type of content that failed validation
    content_type: Type of content that failed validation
    validation_errors: List of specific validation errors
    validation_errors: List of specific validation errors
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if content_type:
    if content_type:
    details["content_type"] = content_type
    details["content_type"] = content_type
    if validation_errors:
    if validation_errors:
    details["validation_errors"] = validation_errors
    details["validation_errors"] = validation_errors




    super().__init__(
    super().__init__(
    message=message, code="content_validation_error", details=details, **kwargs
    message=message, code="content_validation_error", details=details, **kwargs
    )
    )




    class PlatformNotFoundError(MarketingError):
    class PlatformNotFoundError(MarketingError):
    """Error raised when a social media platform connection is not found."""


    def __init__(self, platform_id: str, message: Optional[str] = None, **kwargs):
    """
    """
    Initialize the platform not found error.
    Initialize the platform not found error.


    Args:
    Args:
    platform_id: ID of the platform that was not found
    platform_id: ID of the platform that was not found
    message: Optional custom message
    message: Optional custom message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    details["platform_id"] = platform_id
    details["platform_id"] = platform_id




    if message is None:
    if message is None:
    message = f"Social media platform with ID '{platform_id}' not found"
    message = f"Social media platform with ID '{platform_id}' not found"


    super().__init__(
    super().__init__(
    message=message, code="platform_not_found_error", details=details, **kwargs
    message=message, code="platform_not_found_error", details=details, **kwargs
    )
    )




    class AuthenticationError(MarketingError):
    class AuthenticationError(MarketingError):
    """Error raised when there's an authentication issue with a third-party service."""


    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
    """
    """
    Initialize the authentication error.
    Initialize the authentication error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    service_name: Name of the service that failed authentication
    service_name: Name of the service that failed authentication
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if service_name:
    if service_name:
    details["service_name"] = service_name
    details["service_name"] = service_name




    super().__init__(
    super().__init__(
    message=message, code="authentication_error", details=details, **kwargs
    message=message, code="authentication_error", details=details, **kwargs
    )
    )




    class PostNotFoundError(MarketingError):
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
    """
    Initialize the post not found error.
    Initialize the post not found error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    post_id: ID of the post that was not found
    post_id: ID of the post that was not found
    platform: Social media platform where the post should exist
    platform: Social media platform where the post should exist
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if post_id:
    if post_id:
    details["post_id"] = post_id
    details["post_id"] = post_id
    if platform:
    if platform:
    details["platform"] = platform
    details["platform"] = platform




    super().__init__(
    super().__init__(
    message=message, code="post_not_found_error", details=details, **kwargs
    message=message, code="post_not_found_error", details=details, **kwargs
    )
    )




    class PostingError(MarketingError):
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
    """
    Initialize the posting error.
    Initialize the posting error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    platform: The platform where the posting failed
    platform: The platform where the posting failed
    content_id: ID of the content that failed to post
    content_id: ID of the content that failed to post
    error_details: Additional details about the error
    error_details: Additional details about the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if platform:
    if platform:
    details["platform"] = platform
    details["platform"] = platform
    if content_id:
    if content_id:
    details["content_id"] = content_id
    details["content_id"] = content_id
    if error_details:
    if error_details:
    details["error_details"] = error_details
    details["error_details"] = error_details




    super().__init__(message=message, code="posting_error", details=details, **kwargs)
    super().__init__(message=message, code="posting_error", details=details, **kwargs)




    class DeletionError(MarketingError):
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
    """
    Initialize the deletion error.
    Initialize the deletion error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    content_type: Type of content that failed to delete
    content_type: Type of content that failed to delete
    content_id: ID of the content that failed to delete
    content_id: ID of the content that failed to delete
    platform: The platform where deletion failed
    platform: The platform where deletion failed
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if content_type:
    if content_type:
    details["content_type"] = content_type
    details["content_type"] = content_type
    if content_id:
    if content_id:
    details["content_id"] = content_id
    details["content_id"] = content_id
    if platform:
    if platform:
    details["platform"] = platform
    details["platform"] = platform




    super().__init__(message=message, code="deletion_error", details=details, **kwargs)
    super().__init__(message=message, code="deletion_error", details=details, **kwargs)




    class SchedulingError(MarketingError):
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
    """
    Initialize the scheduling error.
    Initialize the scheduling error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    content_id: ID of the content that failed to schedule
    content_id: ID of the content that failed to schedule
    schedule_time: The time when the content was supposed to be scheduled
    schedule_time: The time when the content was supposed to be scheduled
    platform: The platform where scheduling failed
    platform: The platform where scheduling failed
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if content_id:
    if content_id:
    details["content_id"] = content_id
    details["content_id"] = content_id
    if schedule_time:
    if schedule_time:
    details["schedule_time"] = schedule_time
    details["schedule_time"] = schedule_time
    if platform:
    if platform:
    details["platform"] = platform
    details["platform"] = platform




    super().__init__(message=message, code="scheduling_error", details=details, **kwargs)
    super().__init__(message=message, code="scheduling_error", details=details, **kwargs)




    class NotSupportedError(MarketingError):
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
    """
    Initialize the not supported error.
    Initialize the not supported error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    feature: The feature that is not supported
    feature: The feature that is not supported
    platform: The platform or context where the feature is not supported
    platform: The platform or context where the feature is not supported
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if feature:
    if feature:
    details["feature"] = feature
    details["feature"] = feature
    if platform:
    if platform:
    details["platform"] = platform
    details["platform"] = platform




    super().__init__(message=message, code="not_supported_error", details=details, **kwargs)
    super().__init__(message=message, code="not_supported_error", details=details, **kwargs)




    class PlatformNotSupportedError(Exception):
    class PlatformNotSupportedError(Exception):
    """Exception raised when a feature is not supported by a platform."""


    def __init__(self, platform: str, feature: str):
    self.platform = platform
    self.feature = feature
    super().__init__(f"Feature '{feature}' is not supported by platform '{platform}'")
