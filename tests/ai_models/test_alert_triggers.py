"""
Tests for alert trigger functionality.

This module tests the alert threshold accuracy, alert correlation logic,
and alert suppression rules in the AI models monitoring system.
"""

import os
import pytest
import tempfile
import time
from datetime import datetime, timedelta
import threading
from unittest.mock import MagicMock, patch

from ai_models.metrics.api import MetricsAPI
from ai_models.metrics.enhanced_metrics import (
    EnhancedInferenceMetrics,
    EnhancedPerformanceMonitor
)
from ai_models.performance_monitor import AlertConfig


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Clean up
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def metrics_api(temp_db_path):
    """Create a metrics API instance with a temporary database."""
    api = MetricsAPI(db_path=temp_db_path)
    return api


def test_alert_threshold_accuracy(metrics_api):
    """Test that alerts are triggered accurately at the specified thresholds."""
    model_id = "threshold-test-model"
    
    # Set up alert handlers
    alert_handler = MagicMock()
    metrics_api.register_alert_handler("test", alert_handler)
    
    # Set up alerts for different metrics
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="latency_ms",
        threshold_value=200.0,
        is_upper_bound=True,  # Alert when latency > 200ms
        notification_channels=["test"]
    )
    
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="memory_usage_mb",
        threshold_value=500.0,
        is_upper_bound=True,  # Alert when memory > 500MB
        notification_channels=["test"]
    )
    
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="tokens_per_second",
        threshold_value=20.0,
        is_upper_bound=False,  # Alert when tokens_per_second < 20
        notification_channels=["test"]
    )
    
    # Test cases - each is a tuple of (metric_value, should_trigger)
    test_cases = [
        # Latency tests (threshold: > 200.0)
        {"latency_ms": 199.9, "should_trigger": False},
        {"latency_ms": 200.0, "should_trigger": False},
        {"latency_ms": 200.1, "should_trigger": True},
        {"latency_ms": 250.0, "should_trigger": True},
        
        # Memory tests (threshold: > 500.0)
        {"memory_usage_mb": 499.9, "should_trigger": False},
        {"memory_usage_mb": 500.0, "should_trigger": False},
        {"memory_usage_mb": 500.1, "should_trigger": True},
        {"memory_usage_mb": 600.0, "should_trigger": True},
        
        # Tokens per second tests (threshold: < 20.0)
        {"tokens_per_second": 20.1, "should_trigger": False},
        {"tokens_per_second": 20.0, "should_trigger": False},
        {"tokens_per_second": 19.9, "should_trigger": True},
        {"tokens_per_second": 15.0, "should_trigger": True},
    ]
    
    # Run test cases
    for i, case in enumerate(test_cases):
        # Reset mock
        alert_handler.reset_mock()
        
        # Create metrics with the test value
        metrics = EnhancedInferenceMetrics(
            model_id=model_id,
            latency_ms=case.get("latency_ms", 100.0),
            tokens_per_second=case.get("tokens_per_second", 50.0),
            memory_usage_mb=case.get("memory_usage_mb", 200.0),
            input_tokens=10,
            output_tokens=20
        )
        
        # Save metrics (this should trigger alert check)
        metrics_api.monitor.save_enhanced_metrics(metrics)
        
        # Check if alert was triggered as expected
        if case["should_trigger"]:
            alert_handler.assert_called_once()
        else:
            alert_handler.assert_not_called()


