"""Test module for common_utils.logging.alert_system."""

import datetime
import re
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.alert_system import (
    AlertCondition,
    AlertNotifier,
    AlertRule,
    AlertSeverity,
    AlertSystem,
    EmailNotifier,
    InAppNotifier,
    WebhookNotifier,
)


class TestAlertRule:
    """Test suite for AlertRule class."""

    def test_init(self):
        """Test initialization."""
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
        )
        assert rule.name == "Test Rule"
        assert rule.description == "Test description"
        assert rule.condition == AlertCondition.PATTERN
        assert rule.parameters == {"pattern": "error"}
        assert rule.severity == AlertSeverity.WARNING
        assert rule.notifiers == []
        assert rule.enabled is True
        assert rule.cooldown_period == 300
        assert rule.last_triggered is None
        assert rule.id == "test_rule"

    def test_is_in_cooldown(self):
        """Test cooldown period."""
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
            cooldown_period=1,  # 1 second for testing
        )

        # Initially not in cooldown
        assert rule.is_in_cooldown() is False

        # Mark as triggered
        rule.mark_triggered()
        assert rule.is_in_cooldown() is True

        # Wait for cooldown to expire
        time.sleep(1.1)
        assert rule.is_in_cooldown() is False


class MockNotifier(AlertNotifier):
    """Mock notifier for testing."""

    def __init__(self, name="mock"):
        """Initialize the mock notifier."""
        super().__init__(name)
        self.alerts = []

    def send_alert(self, alert_rule, context):
        """Send a mock alert."""
        self.alerts.append((alert_rule, context))
        return True


class TestAlertSystem:
    """Test suite for AlertSystem class."""

    def test_add_rule(self):
        """Test adding a rule."""
        system = AlertSystem()
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
        )

        system.add_rule(rule)
        assert len(system.rules) == 1
        assert system.rules[0] == rule

    def test_update_rule(self):
        """Test updating a rule."""
        system = AlertSystem()
        rule1 = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
            id="test_rule",
        )
        rule2 = AlertRule(
            name="Updated Rule",
            description="Updated description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "updated"},
            id="test_rule",
        )

        system.add_rule(rule1)
        system.add_rule(rule2)
        assert len(system.rules) == 1
        assert system.rules[0].name == "Updated Rule"
        assert system.rules[0].description == "Updated description"
        assert system.rules[0].parameters == {"pattern": "updated"}

    def test_remove_rule(self):
        """Test removing a rule."""
        system = AlertSystem()
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
        )

        system.add_rule(rule)
        assert len(system.rules) == 1

        result = system.remove_rule(rule.id)
        assert result is True
        assert len(system.rules) == 0

        result = system.remove_rule("nonexistent")
        assert result is False

    def test_add_notifier(self):
        """Test adding a notifier."""
        system = AlertSystem()
        notifier = MockNotifier()

        system.add_notifier(notifier)
        assert len(system.notifiers) == 1
        assert system.notifiers["mock"] == notifier

    def test_remove_notifier(self):
        """Test removing a notifier."""
        system = AlertSystem()
        notifier = MockNotifier()

        system.add_notifier(notifier)
        assert len(system.notifiers) == 1

        result = system.remove_notifier("mock")
        assert result is True
        assert len(system.notifiers) == 0

        result = system.remove_notifier("nonexistent")
        assert result is False

    def test_process_logs_pattern(self):
        """Test processing logs with pattern condition."""
        system = AlertSystem()
        notifier = MockNotifier()
        system.add_notifier(notifier)

        rule = AlertRule(
            name="Error Pattern",
            description="Detect error patterns",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error", "min_matches": 1},
            notifiers=["mock"],
        )
        system.add_rule(rule)

        # Create log entries
        log_entries = [
            {
                "timestamp": datetime.datetime.now(),
                "level": "ERROR",
                "name": "test",
                "message": "This is an error message",
            },
            {
                "timestamp": datetime.datetime.now(),
                "level": "INFO",
                "name": "test",
                "message": "This is an info message",
            },
        ]

        # Process logs
        alerts = system.process_logs(log_entries)

        # Check results
        assert len(alerts) == 1
        assert alerts[0]["rule"] == "Error Pattern"
        assert alerts[0]["severity"] == AlertSeverity.WARNING
        assert "context" in alerts[0]
        assert alerts[0]["context"]["matches"] == 1

        # Check notifier
        assert len(notifier.alerts) == 1
        assert notifier.alerts[0][0] == rule

    def test_process_logs_threshold(self):
        """Test processing logs with threshold condition."""
        system = AlertSystem()
        notifier = MockNotifier()
        system.add_notifier(notifier)

        rule = AlertRule(
            name="High Error Rate",
            description="Detect high error rate",
            condition=AlertCondition.THRESHOLD,
            parameters={"metric": "error_rate", "threshold": 0.3, "operator": ">"},
            notifiers=["mock"],
        )
        system.add_rule(rule)

        # Create log entries with high error rate
        log_entries = [
            {
                "timestamp": datetime.datetime.now(),
                "level": "ERROR",
                "name": "test",
                "message": "This is an error message",
            },
            {
                "timestamp": datetime.datetime.now(),
                "level": "ERROR",
                "name": "test",
                "message": "This is another error message",
            },
            {
                "timestamp": datetime.datetime.now(),
                "level": "INFO",
                "name": "test",
                "message": "This is an info message",
            },
        ]

        # Process logs
        alerts = system.process_logs(log_entries)

        # Check results
        assert len(alerts) == 1
        assert alerts[0]["rule"] == "High Error Rate"
        assert "context" in alerts[0]
        assert alerts[0]["context"]["metric"] == "error_rate"
        assert alerts[0]["context"]["current_value"] > 0.3

        # Check notifier
        assert len(notifier.alerts) == 1
        assert notifier.alerts[0][0] == rule

    def test_process_logs_cooldown(self):
        """Test alert cooldown period."""
        system = AlertSystem()
        notifier = MockNotifier()
        system.add_notifier(notifier)

        rule = AlertRule(
            name="Error Pattern",
            description="Detect error patterns",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error", "min_matches": 1},
            notifiers=["mock"],
            cooldown_period=1,  # 1 second for testing
        )
        system.add_rule(rule)

        # Create log entries
        log_entries = [
            {
                "timestamp": datetime.datetime.now(),
                "level": "ERROR",
                "name": "test",
                "message": "This is an error message",
            },
        ]

        # Process logs first time
        alerts1 = system.process_logs(log_entries)
        assert len(alerts1) == 1
        assert len(notifier.alerts) == 1

        # Process logs again immediately (should be in cooldown)
        alerts2 = system.process_logs(log_entries)
        assert len(alerts2) == 0
        assert len(notifier.alerts) == 1

        # Wait for cooldown to expire
        time.sleep(1.1)

        # Process logs again (cooldown expired)
        alerts3 = system.process_logs(log_entries)
        assert len(alerts3) == 1
        assert len(notifier.alerts) == 2


