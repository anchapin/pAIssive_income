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

### Logging Context Information

Use context managers to add temporary context information to logs:

```python
import logging
from contextlib import contextmanager
from typing import Dict, Any, Generator

# Configure logging
logger = logging.getLogger(__name__)

@contextmanager
def log_context(context_data: Dict[str, Any]) -> Generator[None, None, None]:
    """Add context data to log records within this context.

    Args:
        context_data: Dictionary of context data to add to log records
    """
    # Create a filter that adds context data to log records
    class ContextFilter(logging.Filter):
        def filter(self, record):
            for key, value in context_data.items():
                setattr(record, key, value)
            return True

    # Add the filter to the logger
    context_filter = ContextFilter()
    logger.addFilter(context_filter)

    try:
        yield
    finally:
        # Remove the filter when exiting the context
        logger.removeFilter(context_filter)

# Usage example
def process_request(request_id: str, user_id: str) -> None:
    with log_context({"request_id": request_id, "user_id": user_id}):
        logger.info("Processing request")
        # All logs within this context will include request_id and user_id
        perform_operation()
        logger.info("Request processed successfully")
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

### Adapter Pattern Example

Here's an example of proper logger initialization in an adapter class:

```python
"""adapter_module - Module for adapters.adapter_module."""

# Standard library imports
import logging
import json
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    import requests
    logger.debug("Successfully imported requests")
except ImportError as e:
    logger.warning(f"Failed to import requests: {e}")
    requests = None

# Local imports
from .base_adapter import BaseAdapter
from .exceptions import AdapterError

class ExternalServiceAdapter(BaseAdapter):
    """Adapter for connecting to an external service."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """Initialize the adapter.

        Args:
            base_url: The base URL of the external service
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        logger.info(f"Initialized adapter with base_url={base_url}")

    def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the external service.

        Args:
            endpoint: API endpoint to call
            data: Request payload

        Returns:
            Response data from the service

        Raises:
            AdapterError: If the request fails
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        logger.debug(f"Sending request to {endpoint}")
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Request to {endpoint} successful")
            return response.json()
        except requests.RequestException as e:
            logger.exception(f"Request to {endpoint} failed: {e}")
            raise AdapterError(f"Failed to communicate with external service: {e}") from e
```

### Asynchronous Code Example

Here's an example of proper logger usage in asynchronous code:

```python
"""async_module - Module for async operations."""

# Standard library imports
import logging
import asyncio
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    import aiohttp
    logger.debug("Successfully imported aiohttp")
except ImportError as e:
    logger.warning(f"Failed to import aiohttp: {e}")
    aiohttp = None

async def fetch_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch data from a URL asynchronously.

    Args:
        url: URL to fetch data from
        timeout: Request timeout in seconds

    Returns:
        JSON response data

    Raises:
        ValueError: If aiohttp is not available
        aiohttp.ClientError: If the request fails
    """
    if aiohttp is None:
        logger.error("aiohttp is required for fetch_data")
        raise ValueError("aiohttp is required for fetch_data")

    logger.debug(f"Fetching data from {url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Successfully fetched data from {url}")
                return data
    except aiohttp.ClientError as e:
        logger.exception(f"Error fetching data from {url}: {e}")
        raise
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching data from {url}")
        raise aiohttp.ClientError(f"Timeout fetching data from {url}")

async def fetch_multiple(urls: List[str]) -> List[Dict[str, Any]]:
    """Fetch data from multiple URLs concurrently.

    Args:
        urls: List of URLs to fetch data from

    Returns:
        List of JSON response data
    """
    logger.info(f"Fetching data from {len(urls)} URLs")
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results, handling any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"Failed to fetch data from {urls[i]}: {result}")
        else:
            processed_results.append(result)

    logger.info(f"Successfully fetched data from {len(processed_results)}/{len(urls)} URLs")
    return processed_results
```

### CLI Application Example

Here's an example of proper logger usage in a command-line application:

```python
"""cli_app - Command-line application module."""

# Standard library imports
import logging
import argparse
import sys
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

def configure_logging(verbose: bool = False) -> None:
    """Configure logging for the application.

    Args:
        verbose: Whether to enable verbose (DEBUG) logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # Reduce verbosity of third-party libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger.debug("Logging configured with level %s", "DEBUG" if verbose else "INFO")