def test_alert_correlation_logic(metrics_api):
    """Test that alerts can be correlated across different metrics."""
    model_id = "correlation-test-model"
    
    # Set up alert handlers with correlation tracking
    alerts_triggered = []
    
    def alert_handler(message, alert_config, value):
        alerts_triggered.append({
            "metric": alert_config.metric_name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
    
    metrics_api.register_alert_handler("correlation", alert_handler)
    
    # Set up multiple alerts that might correlate
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="latency_ms",
        threshold_value=200.0,
        is_upper_bound=True,
        notification_channels=["correlation"]
    )
    
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="tokens_per_second",
        threshold_value=20.0,
        is_upper_bound=False,
        notification_channels=["correlation"]
    )
    
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="memory_usage_mb",
        threshold_value=500.0,
        is_upper_bound=True,
        notification_channels=["correlation"]
    )
    
    # Test correlation scenarios
    
    # Scenario 1: No correlation (only latency alert)
    alerts_triggered.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=250.0,  # Triggers alert
        tokens_per_second=30.0,  # No alert
        memory_usage_mb=400.0,  # No alert
        input_tokens=10,
        output_tokens=20
    ))
    
    assert len(alerts_triggered) == 1
    assert alerts_triggered[0]["metric"] == "latency_ms"
    
    # Scenario 2: Correlation between latency and tokens_per_second
    alerts_triggered.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=300.0,  # Triggers alert
        tokens_per_second=15.0,  # Triggers alert
        memory_usage_mb=400.0,  # No alert
        input_tokens=10,
        output_tokens=20
    ))
    
    assert len(alerts_triggered) == 2
    metrics = [alert["metric"] for alert in alerts_triggered]
    assert "latency_ms" in metrics
    assert "tokens_per_second" in metrics
    
    # Scenario 3: All three alerts triggered
    alerts_triggered.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=300.0,  # Triggers alert
        tokens_per_second=15.0,  # Triggers alert
        memory_usage_mb=600.0,  # Triggers alert
        input_tokens=10,
        output_tokens=20
    ))
    
    assert len(alerts_triggered) == 3
    metrics = [alert["metric"] for alert in alerts_triggered]
    assert "latency_ms" in metrics
    assert "tokens_per_second" in metrics
    assert "memory_usage_mb" in metrics
    
    # Implement a simple correlation detector
    def detect_correlations(alerts, time_window_seconds=60):
        """Detect correlations between alerts within a time window."""
        if len(alerts) <= 1:
            return []
        
        correlations = []
        for i, alert1 in enumerate(alerts):
            correlated = [alert1["metric"]]
            time1 = datetime.fromisoformat(alert1["timestamp"])
            
            for j, alert2 in enumerate(alerts):
                if i == j:
                    continue
                
                time2 = datetime.fromisoformat(alert2["timestamp"])
                if abs((time2 - time1).total_seconds()) <= time_window_seconds:
                    correlated.append(alert2["metric"])
            
            if len(correlated) > 1:
                correlations.append(correlated)
        
        return correlations
    
    # Check for correlations in the last scenario
    correlations = detect_correlations(alerts_triggered)
    assert len(correlations) > 0
    
    # At least one correlation should contain all three metrics
    found_all_three = False
    for corr in correlations:
        if set(corr) == {"latency_ms", "tokens_per_second", "memory_usage_mb"}:
            found_all_three = True
            break
    
    assert found_all_three, "Failed to detect correlation between all three metrics"


def test_alert_suppression_rules(metrics_api):
    """Test that alert suppression rules work correctly."""
    model_id = "suppression-test-model"
    
    # Set up alert handler
    alert_handler = MagicMock()
    metrics_api.register_alert_handler("suppression", alert_handler)
    
    # Set up alert with cooldown
    cooldown_minutes = 5
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="latency_ms",
        threshold_value=200.0,
        is_upper_bound=True,
        cooldown_minutes=cooldown_minutes,
        notification_channels=["suppression"]
    )
    
    # Test initial alert
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=250.0,  # Triggers alert
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    
    # Alert should be triggered
    alert_handler.assert_called_once()
    alert_handler.reset_mock()
    
    # Test immediate repeat - should be suppressed
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=300.0,  # Would trigger alert, but suppressed
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    
    # Alert should be suppressed
    alert_handler.assert_not_called()
    
    # Simulate time passing (just over cooldown period)
    # We need to modify the last_triggered time directly in the database
    alert_configs = metrics_api.monitor.metrics_db.get_alert_configs(model_id=model_id)
    for config in alert_configs:
        if config.metric_name == "latency_ms":
            # Set last_triggered to just over cooldown minutes ago
            past_time = datetime.now() - timedelta(minutes=cooldown_minutes, seconds=1)
            config.last_triggered = past_time.isoformat()
            metrics_api.monitor.metrics_db.save_alert_config(config)
    
    # Test after cooldown - should trigger again
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=350.0,  # Triggers alert again
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    
    # Alert should be triggered again
    alert_handler.assert_called_once()