class TestEmailNotifier:
    """Test suite for EmailNotifier class."""

    @patch("smtplib.SMTP")
    def test_send_alert(self, mock_smtp):
        """Test sending an email alert."""
        # Create mock SMTP instance
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Create notifier
        notifier = EmailNotifier(
            smtp_host="smtp.example.com",
            smtp_port=587,
            username="user",
            password="password",
            from_email="alerts@example.com",
            to_emails=["admin@example.com"],
        )

        # Create rule and context
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
            severity=AlertSeverity.WARNING,
        )
        context = {"matches": 1}

        # Send alert
        result = notifier.send_alert(rule, context)

        # Check result
        assert result is True

        # Check SMTP calls
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("user", "password")
        mock_smtp_instance.send_message.assert_called_once()


class TestWebhookNotifier:
    """Test suite for WebhookNotifier class."""

    @patch("requests.post")
    def test_send_alert(self, mock_post):
        """Test sending a webhook alert."""
        # Configure mock
        mock_post.return_value.raise_for_status.return_value = None

        # Create notifier
        notifier = WebhookNotifier(
            url="https://example.com/webhook",
            headers={"Authorization": "Bearer token"},
        )

        # Create rule and context
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
            severity=AlertSeverity.WARNING,
        )
        context = {"matches": 1}

        # Send alert
        result = notifier.send_alert(rule, context)

        # Check result
        assert result is True

        # Check requests.post call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://example.com/webhook"
        assert kwargs["headers"] == {"Authorization": "Bearer token"}
        assert "json" in kwargs
        assert kwargs["json"]["alert"]["name"] == "Test Rule"
        assert kwargs["json"]["context"] == {"matches": 1}


class TestInAppNotifier:
    """Test suite for InAppNotifier class."""

    def test_send_alert(self):
        """Test sending an in-app alert."""
        # Create mock callback
        callback = MagicMock()

        # Create notifier
        notifier = InAppNotifier(callback=callback)

        # Create rule and context
        rule = AlertRule(
            name="Test Rule",
            description="Test description",
            condition=AlertCondition.PATTERN,
            parameters={"pattern": "error"},
            severity=AlertSeverity.WARNING,
        )
        context = {"matches": 1}

        # Send alert
        result = notifier.send_alert(rule, context)

        # Check result
        assert result is True

        # Check callback call
        callback.assert_called_once_with(rule, context)
