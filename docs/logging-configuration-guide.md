# Logging Configuration Guide

This guide provides standardized logging configuration practices for the pAIssive_income project. Following these guidelines ensures consistent logging behavior across the entire codebase.

## Table of Contents

1. [Introduction](#introduction)
2. [Logging Levels](#logging-levels)
3. [Logging Format](#logging-format)
4. [Configuration Methods](#configuration-methods)
5. [Environment-Specific Configuration](#environment-specific-configuration)
6. [Structured Logging](#structured-logging)
7. [Log Rotation](#log-rotation)
8. [Integration with External Services](#integration-with-external-services)
9. [Examples](#examples)

## Introduction

Proper logging configuration is essential for effective debugging, monitoring, and troubleshooting. This guide standardizes how logging should be configured across the pAIssive_income project.

## Logging Levels

Use the following logging levels consistently throughout the application:

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Detailed information for diagnosing problems | `logger.debug("Connection attempt to %s with timeout %d", host, timeout)` |
| INFO | Confirmation that things are working as expected | `logger.info("Server started successfully on port %d", port)` |
| WARNING | Indication that something unexpected happened | `logger.warning("API rate limit at 90%% capacity")` |
| ERROR | Due to a more serious problem, the software couldn't perform some function | `logger.error("Failed to connect to database: %s", err)` |
| CRITICAL | A serious error indicating the program itself may be unable to continue running | `logger.critical("Out of memory - shutting down")` |

### Default Level

- **Development**: Use `DEBUG` level to see all log messages during development
- **Testing**: Use `INFO` level for test environments
- **Production**: Use `WARNING` level for production environments

## Logging Format

### Standard Format

Use this standard format for all log messages:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

This format includes:
- Timestamp with date and time
- Logger name (usually the module name)
- Log level
- The actual log message

### Extended Format

For more detailed logging, especially in development environments, use this extended format:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

This adds:
- File path
- Line number

## Configuration Methods

### Application Entry Point

Configure logging at the application entry point (e.g., `__main__.py` or `app.py`):

```python
import logging
import os
import sys

def configure_logging():
    """Configure logging for the application."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, None)
    
    if not isinstance(numeric_level, int):
        print(f"Invalid log level: {log_level}")
        numeric_level = logging.INFO
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log"),
        ]
    )

if __name__ == "__main__":
    configure_logging()
    # Rest of the application...
```

### Configuration File

For more complex applications, use a configuration file:

```python
import logging
import logging.config
import yaml

def configure_logging():
    """Configure logging from a YAML file."""
    with open("logging_config.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

if __name__ == "__main__":
    configure_logging()
    # Rest of the application...
```

Example `logging_config.yaml`:

```yaml
version: 1
formatters:
  standard:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
  file:
    class: logging.FileHandler
    level: DEBUG
    formatter: standard
    filename: app.log
loggers:
  '':  # Root logger
    level: DEBUG
    handlers: [console, file]
    propagate: true
```

## Environment-Specific Configuration

Adjust logging configuration based on the environment:

```python
import logging
import os

def configure_logging():
    """Configure logging based on environment."""
    env = os.environ.get("ENVIRONMENT", "development").lower()
    
    if env == "production":
        level = logging.WARNING
        log_file = "/var/log/app/app.log"
    elif env == "testing":
        level = logging.INFO
        log_file = "test.log"
    else:  # development
        level = logging.DEBUG
        log_file = "dev.log"
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ]
    )
```

## Structured Logging

For better log analysis, use structured logging:

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "props"):
            log_record.update(record.props)
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)

def configure_structured_logging():
    """Configure structured JSON logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
```

Usage:

```python
logger = logging.getLogger(__name__)

# Add structured data
logger.info("User logged in", extra={"props": {"user_id": "123", "ip": "192.168.1.1"}})
```

## Log Rotation

Configure log rotation to manage log file size:

```python
import logging
from logging.handlers import RotatingFileHandler

def configure_rotating_logs():
    """Configure rotating log files."""
    handler = RotatingFileHandler(
        "app.log",
        maxBytes=10485760,  # 10 MB
        backupCount=5,
    )
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
```

## Integration with External Services

### Sentry Integration

```python
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def configure_sentry_logging():
    """Configure Sentry integration with logging."""
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn="https://your-sentry-dsn@sentry.io/project",
        integrations=[sentry_logging],
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
```

## Examples

### Basic Application Setup

```python
# app.py
import logging
import os
import sys

def configure_logging():
    """Configure logging for the application."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log"),
        ]
    )

if __name__ == "__main__":
    configure_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Application started")
    
    # Rest of the application...
```

### Module-Level Logging

```python
# my_module.py
import logging

# Get a module-specific logger
logger = logging.getLogger(__name__)

def do_something():
    """Do something and log about it."""
    logger.debug("Starting operation")
    try:
        # Some operation
        result = 42
        logger.info("Operation completed with result: %d", result)
        return result
    except Exception as e:
        logger.exception("Operation failed: %s", e)
        raise
```
