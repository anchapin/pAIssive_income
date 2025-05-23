# Alert System

The logging dashboard includes a comprehensive alert system that can detect patterns, thresholds, anomalies, and other conditions in log data. This document provides an overview of the alert system and how to use it.

## Features

- **Multiple Alert Types**: Support for pattern, threshold, anomaly, frequency, and absence alerts
- **Customizable Conditions**: Flexible configuration of alert conditions
- **Multiple Notification Channels**: In-app, email, and webhook notifications
- **Alert Severity Levels**: Info, warning, error, and critical severity levels
- **Alert Management**: View, acknowledge, and dismiss alerts
- **Alert History**: Track alert history and resolution

## Alert Types

The alert system supports the following types of alerts:

### Pattern Alerts

Pattern alerts trigger when a specific pattern is detected in log messages. For example, you can create an alert that triggers when an exception pattern is detected in log messages.

**Configuration Parameters:**
- `pattern`: Regular expression pattern to match
- `min_matches`: Minimum number of matches required to trigger the alert

**Example:**
```python
AlertRule(
    name="Exception Pattern",
    description="Alert when exception patterns are detected",
    condition=AlertCondition.PATTERN,
    parameters={
        "pattern": "Exception|Error|Traceback",
        "min_matches": 3,
    },
    severity=AlertSeverity.ERROR,
    notifiers=["in-app"],
)
```

### Threshold Alerts

Threshold alerts trigger when a metric exceeds a specified threshold. For example, you can create an alert that triggers when the error rate exceeds 5%.

**Configuration Parameters:**
- `metric`: Metric to monitor (e.g., "error_rate", "api_latency")
- `threshold`: Threshold value
- `operator`: Comparison operator (">", "<", ">=", "<=", "==", "!=")
- `window`: Time window in seconds

**Example:**
```python
AlertRule(
    name="High Error Rate",
    description="Alert when error rate exceeds threshold",
    condition=AlertCondition.THRESHOLD,
    parameters={
        "metric": "error_rate",
        "threshold": 0.05,  # 5%
        "window": 300,  # 5 minutes
        "operator": ">",
    },
    severity=AlertSeverity.WARNING,
    notifiers=["in-app"],
)
```

### Anomaly Alerts

Anomaly alerts trigger when a metric exhibits anomalous behavior. For example, you can create an alert that triggers when API latency spikes.

**Configuration Parameters:**
- `metric`: Metric to monitor (e.g., "api_latency", "db_query_time")
- `sensitivity`: Z-score threshold for anomaly detection
- `window`: Time window in seconds

**Example:**
```python
AlertRule(
    name="API Latency Spike",
    description="Alert when API latency spikes",
    condition=AlertCondition.ANOMALY,
    parameters={
        "metric": "api_latency",
        "sensitivity": 3.0,  # z-score threshold
        "window": 600,  # 10 minutes
    },
    severity=AlertSeverity.WARNING,
    notifiers=["in-app"],
)
```

### Frequency Alerts

Frequency alerts trigger when the frequency of a specific log level exceeds a threshold. For example, you can create an alert that triggers when there are more than 10 error logs in a minute.

**Configuration Parameters:**
- `level`: Log level to monitor (e.g., "ERROR", "WARNING")
- `threshold`: Threshold value
- `window`: Time window in seconds

**Example:**
```python
AlertRule(
    name="High Error Frequency",
    description="Alert when error frequency exceeds threshold",
    condition=AlertCondition.FREQUENCY,
    parameters={
        "level": "ERROR",
        "threshold": 10,
        "window": 60,  # 1 minute
    },
    severity=AlertSeverity.WARNING,
    notifiers=["in-app"],
)
```

### Absence Alerts

Absence alerts trigger when a specific pattern is not detected in log messages for a specified period. For example, you can create an alert that triggers when no heartbeat messages are detected for 5 minutes.

**Configuration Parameters:**
- `pattern`: Regular expression pattern to match
- `window`: Time window in seconds

**Example:**
```python
AlertRule(
    name="Missing Heartbeat",
    description="Alert when heartbeat messages are missing",
    condition=AlertCondition.ABSENCE,
    parameters={
        "pattern": "Heartbeat",
        "window": 300,  # 5 minutes
    },
    severity=AlertSeverity.ERROR,
    notifiers=["in-app"],
)
```

## Alert Severity Levels

The alert system supports the following severity levels:

- **INFO**: Informational alerts that don't require immediate attention
- **WARNING**: Warning alerts that may require attention
- **ERROR**: Error alerts that require attention
- **CRITICAL**: Critical alerts that require immediate attention

## Notification Channels

The alert system supports the following notification channels:

### In-App Notifications

In-app notifications appear in the dashboard UI. They can be viewed, acknowledged, and dismissed.

### Email Notifications

Email notifications are sent to specified email addresses. They include alert details and links to the dashboard.

**Configuration:**
```python
EmailNotifier(
    smtp_host="smtp.example.com",
    smtp_port=587,
    username="user",
    password="password",
    from_email="alerts@example.com",
    to_emails=["admin@example.com"]
)
```

### Webhook Notifications

Webhook notifications are sent to specified URLs. They include alert details in JSON format.

**Configuration:**
```python
WebhookNotifier(
    url="https://example.com/webhook",
    headers={"Authorization": "Bearer token"}
)
```

## Managing Alerts

The dashboard includes an "Alerts" tab that allows you to:

- View active alerts
- Acknowledge alerts
- Dismiss alerts
- View alert history
- Configure alert rules

### Adding Alert Rules

To add a new alert rule:

1. Navigate to the "Alerts" tab
2. Click "Add Alert Rule"
3. Configure the alert rule parameters
4. Click "Add Alert Rule"

### Editing Alert Rules

To edit an existing alert rule:

1. Navigate to the "Alerts" tab
2. Find the alert rule you want to edit
3. Click "Edit"
4. Modify the alert rule parameters
5. Click "Save"

### Deleting Alert Rules

To delete an alert rule:

1. Navigate to the "Alerts" tab
2. Find the alert rule you want to delete
3. Click "Delete"
4. Confirm the deletion

## Programmatic Usage

The alert system can also be used programmatically:

```python
from common_utils.logging.alert_system import (
    AlertSystem,
    AlertRule,
    AlertCondition,
    AlertSeverity,
    EmailNotifier,
    WebhookNotifier,
    InAppNotifier,
)

# Create an alert system
alert_system = AlertSystem()

# Add notifiers
alert_system.add_notifier(InAppNotifier(callback=in_app_notification_callback))
alert_system.add_notifier(EmailNotifier(
    smtp_host="smtp.example.com",
    smtp_port=587,
    username="user",
    password="password",
    from_email="alerts@example.com",
    to_emails=["admin@example.com"]
))

# Add alert rules
alert_system.add_rule(
    AlertRule(
        name="High Error Rate",
        description="Alert when error rate exceeds threshold",
        condition=AlertCondition.THRESHOLD,
        parameters={
            "metric": "error_rate",
            "threshold": 0.05,
            "window": 300,
            "operator": ">",
        },
        severity=AlertSeverity.WARNING,
        notifiers=["in-app", "email"],
    )
)

# Process logs
alert_system.process_logs(log_entries)
```
