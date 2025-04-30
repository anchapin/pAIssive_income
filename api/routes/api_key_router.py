"""
API Key router for the API server.

This module re-exports the router from the api_key.py file.
"""

from .api_key import router

# Re-export the router
__all__ = ['router']
