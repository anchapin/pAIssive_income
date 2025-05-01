"""
Error classes for the market analysis module.
"""

from typing import Optional, Dict, Any


class MarketAnalysisError(Exception):
    """Base exception for all market analysis errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            error_code: Optional error code
            details: Optional error details
        """
        self.message = message
        self.error_code = error_code or "MARKET_ANALYSIS_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class CompetitiveIntelligenceError(MarketAnalysisError):
    """Exception raised for errors in competitive intelligence operations."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            error_code: Optional error code
            details: Optional error details
        """
        error_code = error_code or "COMPETITIVE_INTELLIGENCE_ERROR"
        super().__init__(message, error_code, details)


class MarketTrendError(MarketAnalysisError):
    """Exception raised for errors in market trend analysis."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            error_code: Optional error code
            details: Optional error details
        """
        error_code = error_code or "MARKET_TREND_ERROR"
        super().__init__(message, error_code, details)


class InvalidDataError(MarketAnalysisError):
    """Exception raised for invalid data provided to market analysis functions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            error_code: Optional error code
            details: Optional error details
        """
        error_code = error_code or "INVALID_DATA_ERROR"
        super().__init__(message, error_code, details)


class InsufficientDataError(MarketAnalysisError):
    """Exception raised when there is not enough data for analysis."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            error_code: Optional error code
            details: Optional error details
        """
        error_code = error_code or "INSUFFICIENT_DATA_ERROR"
        super().__init__(message, error_code, details)
