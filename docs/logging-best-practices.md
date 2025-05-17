# Logging Best Practices

This document outlines the best practices for using logging in the pAIssive_income project, with a focus on proper logger initialization and usage.

## Table of Contents

1. [Introduction](#introduction)
2. [Logger Initialization](#logger-initialization)
3. [Common Pitfalls](#common-pitfalls)
4. [Logging Levels](#logging-levels)
5. [Structured Logging](#structured-logging)
6. [Performance Considerations](#performance-considerations)
7. [Testing and Debugging](#testing-and-debugging)
8. [Examples](#examples)

## Introduction

Proper logging is essential for debugging, monitoring, and understanding the behavior of our application. The pAIssive_income project uses Python's built-in `logging` module for all logging needs.

## Logger Initialization

### Always Initialize the Logger at the Top of the Module

The most important rule is to initialize the logger at the top of each module, immediately after imports and before any code that might use it:

```python
"""Module docstring."""

# Standard library imports
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
import some_library

# Local imports
from .some_module import SomeClass

# Rest of the module code...
```

### Use `__name__` for Logger Names

Always use `__name__` as the logger name to ensure that logs can be traced back to their source module:

```python
logger = logging.getLogger(__name__)
```

### Never Use the Root Logger Directly

Avoid using the root logger directly (`logging.info()`, `logging.error()`, etc.). Always use a module-specific logger:

```python
# Bad practice
logging.info("This uses the root logger")

# Good practice
logger = logging.getLogger(__name__)
logger.info("This uses a module-specific logger")
```

## Common Pitfalls

### Using Logging Before Initializing the Logger

A common mistake is using logging functions before initializing the logger:

```python
# Bad practice
import logging

# This will use the root logger, not a module-specific logger
logging.info("This is logged before initializing the logger")

# Logger initialized too late
logger = logging.getLogger(__name__)
```

### Forgetting to Import Logging

Another common mistake is forgetting to import the logging module:

```python
# Bad practice - missing import
logger = logging.getLogger(__name__)  # NameError: name 'logging' is not defined
```

### Using String Concatenation Instead of Formatting

Avoid string concatenation in log messages:

```python
# Bad practice
logger.info("User " + user_id + " logged in")

# Good practice
logger.info("User %s logged in", user_id)
# or
logger.info(f"User {user_id} logged in")
```

## Logging Levels

Use the appropriate logging level for each message:

- **DEBUG**: Detailed information, typically useful only for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: An indication that something unexpected happened, or may happen in the near future
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running

```python
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

## Structured Logging

For complex log messages, use structured logging with extra parameters:

```python
logger.info("User action", extra={
    "user_id": user_id,
    "action": "login",
    "ip_address": ip_address,
    "timestamp": timestamp
})
```

## Performance Considerations

### Use Lazy Evaluation for Expensive Operations

If constructing a log message is expensive, use lazy evaluation:

```python
# Bad practice - the expensive_operation is always called
logger.debug("Result: " + expensive_operation())

# Good practice - the lambda is only called if debug level is enabled
logger.debug(lambda: "Result: " + expensive_operation())

# Alternative good practice
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Result: " + expensive_operation())
```

### Avoid Excessive Logging

Excessive logging can impact performance. Be selective about what you log:

```python
# Avoid logging in tight loops
for i in range(1000000):
    logger.debug(f"Iteration {i}")  # This will slow down your application
```

## Testing and Debugging

### Temporarily Increase Log Level for Debugging

During development or debugging, you can temporarily increase the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Capture Logs in Tests

In tests, you can capture and verify logs:

```python
import logging
from unittest.mock import patch

def test_something():
    with patch('logging.Logger.warning') as mock_warning:
        # Code that should log a warning
        assert mock_warning.called
```

## Examples

### Basic Module Template

```python
"""Module docstring."""

# Standard library imports
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    import some_library
    logger.info("Successfully imported some_library")
except ImportError as e:
    logger.warning(f"Failed to import some_library: {e}")

# Local imports
from .some_module import SomeClass

def some_function():
    """Function docstring."""
    logger.debug("Entering some_function")
    try:
        result = perform_operation()
        logger.info("Operation completed successfully")
        return result
    except Exception as e:
        logger.exception(f"Error in some_function: {e}")
        raise
```

### Exception Handling

Always use `logger.exception()` when logging exceptions to include the traceback:

```python
try:
    # Some code that might raise an exception
    result = risky_operation()
except Exception as e:
    logger.exception(f"Error during risky operation: {e}")
    # Handle the exception or re-raise
```
