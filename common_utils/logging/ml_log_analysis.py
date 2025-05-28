"""
Machine learning module for log analysis.

This module provides functionality for analyzing logs using machine learning
techniques, including anomaly detection, pattern recognition, and clustering.

Usage:
    from common_utils.logging.ml_log_analysis import (
        LogAnalyzer,
        AnomalyDetector,
        PatternRecognizer,
        LogClusterer,
        train_anomaly_detector,
        detect_anomalies,
        recognize_patterns,
        cluster_logs,
    )

    # Create a log analyzer
    analyzer = LogAnalyzer()

    # Train an anomaly detector
    analyzer.train_anomaly_detector(log_entries)

    # Detect anomalies
    anomalies = analyzer.detect_anomalies(log_entries)

    # Recognize patterns
    patterns = analyzer.recognize_patterns(log_entries)

    # Cluster logs
    clusters = analyzer.cluster_logs(log_entries)
"""

import datetime
import logging
import re
import sys  # Added sys import
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


# Configure logger for this module

try:
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.ensemble import IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
except ImportError as e:
    logger.error(f"Failed to import scikit-learn or numpy: {e}")
    sys.exit(1)

try:
    from common_utils.logging.secure_logging import get_secure_logger
except ImportError:
    logger.error("Error: common_utils.logging.secure_logging module not found.")
    sys.exit(1)


# Use the existing logger from line 42


