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

## Framework-Specific Examples

### Flask Application

```python
# app.py
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g

app = Flask(__name__)

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information."""

    def format(self, record):
        if hasattr(g, 'request_id'):
            record.request_id = g.request_id
        else:
            record.request_id = 'no-request-id'
        return super().format(record)

def configure_logging(app):
    """Configure logging for the Flask application."""
    # Set up log level based on environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, None)

    # Create formatter
    formatter = RequestFormatter(
        '[%(asctime)s] [%(request_id)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create file handler
    file_handler = RotatingFileHandler(
        'app.log',
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Reduce verbosity of Flask and Werkzeug
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('flask').setLevel(logging.WARNING)

    # Log application startup
    app.logger.info(f"Flask application started with log level: {log_level}")

@app.before_request
def before_request():
    """Set up request context for logging."""
    g.request_id = request.headers.get('X-Request-ID', 'unknown')
    app.logger.debug(f"Processing request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Log after request."""
    app.logger.debug(f"Request completed with status: {response.status_code}")
    return response

# Configure logging
configure_logging(app)

@app.route('/')
def index():
    app.logger.info("Index page accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Application

```python
# settings.py
import os

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'myapp': {  # Add your app loggers here
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# views.py
import logging

# Get a logger for your app
logger = logging.getLogger('myapp')

def my_view(request):
    logger.info(f"Processing request from {request.user}")
    try:
        # View logic
        result = process_data(request.POST)
        logger.info(f"Request processed successfully")
        return result
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        raise
```

### FastAPI Application

```python
# main.py
import logging
import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from logging.handlers import RotatingFileHandler

# Configure logging
def configure_logging():
    """Configure logging for the FastAPI application."""
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create file handler
    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=10485760,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create logger
logger = configure_logging()

# Create FastAPI app
app = FastAPI()

# Logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Measure request processing time
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"processed in {process_time:.4f} seconds"
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            # Log exception
            logger.exception(f"Error {request_id}: {str(e)}")
            raise

# Add middleware
app.add_middleware(LoggingMiddleware)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    logger.info(f"Item endpoint accessed with item_id={item_id}, q={q}")
    return {"item_id": item_id, "q": q}
```

### Celery Tasks

```python
# tasks.py
import logging
import os
from celery import Celery, Task
from celery.signals import setup_logging, task_prerun, task_postrun, task_failure

# Create Celery app
app = Celery('tasks', broker='redis://localhost:6379/0')

# Configure Celery logging
@setup_logging.connect
def configure_logging(loglevel=None, **kwargs):
    """Configure logging for Celery."""
    # Create logger
    logger = logging.getLogger('celery')
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create file handler
    os.makedirs('logs', exist_ok=True)
    file_handler = logging.FileHandler('logs/celery.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Log task execution
@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log before task execution."""
    logger = logging.getLogger('celery')
    logger.info(f"Task {task.name}[{task_id}] started with args: {args}, kwargs: {kwargs}")

@task_postrun.connect
def task_postrun_handler(task_id, task, retval, state, *args, **kwargs):
    """Log after task execution."""
    logger = logging.getLogger('celery')
    logger.info(f"Task {task.name}[{task_id}] completed with state: {state}")

@task_failure.connect
def task_failure_handler(task_id, exception, traceback, einfo, *args, **kwargs):
    """Log task failure."""
    logger = logging.getLogger('celery')
    logger.error(f"Task {task_id} failed: {exception}")
    logger.debug(f"Traceback: {einfo}")

# Base task class with logging
class LoggedTask(Task):
    """Base task class that logs task execution."""

    def __call__(self, *args, **kwargs):
        logger = logging.getLogger('celery')
        logger.debug(f"Executing {self.name} with args: {args}, kwargs: {kwargs}")
        return super().__call__(*args, **kwargs)

# Define tasks
@app.task(base=LoggedTask)
def add(x, y):
    """Add two numbers."""
    logger = logging.getLogger('celery')
    logger.info(f"Adding {x} + {y}")
    return x + y

@app.task(base=LoggedTask)
def process_data(data):
    """Process data."""
    logger = logging.getLogger('celery')
    logger.info(f"Processing data: {data}")
    try:
        # Process data
        result = len(data)
        logger.info(f"Data processed successfully, result: {result}")
        return result
    except Exception as e:
        logger.exception(f"Error processing data: {e}")
        raise
```
