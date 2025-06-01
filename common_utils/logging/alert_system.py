"""
Alert system for logging.

This module provides functionality for setting up alerts based on log patterns,
thresholds, and anomalies. It supports various notification channels such as
email, webhooks, and in-app notifications.

Usage:
    from common_utils.logging.alert_system import (
        AlertSystem,
        AlertRule,
        AlertCondition,
        EmailNotifier,
        WebhookNotifier,
        InAppNotifier,
    )

    # Create an alert system
    alert_system = AlertSystem()

    # Add notifiers
    alert_system.add_notifier(EmailNotifier(
        smtp_host="smtp.example.com",
        smtp_port=587,
        username="user",
        password="password",
        from_email="alerts@example.com",
        to_emails=["admin@example.com"]
    ))

    alert_system.add_notifier(WebhookNotifier(
        url="https://example.com/webhook",
        headers={"Authorization": "Bearer token"}
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
                "window": 300,  # 5 minutes
                "operator": ">",
            },
            severity="warning",
            notifiers=["email", "webhook"],
        )
    )

    alert_system.add_rule(
        AlertRule(
            name="API Latency Spike",
            description="Alert when API latency spikes",
            condition=AlertCondition.ANOMALY,
            parameters={
                "metric": "api_latency",
                "sensitivity": 3.0,  # z-score threshold
                "window": 600,  # 10 minutes
            },
            severity="critical",
            notifiers=["email", "webhook", "in-app"],
        )
    )

    # Process logs and trigger alerts
    alert_system.process_logs(log_entries)
"""

import datetime
import json
import logging
import re
import smtplib
import sys  # Added sys import
import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Optional

_logger = logging.getLogger(__name__)

try:
    import numpy as np
    import requests
    from scipy import stats
    HAS_SCIPY_NUMPY = True
except ImportError as e:
    _logger.warning(f"Optional dependencies not available: {e}. Some alert features may be limited.")
    np = None
    requests = None
    stats = None
    HAS_SCIPY_NUMPY = False




class AlertCondition(str, Enum):
    """Alert condition types."""

    PATTERN = "pattern"
    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    FREQUENCY = "frequency"
    ABSENCE = "absence"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """Alert rule configuration."""

    name: str
    description: str
    condition: AlertCondition
    parameters: dict[str, Any]
    severity: str = AlertSeverity.WARNING
    notifiers: list[str] = field(default_factory=list)
    enabled: bool = True
    cooldown_period: int = 300  # 5 minutes in seconds
    last_triggered: Optional[datetime.datetime] = None
    id: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize the alert rule."""
        if self.id is None:
            # Generate a simple ID based on the name
            self.id = self.name.lower().replace(" ", "_")

    def is_in_cooldown(self) -> bool:
        """Check if the alert is in cooldown period."""
        if self.last_triggered is None:
            return False

        elapsed = (datetime.datetime.now() - self.last_triggered).total_seconds()
        return elapsed < self.cooldown_period

    def mark_triggered(self) -> None:
        """Mark the alert as triggered."""
        self.last_triggered = datetime.datetime.now()


class AlertNotifier(ABC):
    """Base class for alert notifiers."""

    def __init__(self, name: str) -> None:
        """
        Initialize the notifier.

        Args:
            name: Name of the notifier

        """
        self.name = name

    @abstractmethod
    def send_alert(self, alert_rule: AlertRule, context: dict[str, Any]) -> bool:
        """
        Send an alert notification.

        Args:
            alert_rule: The alert rule that triggered
            context: Additional context for the alert

        Returns:
            bool: True if the alert was sent successfully, False otherwise

        """


class EmailNotifier(AlertNotifier):
    """Email notifier for alerts."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: list[str],
        use_tls: bool = True,
        name: str = "email",
    ) -> None:
        """
        Initialize the email notifier.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            from_email: Sender email address
            to_emails: List of recipient email addresses
            use_tls: Whether to use TLS
            name: Name of the notifier

        """
        super().__init__(name)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.use_tls = use_tls

    def send_alert(self, alert_rule: AlertRule, context: dict[str, Any]) -> bool:
        """
        Send an email alert.

        Args:
            alert_rule: The alert rule that triggered
            context: Additional context for the alert

        Returns:
            bool: True if the alert was sent successfully, False otherwise

        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = f"[{alert_rule.severity.upper()}] {alert_rule.name}"

            # Create message body
            body = f"""
            <html>
            <body>
                <h2>{alert_rule.name}</h2>
                <p><strong>Description:</strong> {alert_rule.description}</p>
                <p><strong>Severity:</strong> {alert_rule.severity}</p>
                <p><strong>Time:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h3>Details:</h3>
                <pre>{json.dumps(context, indent=2)}</pre>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, "html"))

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            _logger.info(f"Sent email alert: {alert_rule.name}")
            return True
        except Exception as e:
            _logger.exception(f"Failed to send email alert '{alert_rule.name}': {e}")
            return False


