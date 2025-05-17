# Advanced Logging Features

This document describes the advanced logging features available in the pAIssive_income project, including centralized logging, log aggregation, and integration with the ELK stack.

## Table of Contents

1. [Introduction](#introduction)
2. [Centralized Logging Service](#centralized-logging-service)
3. [Log Aggregation](#log-aggregation)
4. [ELK Stack Integration](#elk-stack-integration)
5. [Log Dashboard](#log-dashboard)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Introduction

The pAIssive_income project includes several advanced logging features to help with debugging, monitoring, and analyzing application behavior:

- **Centralized Logging Service**: Collects logs from distributed applications
- **Log Aggregation**: Aggregates logs from multiple sources
- **ELK Stack Integration**: Integrates with Elasticsearch, Logstash, and Kibana for advanced log analysis
- **Log Dashboard**: Provides a web-based dashboard for visualizing logs

## Centralized Logging Service

The centralized logging service collects logs from distributed applications and stores them in a central location. This is useful for applications that run on multiple servers or in multiple containers.

### Starting the Service

To start the centralized logging service:

```bash
python tools/run_centralized_logging_service.py --host 0.0.0.0 --port 5000 --log-dir logs
```

### Configuring Clients

To configure an application to send logs to the centralized logging service:

```python
from common_utils.logging.centralized_logging import configure_centralized_logging, get_centralized_logger

# Configure centralized logging
configure_centralized_logging(
    app_name="my_app",
    host="logging_server",
    port=5000,
    level=logging.INFO,
)

# Get a logger
logger = get_centralized_logger(__name__)

# Log messages
logger.info("This is an info message")
logger.error("This is an error message")
```

### Log Format

The centralized logging service stores logs in files named after the application that generated them. Each log entry includes:

- Timestamp
- Logger name
- Log level
- Message
- Additional metadata (if provided)

## Log Aggregation

The log aggregation module collects logs from multiple sources and sends them to various destinations, such as Elasticsearch, Logstash, or files.

### Configuring Log Aggregation

To configure log aggregation:

```python
from common_utils.logging.log_aggregation import configure_log_aggregation

# Configure log aggregation
configure_log_aggregation(
    app_name="my_app",
    log_dir="logs",
    es_host="elasticsearch",
    es_port=9200,
    es_index="logs",
    logstash_host="logstash",
    logstash_port=5000,
    output_file="aggregated.log",
)
```

### Manual Aggregation

You can also manually aggregate logs:

```python
from common_utils.logging.log_aggregation import (
    LogAggregator,
    ElasticsearchHandler,
    LogstashHandler,
    FileRotatingHandler,
)

# Create a log aggregator
aggregator = LogAggregator(app_name="my_app")

# Add handlers
aggregator.add_handler(ElasticsearchHandler(es_client=es_client, index_name="logs"))
aggregator.add_handler(LogstashHandler(host="logstash", port=5000))
aggregator.add_handler(FileRotatingHandler(filename="aggregated.log"))

# Aggregate logs from a file
aggregator.aggregate_log_file("app.log")

# Aggregate logs from a directory
aggregator.aggregate_log_directory("logs")
```

## ELK Stack Integration

The ELK stack (Elasticsearch, Logstash, Kibana) is a powerful set of tools for collecting, processing, storing, and visualizing logs.

### Setting Up the ELK Stack

To set up the ELK stack:

```bash
cd tools/elk_stack
docker-compose up -d
```

This will start:
- Elasticsearch on port 9200
- Logstash on port 5000
- Kibana on port 5601
- Filebeat (optional)

### Sending Logs to the ELK Stack

You can send logs to the ELK stack using the log aggregation module:

```python
from common_utils.logging.log_aggregation import configure_log_aggregation

# Configure log aggregation
configure_log_aggregation(
    app_name="my_app",
    log_dir="logs",
    es_host="elasticsearch",
    es_port=9200,
    logstash_host="logstash",
    logstash_port=5000,
)
```

### Viewing Logs in Kibana

1. Open Kibana at http://localhost:5601
2. Create an index pattern:
   - Go to Management > Stack Management > Kibana > Index Patterns
   - Create a new index pattern with the pattern `logs-*`
   - Select `@timestamp` as the time field
   - Click "Create index pattern"
3. View logs:
   - Go to Analytics > Discover
   - Select the `logs-*` index pattern
   - Use the time picker to select a time range
   - Use the search bar to filter logs

## Log Dashboard

The log dashboard provides a web-based interface for visualizing and analyzing logs.

### Starting the Dashboard

To start the log dashboard:

```bash
python tools/log_dashboard.py --port 8050 --log-dir logs
```

Then open your web browser and navigate to http://localhost:8050.

### Dashboard Features

The log dashboard includes:
- Log file selection
- Filtering by log level, module, and time range
- Visualizations of log data
- Search functionality
- Real-time updates

## Best Practices

### Choosing the Right Logging Solution

- **Simple Applications**: Use the built-in logging module with file output
- **Distributed Applications**: Use the centralized logging service
- **Advanced Analysis**: Use the ELK stack integration

### Log Levels

Use appropriate log levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application operation
- **WARNING**: Potential issues that don't prevent the application from working
- **ERROR**: Errors that prevent a function from working
- **CRITICAL**: Errors that prevent the application from working

### Structured Logging

Use structured logging for better analysis:

```python
logger.info("User logged in", extra={"user_id": user_id, "ip_address": ip_address})
```

### Sensitive Information

Be careful not to log sensitive information:

```python
# Instead of:
logger.info(f"User {user_id} logged in with password {password}")

# Use:
logger.info(f"User {user_id} logged in")
```

## Troubleshooting

### Centralized Logging Service

If logs are not being sent to the centralized logging service:
- Check that the service is running
- Verify the host and port configuration
- Check network connectivity between the client and server

### Log Aggregation

If log aggregation is not working:
- Check that the log directory exists
- Verify that log files have the correct format
- Check permissions on the log directory

### ELK Stack

If the ELK stack is not working:
- Check that all services are running (`docker-compose ps`)
- Verify network connectivity between services
- Check Elasticsearch, Logstash, and Kibana logs for errors

### Log Dashboard

If the log dashboard is not working:
- Check that the log directory exists
- Verify that log files have the correct format
- Check that the dashboard is running on the correct port
