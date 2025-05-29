"""Test module for common_utils.logging.ml_log_analysis."""

import datetime
import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from common_utils.logging.ml_log_analysis import (
    AnomalyDetector,
    LogAnalyzer,
    LogClusterer,
    PatternRecognizer,
    cluster_logs,
    detect_anomalies,
    recognize_patterns,
    train_anomaly_detector,
)


@pytest.fixture
def sample_log_entries():
    """Create sample log entries for testing."""
    return [
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 0, 0),
            "level": "INFO",
            "name": "test",
            "message": "This is a normal log message",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 1, 0),
            "level": "INFO",
            "name": "test",
            "message": "Another normal log message",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 2, 0),
            "level": "ERROR",
            "name": "test",
            "message": "This is an error message",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 3, 0),
            "level": "ERROR",
            "name": "test",
            "message": 'Another error message with exception\nTraceback (most recent call last):\n  File "test.py", line 10, in <module>\n    raise Exception("Test exception")\nException: Test exception',
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 4, 0),
            "level": "WARNING",
            "name": "test",
            "message": "This is a warning message",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 5, 0),
            "level": "INFO",
            "name": "test",
            "message": "Database query took 100 ms",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 6, 0),
            "level": "INFO",
            "name": "test",
            "message": "Database query took 150 ms",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 7, 0),
            "level": "INFO",
            "name": "test",
            "message": "Database query took 200 ms",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 8, 0),
            "level": "INFO",
            "name": "test",
            "message": "API request completed in 50 ms",
        },
        {
            "timestamp": datetime.datetime(2023, 1, 1, 12, 9, 0),
            "level": "INFO",
            "name": "test",
            "message": "API request completed in 60 ms",
        },
    ]


class TestAnomalyDetector:
    """Test suite for AnomalyDetector class."""

    def test_init(self):
        """Test initialization."""
        detector = AnomalyDetector()
        assert detector.threshold == 3.0
        assert detector.trained is False

    def test_extract_features(self, sample_log_entries):
        """Test feature extraction."""
        detector = AnomalyDetector()
        features = detector.extract_features(sample_log_entries)

        # Check feature shape
        assert features.shape == (len(sample_log_entries), 13)

        # Check feature names
        assert len(detector.feature_names) == 13
        assert "hour" in detector.feature_names
        assert "is_error" in detector.feature_names

        # Check feature values
        assert features[2, detector.feature_names.index("is_error")] == 1  # ERROR entry
        assert features[0, detector.feature_names.index("is_error")] == 0  # INFO entry

    def test_train(self, sample_log_entries):
        """Test training."""
        detector = AnomalyDetector()
        detector.train(sample_log_entries)

        assert detector.trained is True
        assert hasattr(detector, 'threshold')

    def test_detect(self, sample_log_entries):
        """Test anomaly detection."""
        detector = AnomalyDetector(threshold=1.0)
        detector.train(sample_log_entries)

        anomalies = detector.detect(sample_log_entries)

        # Check that anomalies were detected
        assert len(anomalies) > 0

        # Check anomaly structure
        for anomaly in anomalies:
            assert "anomaly_score" in anomaly
            assert "feature_values" in anomaly
            assert isinstance(anomaly["anomaly_score"], float)
            assert isinstance(anomaly["feature_values"], dict)

    def test_detect_without_training(self, sample_log_entries):
        """Test detection without training."""
        detector = AnomalyDetector()
        anomalies = detector.detect(sample_log_entries)

        assert anomalies == []


class TestPatternRecognizer:
    """Test suite for PatternRecognizer class."""

    def test_init(self):
        """Test initialization."""
        recognizer = PatternRecognizer(min_pattern_count=5)
        assert recognizer.min_pattern_count == 5
        assert recognizer.trained is False

    def test_train(self, sample_log_entries):
        """Test training."""
        recognizer = PatternRecognizer()
        recognizer.train(sample_log_entries)

        assert recognizer.trained is True
        assert hasattr(recognizer, 'vocab')
        assert hasattr(recognizer, 'idf')

    def test_recognize(self, sample_log_entries):
        """Test pattern recognition."""
        recognizer = PatternRecognizer(min_pattern_count=2)
        recognizer.train(sample_log_entries)

        patterns = recognizer.recognize(sample_log_entries)

        # Check that patterns were recognized
        assert len(patterns) > 0

        # Check pattern structure
        for pattern in patterns:
            assert "pattern" in pattern
            assert "count" in pattern
            assert "examples" in pattern
            assert isinstance(pattern["pattern"], str)
            assert isinstance(pattern["count"], int)
            assert isinstance(pattern["examples"], list)

    def test_recognize_without_training(self, sample_log_entries):
        """Test recognition without training."""
        recognizer = PatternRecognizer()
        patterns = recognizer.recognize(sample_log_entries)

        assert patterns == []