class WebhookNotifier(AlertNotifier):
    """Webhook notifier for alerts."""

    def __init__(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: int = 10,
        name: str = "webhook",
    ) -> None:
        """
        Initialize the webhook notifier.

        Args:
            url: Webhook URL
            headers: HTTP headers
            timeout: Request timeout in seconds
            name: Name of the notifier

        """
        super().__init__(name)
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout

    def send_alert(self, alert_rule: AlertRule, context: dict[str, Any]) -> bool:
        """
        Send a webhook alert.

        Args:
            alert_rule: The alert rule that triggered
            context: Additional context for the alert

        Returns:
            bool: True if the alert was sent successfully, False otherwise

        """
        try:
            payload = {
                "alert": {
                    "name": alert_rule.name,
                    "description": alert_rule.description,
                    "severity": alert_rule.severity,
                    "time": datetime.datetime.now().isoformat(),
                },
                "context": context,
            }

            if requests is None:
                _logger.error("requests library not available. Cannot send webhook alert.")
                return False

            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            _logger.info(f"Sent webhook alert: {alert_rule.name}")
            return True
        except Exception as e:
            _logger.exception(f"Failed to send webhook alert '{alert_rule.name}': {e}")
            return False


class InAppNotifier(AlertNotifier):
    """In-app notifier for alerts."""

    def __init__(
        self,
        callback: Callable[[AlertRule, dict[str, Any]], None],
        name: str = "in-app",
    ) -> None:
        """
        Initialize the in-app notifier.

        Args:
            callback: Callback function to handle in-app notifications
            name: Name of the notifier

        """
        super().__init__(name)
        self.callback = callback

    def send_alert(self, alert_rule: AlertRule, context: dict[str, Any]) -> bool:
        """
        Send an in-app alert.

        Args:
            alert_rule: The alert rule that triggered
            context: Additional context for the alert

        Returns:
            bool: True if the alert was sent successfully, False otherwise

        """
        try:
            self.callback(alert_rule, context)
            _logger.info(f"Sent in-app alert: {alert_rule.name}")
            return True
        except Exception as e:
            _logger.exception(f"Error in in-app notification callback for alert '{alert_rule.name}': {e}")
            return False


