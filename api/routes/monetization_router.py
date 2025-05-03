"""
Monetization router for the API server.

This module re-exports the router from the monetization.py file.
"""


from .monetization import router



# Re-export the router
__all__ = ["router"]