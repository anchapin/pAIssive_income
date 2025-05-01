"""
Tests for metric collection functionality.

This module tests the accuracy, aggregation, and custom definition of metrics
in the AI models monitoring system.
"""

import os
import pytest
import tempfile
import time
from datetime import datetime, timedelta
import random
import sqlite3

from ai_models.metrics.api import MetricsAPI
from ai_models.metrics.enhanced_metrics import (
    EnhancedInferenceMetrics,
    TokenUsageMetrics,
    EnhancedPerformanceMonitor
)


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


def test_metric_accuracy(metrics_api):
    """Test that metrics are recorded accurately."""
    # Create test metrics
    test_metrics = EnhancedInferenceMetrics(
        model_id="test-model",
        latency_ms=123.45,
        tokens_per_second=67.89,
        memory_usage_mb=256.0,
        input_tokens=10,
        output_tokens=20,
        time_to_first_token=50.5,
        prompt_cost=0.0002,
        completion_cost=0.0003
    )
    
    # Save metrics
    metrics_api.monitor.save_enhanced_metrics(test_metrics)
    
    # Retrieve metrics
    retrieved_metrics = metrics_api.monitor.metrics_db.get_metrics(
        model_id="test-model",
        limit=1
    )[0]
    
    # Check accuracy of key metrics
    assert retrieved_metrics["model_id"] == "test-model"
    assert abs(retrieved_metrics["latency_ms"] - 123.45) < 0.001
    assert abs(retrieved_metrics["tokens_per_second"] - 67.89) < 0.001
    assert abs(retrieved_metrics["memory_usage_mb"] - 256.0) < 0.001
    assert retrieved_metrics["input_tokens"] == 10
    assert retrieved_metrics["output_tokens"] == 20
    assert abs(retrieved_metrics["time_to_first_token"] - 50.5) < 0.001
    assert abs(retrieved_metrics["prompt_cost"] - 0.0002) < 0.0001
    assert abs(retrieved_metrics["completion_cost"] - 0.0003) < 0.0001


def test_metric_aggregation_at_scale(metrics_api, temp_db_path):
    """Test that metrics can be aggregated correctly at scale."""
    # Generate a large number of test metrics
    num_metrics = 1000
    model_ids = ["model-A", "model-B", "model-C"]
    
    # Insert test metrics
    for i in range(num_metrics):
        model_id = model_ids[i % len(model_ids)]
        metrics = EnhancedInferenceMetrics(
            model_id=model_id,
            latency_ms=random.uniform(50, 500),
            tokens_per_second=random.uniform(10, 100),
            memory_usage_mb=random.uniform(100, 1000),
            input_tokens=random.randint(5, 50),
            output_tokens=random.randint(10, 100),
            time_to_first_token=random.uniform(10, 100),
            prompt_cost=random.uniform(0.0001, 0.001),
            completion_cost=random.uniform(0.0002, 0.002)
        )
        metrics_api.monitor.save_enhanced_metrics(metrics)
    
    # Test aggregation by model
    for model_id in model_ids:
        # Get metrics for this model
        model_metrics = metrics_api.monitor.metrics_db.get_metrics(
            model_id=model_id
        )
        
        # Check that we have the expected number of metrics
        assert len(model_metrics) == num_metrics // len(model_ids)
        
        # Generate a report for this model
        report = metrics_api.generate_report(
            model_id=model_id
        )
        
        # Check that the report contains aggregated metrics
        assert report.avg_latency_ms > 0
        assert report.avg_tokens_per_second > 0
        assert report.avg_memory_usage_mb > 0
        assert report.total_input_tokens > 0
        assert report.total_output_tokens > 0
        assert report.avg_time_to_first_token > 0
        assert report.total_prompt_cost > 0
        assert report.total_completion_cost > 0
        assert report.total_cost > 0
        
        # Verify that the aggregated metrics are correct
        total_latency = sum(m["latency_ms"] for m in model_metrics)
        avg_latency = total_latency / len(model_metrics)
        assert abs(report.avg_latency_ms - avg_latency) < 0.01


