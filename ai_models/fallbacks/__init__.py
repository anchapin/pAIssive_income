"""
This module provides classes and utilities for managing model fallbacks
when primary model selection fails. It includes configurable strategies
for selecting alternative models based on various criteria.
"""

from .fallback_strategy import FallbackEvent, FallbackManager, FallbackStrategy

__all__ = ["FallbackEvent", "FallbackManager", "FallbackStrategy"]
