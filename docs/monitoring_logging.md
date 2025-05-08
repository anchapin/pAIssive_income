# Monitoring and Logging

This document describes the monitoring and logging system for the pAIssive Income project.

## Overview

The monitoring and logging system provides visibility into the application's behavior, performance, and health. It consists of the following components:

1. **Logging**: Structured logging for application events
2. **Metrics**: Collection and exposure of application metrics
3. **Health Checks**: Verification of application health
4. **Monitoring Dashboard**: Visualization of application metrics and health

## Logging

### Configuration

The logging system is configured in the `logging_config.py` file. It provides the following features:

- **Structured Logging**: Logs are formatted as JSON for easy parsing and analysis
- **Log Rotation**: Logs are rotated to prevent disk space issues
- **Multiple Log Levels**: Different log levels for different types of events
- **Multiple Log Destinations**: Logs can be sent to the console, files, and other destinations

### Log Types

The logging system supports the following log types:

- **Application Logs**: General application events
- **Error Logs**: Error events
- **Access Logs**: HTTP request and response events
- **Security Logs**: Authentication and authorization events

### Usage

To use the logging system, import the appropriate logger from the `logging_config` module:

```python
from logging_config import get_logger

# Get a logger for a specific module
logger = get_logger("module_name")

# Log events
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

For security events, use the `log_security_event` function:

```python
from logging_config import log_security_event

# Log a security event
log_security_event("login", user_id="user123", details={"ip": "192.168.1.1"})
```

For HTTP requests, use the `log_request` function:

```python
from logging_config import log_request

# Log an HTTP request
log_request(request, response)
```

## Metrics

### Configuration

The metrics system is configured in the `monitoring/metrics.py` file. It provides the following features:

- **Counters**: Incrementing values for counting events
- **Gauges**: Current values for measuring states
- **Histograms**: Distribution of values for measuring distributions
- **Timers**: Duration measurements for measuring execution time

### Usage

To use the metrics system, import the appropriate functions from the `monitoring.metrics` module:

```python
from monitoring.metrics import increment_counter, observe_value, start_timer

# Increment a counter
increment_counter("api_requests_total", labels={"method": "GET", "path": "/api/users"})

# Observe a value
observe_value("memory_usage_bytes", 1024 * 1024 * 100)

# Measure execution time
timer = start_timer("function_duration_seconds", labels={"function": "process_data"})
# ... do something ...
elapsed = timer()  # Stop the timer and get the elapsed time
```

## Health Checks

### Configuration

The health check system is configured in the `monitoring/health.py` file. It provides the following features:

- **System Information**: Information about the operating system
- **Python Information**: Information about the Python runtime
- **Memory Information**: Information about memory usage
- **Disk Information**: Information about disk usage
- **Network Information**: Information about network connections

### Usage

To use the health check system, import the `health_check` function from the `monitoring.health` module:

```python
from monitoring.health import health_check

# Perform a health check
health_data = health_check()
```

## Monitoring Dashboard

The monitoring dashboard is implemented in the `ui/api_server_monitoring.py` file. It provides the following endpoints:

- **/api/monitoring/health**: Health check endpoint
- **/api/monitoring/metrics**: Metrics endpoint
- **/api/monitoring/info**: System information endpoint

### Usage

To access the monitoring dashboard, navigate to the following URLs:

- **Health Check**: `http://localhost:5000/api/monitoring/health`
- **Metrics**: `http://localhost:5000/api/monitoring/metrics`
- **System Information**: `http://localhost:5000/api/monitoring/info`

## Integration with External Systems

The monitoring and logging system can be integrated with external systems for more advanced monitoring and analysis:

### Logging Integration

- **ELK Stack**: Elasticsearch, Logstash, and Kibana for log storage, processing, and visualization
- **Graylog**: Centralized log management
- **Splunk**: Log analysis and monitoring

### Metrics Integration

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Metrics visualization
- **Datadog**: Metrics collection, visualization, and alerting

### Health Check Integration

- **Kubernetes**: Health checks for container orchestration
- **AWS CloudWatch**: Health monitoring for AWS resources
- **Pingdom**: External health monitoring

## Best Practices

1. **Log Levels**: Use appropriate log levels for different types of events
2. **Structured Logging**: Use structured logging for easier parsing and analysis
3. **Contextual Information**: Include contextual information in logs (e.g., request ID, user ID)
4. **Sensitive Information**: Avoid logging sensitive information (e.g., passwords, tokens)
5. **Performance**: Be mindful of the performance impact of logging and monitoring
6. **Retention**: Configure appropriate retention periods for logs and metrics
7. **Alerting**: Set up alerts for critical events and thresholds