def test_alert_suppression_with_severity(metrics_api):
    """Test alert suppression with severity levels."""
    model_id = "severity-test-model"
    
    # Track alerts with severity
    alerts_with_severity = []
    
    def severity_alert_handler(message, alert_config, value):
        # Calculate severity based on how far the value is from the threshold
        if alert_config.is_upper_bound:
            # For upper bound, higher values = higher severity
            ratio = value / alert_config.threshold_value
        else:
            # For lower bound, lower values = higher severity
            ratio = alert_config.threshold_value / value
        
        # Determine severity level
        if ratio > 2.0:
            severity = "critical"
        elif ratio > 1.5:
            severity = "high"
        elif ratio > 1.2:
            severity = "medium"
        else:
            severity = "low"
        
        alerts_with_severity.append({
            "metric": alert_config.metric_name,
            "value": value,
            "threshold": alert_config.threshold_value,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
    
    metrics_api.register_alert_handler("severity", severity_alert_handler)
    
    # Set up alert with severity-based suppression
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="latency_ms",
        threshold_value=100.0,
        is_upper_bound=True,
        cooldown_minutes=5,
        notification_channels=["severity"]
    )
    
    # Test different severity levels
    test_values = [
        120.0,  # Low severity (20% above threshold)
        150.0,  # Medium severity (50% above threshold)
        200.0,  # High severity (100% above threshold)
        300.0,  # Critical severity (200% above threshold)
    ]
    
    for value in test_values:
        alerts_with_severity.clear()
        
        metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
            model_id=model_id,
            latency_ms=value,
            tokens_per_second=30.0,
            memory_usage_mb=400.0,
            input_tokens=10,
            output_tokens=20
        ))
        
        assert len(alerts_with_severity) == 1
        
        # Verify severity calculation
        alert = alerts_with_severity[0]
        ratio = value / 100.0  # value / threshold
        
        if ratio > 2.0:
            assert alert["severity"] == "critical"
        elif ratio > 1.5:
            assert alert["severity"] == "high"
        elif ratio > 1.2:
            assert alert["severity"] == "medium"
        else:
            assert alert["severity"] == "low"
    
    # Implement a severity-based suppression rule
    # Higher severity alerts can override cooldown
    
    # First, clear the alerts and set up a new handler with this logic
    alerts_with_override = []
    last_alert_time = None
    last_alert_severity = None
    
    def override_alert_handler(message, alert_config, value):
        nonlocal last_alert_time, last_alert_severity
        
        # Calculate severity
        if alert_config.is_upper_bound:
            ratio = value / alert_config.threshold_value
        else:
            ratio = alert_config.threshold_value / value
        
        if ratio > 2.0:
            severity = "critical"
        elif ratio > 1.5:
            severity = "high"
        elif ratio > 1.2:
            severity = "medium"
        else:
            severity = "low"
        
        # Check if we should suppress based on cooldown and severity
        should_suppress = False
        if last_alert_time is not None:
            time_since_last = (datetime.now() - last_alert_time).total_seconds()
            cooldown_seconds = alert_config.cooldown_minutes * 60
            
            if time_since_last < cooldown_seconds:
                # Within cooldown period
                severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                
                # Only allow if current severity is higher than previous
                if severity_levels.get(severity, 0) <= severity_levels.get(last_alert_severity, 0):
                    should_suppress = True
        
        if not should_suppress:
            alerts_with_override.append({
                "metric": alert_config.metric_name,
                "value": value,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            })
            last_alert_time = datetime.now()
            last_alert_severity = severity
    
    # Register the new handler
    metrics_api.register_alert_handler("override", override_alert_handler)
    
    # Update alert config to use the new handler
    metrics_api.set_alert_threshold(
        model_id=model_id,
        metric_name="latency_ms",
        threshold_value=100.0,
        is_upper_bound=True,
        cooldown_minutes=5,
        notification_channels=["override"]
    )
    
    # Test severity-based override
    # First alert (medium severity)
    alerts_with_override.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=150.0,  # Medium severity
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    assert len(alerts_with_override) == 1
    assert alerts_with_override[0]["severity"] == "medium"
    
    # Second alert (low severity) - should be suppressed
    alerts_with_override.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=120.0,  # Low severity
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    assert len(alerts_with_override) == 0  # Suppressed
    
    # Third alert (high severity) - should override cooldown
    alerts_with_override.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=200.0,  # High severity
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    assert len(alerts_with_override) == 1  # Not suppressed
    assert alerts_with_override[0]["severity"] == "high"
    
    # Fourth alert (high severity again) - should be suppressed
    alerts_with_override.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=200.0,  # High severity
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    assert len(alerts_with_override) == 0  # Suppressed
    
    # Fifth alert (critical severity) - should override cooldown
    alerts_with_override.clear()
    metrics_api.monitor.save_enhanced_metrics(EnhancedInferenceMetrics(
        model_id=model_id,
        latency_ms=300.0,  # Critical severity
        tokens_per_second=30.0,
        memory_usage_mb=400.0,
        input_tokens=10,
        output_tokens=20
    ))
    assert len(alerts_with_override) == 1  # Not suppressed
    assert alerts_with_override[0]["severity"] == "critical"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
