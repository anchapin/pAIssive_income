"""
Centralized error handling module for the pAIssive Income project.

This module provides custom exception classes and error handling utilities
for consistent error management across the project.
"""

from typing import Dict, Any, Optional, List, Type, Union
import logging
import traceback
import sys
import json
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class BaseError(Exception):
    """Base exception class for all custom exceptions in the project."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: int = 500,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize the base error.

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional error details
            http_status: HTTP status code for API responses
            original_exception: Original exception if this is a wrapper
        """
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.http_status = http_status
        self.original_exception = original_exception
        self.timestamp = datetime.now().isoformat()

        # Add traceback information if available
        if original_exception:
            self.details["original_error"] = str(original_exception)
            self.details["original_error_type"] = original_exception.__class__.__name__

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        }

    def to_json(self) -> str:
        """
        Convert the error to a JSON string.

        Returns:
            JSON string representation of the error
        """
        return json.dumps(self.to_dict(), indent=2)

    def log(self, level: int = logging.ERROR) -> None:
        """
        Log the error.

        Args:
            level: Logging level
        """
        logger.log(level, f"{self.code}: {self.message}", exc_info=self.original_exception)


# Configuration Errors

class ConfigurationError(BaseError):
    """Error raised when there's an issue with configuration."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the configuration error.

        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            code="configuration_error",
            details=details,
            http_status=500,
            **kwargs
        )


class ValidationError(BaseError):
    """Error raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """
        Initialize the validation error.

        Args:
            message: Human-readable error message
            field: The field that failed validation
            validation_errors: List of validation errors
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(
            message=message,
            code="validation_error",
            details=details,
            http_status=400,
            **kwargs
        )


# AI Model Errors

class ModelError(BaseError):
    """Base class for all model-related errors."""

    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the model error.

        Args:
            message: Human-readable error message
            model_id: ID of the model that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if model_id:
            details["model_id"] = model_id

        super().__init__(
            message=message,
            code="model_error",
            details=details,
            http_status=500,
            **kwargs
        )


class ModelNotFoundError(ModelError):
    """Error raised when a model is not found."""

    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the model not found error.

        Args:
            message: Human-readable error message
            model_id: ID of the model that was not found
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            model_id=model_id,
            code="model_not_found",
            http_status=404,
            **kwargs
        )


class ModelLoadError(ModelError):
    """Error raised when a model fails to load."""

    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the model load error.

        Args:
            message: Human-readable error message
            model_id: ID of the model that failed to load
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            model_id=model_id,
            code="model_load_error",
            **kwargs
        )


class ModelInferenceError(ModelError):
    """Error raised when model inference fails."""

    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the model inference error.

        Args:
            message: Human-readable error message
            model_id: ID of the model that failed during inference
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            model_id=model_id,
            code="model_inference_error",
            **kwargs
        )


class ModelDownloadError(ModelError):
    """Error raised when model download fails."""

    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        source: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the model download error.

        Args:
            message: Human-readable error message
            model_id: ID of the model that failed to download
            source: Source of the model download
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if source:
            details["source"] = source

        super().__init__(
            message=message,
            model_id=model_id,
            code="model_download_error",
            details=details,
            **kwargs
        )


# Monetization Errors

class MonetizationError(BaseError):
    """Base class for all monetization-related errors."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the monetization error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="monetization_error",
            http_status=500,
            **kwargs
        )


