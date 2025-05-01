"""
Routes for the API server.

This module provides route handlers for the API server.
"""

from .niche_analysis import router as niche_analysis_router

__all__ = [
    "niche_analysis_router",
]
