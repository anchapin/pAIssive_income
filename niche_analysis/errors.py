"""
Error handling for the Niche Analysis module.

This module provides custom exceptions and error handling utilities
specific to the Niche Analysis module.
"""

import sys
import os
from typing import Optional

# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from errors import (
    NicheAnalysisError,
    MarketAnalysisError,
    OpportunityScoringError,
    ValidationError,
    handle_exception,
)

# Re-export the error classes for convenience
__all__ = [
    "NicheAnalysisError",
    "MarketAnalysisError",
    "OpportunityScoringError",
    "ValidationError",
    "handle_exception",
    "MarketSegmentError",
    "ProblemIdentificationError",
    "CompetitionAnalysisError",
    "TrendAnalysisError",
    "TargetUserAnalysisError",
]


class MarketSegmentError(MarketAnalysisError):
    """Error raised when there's an issue with market segment analysis."""

    def __init__(self, message: str, segment: Optional[str] = None, **kwargs):
        """
        Initialize the market segment error.

        Args:
            message: Human-readable error message
            segment: Market segment that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message, segment=segment, code="market_segment_error", **kwargs
        )


class ProblemIdentificationError(NicheAnalysisError):
    """Error raised when there's an issue with problem identification."""

    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
        """
        Initialize the problem identification error.

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
            code="problem_identification_error",
            details=details,
            **kwargs
        )


class CompetitionAnalysisError(MarketAnalysisError):
    """Error raised when there's an issue with competition analysis."""

    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
        """
        Initialize the competition analysis error.

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
            code="competition_analysis_error",
            details=details,
            **kwargs
        )


class TrendAnalysisError(MarketAnalysisError):
    """Error raised when there's an issue with trend analysis."""

    def __init__(self, message: str, segment: Optional[str] = None, **kwargs):
        """
        Initialize the trend analysis error.

        Args:
            message: Human-readable error message
            segment: Market segment that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message, segment=segment, code="trend_analysis_error", **kwargs
        )


class TargetUserAnalysisError(MarketAnalysisError):
    """Error raised when there's an issue with target user analysis."""

    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
        """
        Initialize the target user analysis error.

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
            code="target_user_analysis_error",
            details=details,
            **kwargs
        )