class AnomalyDetector:
    """Anomaly detector for log entries."""

    def __init__(self, contamination: float = 0.05) -> None:
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies in the data

        """
        self.contamination = contamination
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.trained = False

    def extract_features(self, log_entries: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract features from log entries.
        
        Args:
            log_entries: List of log entries
            
        Returns:
            numpy.ndarray: Feature matrix

        """
        if not log_entries:
            return np.array([])

        # Extract basic features
        features = []
        for entry in log_entries:
            # Extract timestamp features
            timestamp = entry.get("timestamp", datetime.datetime.now())
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    timestamp = datetime.datetime.now()

            # Create feature vector
            feature_vector = [
                timestamp.hour,
                timestamp.minute,
                timestamp.second,
                timestamp.weekday(),
                len(entry.get("message", "")),
                1 if entry.get("level") == "ERROR" else 0,
                1 if entry.get("level") == "WARNING" else 0,
                1 if entry.get("level") == "CRITICAL" else 0,
            ]

            # Add custom features
            message = entry.get("message", "")
            feature_vector.extend([
                1 if "error" in message.lower() else 0,
                1 if "exception" in message.lower() else 0,
                1 if "fail" in message.lower() else 0,
                1 if "timeout" in message.lower() else 0,
                message.count("\n"),  # Number of newlines (e.g., for stack traces)
            ])

            features.append(feature_vector)

        # Set feature names
        self.feature_names = [
            "hour", "minute", "second", "weekday", "message_length",
            "is_error", "is_warning", "is_critical",
            "has_error_text", "has_exception_text", "has_fail_text", "has_timeout_text",
            "newline_count",
        ]

        return np.array(features)

    def train(self, log_entries: List[Dict[str, Any]]) -> None:
        """
        Train the anomaly detector.
        
        Args:
            log_entries: List of log entries for training

        """
        if not log_entries:
            logger.warning("No log entries provided for training")
            return

        # Extract features
        features = self.extract_features(log_entries)
        if len(features) == 0:
            logger.warning("No features extracted from log entries")
            return

        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        # Train isolation forest model
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
        )
        self.model.fit(scaled_features)

        self.trained = True
        logger.info(f"Trained anomaly detector on {len(log_entries)} log entries")

    def detect(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in log entries.
        
        Args:
            log_entries: List of log entries to analyze
            
        Returns:
            List of anomalous log entries with anomaly scores

        """
        if not self.trained:
            logger.warning("Anomaly detector not trained")
            return []

        if not log_entries:
            return []

        # Extract features
        features = self.extract_features(log_entries)
        if len(features) == 0:
            return []

        # Scale features
        scaled_features = self.scaler.transform(features)

        # Predict anomalies
        # -1 for anomalies, 1 for normal points
        predictions = self.model.predict(scaled_features)

        # Get anomaly scores
        scores = self.model.decision_function(scaled_features)

        # Find anomalies
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                anomaly = log_entries[i].copy()
                anomaly["anomaly_score"] = float(score)
                anomaly["feature_values"] = {
                    name: float(features[i, j])
                    for j, name in enumerate(self.feature_names)
                }
                anomalies.append(anomaly)

        return anomalies


class PatternRecognizer:
    """Pattern recognizer for log entries."""

    def __init__(self, min_pattern_count: int = 3) -> None:
        """
        Initialize the pattern recognizer.
        
        Args:
            min_pattern_count: Minimum number of occurrences for a pattern

        """
        self.min_pattern_count = min_pattern_count
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 3),
        )
        self.trained = False

    def train(self, log_entries: List[Dict[str, Any]]) -> None:
        """
        Train the pattern recognizer.
        
        Args:
            log_entries: List of log entries for training

        """
        if not log_entries:
            logger.warning("No log entries provided for training")
            return

        # Extract messages
        messages = [entry.get("message", "") for entry in log_entries]

        # Fit vectorizer
        self.vectorizer.fit(messages)

        self.trained = True
        logger.info(f"Trained pattern recognizer on {len(log_entries)} log entries")

    def recognize(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recognize patterns in log entries.
        
        Args:
            log_entries: List of log entries to analyze
            
        Returns:
            List of recognized patterns with counts and examples

        """
        if not self.trained:
            logger.warning("Pattern recognizer not trained")
            return []

        if not log_entries:
            return []

        # Extract messages
        messages = [entry.get("message", "") for entry in log_entries]

        # Transform messages to TF-IDF vectors
        tfidf_matrix = self.vectorizer.transform(messages)

        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()

        # Find common patterns
        patterns = []
        for i, feature in enumerate(feature_names):
            # Get entries with this feature
            feature_indices = tfidf_matrix[:, i].nonzero()[0]

            if len(feature_indices) >= self.min_pattern_count:
                # Get examples
                examples = [log_entries[idx] for idx in feature_indices[:5]]

                # Add pattern
                patterns.append({
                    "pattern": feature,
                    "count": len(feature_indices),
                    "examples": examples,
                })

        # Sort patterns by count (descending)
        patterns.sort(key=lambda x: x["count"], reverse=True)

        return patterns


class LogClusterer:
    """Clusterer for log entries."""

    def __init__(self, eps: float = 0.5, min_samples: int = 5) -> None:
        """
        Initialize the log clusterer.
        
        Args:
            eps: Maximum distance between samples in a cluster
            min_samples: Minimum number of samples in a cluster

        """
        self.eps = eps
        self.min_samples = min_samples
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
        )
        self.model = DBSCAN(eps=eps, min_samples=min_samples)
        self.trained = False

    def train(self, log_entries: List[Dict[str, Any]]) -> None:
        """
        Train the log clusterer.
        
        Args:
            log_entries: List of log entries for training

        """
        if not log_entries:
            logger.warning("No log entries provided for training")
            return

        # Extract messages
        messages = [entry.get("message", "") for entry in log_entries]

        # Fit vectorizer and transform messages
        tfidf_matrix = self.vectorizer.fit_transform(messages)

        # Fit DBSCAN model
        self.model.fit(tfidf_matrix)

        self.trained = True
        logger.info(f"Trained log clusterer on {len(log_entries)} log entries")

    def cluster(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cluster log entries.
        
        Args:
            log_entries: List of log entries to cluster
            
        Returns:
            List of clusters with entries and common terms

        """
        if not self.trained:
            logger.warning("Log clusterer not trained")
            return []

        if not log_entries:
            return []

        # Extract messages
        messages = [entry.get("message", "") for entry in log_entries]

        # Transform messages to TF-IDF vectors
        tfidf_matrix = self.vectorizer.transform(messages)

        # Predict clusters
        labels = self.model.fit_predict(tfidf_matrix)

        # Group entries by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(labels):
            if label != -1:  # -1 is noise
                clusters[label].append(log_entries[i])

        # Extract common terms for each cluster
        result = []
        for label, entries in clusters.items():
            # Get cluster messages
            cluster_messages = [entry.get("message", "") for entry in entries]

            # Get common terms
            common_terms = self._extract_common_terms(cluster_messages)

            result.append({
                "cluster_id": int(label),
                "size": len(entries),
                "common_terms": common_terms,
                "entries": entries[:5],  # Limit to 5 examples
            })

        # Sort clusters by size (descending)
        result.sort(key=lambda x: x["size"], reverse=True)

        return result

    def _extract_common_terms(self, messages: List[str]) -> List[str]:
        """
        Extract common terms from a list of messages.
        
        Args:
            messages: List of messages
            
        Returns:
            List of common terms

        """
        # Tokenize messages
        tokens = []
        for message in messages:
            tokens.extend(re.findall(r"\b\w+\b", message.lower()))

        # Count tokens
        token_counts = Counter(tokens)

        # Get common terms (appear in at least 50% of messages)
        threshold = len(messages) * 0.5
        common_terms = [
            term for term, count in token_counts.most_common(10)
            if count >= threshold and len(term) > 2
        ]

        return common_terms


class LogAnalyzer:
    """Machine learning-based log analyzer."""

    def __init__(self) -> None:
        """Initialize the log analyzer."""
        self.anomaly_detector = AnomalyDetector()
        self.pattern_recognizer = PatternRecognizer()
        self.log_clusterer = LogClusterer()

    def train_anomaly_detector(self, log_entries: List[Dict[str, Any]]) -> None:
        """
        Train the anomaly detector.
        
        Args:
            log_entries: List of log entries for training

        """
        self.anomaly_detector.train(log_entries)

    def detect_anomalies(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in log entries.
        
        Args:
            log_entries: List of log entries to analyze
            
        Returns:
            List of anomalous log entries with anomaly scores

        """
        return self.anomaly_detector.detect(log_entries)

    def train_pattern_recognizer(self, log_entries: List[Dict[str, Any]]) -> None:
        """
        Train the pattern recognizer.
        
        Args:
            log_entries: List of log entries for training

        """
        self.pattern_recognizer.train(log_entries)

    def recognize_patterns(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recognize patterns in log entries.
        
        Args:
            log_entries: List of log entries to analyze
            
        Returns:
            List of recognized patterns with counts and examples

        """
        return self.pattern_recognizer.recognize(log_entries)

    def train_log_clusterer(self, log_entries: List[Dict[str, Any]]) -> None:
        """
        Train the log clusterer.
        
        Args:
            log_entries: List of log entries for training

        """
        self.log_clusterer.train(log_entries)

    def cluster_logs(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cluster log entries.
        
        Args:
            log_entries: List of log entries to cluster
            
        Returns:
            List of clusters with entries and common terms

        """
        return self.log_clusterer.cluster(log_entries)

    def analyze_logs(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of log entries.
        
        Args:
            log_entries: List of log entries to analyze
            
        Returns:
            Dictionary containing analysis results

        """
        # Train models if needed
        if not self.anomaly_detector.trained:
            self.train_anomaly_detector(log_entries)

        if not self.pattern_recognizer.trained:
            self.train_pattern_recognizer(log_entries)

        if not self.log_clusterer.trained:
            self.train_log_clusterer(log_entries)

        # Perform analysis
        anomalies = self.detect_anomalies(log_entries)
        patterns = self.recognize_patterns(log_entries)
        clusters = self.cluster_logs(log_entries)

        return {
            "anomalies": anomalies,
            "patterns": patterns,
            "clusters": clusters,
        }


# Convenience functions
def train_anomaly_detector(log_entries: List[Dict[str, Any]]) -> AnomalyDetector:
    """
    Train an anomaly detector on log entries.
    
    Args:
        log_entries: List of log entries for training
        
    Returns:
        Trained anomaly detector

    """
    detector = AnomalyDetector()
    detector.train(log_entries)
    return detector

def detect_anomalies(log_entries: List[Dict[str, Any]], detector: Optional[AnomalyDetector] = None) -> List[Dict[str, Any]]:
    """
    Detect anomalies in log entries.
    
    Args:
        log_entries: List of log entries to analyze
        detector: Optional pre-trained detector (will train a new one if not provided)
        
    Returns:
        List of anomalous log entries with anomaly scores

    """
    if detector is None:
        detector = train_anomaly_detector(log_entries)
    return detector.detect(log_entries)

def recognize_patterns(log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recognize patterns in log entries.
    
    Args:
        log_entries: List of log entries to analyze
        
    Returns:
        List of recognized patterns with counts and examples

    """
    recognizer = PatternRecognizer()
    recognizer.train(log_entries)
    return recognizer.recognize(log_entries)

def cluster_logs(log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cluster log entries.
    
    Args:
        log_entries: List of log entries to cluster
        
    Returns:
        List of clusters with entries and common terms

    """
    clusterer = LogClusterer()
    clusterer.train(log_entries)
    return clusterer.cluster(log_entries)
