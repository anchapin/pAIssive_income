"""decorators - Module for common_utils/validation.decorators."""

# Standard library imports
import functools
from typing import Callable, Type, TypeVar

# Third-party imports
from pydantic import BaseModel

# Local imports
from common_utils.logging import get_logger
from common_utils.validation.core import (
    ValidationError,
    validate_input,
    validation_error_response,
)

logger = get_logger(__name__)

# Type variable for the model
T = TypeVar("T", bound=BaseModel)


def validate_request_body(model_class: Type[T]) -> Callable:
    """
    Decorator to validate request body against a Pydantic model.

    Args:
        model_class: The Pydantic model class to validate against

    Returns:
        Decorated function

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            try:
                # Get the request body as JSON
                request_data = await request.get_json()

                # Validate the request data against the model
                model_instance = validate_input(model_class, request_data)

                # Call the original function with the validated model
                return await func(request, model_instance, *args, **kwargs)

            except ValidationError as e:
                # Return a validation error response
                logger.warning(f"Validation error: {e!s}")
                return validation_error_response(e)

            except Exception as e:
                # Handle other exceptions
                logger.error(f"Error processing request: {e!s}")
                return {
                    "errors": [
                        {
                            "message": "An error occurred processing the request",
                            "details": str(e)
                        }
                    ]
                }

        return wrapper
    return decorator


def validate_query_params(model_class: Type[T]) -> Callable:
    """
    Decorator to validate query parameters against a Pydantic model.

    Args:
        model_class: The Pydantic model class to validate against

    Returns:
        Decorated function

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            try:
                # Get the query parameters as a dict
                query_params = dict(request.query_params)

                # Validate the query parameters against the model
                model_instance = validate_input(model_class, query_params)

                # Call the original function with the validated model
                return await func(request, model_instance, *args, **kwargs)

            except ValidationError as e:
                # Return a validation error response
                logger.warning(f"Query parameter validation error: {e!s}")
                return validation_error_response(e)

            except Exception as e:
                # Handle other exceptions
                logger.error(f"Error processing request: {e!s}")
                return {
                    "errors": [
                        {
                            "message": "An error occurred processing the request",
                            "details": str(e)
                        }
                    ]
                }

        return wrapper
    return decorator


def validate_path_params(model_class: Type[T]) -> Callable:
    """
    Decorator to validate path parameters against a Pydantic model.

    Args:
        model_class: The Pydantic model class to validate against

    Returns:
        Decorated function

    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            try:
                # Get the path parameters as a dict
                path_params = dict(request.path_params)

                # Validate the path parameters against the model
                model_instance = validate_input(model_class, path_params)

                # Call the original function with the validated model
                return await func(request, model_instance, *args, **kwargs)

            except ValidationError as e:
                # Return a validation error response
                logger.warning(f"Path parameter validation error: {e!s}")
                return validation_error_response(e)

            except Exception as e:
                # Handle other exceptions
                logger.error(f"Error processing request: {e!s}")
                return {
                    "errors": [
                        {
                            "message": "An error occurred processing the request",
                            "details": str(e)
                        }
                    ]
                }

        return wrapper
    return decorator
