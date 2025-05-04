"""
"""
Error handling for the Niche Analysis module.
Error handling for the Niche Analysis module.


This module provides custom exceptions and error handling utilities
This module provides custom exceptions and error handling utilities
specific to the Niche Analysis module.
specific to the Niche Analysis module.
"""
"""


import os
import os
import sys
import sys
from typing import Optional
from typing import Optional


# Add the project root to the Python path to import the errors module
# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from errors import (MarketAnalysisError, NicheAnalysisError,
from errors import (MarketAnalysisError, NicheAnalysisError,
OpportunityScoringError, ValidationError, handle_exception)
OpportunityScoringError, ValidationError, handle_exception)


# Re-export the error classes for convenience
# Re-export the error classes for convenience
__all__ = [
__all__ = [
"NicheAnalysisError",
"NicheAnalysisError",
"MarketAnalysisError",
"MarketAnalysisError",
"OpportunityScoringError",
"OpportunityScoringError",
"ValidationError",
"ValidationError",
"handle_exception",
"handle_exception",
"MarketSegmentError",
"MarketSegmentError",
"ProblemIdentificationError",
"ProblemIdentificationError",
"CompetitionAnalysisError",
"CompetitionAnalysisError",
"TrendAnalysisError",
"TrendAnalysisError",
"TargetUserAnalysisError",
"TargetUserAnalysisError",
]
]




class MarketSegmentError(MarketAnalysisError):
    class MarketSegmentError(MarketAnalysisError):
    """Error raised when there's an issue with market segment analysis."""


    def __init__(self, message: str, segment: Optional[str] = None, **kwargs):
    """
    """
    Initialize the market segment error.
    Initialize the market segment error.


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
    super().__init__(
    super().__init__(
    message=message, segment=segment, code="market_segment_error", **kwargs
    message=message, segment=segment, code="market_segment_error", **kwargs
    )
    )




    class ProblemIdentificationError(NicheAnalysisError):
    class ProblemIdentificationError(NicheAnalysisError):
    """Error raised when there's an issue with problem identification."""


    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
    """
    """
    Initialize the problem identification error.
    Initialize the problem identification error.


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




    super().__init__(
    super().__init__(
    message=message, code="problem_identification_error", details=details, **kwargs
    message=message, code="problem_identification_error", details=details, **kwargs
    )
    )




    class CompetitionAnalysisError(MarketAnalysisError):
    class CompetitionAnalysisError(MarketAnalysisError):
    """Error raised when there's an issue with competition analysis."""


    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
    """
    """
    Initialize the competition analysis error.
    Initialize the competition analysis error.


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




    super().__init__(
    super().__init__(
    message=message, code="competition_analysis_error", details=details, **kwargs
    message=message, code="competition_analysis_error", details=details, **kwargs
    )
    )




    class TrendAnalysisError(MarketAnalysisError):
    class TrendAnalysisError(MarketAnalysisError):
    """Error raised when there's an issue with trend analysis."""


    def __init__(self, message: str, segment: Optional[str] = None, **kwargs):
    """
    """
    Initialize the trend analysis error.
    Initialize the trend analysis error.


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
    super().__init__(
    super().__init__(
    message=message, segment=segment, code="trend_analysis_error", **kwargs
    message=message, segment=segment, code="trend_analysis_error", **kwargs
    )
    )




    class TargetUserAnalysisError(MarketAnalysisError):
    class TargetUserAnalysisError(MarketAnalysisError):
    """Error raised when there's an issue with target user analysis."""


    def __init__(self, message: str, niche: Optional[str] = None, **kwargs):
    """
    """
    Initialize the target user analysis error.
    Initialize the target user analysis error.


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




    super().__init__(
    super().__init__(
    message=message, code="target_user_analysis_error", details=details, **kwargs
    message=message, code="target_user_analysis_error", details=details, **kwargs
    )
    )