def process_file(file_path: str) -> bool:
    """Process a file.

    Args:
        file_path: Path to the file to process

    Returns:
        True if processing was successful, False otherwise
    """
    logger.info("Processing file: %s", file_path)
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Process the file content
        logger.debug("File content length: %d bytes", len(content))

        # Simulate processing
        result = len(content) > 0

        if result:
            logger.info("Successfully processed file: %s", file_path)
        else:
            logger.warning("File was empty: %s", file_path)

        return result
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return False
    except Exception as e:
        logger.exception("Error processing file %s: %s", file_path, e)
        return False

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the application.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Process files")
    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parsed_args = parser.parse_args(args)

    # Configure logging based on verbosity
    configure_logging(parsed_args.verbose)

    logger.info("Starting file processing")

    success_count = 0
    for file_path in parsed_args.files:
        if process_file(file_path):
            success_count += 1

    logger.info("Processed %d/%d files successfully", success_count, len(parsed_args.files))

    return 0 if success_count == len(parsed_args.files) else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Web Application Example

Here's an example of proper logger usage in a web application:

```python
"""web_app - Web application module."""

# Standard library imports
import logging
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    from flask import Flask, request, jsonify
    logger.debug("Successfully imported Flask")
except ImportError as e:
    logger.critical(f"Failed to import Flask: {e}")
    raise

# Create Flask app
app = Flask(__name__)

# Configure application-wide logging
def configure_logging() -> None:
    """Configure logging for the web application."""
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Reduce verbosity of Flask and Werkzeug
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("flask").setLevel(logging.WARNING)

    logger.info("Web application logging configured with level %s", log_level_name)

# Configure logging before request handling
configure_logging()

@app.before_request
def log_request_info() -> None:
    """Log information about each incoming request."""
    logger.debug(
        "Request: %s %s - Headers: %s",
        request.method,
        request.path,
        {k: v for k, v in request.headers.items() if k.lower() not in ("authorization", "cookie")}
    )

@app.after_request
def log_response_info(response: Any) -> Any:
    """Log information about each outgoing response.

    Args:
        response: The Flask response object

    Returns:
        The unchanged response object
    """
    logger.debug(
        "Response: %s %s - Status: %d",
        request.method,
        request.path,
        response.status_code
    )
    return response

@app.route("/api/data", methods=["GET"])
def get_data() -> Dict[str, Any]:
    """API endpoint to get data.

    Returns:
        JSON response with data
    """
    logger.info("Handling request for /api/data")
    try:
        # Simulate data retrieval
        data = {"message": "Hello, world!", "status": "success"}
        logger.debug("Retrieved data: %s", data)
        return jsonify(data)
    except Exception as e:
        logger.exception("Error retrieving data: %s", e)
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route("/api/data", methods=["POST"])
def create_data() -> Dict[str, Any]:
    """API endpoint to create data.

    Returns:
        JSON response with result
    """
    logger.info("Handling POST request for /api/data")
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            logger.warning("No JSON data in request")
            return jsonify({"error": "No JSON data provided", "status": "error"}), 400

        logger.debug("Received data: %s", data)

        # Simulate data processing
        result = {"id": 123, "status": "created"}

        logger.info("Successfully created data with ID %d", result["id"])
        return jsonify(result), 201
    except Exception as e:
        logger.exception("Error creating data: %s", e)
        return jsonify({"error": str(e), "status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting web application on port %d", port)
    app.run(host="0.0.0.0", port=port)
```

### FastAPI Application Example

Here's an example of proper logger usage in a FastAPI application:

