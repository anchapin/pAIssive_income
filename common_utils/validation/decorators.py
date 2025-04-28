"""
Decorators for input validation on API endpoints.

This module provides decorators that can be used to validate inputs for API endpoints.
"""

import functools
from typing import Dict, Any, Callable
from flask import request, jsonify

from .schemas import validate_api_request
from .exceptions import ValidationError


def validate_request(schema: Dict[str, Any]):
    """
    Decorator to validate API requests against a schema.
    
    Args:
        schema: Schema definition for request validation
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = validate_api_request(request, schema)
            if not result.valid:
                error = ValidationError(
                    message="Invalid request data",
                    validation_errors=result.errors
                )
                return jsonify(error.to_dict()), error.http_status
            return func(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_input(func: Callable):
    """
    Decorator to sanitize input data to prevent security issues.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.is_json:
            data = request.get_json()
            # Apply sanitization to string values
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str):
                        # Basic sanitization - remove script tags
                        data[key] = value.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")
            
        return func(*args, **kwargs)
    return wrapper