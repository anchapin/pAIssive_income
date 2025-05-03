"""
Tests for metric collection functionality.

This module tests the accuracy, aggregation, and custom definition of metrics
in the AI models monitoring system.
"""

import os
import random
import sqlite3
import tempfile
import time
from datetime import datetime, timedelta

import pytest

from ai_models.metrics.api import MetricsAPI
from ai_models.metrics.enhanced_metrics import (
    EnhancedInferenceMetrics,
    EnhancedPerformanceMonitor,
    TokenUsageMetrics,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
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
        model_id="test - model",
        latency_ms=123.45,
        tokens_per_second=67.89,
        memory_usage_mb=256.0,
        input_tokens=10,
        output_tokens=20,
        time_to_first_token=50.5,
        prompt_cost=0.0002,
        completion_cost=0.0003,
    )

    # Save metrics
    metrics_api.monitor.save_enhanced_metrics(test_metrics)

    # Retrieve metrics
    retrieved_metrics = metrics_api.monitor.metrics_db.get_metrics(model_id="test - model", 
        limit=1)[
        0
    ]

    # Check accuracy of key metrics
    assert retrieved_metrics["model_id"] == "test - model"
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
    model_ids = ["model - A", "model - B", "model - C"]

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
            completion_cost=random.uniform(0.0002, 0.002),
        )
        metrics_api.monitor.save_enhanced_metrics(metrics)

    # Test aggregation by model
    for model_id in model_ids:
        # Get metrics for this model
        model_metrics = metrics_api.monitor.metrics_db.get_metrics(model_id=model_id)

        # Check that we have the expected number of metrics
        assert len(model_metrics) == num_metrics // len(model_ids)

        # Generate a report for this model
        report = metrics_api.generate_report(model_id=model_id)

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
            self.custom_metric1 = kwargs.get("custom_metric1", 0)
            self.custom_metric2 = kwargs.get("custom_metric2", 0)
            self.custom_timestamp = kwargs.get("timestamp", datetime.now().isoformat())

        def to_dict(self):
            base_dict = super().to_dict()
            base_dict.update(
                {
                    "custom_metric1": self.custom_metric1,
                    "custom_metric2": self.custom_metric2,
                    "timestamp": self.custom_timestamp,
                }
            )
            return base_dict

        @classmethod
        def from_dict(cls, data):
            return cls(**data)

    # Create and save custom metrics with timestamps over a time period
    base_time = datetime.now()
    custom_metrics_list = []

    for i in range(5):
        timestamp = (base_time - timedelta(hours=i)).isoformat()
        custom_metrics = CustomMetrics(
            model_id="custom - model",
            latency_ms=100.0 + i * 10,
            tokens_per_second=50.0 - i * 2,
            memory_usage_mb=200.0 + i * 20,
            input_tokens=15 + i,
            output_tokens=25 + i * 2,
            custom_metric1=40 + i,
            custom_metric2=95 + i * 2,
            timestamp=timestamp,
        )
        custom_metrics_list.append(custom_metrics)

    # Create schema in database
    conn = sqlite3.connect(metrics_api.monitor.metrics_db.db_path)
    cursor = conn.cursor()

    # Create table with proper schema including time - series support
    cursor.execute(
        """
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
            custom_metric2 INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create index on timestamp for time - series queries
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_custom_metrics_timestamp 
        ON custom_metrics(timestamp)
    """
    )

    # Insert metrics with timestamps
    for metrics in custom_metrics_list:
        metrics_dict = metrics.to_dict()
        cursor.execute(
            """
            INSERT INTO custom_metrics (
                model_id, timestamp, latency_ms, tokens_per_second, memory_usage_mb,
                input_tokens, output_tokens, custom_metric1, custom_metric2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics_dict["model_id"],
                metrics_dict["timestamp"],
                metrics_dict["latency_ms"],
                metrics_dict["tokens_per_second"],
                metrics_dict["memory_usage_mb"],
                metrics_dict["input_tokens"],
                metrics_dict["output_tokens"],
                metrics_dict["custom_metric1"],
                metrics_dict["custom_metric2"],
            ),
        )

    conn.commit()

    # Test time - series queries
    # Get metrics for last 3 hours
    cursor.execute(
        """
        SELECT * FROM custom_metrics 
        WHERE timestamp >= ? 
        ORDER BY timestamp DESC
        LIMIT 3
    """,
        ((base_time - timedelta(hours=3)).isoformat(),),
    )

    recent_metrics = cursor.fetchall()
    assert len(recent_metrics) == 3

    # Verify values are correctly stored and retrieved
    first_metric = recent_metrics[0]
    assert first_metric[1] == "custom - model"  # model_id
    assert abs(first_metric[3] - 100.0) < 0.001  # latency_ms
    assert first_metric[7] == 15  # input_tokens
    assert first_metric[8] == 40  # custom_metric1
    assert first_metric[9] == 95  # custom_metric2

    # Test aggregations
    cursor.execute(
        """
        SELECT 
            AVG(latency_ms) as avg_latency,
            AVG(custom_metric1) as avg_custom1,
            MAX(custom_metric2) as max_custom2
        FROM custom_metrics
        WHERE model_id = ?
    """,
        ("custom - model",),
    )

    aggs = cursor.fetchone()
    assert 100.0 <= aggs[0] <= 140.0  # avg_latency
    assert 40 <= aggs[1] <= 44  # avg_custom1
    assert aggs[2] >= 95  # max_custom2

    # Clean up
    conn.close()


def test_metric_collection_over_time(metrics_api):
    """Test that metrics can be collected and analyzed over time."""
    model_id = "time - series - model"

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
                timestamp=timestamp.isoformat(),
            )

            metrics_api.monitor.save_enhanced_metrics(metrics)

    # Test time - based queries
    # Get metrics for the last 2 days
    two_days_ago = now - timedelta(days=2)
    recent_metrics = metrics_api.monitor.metrics_db.get_metrics(
        model_id=model_id, time_range=(two_days_ago.isoformat(), now.isoformat())
    )

    # Should have metrics for days 0, 1, and 2 (partial)
    expected_count = 10 * 3  # 10 metrics per day for 3 days
    assert len(recent_metrics) == expected_count

    # Test time - based aggregation
    daily_reports = []
    for day in range(5):
        day_start = (now - timedelta(days=day)).replace(hour=0, minute=0, second=0, 
            microsecond=0)
        day_end = day_start + timedelta(days=1) - timedelta(microseconds=1)

        day_metrics = metrics_api.monitor.metrics_db.get_metrics(
            model_id=model_id, time_range=(day_start.isoformat(), day_end.isoformat())
        )

        if day_metrics:
            # Calculate daily average latency
            avg_latency = sum(m["latency_ms"] for m in day_metrics) / len(day_metrics)
            daily_reports.append(
                {"day": day, "avg_latency": avg_latency, "count": len(day_metrics)}
            )

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
            # Weekdays have a mix of peak and off - peak hours
            assert 100.0 <= report["avg_latency"] <= 150.0


def test_custom_metric_validation(metrics_api):
    """Test validation and configuration of custom metrics."""

    class ValidatedMetrics(EnhancedInferenceMetrics):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.custom_metric1 = self._validate_metric1(kwargs.get("custom_metric1", 
                0))
            self.custom_metric2 = self._validate_metric2(kwargs.get("custom_metric2", 
                0))

        def _validate_metric1(self, value):
            """Validate custom_metric1 is within acceptable range."""
            if not isinstance(value, int):
                raise ValueError("custom_metric1 must be an integer")
            if not 0 <= value <= 100:
                raise ValueError("custom_metric1 must be between 0 and 100")
            return value

        def _validate_metric2(self, value):
            """Validate custom_metric2 is within acceptable range."""
            if not isinstance(value, int):
                raise ValueError("custom_metric2 must be an integer")
            if not 0 <= value <= 1000:
                raise ValueError("custom_metric2 must be between 0 and 1000")
            return value

        @classmethod
        def get_metric_config(cls):
            """Get metric configuration including valid ranges."""
            base_config = super().get_metric_config()
            base_config.update(
                {
                    "custom_metric1": {
                        "type": "integer",
                        "range": [0, 100],
                        "description": "Custom metric 1 with range 0 - 100",
                    },
                    "custom_metric2": {
                        "type": "integer",
                        "range": [0, 1000],
                        "description": "Custom metric 2 with range 0 - 1000",
                    },
                }
            )
            return base_config

    # Test valid metric creation
    valid_metrics = ValidatedMetrics(
        model_id="validated - model",
        latency_ms=100.0,
        tokens_per_second=50.0,
        memory_usage_mb=200.0,
        custom_metric1=50,  # Valid value
        custom_metric2=500,  # Valid value
    )

    # Verify valid metrics were created successfully
    assert valid_metrics.custom_metric1 == 50
    assert valid_metrics.custom_metric2 == 500

    # Test invalid metric1 value
    with pytest.raises(ValueError) as exc_info:
        ValidatedMetrics(
            model_id="validated - model", latency_ms=100.0, 
                custom_metric1=150  # Invalid: > 100
        )
    assert "custom_metric1 must be between 0 and 100" in str(exc_info.value)

    # Test invalid metric2 value
    with pytest.raises(ValueError) as exc_info:
        ValidatedMetrics(
            model_id="validated - model", latency_ms=100.0, 
                custom_metric2=1500  # Invalid: > 1000
        )
    assert "custom_metric2 must be between 0 and 1000" in str(exc_info.value)

    # Test invalid type
    with pytest.raises(ValueError) as exc_info:
        ValidatedMetrics(
            model_id="validated - model",
            latency_ms=100.0,
            custom_metric1=50.5,  # Invalid: float instead of int
        )
    assert "custom_metric1 must be an integer" in str(exc_info.value)

    # Verify metric configuration is correctly exposed
    config = ValidatedMetrics.get_metric_config()
    assert "custom_metric1" in config
    assert config["custom_metric1"]["type"] == "integer"
    assert config["custom_metric1"]["range"] == [0, 100]
    assert "custom_metric2" in config
    assert config["custom_metric2"]["type"] == "integer"
    assert config["custom_metric2"]["range"] == [0, 1000]


if __name__ == "__main__":
    pytest.main([" - xvs", __file__])