def test_custom_metric_definition(metrics_api):
    """Test that custom metrics can be defined and tracked."""
    # Define a custom metric by extending EnhancedInferenceMetrics
    class CustomMetrics(EnhancedInferenceMetrics):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.custom_metric1 = kwargs.get('custom_metric1', 0)
            self.custom_metric2 = kwargs.get('custom_metric2', 0)
    
    # Create and save custom metrics
    custom_metrics = CustomMetrics(
        model_id="custom-model",
        latency_ms=100.0,
        tokens_per_second=50.0,
        memory_usage_mb=200.0,
        input_tokens=15,
        output_tokens=25,
        custom_metric1=42,
        custom_metric2=99
    )
    
    # Save metrics using the raw database connection
    # Note: This is a test-only approach as the standard API doesn't support custom metrics directly
    conn = sqlite3.connect(metrics_api.monitor.metrics_db.db_path)
    cursor = conn.cursor()
    
    # Convert metrics to dictionary
    metrics_dict = custom_metrics.to_dict()
    
    # Add custom metrics to the dictionary
    metrics_dict['custom_metric1'] = custom_metrics.custom_metric1
    metrics_dict['custom_metric2'] = custom_metrics.custom_metric2
    
    # Create a table for custom metrics if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            latency_ms REAL,
            tokens_per_second REAL,
            memory_usage_mb REAL,
            input_tokens INTEGER,
            output_tokens INTEGER,
            custom_metric1 INTEGER,
            custom_metric2 INTEGER
        )
    """)
    
    # Insert custom metrics
    cursor.execute("""
        INSERT INTO custom_metrics (
            model_id, timestamp, latency_ms, tokens_per_second, memory_usage_mb,
            input_tokens, output_tokens, custom_metric1, custom_metric2
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metrics_dict['model_id'],
        metrics_dict['timestamp'],
        metrics_dict['latency_ms'],
        metrics_dict['tokens_per_second'],
        metrics_dict['memory_usage_mb'],
        metrics_dict['input_tokens'],
        metrics_dict['output_tokens'],
        metrics_dict['custom_metric1'],
        metrics_dict['custom_metric2']
    ))
    
    conn.commit()
    
    # Retrieve and verify custom metrics
    cursor.execute("""
        SELECT * FROM custom_metrics WHERE model_id = ?
    """, (custom_metrics.model_id,))
    
    row = cursor.fetchone()
    assert row is not None
    
    # Check that custom metrics were saved correctly
    assert row[1] == custom_metrics.model_id  # model_id
    assert abs(row[3] - custom_metrics.latency_ms) < 0.001  # latency_ms
    assert row[7] == custom_metrics.input_tokens  # input_tokens
    assert row[8] == custom_metrics.custom_metric1  # custom_metric1
    assert row[9] == custom_metrics.custom_metric2  # custom_metric2
    
    conn.close()


def test_metric_collection_over_time(metrics_api):
    """Test that metrics can be collected and analyzed over time."""
    model_id = "time-series-model"
    
    # Generate metrics over a time period (simulating 5 days of data)
    now = datetime.now()
    for day in range(5):
        # Generate 10 metrics per day
        for hour in range(0, 24, 2):
            timestamp = now - timedelta(days=day, hours=hour)
            
            # Create metrics with a pattern (higher latency during peak hours)
            peak_factor = 1.0
            if 9 <= hour <= 17:  # Business hours
                peak_factor = 1.5
            
            metrics = EnhancedInferenceMetrics(
                model_id=model_id,
                latency_ms=100.0 * peak_factor,
                tokens_per_second=50.0 / peak_factor,
                memory_usage_mb=200.0 * peak_factor,
                input_tokens=15,
                output_tokens=25,
                timestamp=timestamp.isoformat()
            )
            
            metrics_api.monitor.save_enhanced_metrics(metrics)
    
    # Test time-based queries
    # Get metrics for the last 2 days
    two_days_ago = now - timedelta(days=2)
    recent_metrics = metrics_api.monitor.metrics_db.get_metrics(
        model_id=model_id,
        time_range=(two_days_ago.isoformat(), now.isoformat())
    )
    
    # Should have metrics for days 0, 1, and 2 (partial)
    expected_count = 10 * 3  # 10 metrics per day for 3 days
    assert len(recent_metrics) == expected_count
    
    # Test time-based aggregation
    daily_reports = []
    for day in range(5):
        day_start = (now - timedelta(days=day)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1) - timedelta(microseconds=1)
        
        day_metrics = metrics_api.monitor.metrics_db.get_metrics(
            model_id=model_id,
            time_range=(day_start.isoformat(), day_end.isoformat())
        )
        
        if day_metrics:
            # Calculate daily average latency
            avg_latency = sum(m["latency_ms"] for m in day_metrics) / len(day_metrics)
            daily_reports.append({
                "day": day,
                "avg_latency": avg_latency,
                "count": len(day_metrics)
            })
    
    # Verify we have reports for each day
    assert len(daily_reports) == 5
    
    # Verify the pattern (higher latency during business days)
    # This assumes the current day is a weekday; adjust if needed
    weekday = now.weekday()
    for report in daily_reports:
        day = (weekday - report["day"]) % 7
        # Weekend days should have lower average latency
        if day in [5, 6]:  # Saturday or Sunday
            assert report["avg_latency"] < 120.0
        else:
            # Weekdays have a mix of peak and off-peak hours
            assert 100.0 <= report["avg_latency"] <= 150.0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
