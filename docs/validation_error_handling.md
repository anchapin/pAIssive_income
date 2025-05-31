# Validation Error Handling

This document describes how validation errors are handled in the pAIssive_income project.

## Overview

The project uses Pydantic for data validation. When validation errors occur, they are handled by the `ValidationError` class in `common_utils/validation/core.py`.

## ValidationError Class

The `ValidationError` class is used to represent validation errors in the project. It has the following attributes:

- `message`: A human-readable error message
- `details`: A list of error details, each containing:
  - `field`: The field that failed validation
  - `message`: A human-readable error message for the field
  - `type`: The type of validation error

## Error Formatting

The `format_validation_error` function is used to format Pydantic validation errors into a standardized format. It takes a Pydantic validation error and returns a list of formatted error details.

```python
def format_validation_error(error: PydanticValidationError) -> List[Dict[str, Any]]:
    """
    Format a Pydantic validation error into a standardized format.

    Args:
        error: The PydanticValidationError instance.

    Returns:
        List of formatted error details.
    """
    formatted_errors = []

    for err in error.errors():
        # Extract field and error message
        loc = err.get("loc", [])
        field = ".".join(str(item) for item in loc) if loc else "unknown"
        err_message = err.get("msg", "Invalid value")
        err_type = err.get("type", "validation_error")

        formatted_errors.append({
            "field": field,
            "message": err_message,
            "type": err_type
        })

    return formatted_errors
```

## Error Response

The `validation_error_response` function is used to create a standardized error response for validation errors. It takes a validation error and returns a dictionary with the following structure:

```python
{
    "error_code": "validation_error",
    "message": "Validation error",
    "errors": [
        {
            "field": "name",
            "message": "Field required",
            "type": "missing"
        }
    ]
}
```

## Usage

### In Config Loader

The `load_config` function in `common_utils/config_loader.py` uses the `ValidationError` class to handle validation errors when loading configuration files.

```python
try:
    # Validate the config against the model
    config_instance = model(**config_data)
    return config_instance
except PydanticValidationError as e:
    # Format the validation error
    error_details = format_validation_error(e)
    
    # Create a ValidationError instance
    validation_error = ValidationError(
        message="Invalid configuration",
        details=error_details
    )
    
    # Log the error
    logger.error(f"Validation error: {validation_error.message}")
    for error in validation_error.details:
        logger.error(f"  {error['field']}: {error['message']}")
    
    # Raise the error
    raise validation_error
```

### In API Endpoints

The `validation_error_response` function can be used in API endpoints to create standardized error responses for validation errors.

```python
@app.exception_handler(ValidationError)
def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=validation_error_response(exc)
    )
```

## Best Practices

1. Always use the `ValidationError` class to represent validation errors
2. Use the `format_validation_error` function to format Pydantic validation errors
3. Use the `validation_error_response` function to create standardized error responses
4. Log validation errors with sufficient detail for debugging
