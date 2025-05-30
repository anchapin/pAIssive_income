# import pandas as pd  # Ensure pandas is imported for sklearn type checks
import sys

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
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


# Configure logger for this module

try:
    import numpy as np
    # from sentence_transformers import SentenceTransformer
except ImportError as e:
    logger.error(f"Failed to import required ML packages: {e}")
    sys.exit(1)

try:
    from common_utils.logging.secure_logging import get_secure_logger

# Configure logging


# Configure logging


# Configure logging


# Configure logging



# Configure logging
except ImportError:

    logger.error("Error: common_utils.logging.secure_logging module not found.")
    sys.exit(1)


# Use the existing logger from line 42


class AnomalyDetector:
    """Anomaly detector for log entries using z-score."""

    def __init__(self, threshold: float = 3.0) -> None:
        """
        Initialize the anomaly detector.

        Args:
            threshold: Z-score threshold for anomaly detection

        """
        self.threshold = threshold
        self.trained = False
        self.feature_names = []
        self.mean = None
        self.std = None

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
        if not log_entries:
            logger.warning("No log entries provided for training")
            return
        features = self.extract_features(log_entries)
        if len(features) == 0:
            logger.warning("No features extracted from log entries")
            return
        self.mean = np.mean(features, axis=0)
        self.std = np.std(features, axis=0)
        self.std[self.std == 0] = 1
        self.trained = True
        logger.info(f"Trained anomaly detector on {len(log_entries)} log entries")

    def detect(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.trained:
            logger.warning("Anomaly detector not trained")
            return []
        if not log_entries:
            return []
        features = self.extract_features(log_entries)
        if len(features) == 0:
            return []
        z_scores = np.abs((features - self.mean) / self.std)
        anomaly_mask = (z_scores > self.threshold).any(axis=1)
        anomalies = []
        for i, is_anomaly in enumerate(anomaly_mask):
            if is_anomaly:
                anomaly = log_entries[i].copy()
                anomaly["anomaly_score"] = float(np.max(z_scores[i]))
                anomaly["feature_values"] = {
                    name: float(features[i, j])
                    for j, name in enumerate(self.feature_names)
                }
                anomalies.append(anomaly)
        return anomalies


class PatternRecognizer:
    """Pattern recognizer for log entries using pure Python TF-IDF."""

    def __init__(self, min_pattern_count: int = 3) -> None:
        self.min_pattern_count = min_pattern_count
        self.trained = False
        self.vocab = None
        self.idf = None
        self.tf_matrix = None

    def train(self, log_entries: List[Dict[str, Any]]) -> None:
        if not log_entries:
            logger.warning("No log entries provided for training")
            return
        messages = [entry.get("message", "") for entry in log_entries]
        # Build vocabulary
        vocab = {}
        doc_freq = {}
        for msg in messages:
            words = set(msg.lower().split())
            for word in words:
                doc_freq[word] = doc_freq.get(word, 0) + 1
        vocab = {word: i for i, word in enumerate(doc_freq)}
        N = len(messages)
        idf = {word: np.log((N + 1) / (df + 1)) + 1 for word, df in doc_freq.items()}
        # Build TF matrix
        tf_matrix = np.zeros((N, len(vocab)))
        for i, msg in enumerate(messages):
            words = msg.lower().split()
            for word in words:
                if word in vocab:
                    tf_matrix[i, vocab[word]] += 1
        self.vocab = vocab
        self.idf = idf
        self.tf_matrix = tf_matrix
        self.trained = True
        logger.info(f"Trained pattern recognizer on {len(log_entries)} log entries")

    def recognize(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.trained:
            logger.warning("Pattern recognizer not trained")
            return []
        if not log_entries:
            return []
        messages = [entry.get("message", "") for entry in log_entries]
        N = len(messages)
        tfidf_matrix = np.zeros((N, len(self.vocab)))
        for i, msg in enumerate(messages):
            words = msg.lower().split()
            for word in words:
                if word in self.vocab:
                    tf = words.count(word)
                    tfidf_matrix[i, self.vocab[word]] = tf * self.idf[word]
        patterns = []
        for word, idx in self.vocab.items():
            feature_indices = np.where(tfidf_matrix[:, idx] > 0)[0]
            if len(feature_indices) >= self.min_pattern_count:
                examples = [log_entries[idx] for idx in feature_indices[:5]]
                patterns.append({
                    "pattern": word,
                    "count": len(feature_indices),
                    "examples": examples,
                })
        patterns.sort(key=lambda x: x["count"], reverse=True)
        return patterns


class LogClusterer:
    """Clusterer for log entries using pure numpy k-means."""

    def __init__(self, n_clusters: int = 3, max_iter: int = 100) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.trained = False
        self.vocab = None
        self.idf = None
        self.tf_matrix = None
        self.centroids = None
        self.labels_ = None

    def train(self, log_entries: List[Dict[str, Any]]) -> None:
        if not log_entries:
            logger.warning("No log entries provided for training")
            return
        messages = [entry.get("message", "") for entry in log_entries]
        # Build vocabulary and TF-IDF as in PatternRecognizer
        vocab = {}
        doc_freq = {}
        for msg in messages:
            words = set(msg.lower().split())
            for word in words:
                doc_freq[word] = doc_freq.get(word, 0) + 1
        vocab = {word: i for i, word in enumerate(doc_freq)}
        N = len(messages)
        idf = {word: np.log((N + 1) / (df + 1)) + 1 for word, df in doc_freq.items()}
        tf_matrix = np.zeros((N, len(vocab)))
        for i, msg in enumerate(messages):
            words = msg.lower().split()
            for word in words:
                if word in vocab:
                    tf_matrix[i, vocab[word]] += 1
        tfidf_matrix = tf_matrix.copy()
        for word, idx in vocab.items():
            tfidf_matrix[:, idx] *= idf[word]
        self.vocab = vocab
        self.idf = idf
        self.tf_matrix = tf_matrix
        # K-means clustering
        centroids = tfidf_matrix[np.random.choice(N, self.n_clusters, replace=False)]
        for _ in range(self.max_iter):
            distances = np.linalg.norm(tfidf_matrix[:, None] - centroids, axis=2)
            labels = np.argmin(distances, axis=1)
            new_centroids = np.array([tfidf_matrix[labels == k].mean(axis=0) if np.any(labels == k) else centroids[k] for k in range(self.n_clusters)])
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids
        self.centroids = centroids
        self.labels_ = labels
        self.trained = True
        logger.info(f"Trained log clusterer on {len(log_entries)} log entries with {self.n_clusters} clusters")

    def cluster(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.trained:
            logger.warning("Log clusterer not trained")
            return []
        if not log_entries:
            return []
        messages = [entry.get("message", "") for entry in log_entries]
        N = len(messages)
        tfidf_matrix = np.zeros((N, len(self.vocab)))
        for i, msg in enumerate(messages):
            words = msg.lower().split()
            for word in words:
                if word in self.vocab:
                    tf = words.count(word)
                    tfidf_matrix[i, self.vocab[word]] = tf * self.idf[word]
        # Assign clusters
        distances = np.linalg.norm(tfidf_matrix[:, None] - self.centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        clusters = defaultdict(list)
        for i, label in enumerate(labels):
            clusters[label].append(log_entries[i])
        result = []
        for label, entries in clusters.items():
            cluster_messages = [entry.get("message", "") for entry in entries]
            common_terms = self._extract_common_terms(cluster_messages)
            result.append({
                "cluster_id": int(label),
                "size": len(entries),
                "common_terms": common_terms,
                "entries": entries[:5],
            })
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
