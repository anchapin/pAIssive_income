"""
"""
Centralized error handling module for the pAIssive Income project.
Centralized error handling module for the pAIssive Income project.


This module provides custom exception classes and error handling utilities
This module provides custom exception classes and error handling utilities
for consistent error management across the project.
for consistent error management across the project.
"""
"""


import json
import json
import logging
import logging
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union
from typing import Any, Dict, List, Optional, Type, Union


from monetization.errors import MonetizationError
from monetization.errors import MonetizationError


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class BaseError(Exception):
    class BaseError(Exception):
    """Base exception class for all custom exceptions in the project."""

    def __init__(
    self,
    message: str,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    http_status: int = 500,
    original_exception: Optional[Exception] = None,
    ):
    """
    """
    Initialize the base error.
    Initialize the base error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    code: Error code for programmatic handling
    code: Error code for programmatic handling
    details: Additional error details
    details: Additional error details
    http_status: HTTP status code for API responses
    http_status: HTTP status code for API responses
    original_exception: Original exception if this is a wrapper
    original_exception: Original exception if this is a wrapper
    """
    """
    self.message = message
    self.message = message
    # Use provided code if available, otherwise use class name
    # Use provided code if available, otherwise use class name
    self.code = code or self.__class__.__name__
    self.code = code or self.__class__.__name__
    self.details = details or {}
    self.details = details or {}
    self.http_status = http_status
    self.http_status = http_status
    self.original_exception = original_exception
    self.original_exception = original_exception
    self.timestamp = datetime.now().isoformat()
    self.timestamp = datetime.now().isoformat()


    # Add traceback information if available
    # Add traceback information if available
    if original_exception:
    if original_exception:
    self.details["original_error"] = str(original_exception)
    self.details["original_error"] = str(original_exception)
    self.details["original_error_type"] = original_exception.__class__.__name__
    self.details["original_error_type"] = original_exception.__class__.__name__


    super().__init__(self.message)
    super().__init__(self.message)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the error to a dictionary.
    Convert the error to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the error
    Dictionary representation of the error
    """
    """
    return {
    return {
    "error": {
    "error": {
    "code": self.code,
    "code": self.code,
    "message": self.message,
    "message": self.message,
    "details": self.details,
    "details": self.details,
    "timestamp": self.timestamp,
    "timestamp": self.timestamp,
    }
    }
    }
    }


    def to_json(self) -> str:
    def to_json(self) -> str:
    """
    """
    Convert the error to a JSON string.
    Convert the error to a JSON string.


    Returns:
    Returns:
    JSON string representation of the error
    JSON string representation of the error
    """
    """
    return json.dumps(self.to_dict(), indent=2)
    return json.dumps(self.to_dict(), indent=2)


    def log(self, level: int = logging.ERROR) -> None:
    def log(self, level: int = logging.ERROR) -> None:
    """
    """
    Log the error.
    Log the error.


    Args:
    Args:
    level: Logging level
    level: Logging level
    """
    """
    logger.log(
    logger.log(
    level, f"{self.code}: {self.message}", exc_info=self.original_exception
    level, f"{self.code}: {self.message}", exc_info=self.original_exception
    )
    )




    # Configuration Errors
    # Configuration Errors




    class ConfigurationError(BaseError):
    class ConfigurationError(BaseError):
    """Error raised when there's an issue with configuration."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
    """
    """
    Initialize the configuration error.
    Initialize the configuration error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    config_key: The configuration key that caused the error
    config_key: The configuration key that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if config_key:
    if config_key:
    details["config_key"] = config_key
    details["config_key"] = config_key


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "configuration_error"
    kwargs["code"] = "configuration_error"


    super().__init__(message=message, details=details, http_status=500, **kwargs)
    super().__init__(message=message, details=details, http_status=500, **kwargs)




    class ValidationError(BaseError):
    class ValidationError(BaseError):
    """Error raised when validation fails."""

    def __init__(
    self,
    message: str,
    field: Optional[str] = None,
    validation_errors: Optional[List[Dict[str, Any]]] = None,
    **kwargs,
    ):
    """
    """
    Initialize the validation error.
    Initialize the validation error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    field: The field that failed validation
    field: The field that failed validation
    validation_errors: List of validation errors
    validation_errors: List of validation errors
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if field:
    if field:
    details["field"] = field
    details["field"] = field
    if validation_errors:
    if validation_errors:
    details["validation_errors"] = validation_errors
    details["validation_errors"] = validation_errors


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "validation_error"
    kwargs["code"] = "validation_error"


    super().__init__(message=message, details=details, http_status=400, **kwargs)
    super().__init__(message=message, details=details, http_status=400, **kwargs)




    # AI Model Errors
    # AI Model Errors




    class ModelError(BaseError):
    class ModelError(BaseError):
    """Base class for all model-related errors."""

    def __init__(self, message: str, model_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the model error.
    Initialize the model error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    model_id: ID of the model that caused the error
    model_id: ID of the model that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if model_id:
    if model_id:
    details["model_id"] = model_id
    details["model_id"] = model_id


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "model_error"
    kwargs["code"] = "model_error"


    super().__init__(message=message, details=details, http_status=500, **kwargs)
    super().__init__(message=message, details=details, http_status=500, **kwargs)




    class ModelNotFoundError(ModelError):
    class ModelNotFoundError(ModelError):
    """Error raised when a model is not found."""

    def __init__(self, message: str, model_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the model not found error.
    Initialize the model not found error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    model_id: ID of the model that was not found
    model_id: ID of the model that was not found
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "model_not_found"
    kwargs["code"] = "model_not_found"


    super().__init__(message=message, model_id=model_id, http_status=404, **kwargs)
    super().__init__(message=message, model_id=model_id, http_status=404, **kwargs)




    class ModelLoadError(ModelError):
    class ModelLoadError(ModelError):
    """Error raised when a model fails to load."""

    def __init__(self, message: str, model_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the model load error.
    Initialize the model load error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    model_id: ID of the model that failed to load
    model_id: ID of the model that failed to load
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "model_load_error"
    kwargs["code"] = "model_load_error"


    super().__init__(message=message, model_id=model_id, **kwargs)
    super().__init__(message=message, model_id=model_id, **kwargs)




    class ModelInferenceError(ModelError):
    class ModelInferenceError(ModelError):
    """Error raised when model inference fails."""

    def __init__(self, message: str, model_id: Optional[str] = None, **kwargs):
    """
    """
    Initialize the model inference error.
    Initialize the model inference error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    model_id: ID of the model that failed during inference
    model_id: ID of the model that failed during inference
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "model_inference_error"
    kwargs["code"] = "model_inference_error"


    super().__init__(message=message, model_id=model_id, **kwargs)
    super().__init__(message=message, model_id=model_id, **kwargs)




    class ModelAPIError(ModelError):
    class ModelAPIError(ModelError):
    """Error raised when there's an issue with the model API."""

    def __init__(
    self,
    message: str,
    model_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    **kwargs,
    ):
    """
    """
    Initialize the model API error.
    Initialize the model API error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    model_id: ID of the model that had an API issue
    model_id: ID of the model that had an API issue
    endpoint: API endpoint that caused the error
    endpoint: API endpoint that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if endpoint:
    if endpoint:
    details["endpoint"] = endpoint
    details["endpoint"] = endpoint


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "model_api_error"
    kwargs["code"] = "model_api_error"


    super().__init__(message=message, model_id=model_id, details=details, **kwargs)
    super().__init__(message=message, model_id=model_id, details=details, **kwargs)




    class ModelDownloadError(ModelError):
    class ModelDownloadError(ModelError):
    """Error raised when model download fails."""

    def __init__(
    self,
    message: str,
    model_id: Optional[str] = None,
    source: Optional[str] = None,
    **kwargs,
    ):
    """
    """
    Initialize the model download error.
    Initialize the model download error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    model_id: ID of the model that failed to download
    model_id: ID of the model that failed to download
    source: Source of the model download
    source: Source of the model download
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if source:
    if source:
    details["source"] = source
    details["source"] = source


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "model_download_error"
    kwargs["code"] = "model_download_error"


    super().__init__(message=message, model_id=model_id, details=details, **kwargs)
    super().__init__(message=message, model_id=model_id, details=details, **kwargs)




    # Monetization Errors
    # Monetization Errors




    class MonetizationError(BaseError):
    class MonetizationError(BaseError):
    """Base class for all monetization-related errors."""

    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the monetization error.
    Initialize the monetization error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "monetization_error"
    kwargs["code"] = "monetization_error"


    super().__init__(message=message, http_status=500, **kwargs)
    super().__init__(message=message, http_status=500, **kwargs)




    class SubscriptionError(MonetizationError):
    class SubscriptionError(MonetizationError):
    """Error raised when there's an issue with subscriptions."""

    def __init__(
    self,
    message: str,
    subscription_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs,
    ):
    """
    """
    Initialize the subscription error.
    Initialize the subscription error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    user_id: ID of the user
    user_id: ID of the user
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if subscription_id:
    if subscription_id:
    details["subscription_id"] = subscription_id
    details["subscription_id"] = subscription_id
    if user_id:
    if user_id:
    details["user_id"] = user_id
    details["user_id"] = user_id


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "subscription_error"
    kwargs["code"] = "subscription_error"


    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    class PaymentError(MonetizationError):
    class PaymentError(MonetizationError):
    """Error raised when there's an issue with payments."""

    def __init__(
    self,
    message: str,
    transaction_id: Optional[str] = None,
    payment_method: Optional[str] = None,
    **kwargs,
    ):
    """
    """
    Initialize the payment error.
    Initialize the payment error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction
    payment_method: Payment method used
    payment_method: Payment method used
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if transaction_id:
    if transaction_id:
    details["transaction_id"] = transaction_id
    details["transaction_id"] = transaction_id
    if payment_method:
    if payment_method:
    details["payment_method"] = payment_method
    details["payment_method"] = payment_method


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "payment_error"
    kwargs["code"] = "payment_error"


    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    # Niche Analysis Errors
    # Niche Analysis Errors




    class NicheAnalysisError(BaseError):
    class NicheAnalysisError(BaseError):
    """Base class for all niche analysis-related errors."""

    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the niche analysis error.
    Initialize the niche analysis error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "niche_analysis_error"
    kwargs["code"] = "niche_analysis_error"


    super().__init__(message=message, http_status=500, **kwargs)
    super().__init__(message=message, http_status=500, **kwargs)




    class MarketAnalysisError(NicheAnalysisError):
    class MarketAnalysisError(NicheAnalysisError):
    """Error raised when market analysis fails."""

    def __init__(self, message: str, segment: Optional[str] = None, **kwargs):
    """
    """
    Initialize the market analysis error.
    Initialize the market analysis error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    segment: Market segment that caused the error
    segment: Market segment that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if segment:
    if segment:
    details["segment"] = segment
    details["segment"] = segment


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "market_analysis_error"
    kwargs["code"] = "market_analysis_error"


    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    class OpportunityScoringError(NicheAnalysisError):
    class OpportunityScoringError(NicheAnalysisError):
    """Error raised when opportunity scoring fails."""

    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
    """
    """
    Initialize the opportunity scoring error.
    Initialize the opportunity scoring error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    niche: Niche that caused the error
    niche: Niche that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if niche:
    if niche:
    details["niche"] = niche
    details["niche"] = niche


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "opportunity_scoring_error"
    kwargs["code"] = "opportunity_scoring_error"


    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    # Agent Team Errors
    # Agent Team Errors




    class AgentTeamError(BaseError):
    class AgentTeamError(BaseError):
    """Base class for all agent team-related errors."""

    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the agent team error.
    Initialize the agent team error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "agent_team_error"
    kwargs["code"] = "agent_team_error"


    super().__init__(message=message, http_status=500, **kwargs)
    super().__init__(message=message, http_status=500, **kwargs)




    class AgentError(AgentTeamError):
    class AgentError(AgentTeamError):
    """Error raised when an agent operation fails."""

    def __init__(self, message: str, agent_name: Optional[str] = None, **kwargs):
    """
    """
    Initialize the agent error.
    Initialize the agent error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    agent_name: Name of the agent that caused the error
    agent_name: Name of the agent that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if agent_name:
    if agent_name:
    details["agent_name"] = agent_name
    details["agent_name"] = agent_name


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "agent_error"
    kwargs["code"] = "agent_error"


    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    # Marketing Errors
    # Marketing Errors




    class MarketingError(BaseError):
    class MarketingError(BaseError):
    """Base class for all marketing-related errors."""

    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the marketing error.
    Initialize the marketing error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "marketing_error"
    kwargs["code"] = "marketing_error"


    super().__init__(message=message, http_status=500, **kwargs)
    super().__init__(message=message, http_status=500, **kwargs)




    # UI Errors
    # UI Errors




    class UIError(BaseError):
    class UIError(BaseError):
    """Base class for all UI-related errors."""

    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the UI error.
    Initialize the UI error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "ui_error"
    kwargs["code"] = "ui_error"


    super().__init__(message=message, http_status=500, **kwargs)
    super().__init__(message=message, http_status=500, **kwargs)




    class APIError(UIError):
    class APIError(UIError):
    """Error raised when an API operation fails."""

    def __init__(
    self,
    message: str,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    **kwargs,
    ):
    """
    """
    Initialize the API error.
    Initialize the API error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    endpoint: API endpoint that caused the error
    endpoint: API endpoint that caused the error
    method: HTTP method used
    method: HTTP method used
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if endpoint:
    if endpoint:
    details["endpoint"] = endpoint
    details["endpoint"] = endpoint
    if method:
    if method:
    details["method"] = method
    details["method"] = method


    # Only set code if it's not already provided in kwargs
    # Only set code if it's not already provided in kwargs
    if "code" not in kwargs:
    if "code" not in kwargs:
    kwargs["code"] = "api_error"
    kwargs["code"] = "api_error"


    super().__init__(message=message, details=details, **kwargs)
    super().__init__(message=message, details=details, **kwargs)




    # Error handling utilities
    # Error handling utilities




    def handle_exception(
    def handle_exception(
    exception: Exception,
    exception: Exception,
    log_level: int = logging.ERROR,
    log_level: int = logging.ERROR,
    reraise: bool = True,
    reraise: bool = True,
    error_class: Type[BaseError] = BaseError,
    error_class: Type[BaseError] = BaseError,
    message: Optional[str] = None,
    message: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> BaseError:
    ) -> BaseError:
    """
    """
    Handle an exception by converting it to a custom error and logging it.
    Handle an exception by converting it to a custom error and logging it.


    Args:
    Args:
    exception: The exception to handle
    exception: The exception to handle
    log_level: Logging level
    log_level: Logging level
    reraise: Whether to reraise the exception
    reraise: Whether to reraise the exception
    error_class: Custom error class to use
    error_class: Custom error class to use
    message: Optional custom error message (overrides the exception message)
    message: Optional custom error message (overrides the exception message)
    **kwargs: Additional arguments to pass to the error class constructor
    **kwargs: Additional arguments to pass to the error class constructor


    Returns:
    Returns:
    Custom error instance
    Custom error instance


    Raises:
    Raises:
    The custom error if reraise is True
    The custom error if reraise is True
    """
    """
    # If it's already a BaseError, just log it and reraise if needed
    # If it's already a BaseError, just log it and reraise if needed
    if isinstance(exception, BaseError):
    if isinstance(exception, BaseError):
    exception.log(log_level)
    exception.log(log_level)
    if reraise:
    if reraise:
    raise exception
    raise exception
    return exception
    return exception


    # Create a custom error from the exception
    # Create a custom error from the exception
    error = error_class(
    error = error_class(
    message=message if message is not None else str(exception),
    message=message if message is not None else str(exception),
    original_exception=exception,
    original_exception=exception,
    **kwargs,
    **kwargs,
    )
    )


    # Log the error
    # Log the error
    error.log(log_level)
    error.log(log_level)


    # Reraise if needed
    # Reraise if needed
    if reraise:
    if reraise:
    raise error
    raise error


    return error
    return error




    def error_to_response(error: Union[BaseError, Exception]) -> Dict[str, Any]:
    def error_to_response(error: Union[BaseError, Exception]) -> Dict[str, Any]:
    """
    """
    Convert an error to an API response.
    Convert an error to an API response.


    Args:
    Args:
    error: The error to convert
    error: The error to convert


    Returns:
    Returns:
    API response dictionary
    API response dictionary
    """
    """
    if isinstance(error, BaseError):
    if isinstance(error, BaseError):
    return error.to_dict()
    return error.to_dict()


    # Convert standard exception to BaseError
    # Convert standard exception to BaseError
    base_error = BaseError(
    base_error = BaseError(
    message=str(error), code=error.__class__.__name__, original_exception=error
    message=str(error), code=error.__class__.__name__, original_exception=error
    )
    )


    return base_error.to_dict()
    return base_error.to_dict()

