"""
Tests for the PerformanceMonitor class.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

from ai_models.performance_monitor import (
    PerformanceMonitor,
    InferenceTracker,
    InferenceMetrics,
    ModelPerformanceReport,
)


@pytest.fixture
def mock_model():
    """Create a mock model."""
    model = MagicMock()
    model.name = "Test Model"
    model.id = "test-model"
    return model


def test_inference_metrics_init():
    """Test InferenceMetrics initialization."""
    metrics = InferenceMetrics(
        model_id="test-model",
        latency_ms=100,
        tokens_per_second=10,
        memory_usage_mb=1000,
        input_tokens=10,
        output_tokens=20,
    )

    # Check that the metrics have the expected attributes
    assert metrics.model_id == "test-model"
    assert metrics.latency_ms == 100
    assert metrics.tokens_per_second == 10
    assert metrics.memory_usage_mb == 1000
    assert metrics.input_tokens == 10
    assert metrics.output_tokens == 20
    assert isinstance(metrics.timestamp, str)


def test_inference_metrics_to_dict():
    """Test to_dict method of InferenceMetrics."""
    metrics = InferenceMetrics(
        model_id="test-model",
        latency_ms=100,
        tokens_per_second=10,
        memory_usage_mb=1000,
        input_tokens=10,
        output_tokens=20,
    )

    # Convert to dictionary
    metrics_dict = metrics.to_dict()

    # Check that the dictionary has the expected keys
    assert "model_id" in metrics_dict
    assert "latency_ms" in metrics_dict
    assert "tokens_per_second" in metrics_dict
    assert "memory_usage_mb" in metrics_dict
    assert "input_tokens" in metrics_dict
    assert "output_tokens" in metrics_dict
    assert "timestamp" in metrics_dict

    # Check that the values are correct
    assert metrics_dict["model_id"] == "test-model"
    assert metrics_dict["latency_ms"] == 100
    assert metrics_dict["tokens_per_second"] == 10
    assert metrics_dict["memory_usage_mb"] == 1000
    assert metrics_dict["input_tokens"] == 10
    assert metrics_dict["output_tokens"] == 20


def test_inference_tracker_init():
    """Test InferenceTracker initialization."""
    monitor = PerformanceMonitor()
    tracker = InferenceTracker(monitor=monitor, model_id="test-model")

    # Check that the tracker has the expected attributes
    assert tracker.model_id == "test-model"
    assert tracker.monitor == monitor
    assert hasattr(tracker, "start_time")
    assert hasattr(tracker, "end_time")
    assert hasattr(tracker, "input_tokens")
    assert hasattr(tracker, "output_tokens")
    assert hasattr(tracker, "memory_usage_start")
    assert hasattr(tracker, "memory_usage_end")


def test_inference_tracker_start_stop(mock_model):
    """Test start and stop methods of InferenceTracker."""
    monitor = PerformanceMonitor()
    tracker = InferenceTracker(monitor=monitor, model_id=mock_model.id)

    # Start tracking
    tracker.start(input_text="Hello, world!")

    # Check that start_time is set
    assert tracker.start_time is not None

    # Add a small delay to ensure latency is measurable
    import time

    time.sleep(0.01)

    # Stop tracking
    metrics = tracker.stop(output_text="Hello, AI!")

    # Check that end_time is set
    assert tracker.end_time is not None

    # Check that metrics were returned
    assert isinstance(metrics, InferenceMetrics)
    assert metrics.model_id == mock_model.id
    assert metrics.latency_ms > 0
    assert metrics.input_tokens > 0
    assert metrics.output_tokens > 0


def test_performance_monitor_init():
    """Test PerformanceMonitor initialization."""
    monitor = PerformanceMonitor()

    # Check that the monitor has the expected attributes
    assert hasattr(monitor, "metrics_history")
    assert isinstance(monitor.metrics_history, dict)
    assert hasattr(monitor, "report_cache")
    assert isinstance(monitor.report_cache, dict)


def test_performance_monitor_track_inference(mock_model):
    """Test track_inference method of PerformanceMonitor."""
    monitor = PerformanceMonitor()

    # Track inference
    metrics = monitor.track_inference(
        model=mock_model, input_text="Hello, world!", output_text="Hello, AI!"
    )

    # Check that metrics were returned
    assert isinstance(metrics, InferenceMetrics)
    assert metrics.model_id == mock_model.id
    assert metrics.latency_ms > 0
    assert metrics.input_tokens > 0
    assert metrics.output_tokens > 0

    # Check that metrics were added to history
    assert mock_model.id in monitor.metrics_history
    assert len(monitor.metrics_history[mock_model.id]) == 1
    assert monitor.metrics_history[mock_model.id][0] == metrics


def test_performance_monitor_get_model_metrics(mock_model):
    """Test get_model_metrics method of PerformanceMonitor."""
    monitor = PerformanceMonitor()

    # Add some metrics to history
    metrics1 = InferenceMetrics(
        model_id=mock_model.id,
        latency_ms=100,
        tokens_per_second=10,
        memory_usage_mb=1000,
        input_tokens=10,
        output_tokens=20,
    )

    metrics2 = InferenceMetrics(
        model_id=mock_model.id,
        latency_ms=200,
        tokens_per_second=20,
        memory_usage_mb=1100,
        input_tokens=15,
        output_tokens=25,
    )

    monitor.metrics_history[mock_model.id] = [metrics1, metrics2]

    # Get model metrics
    model_metrics = monitor.get_model_metrics(mock_model.id)

    # Check that metrics were returned
    assert isinstance(model_metrics, list)
    assert len(model_metrics) == 2
    assert model_metrics[0] == metrics1
    assert model_metrics[1] == metrics2


def test_performance_monitor_generate_report(mock_model):
    """Test generate_report method of PerformanceMonitor."""
    monitor = PerformanceMonitor()

    # Add some metrics to history
    metrics1 = InferenceMetrics(
        model_id=mock_model.id,
        latency_ms=100,
        tokens_per_second=10,
        memory_usage_mb=1000,
        input_tokens=10,
        output_tokens=20,
    )

    metrics2 = InferenceMetrics(
        model_id=mock_model.id,
        latency_ms=200,
        tokens_per_second=20,
        memory_usage_mb=1100,
        input_tokens=15,
        output_tokens=25,
    )

    monitor.metrics_history[mock_model.id] = [metrics1, metrics2]

    # Generate report
    report = monitor.generate_report(mock_model.id)

    # Check that report was returned
    assert isinstance(report, ModelPerformanceReport)
    assert report.model_id == mock_model.id
    assert report.num_inferences == 2
    assert report.avg_latency_ms == 150  # (100 + 200) / 2
    assert report.avg_tokens_per_second == 15  # (10 + 20) / 2
    assert report.avg_memory_usage_mb == 1050  # (1000 + 1100) / 2
    assert report.total_input_tokens == 25  # 10 + 15
    assert report.total_output_tokens == 45  # 20 + 25


def test_model_performance_report_init():
    """Test ModelPerformanceReport initialization."""
    report = ModelPerformanceReport(
        model_id="test-model",
        num_inferences=10,
        avg_latency_ms=150,
        avg_tokens_per_second=15,
        avg_memory_usage_mb=1050,
        total_input_tokens=100,
        total_output_tokens=200,
    )

    # Check that the report has the expected attributes
    assert report.model_id == "test-model"
    assert report.num_inferences == 10
    assert report.avg_latency_ms == 150
    assert report.avg_tokens_per_second == 15
    assert report.avg_memory_usage_mb == 1050
    assert report.total_input_tokens == 100
    assert report.total_output_tokens == 200
    assert isinstance(report.timestamp, str)


def test_model_performance_report_to_dict():
    """Test to_dict method of ModelPerformanceReport."""
    report = ModelPerformanceReport(
        model_id="test-model",
        num_inferences=10,
        avg_latency_ms=150,
        avg_tokens_per_second=15,
        avg_memory_usage_mb=1050,
        total_input_tokens=100,
        total_output_tokens=200,
    )

    # Convert to dictionary
    report_dict = report.to_dict()

    # Check that the dictionary has the expected keys
    assert "model_id" in report_dict
    assert "num_inferences" in report_dict
    assert "avg_latency_ms" in report_dict
    assert "avg_tokens_per_second" in report_dict
    assert "avg_memory_usage_mb" in report_dict
    assert "total_input_tokens" in report_dict
    assert "total_output_tokens" in report_dict
    assert "timestamp" in report_dict

    # Check that the values are correct
    assert report_dict["model_id"] == "test-model"
    assert report_dict["num_inferences"] == 10
    assert report_dict["avg_latency_ms"] == 150
    assert report_dict["avg_tokens_per_second"] == 15
    assert report_dict["avg_memory_usage_mb"] == 1050
    assert report_dict["total_input_tokens"] == 100
    assert report_dict["total_output_tokens"] == 200