class AlertSystem:
    """Alert system for logging."""

    def __init__(self) -> None:
        """Initialize the alert system."""
        self.rules: list[AlertRule] = []
        self.notifiers: dict[str, AlertNotifier] = {}
        self.metrics_history: dict[str, list[dict[str, Any]]] = {}
        self.lock = threading.Lock()

    def add_rule(self, rule: AlertRule) -> None:
        """
        Add an alert rule.

        Args:
            rule: The alert rule to add

        """
        with self.lock:
            # Check if rule with same ID already exists
            for i, existing_rule in enumerate(self.rules):
                if existing_rule.id == rule.id:
                    # Replace existing rule
                    self.rules[i] = rule
                    _logger.info(f"Updated alert rule: {rule.name}")
                    return

            # Add new rule
            self.rules.append(rule)
            _logger.info(f"Added alert rule: {rule.name}")

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove an alert rule.

        Args:
            rule_id: ID of the rule to remove

        Returns:
            bool: True if the rule was removed, False if not found

        """
        with self.lock:
            for i, rule in enumerate(self.rules):
                if rule.id == rule_id:
                    self.rules.pop(i)
                    _logger.info(f"Removed alert rule: {rule.name}")
                    return True
            return False

    def add_notifier(self, notifier: AlertNotifier) -> None:
        """
        Add a notifier.

        Args:
            notifier: The notifier to add

        """
        with self.lock:
            self.notifiers[notifier.name] = notifier
            _logger.info(f"Added notifier: {notifier.name}")

    def remove_notifier(self, name: str) -> bool:
        """
        Remove a notifier.

        Args:
            name: Name of the notifier to remove

        Returns:
            bool: True if the notifier was removed, False if not found

        """
        with self.lock:
            if name in self.notifiers:
                del self.notifiers[name]
                _logger.info(f"Removed notifier: {name}")
                return True
            _logger.error(f"Notifier '{name}' not found")
            return False

    def process_logs(self, log_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Process logs and trigger alerts.

        Args:
            log_entries: List of log entries to process

        Returns:
            List[Dict[str, Any]]: List of triggered alerts

        """
        if not log_entries:
            return []

        triggered_alerts = []

        # Update metrics history
        self._update_metrics_history(log_entries)

        # Check each rule
        for rule in self.rules:
            if not rule.enabled or rule.is_in_cooldown():
                continue

            try:
                # Check if rule condition is met
                is_triggered, context = self._check_rule_condition(rule, log_entries)

                if is_triggered:
                    # Mark rule as triggered
                    rule.mark_triggered()

                    # Send notifications
                    self._send_notifications(rule, context)

                    # Add to triggered alerts
                    triggered_alerts.append({
                        "rule": rule.name,
                        "severity": rule.severity,
                        "time": datetime.datetime.now().isoformat(),
                        "context": context,
                    })
            except Exception as e:
                _logger.exception(f"Error processing rule {rule.name}: {e}")

        return triggered_alerts

    def _update_metrics_history(self, log_entries: list[dict[str, Any]]) -> None:
        """
        Update metrics history.

        Args:
            log_entries: List of log entries

        """
        # Extract timestamp from first entry
        if not log_entries:
            return

        timestamp = log_entries[0].get("timestamp", datetime.datetime.now())

        # Calculate metrics
        metrics = self._calculate_metrics(log_entries)

        # Add to history
        for metric_name, value in metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []

            self.metrics_history[metric_name].append({
                "timestamp": timestamp,
                "value": value,
            })

            # Limit history size (keep last 1000 entries)
            if len(self.metrics_history[metric_name]) > 1000:
                self.metrics_history[metric_name] = self.metrics_history[metric_name][-1000:]

    def _calculate_metrics(self, log_entries: list[dict[str, Any]]) -> dict[str, float]:
        """
        Calculate metrics from log entries.

        Args:
            log_entries: List of log entries

        Returns:
            Dict[str, float]: Dictionary of metrics

        """
        metrics = {}

        # Calculate error rate
        error_count = sum(1 for entry in log_entries if entry.get("level") in ["ERROR", "CRITICAL"])
        metrics["error_rate"] = error_count / len(log_entries) if log_entries else 0

        # Calculate log frequency
        metrics["log_frequency"] = len(log_entries)

        # Extract performance metrics
        # This is a simplified example - in a real system, you would extract
        # metrics based on your application's specific log format
        for entry in log_entries:
            message = entry.get("message", "")

            # Example: Extract API latency
            api_latency_match = re.search(r"API request completed in (\d+\.?\d*) ms", message)
            if api_latency_match:
                metrics["api_latency"] = float(api_latency_match.group(1))

            # Example: Extract database query time
            db_time_match = re.search(r"Database query took (\d+\.?\d*) ms", message)
            if db_time_match:
                metrics["db_query_time"] = float(db_time_match.group(1))

        return metrics

    def _check_rule_condition(
        self, rule: AlertRule, log_entries: list[dict[str, Any]]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check if a rule condition is met.

        Args:
            rule: The alert rule to check
            log_entries: List of log entries

        Returns:
            tuple[bool, Dict[str, Any]]: Tuple of (is_triggered, context)

        """
        context = {
            "log_count": len(log_entries),
            "first_log_time": log_entries[0].get("timestamp") if log_entries else None,
            "last_log_time": log_entries[-1].get("timestamp") if log_entries else None,
        }

        if rule.condition == AlertCondition.PATTERN:
            return self._check_pattern_condition(rule, log_entries, context)
        if rule.condition == AlertCondition.THRESHOLD:
            return self._check_threshold_condition(rule, context)
        if rule.condition == AlertCondition.ANOMALY:
            return self._check_anomaly_condition(rule, context)
        if rule.condition == AlertCondition.FREQUENCY:
            return self._check_frequency_condition(rule, log_entries, context)
        if rule.condition == AlertCondition.ABSENCE:
            return self._check_absence_condition(rule, log_entries, context)
        _logger.warning(f"Unknown alert condition: {rule.condition}")
        return False, context

    def _check_pattern_condition(
        self, rule: AlertRule, log_entries: list[dict[str, Any]], context: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check pattern condition.

        Args:
            rule: The alert rule
            log_entries: List of log entries
            context: Alert context

        Returns:
            tuple[bool, Dict[str, Any]]: Tuple of (is_triggered, context)

        """
        pattern = rule.parameters.get("pattern", "")
        if not pattern:
            return False, context

        # Compile regex pattern
        try:
            regex = re.compile(pattern)
        except re.error:
            _logger.exception(f"Invalid regex pattern in rule {rule.name}: {pattern}")
            return False, context

        # Check for matches
        matches = []
        for entry in log_entries:
            message = entry.get("message", "")
            if regex.search(message):
                matches.append(entry)

        # Check if threshold is met
        min_matches = rule.parameters.get("min_matches", 1)
        is_triggered = len(matches) >= min_matches

        # Update context
        context.update({
            "pattern": pattern,
            "matches": len(matches),
            "min_matches": min_matches,
            "matching_logs": matches[:10],  # Limit to first 10 matches
        })

        return is_triggered, context

    def _check_threshold_condition(
        self, rule: AlertRule, context: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check threshold condition.

        Args:
            rule: The alert rule
            context: Alert context

        Returns:
            tuple[bool, Dict[str, Any]]: Tuple of (is_triggered, context)

        """
        metric_name = rule.parameters.get("metric")
        threshold = rule.parameters.get("threshold")
        operator = rule.parameters.get("operator", ">")
        window = rule.parameters.get("window", 300)  # 5 minutes in seconds

        if not metric_name or threshold is None:
            return False, context

        # Get metric history
        history = self.metrics_history.get(metric_name, [])

        # Filter by time window
        now = datetime.datetime.now()
        window_start = now - datetime.timedelta(seconds=window)
        window_history = [
            item for item in history
            if item["timestamp"] >= window_start
        ]

        if not window_history:
            return False, context

        # Calculate current value (average over window)
        current_value = sum(item["value"] for item in window_history) / len(window_history)

        # Check threshold
        is_triggered = False
        if operator == ">":
            is_triggered = current_value > threshold
        elif operator == ">=":
            is_triggered = current_value >= threshold
        elif operator == "<":
            is_triggered = current_value < threshold
        elif operator == "<=":
            is_triggered = current_value <= threshold
        elif operator == "==":
            is_triggered = current_value == threshold
        elif operator == "!=":
            is_triggered = current_value != threshold

        # Update context
        context.update({
            "metric": metric_name,
            "current_value": current_value,
            "threshold": threshold,
            "operator": operator,
            "window_seconds": window,
            "data_points": len(window_history),
        })

        return is_triggered, context

    def _check_anomaly_condition(
        self, rule: AlertRule, context: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check anomaly condition.

        Args:
            rule: The alert rule
            context: Alert context

        Returns:
            tuple[bool, Dict[str, Any]]: Tuple of (is_triggered, context)

        """
        metric_name = rule.parameters.get("metric")
        sensitivity = rule.parameters.get("sensitivity", 3.0)  # z-score threshold
        window = rule.parameters.get("window", 3600)  # 1 hour in seconds
        min_data_points = rule.parameters.get("min_data_points", 10)

        if not metric_name:
            return False, context

        # Get metric history
        history = self.metrics_history.get(metric_name, [])

        # Filter by time window
        now = datetime.datetime.now()
        window_start = now - datetime.timedelta(seconds=window)
        window_history = [
            item for item in history
            if item["timestamp"] >= window_start
        ]

        if len(window_history) < min_data_points:
            return False, context

        # Extract values
        values = [item["value"] for item in window_history]

        # Calculate z-score for the most recent value
        if len(values) >= 2:
            # Calculate mean and standard deviation excluding the most recent value
            historical_values = values[:-1]
            recent_value = values[-1]

            if np is None:
                # Fallback to basic Python statistics
                mean = sum(historical_values) / len(historical_values)
                variance = sum((x - mean) ** 2 for x in historical_values) / len(historical_values)
                std = variance ** 0.5
            else:
                mean = np.mean(historical_values)
                std = np.std(historical_values)

            # Avoid division by zero
            z_score = 0 if std == 0 else abs((recent_value - mean) / std)

            is_triggered = z_score > sensitivity

            # Update context
            context.update({
                "metric": metric_name,
                "current_value": recent_value,
                "mean": mean,
                "std": std,
                "z_score": z_score,
                "sensitivity": sensitivity,
                "window_seconds": window,
                "data_points": len(window_history),
            })

            return is_triggered, context

        return False, context

    def _check_frequency_condition(
        self, rule: AlertRule, log_entries: list[dict[str, Any]], context: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check frequency condition.

        Args:
            rule: The alert rule
            log_entries: List of log entries
            context: Alert context

        Returns:
            tuple[bool, Dict[str, Any]]: Tuple of (is_triggered, context)

        """
        threshold = rule.parameters.get("threshold", 100)
        level = rule.parameters.get("level")
        window = rule.parameters.get("window", 60)  # 1 minute in seconds

        # Filter logs by level if specified
        if level:
            filtered_logs = [entry for entry in log_entries if entry.get("level") == level]
        else:
            filtered_logs = log_entries

        # Filter logs by time window
        now = datetime.datetime.now()
        window_start = now - datetime.timedelta(seconds=window)
        window_logs = [
            entry for entry in filtered_logs
            if entry.get("timestamp", now) >= window_start
        ]

        # Check frequency
        frequency = len(window_logs)
        is_triggered = frequency > threshold

        # Update context
        context.update({
            "frequency": frequency,
            "threshold": threshold,
            "level": level,
            "window_seconds": window,
        })

        return is_triggered, context

    def _check_absence_condition(
        self, rule: AlertRule, log_entries: list[dict[str, Any]], context: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check absence condition.

        Args:
            rule: The alert rule
            log_entries: List of log entries
            context: Alert context

        Returns:
            tuple[bool, Dict[str, Any]]: Tuple of (is_triggered, context)

        """
        pattern = rule.parameters.get("pattern", "")
        level = rule.parameters.get("level")
        window = rule.parameters.get("window", 300)  # 5 minutes in seconds

        # Filter logs by level if specified
        if level:
            filtered_logs = [entry for entry in log_entries if entry.get("level") == level]
        else:
            filtered_logs = log_entries

        # Filter logs by time window
        now = datetime.datetime.now()
        window_start = now - datetime.timedelta(seconds=window)
        window_logs = [
            entry for entry in filtered_logs
            if entry.get("timestamp", now) >= window_start
        ]

        # Check for pattern matches
        if pattern:
            try:
                regex = re.compile(pattern)
                matches = [
                    entry for entry in window_logs
                    if regex.search(entry.get("message", ""))
                ]
            except re.error:
                _logger.exception(f"Invalid regex pattern in rule {rule.name}: {pattern}")
                matches = []
        else:
            matches = window_logs

        # Check absence
        is_triggered = len(matches) == 0

        # Update context
        context.update({
            "pattern": pattern,
            "level": level,
            "window_seconds": window,
            "logs_in_window": len(window_logs),
        })

        return is_triggered, context

    def _send_notifications(self, rule: AlertRule, context: dict[str, Any]) -> None:
        """
        Send notifications for a triggered alert.

        Args:
            rule: The triggered alert rule
            context: Alert context

        """
        for notifier_name in rule.notifiers:
            if notifier_name in self.notifiers:
                notifier = self.notifiers[notifier_name]
                try:
                    notifier.send_alert(rule, context)
                except Exception as e:
                    _logger.exception(f"Error sending notification via {notifier_name}: {e}")
            else:
                _logger.error(f"Notifier '{notifier_name}' not found for alert '{rule.name}'")
