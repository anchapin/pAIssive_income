# Logging Best Practices

This document describes the best practices for logging in the pAIssive_income project.

## Overview

The project uses Python's built-in logging module with some enhancements for secure logging. The main logging utilities are in the `common_utils/logging` package.

## Getting a Logger

Always use the `get_logger` function from `common_utils/logging/log_utils.py` to get a logger instance:

```python
from common_utils.logging.log_utils import get_logger

logger = get_logger(__name__)
```

## Logging Levels

Use the appropriate logging level for each message:

- `DEBUG`: Detailed information, typically of interest only when diagnosing problems
- `INFO`: Confirmation that things are working as expected
- `WARNING`: An indication that something unexpected happened, or may happen in the near future
- `ERROR`: Due to a more serious problem, the software has not been able to perform some function
- `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running

## Secure Logging

For secure logging, use the `configure_secure_logging` function from `common_utils/logging/log_utils.py`:

```python
from common_utils.logging.log_utils import configure_secure_logging
import logging

# Configure secure logging for the entire application
configure_secure_logging(
    level=logging.INFO,
    format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Formatting

The default log format is:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

You can customize the format by passing a `format_string` to the `configure_secure_logging` function or the `setup_logger` function.

## Setting Up a Logger

If you need to set up a logger with custom handlers, use the `setup_logger` function from `common_utils/logging/logger.py`:

```python
from common_utils.logging.logger import setup_logger
import logging

# Set up a logger with a file handler
logger = setup_logger(
    name='my_logger',
    level=logging.INFO,
    log_file='my_log.log',
    format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Logging User Input

When logging user input, use the `log_user_input_safely` function from `common_utils/logging/log_utils.py` to prevent log injection attacks:

```python
from common_utils.logging.log_utils import log_user_input_safely

# Log user input safely
log_user_input_safely(logger, "User input: {}", user_input)
```

## Logging Validation Errors

When logging validation errors, include sufficient detail for debugging:

```python
logger.error(f"Validation error: {validation_error.message}")
for error in validation_error.details:
    logger.error(f"  {error['field']}: {error['message']}")
```

## Best Practices

1. Always use the `get_logger` function to get a logger instance
2. Use the appropriate logging level for each message
3. Include context in log messages (e.g., request ID, user ID)
4. Use structured logging for machine-readable logs
5. Log validation errors with sufficient detail for debugging
6. Use the `log_user_input_safely` function when logging user input
7. Configure secure logging at application startup
8. Use a custom formatter for consistent log formatting
9. Set up log rotation for production environments
10. Monitor logs for errors and warnings
