"""
Middleware for the Flask application.

This module provides middleware for the Flask application.
"""

from .logging_middleware import init_app as init_logging_middleware

__all__ = ['init_logging_middleware']
