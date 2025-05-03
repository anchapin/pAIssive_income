"""
Analytics router for the API server.

This module re - exports the router from the analytics.py file.
"""

from .analytics import router

# Re - export the router
__all__ = ["router"]