class TestLogClusterer:
    """Test suite for LogClusterer class."""

    def test_init(self):
        """Test initialization."""
        clusterer = LogClusterer(n_clusters=2)
        assert clusterer.n_clusters == 2
        assert clusterer.trained is False

    def test_train(self, sample_log_entries):
        """Test training."""
        clusterer = LogClusterer()
        clusterer.train(sample_log_entries)

        assert clusterer.trained is True
        assert hasattr(clusterer, 'centroids')
        assert hasattr(clusterer, 'labels_')
        assert hasattr(clusterer, 'vocab')
        assert hasattr(clusterer, 'idf')

    def test_cluster(self, sample_log_entries):
        """Test log clustering."""
        clusterer = LogClusterer(n_clusters=2)
        clusterer.train(sample_log_entries)

        clusters = clusterer.cluster(sample_log_entries)

        # Check that clusters were found
        assert len(clusters) > 0

        # Check cluster structure
        for cluster in clusters:
            assert "cluster_id" in cluster
            assert "size" in cluster
            assert "common_terms" in cluster
            assert "entries" in cluster
            assert isinstance(cluster["cluster_id"], int)
            assert isinstance(cluster["size"], int)
            assert isinstance(cluster["common_terms"], list)
            assert isinstance(cluster["entries"], list)

    def test_cluster_without_training(self, sample_log_entries):
        """Test clustering without training."""
        clusterer = LogClusterer()
        clusters = clusterer.cluster(sample_log_entries)

        assert clusters == []

    def test_extract_common_terms(self):
        """Test extracting common terms."""
        clusterer = LogClusterer()
        messages = [
            "Database query took 100 ms",
            "Database query took 150 ms",
            "Database query took 200 ms",
        ]

        common_terms = clusterer._extract_common_terms(messages)

        assert "database" in common_terms
        assert "query" in common_terms
        assert "took" in common_terms


class TestLogAnalyzer:
    """Test suite for LogAnalyzer class."""

    def test_init(self):
        """Test initialization."""
        analyzer = LogAnalyzer()
        assert isinstance(analyzer.anomaly_detector, AnomalyDetector)
        assert isinstance(analyzer.pattern_recognizer, PatternRecognizer)
        assert isinstance(analyzer.log_clusterer, LogClusterer)

    def test_train_anomaly_detector(self, sample_log_entries):
        """Test training anomaly detector."""
        analyzer = LogAnalyzer()
        analyzer.train_anomaly_detector(sample_log_entries)

        assert analyzer.anomaly_detector.trained is True

    def test_detect_anomalies(self, sample_log_entries):
        """Test detecting anomalies."""
        analyzer = LogAnalyzer()
        analyzer.train_anomaly_detector(sample_log_entries)

        anomalies = analyzer.detect_anomalies(sample_log_entries)

        assert isinstance(anomalies, list)

    def test_train_pattern_recognizer(self, sample_log_entries):
        """Test training pattern recognizer."""
        analyzer = LogAnalyzer()
        analyzer.train_pattern_recognizer(sample_log_entries)

        assert analyzer.pattern_recognizer.trained is True

    def test_recognize_patterns(self, sample_log_entries):
        """Test recognizing patterns."""
        analyzer = LogAnalyzer()
        analyzer.train_pattern_recognizer(sample_log_entries)

        patterns = analyzer.recognize_patterns(sample_log_entries)

        assert isinstance(patterns, list)

    def test_train_log_clusterer(self, sample_log_entries):
        """Test training log clusterer."""
        analyzer = LogAnalyzer()
        analyzer.train_log_clusterer(sample_log_entries)

        assert analyzer.log_clusterer.trained is True

    def test_cluster_logs(self, sample_log_entries):
        """Test clustering logs."""
        analyzer = LogAnalyzer()
        analyzer.train_log_clusterer(sample_log_entries)

        clusters = analyzer.cluster_logs(sample_log_entries)

        assert isinstance(clusters, list)

    def test_analyze_logs(self, sample_log_entries):
        """Test analyzing logs."""
        analyzer = LogAnalyzer()

        results = analyzer.analyze_logs(sample_log_entries)

        assert "anomalies" in results
        assert "patterns" in results
        assert "clusters" in results
        assert isinstance(results["anomalies"], list)
        assert isinstance(results["patterns"], list)
        assert isinstance(results["clusters"], list)


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    def test_train_anomaly_detector(self, sample_log_entries):
        """Test train_anomaly_detector function."""
        detector = train_anomaly_detector(sample_log_entries)

        assert isinstance(detector, AnomalyDetector)
        assert detector.trained is True

    def test_detect_anomalies(self, sample_log_entries):
        """Test detect_anomalies function."""
        anomalies = detect_anomalies(sample_log_entries)

        assert isinstance(anomalies, list)

    def test_recognize_patterns(self, sample_log_entries):
        """Test recognize_patterns function."""
        patterns = recognize_patterns(sample_log_entries)

        assert isinstance(patterns, list)

    def test_cluster_logs(self, sample_log_entries):
        """Test cluster_logs function."""
        clusters = cluster_logs(sample_log_entries)

        assert isinstance(clusters, list)