class SubscriptionError(MonetizationError):
    """Error raised when there's an issue with subscriptions."""

    def __init__(
        self,
        message: str,
        subscription_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the subscription error.

        Args:
            message: Human-readable error message
            subscription_id: ID of the subscription
            user_id: ID of the user
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if subscription_id:
            details["subscription_id"] = subscription_id
        if user_id:
            details["user_id"] = user_id

        super().__init__(
            message=message,
            code="subscription_error",
            details=details,
            **kwargs
        )


class PaymentError(MonetizationError):
    """Error raised when there's an issue with payments."""

    def __init__(
        self,
        message: str,
        transaction_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the payment error.

        Args:
            message: Human-readable error message
            transaction_id: ID of the transaction
            payment_method: Payment method used
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if transaction_id:
            details["transaction_id"] = transaction_id
        if payment_method:
            details["payment_method"] = payment_method

        super().__init__(
            message=message,
            code="payment_error",
            details=details,
            **kwargs
        )


# Niche Analysis Errors

class NicheAnalysisError(BaseError):
    """Base class for all niche analysis-related errors."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the niche analysis error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="niche_analysis_error",
            http_status=500,
            **kwargs
        )


class MarketAnalysisError(NicheAnalysisError):
    """Error raised when market analysis fails."""

    def __init__(
        self,
        message: str,
        segment: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the market analysis error.

        Args:
            message: Human-readable error message
            segment: Market segment that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if segment:
            details["segment"] = segment

        super().__init__(
            message=message,
            code="market_analysis_error",
            details=details,
            **kwargs
        )


class OpportunityScoringError(NicheAnalysisError):
    """Error raised when opportunity scoring fails."""

    def __init__(
        self,
        message: str,
        niche: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the opportunity scoring error.

        Args:
            message: Human-readable error message
            niche: Niche that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if niche:
            details["niche"] = niche

        super().__init__(
            message=message,
            code="opportunity_scoring_error",
            details=details,
            **kwargs
        )


# Agent Team Errors

class AgentTeamError(BaseError):
    """Base class for all agent team-related errors."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the agent team error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="agent_team_error",
            http_status=500,
            **kwargs
        )


class AgentError(AgentTeamError):
    """Error raised when an agent operation fails."""

    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the agent error.

        Args:
            message: Human-readable error message
            agent_name: Name of the agent that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if agent_name:
            details["agent_name"] = agent_name

        super().__init__(
            message=message,
            code="agent_error",
            details=details,
            **kwargs
        )


# Marketing Errors

class MarketingError(BaseError):
    """Base class for all marketing-related errors."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the marketing error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        # Only set code if it's not already provided in kwargs
        if 'code' not in kwargs:
            kwargs['code'] = "marketing_error"

        super().__init__(
            message=message,
            http_status=500,
            **kwargs
        )


class StrategyGenerationError(MarketingError):
    """Error raised when strategy generation fails."""

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
            strategy_type: Type of strategy that failed to generate
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if strategy_type:
            details["strategy_type"] = strategy_type

        # Only set code if it's not already provided in kwargs
        if 'code' not in kwargs:
            kwargs['code'] = "strategy_generation_error"

        super().__init__(
            message=message,
            details=details,
            **kwargs
        )


# UI Errors

class UIError(BaseError):
    """Base class for all UI-related errors."""

    def __init__(
        self,
        message: str,
        **kwargs
    ):
        """
        Initialize the UI error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            code="ui_error",
            http_status=500,
            **kwargs
        )


class APIError(UIError):
    """Error raised when an API operation fails."""

    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the API error.

        Args:
            message: Human-readable error message
            endpoint: API endpoint that caused the error
            method: HTTP method used
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if endpoint:
            details["endpoint"] = endpoint
        if method:
            details["method"] = method

        super().__init__(
            message=message,
            code="api_error",
            details=details,
            **kwargs
        )


# Error handling utilities

def handle_exception(
    exception: Exception,
    log_level: int = logging.ERROR,
    reraise: bool = True,
    error_class: Type[BaseError] = BaseError,
    message: Optional[str] = None,
    **kwargs
) -> BaseError:
    """
    Handle an exception by converting it to a custom error and logging it.

    Args:
        exception: The exception to handle
        log_level: Logging level
        reraise: Whether to reraise the exception
        error_class: Custom error class to use
        message: Optional custom error message (overrides the exception message)
        **kwargs: Additional arguments to pass to the error class constructor

    Returns:
        Custom error instance

    Raises:
        The custom error if reraise is True
    """
    # If it's already a BaseError, just log it and reraise if needed
    if isinstance(exception, BaseError):
        exception.log(log_level)
        if reraise:
            raise exception
        return exception

    # Create a custom error from the exception
    error = error_class(
        message=message if message is not None else str(exception),
        original_exception=exception,
        **kwargs
    )

    # Log the error
    error.log(log_level)

    # Reraise if needed
    if reraise:
        raise error

    return error


def error_to_response(error: Union[BaseError, Exception]) -> Dict[str, Any]:
    """
    Convert an error to an API response.

    Args:
        error: The error to convert

    Returns:
        API response dictionary
    """
    if isinstance(error, BaseError):
        return error.to_dict()

    # Convert standard exception to BaseError
    base_error = BaseError(
        message=str(error),
        code=error.__class__.__name__,
        original_exception=error
    )

    return base_error.to_dict()