```python
"""fastapi_app - FastAPI application module."""

# Standard library imports
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    from fastapi import FastAPI, Request, Response, Depends, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    logger.debug("Successfully imported FastAPI and dependencies")
except ImportError as e:
    logger.critical(f"Failed to import FastAPI dependencies: {e}")
    raise

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
    from logging.handlers import RotatingFileHandler
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

# Create FastAPI app
app = FastAPI(title="FastAPI Example")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
configure_logging()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware to log request and response information."""
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process the request
    try:
        response = await call_next(request)
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        raise

@app.get("/api/items/", response_model=Dict[str, Any])
async def get_items():
    """Get all items."""
    logger.info("Handling request for all items")
    try:
        # Simulate data retrieval
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        logger.debug(f"Retrieved {len(items)} items")
        return {"items": items}
    except Exception as e:
        logger.exception(f"Error retrieving items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/items/{item_id}", response_model=Dict[str, Any])
async def get_item(item_id: int):
    """Get a specific item by ID."""
    logger.info(f"Handling request for item {item_id}")
    try:
        # Simulate data retrieval
        if item_id <= 0:
            logger.warning(f"Invalid item ID: {item_id}")
            raise HTTPException(status_code=400, detail="Invalid item ID")

        # Simulate item not found
        if item_id > 100:
            logger.warning(f"Item not found: {item_id}")
            raise HTTPException(status_code=404, detail="Item not found")

        # Simulate successful retrieval
        item = {"id": item_id, "name": f"Item {item_id}"}
        logger.debug(f"Retrieved item: {item}")
        return item
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Error retrieving item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting FastAPI application on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
```

### Django Application Example

Here's an example of proper logger usage in a Django application:

```python
"""views.py - Django views module."""

# Standard library imports
import logging
import json
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Django imports
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist

# Local imports
from .models import Item
from .serializers import ItemSerializer

@require_http_methods(["GET"])
def get_items(request: HttpRequest) -> JsonResponse:
    """API endpoint to get all items.

    Args:
        request: The HTTP request

    Returns:
        JSON response with items data
    """
    logger.info("Handling request for all items")
    try:
        # Get query parameters
        limit = request.GET.get("limit")
        if limit:
            try:
                limit = int(limit)
                logger.debug(f"Limiting results to {limit} items")
            except ValueError:
                logger.warning(f"Invalid limit parameter: {limit}")
                return JsonResponse({"error": "Invalid limit parameter"}, status=400)

        # Get items from database
        if limit:
            items = Item.objects.all()[:limit]
        else:
            items = Item.objects.all()

        # Serialize items
        serializer = ItemSerializer(items, many=True)
        logger.debug(f"Retrieved {len(serializer.data)} items")

        return JsonResponse({"items": serializer.data})
    except Exception as e:
        logger.exception(f"Error retrieving items: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_item(request: HttpRequest, item_id: int) -> JsonResponse:
    """API endpoint to get a specific item.

    Args:
        request: The HTTP request
        item_id: The ID of the item to retrieve

    Returns:
        JSON response with item data
    """
    logger.info(f"Handling request for item {item_id}")
    try:
        # Get item from database
        item = Item.objects.get(pk=item_id)

        # Serialize item
        serializer = ItemSerializer(item)
        logger.debug(f"Retrieved item: {serializer.data}")

        return JsonResponse(serializer.data)
    except ObjectDoesNotExist:
        logger.warning(f"Item not found: {item_id}")
        return JsonResponse({"error": "Item not found"}, status=404)
    except Exception as e:
        logger.exception(f"Error retrieving item {item_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_item(request: HttpRequest) -> JsonResponse:
    """API endpoint to create a new item.

    Args:
        request: The HTTP request

    Returns:
        JSON response with created item data
    """
    logger.info("Handling request to create item")
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in request: {e}")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        logger.debug(f"Received data: {data}")

        # Create item
        serializer = ItemSerializer(data=data)
        if serializer.is_valid():
            item = serializer.save()
            logger.info(f"Created item with ID {item.id}")
            return JsonResponse(serializer.data, status=201)
        else:
            logger.warning(f"Validation errors: {serializer.errors}")
            return JsonResponse({"errors": serializer.errors}, status=400)
    except Exception as e:
        logger.exception(f"Error creating item: {e}")
        return JsonResponse({"error": str(e)}, status=500)
```
