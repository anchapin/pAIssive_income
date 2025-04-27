"""
Error handling for the Monetization module.

This module provides custom exceptions and error handling utilities
specific to the Monetization module.
"""

import sys
import os
from typing import Dict, Any, Optional, List, Type, Union

# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from errors import (
    MonetizationError, SubscriptionError, PaymentError, 
    ValidationError, handle_exception
)

# Re-export the error classes for convenience
__all__ = [
    'MonetizationError',
    'SubscriptionError',
    'PaymentError',
    'ValidationError',
    'handle_exception',
    'TierNotFoundError',
    'FeatureNotFoundError',
    'PricingError',
    'RevenueProjectionError',
    'BillingError',
    'InvoiceError',
    'UsageTrackingError'
]


class TierNotFoundError(SubscriptionError):
    """Error raised when a subscription tier is not found."""
    
    def __init__(
        self, 
        message: str, 
        tier_id: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the tier not found error.
        
        Args:
            message: Human-readable error message
            tier_id: ID of the tier that was not found
            model_id: ID of the subscription model
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if tier_id:
            details["tier_id"] = tier_id
        if model_id:
            details["model_id"] = model_id
        
        super().__init__(
            message=message,
            code="tier_not_found",
            details=details,
            http_status=404,
            **kwargs
        )


class FeatureNotFoundError(SubscriptionError):
    """Error raised when a subscription feature is not found."""
    
    def __init__(
        self, 
        message: str, 
        feature_id: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the feature not found error.
        
        Args:
            message: Human-readable error message
            feature_id: ID of the feature that was not found
            model_id: ID of the subscription model
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if feature_id:
            details["feature_id"] = feature_id
        if model_id:
            details["model_id"] = model_id
        
        super().__init__(
            message=message,
            code="feature_not_found",
            details=details,
            http_status=404,
            **kwargs
        )


class PricingError(MonetizationError):
    """Error raised when there's an issue with pricing calculations."""
    
    def __init__(
        self, 
        message: str, 
        calculator_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the pricing error.
        
        Args:
            message: Human-readable error message
            calculator_id: ID of the pricing calculator
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if calculator_id:
            details["calculator_id"] = calculator_id
        
        super().__init__(
            message=message,
            code="pricing_error",
            details=details,
            **kwargs
        )


class RevenueProjectionError(MonetizationError):
    """Error raised when there's an issue with revenue projections."""
    
    def __init__(
        self, 
        message: str, 
        projector_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the revenue projection error.
        
        Args:
            message: Human-readable error message
            projector_id: ID of the revenue projector
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if projector_id:
            details["projector_id"] = projector_id
        
        super().__init__(
            message=message,
            code="revenue_projection_error",
            details=details,
            **kwargs
        )


class BillingError(MonetizationError):
    """Error raised when there's an issue with billing calculations."""
    
    def __init__(
        self, 
        message: str, 
        calculator_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the billing error.
        
        Args:
            message: Human-readable error message
            calculator_id: ID of the billing calculator
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if calculator_id:
            details["calculator_id"] = calculator_id
        
        super().__init__(
            message=message,
            code="billing_error",
            details=details,
            **kwargs
        )


class InvoiceError(MonetizationError):
    """Error raised when there's an issue with invoices."""
    
    def __init__(
        self, 
        message: str, 
        invoice_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the invoice error.
        
        Args:
            message: Human-readable error message
            invoice_id: ID of the invoice
            customer_id: ID of the customer
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if invoice_id:
            details["invoice_id"] = invoice_id
        if customer_id:
            details["customer_id"] = customer_id
        
        super().__init__(
            message=message,
            code="invoice_error",
            details=details,
            **kwargs
        )


class UsageTrackingError(MonetizationError):
    """Error raised when there's an issue with usage tracking."""
    
    def __init__(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        metric: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the usage tracking error.
        
        Args:
            message: Human-readable error message
            user_id: ID of the user
            metric: Usage metric
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if user_id:
            details["user_id"] = user_id
        if metric:
            details["metric"] = metric
        
        super().__init__(
            message=message,
            code="usage_tracking_error",
            details=details,
            **kwargs
        )
