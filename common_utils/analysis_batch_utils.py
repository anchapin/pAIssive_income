"""
Data analysis batch processing utilities.

This module provides utilities for performing batch processing on data analysis tasks,
such as feature extraction, data transformation, and model evaluation.
"""

import logging
import time
from typing import (
    List,
    Dict,
    Any,
    Tuple,
    Optional,
    Union,
    Callable,
    TypeVar,
    Generic,
    Iterable,
)
from dataclasses import dataclass, field
import concurrent.futures
from datetime import datetime
import uuid
import numpy as np
from functools import partial

from .batch_utils import (
    BatchProcessingStats,
    BatchResult,
    BatchProcessor,
    process_batch,
)

# Type variables for generic functions
T = TypeVar("T")  # Input item type
R = TypeVar("R")  # Result item type

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class AnalysisBatchConfig:
    """Configuration for data analysis batch processing."""

    batch_size: int = 100
    max_workers: int = None
    timeout: float = None
    retry_count: int = 0
    include_input_in_result: bool = False


class AnalysisBatchProcessor(Generic[T, R]):
    """
    Specialized batch processor for data analysis tasks.
    """

    def __init__(
        self, processor_func: Callable[[T], R], config: AnalysisBatchConfig = None
    ):
        """
        Initialize the analysis batch processor.

        Args:
            processor_func: Function to process each item
            config: Configuration for batch processing
        """
        self.processor_func = processor_func
        self.config = config or AnalysisBatchConfig()
        self.batch_processor = BatchProcessor(
            processor_func=processor_func,
            batch_size=self.config.batch_size,
            max_workers=self.config.max_workers,
            timeout=self.config.timeout,
        )

    def process_dataset(
        self, items: List[T], batch_size: int = None
    ) -> BatchResult[T, R]:
        """
        Process a dataset in batches.

        Args:
            items: Dataset items to process
            batch_size: Override the default batch size

        Returns:
            BatchResult with processing results
        """
        effective_batch_size = batch_size or self.config.batch_size

        # Process the items
        result = self.batch_processor.process(items, batch_size=effective_batch_size)

        return result

    def extract_features(
        self,
        items: List[T],
        feature_extractors: Dict[str, Callable[[T], Any]],
        batch_size: int = None,
    ) -> Dict[str, List[Any]]:
        """
        Extract multiple features from a dataset in batches.

        Args:
            items: Dataset items to process
            feature_extractors: Dictionary of feature name to extractor function
            batch_size: Override the default batch size

        Returns:
            Dictionary of feature name to list of extracted values
        """
        effective_batch_size = batch_size or self.config.batch_size
        features = {name: [] for name in feature_extractors}

        # Process each feature extractor
        for name, extractor in feature_extractors.items():
            processor = BatchProcessor(
                processor_func=extractor,
                batch_size=effective_batch_size,
                max_workers=self.config.max_workers,
                timeout=self.config.timeout,
            )

            result = processor.process(items)
            features[name] = result.results

        return features

    def train_test_split(
        self,
        items: List[T],
        labels: List[Any] = None,
        test_size: float = 0.2,
        random_state: int = None,
    ) -> Tuple[List[T], List[T], List[Any], List[Any]]:
        """
        Split a dataset into training and testing sets.

        Args:
            items: Dataset items
            labels: Optional labels
            test_size: Proportion of the dataset to include in the test split
            random_state: Seed for random number generator

        Returns:
            Tuple of (train_items, test_items, train_labels, test_labels)
        """
        if random_state is not None:
            np.random.seed(random_state)

        # Create indices and shuffle them
        indices = np.arange(len(items))
        np.random.shuffle(indices)

        # Calculate split point
        split_idx = int(len(items) * (1 - test_size))

        # Split indices
        train_indices = indices[:split_idx]
        test_indices = indices[split_idx:]

        # Split items
        train_items = [items[i] for i in train_indices]
        test_items = [items[i] for i in test_indices]

        # Split labels if provided
        train_labels = None
        test_labels = None

        if labels is not None:
            train_labels = [labels[i] for i in train_indices]
            test_labels = [labels[i] for i in test_indices]

        return train_items, test_items, train_labels, test_labels

    def cross_validation(
        self,
        items: List[T],
        labels: List[Any],
        model_func: Callable[[List[T], List[Any]], Any],
        eval_func: Callable[[Any, List[T], List[Any]], float],
        n_splits: int = 5,
        random_state: int = None,
    ) -> Dict[str, Any]:
        """
        Perform cross-validation on a dataset.

        Args:
            items: Dataset items
            labels: Labels for the items
            model_func: Function that takes (train_items, train_labels) and returns a model
            eval_func: Function that takes (model, test_items, test_labels) and returns a score
            n_splits: Number of cross-validation splits
            random_state: Seed for random number generator

        Returns:
            Dictionary with cross-validation results
        """
        if random_state is not None:
            np.random.seed(random_state)

        # Create indices
        indices = np.arange(len(items))
        np.random.shuffle(indices)

        # Calculate fold size
        fold_size = len(items) // n_splits

        # Perform cross-validation
        scores = []
        fold_results = []

        for i in range(n_splits):
            # Create test indices for this fold
            start_idx = i * fold_size
            end_idx = start_idx + fold_size if i < n_splits - 1 else len(items)
            test_indices = indices[start_idx:end_idx]

            # Create train indices (all indices not in test)
            train_indices = np.array(
                [idx for idx in indices if idx not in test_indices]
            )

            # Split data
            train_items = [items[i] for i in train_indices]
            train_labels = [labels[i] for i in train_indices]
            test_items = [items[i] for i in test_indices]
            test_labels = [labels[i] for i in test_indices]

            # Train model
            start_time = time.time()
            model = model_func(train_items, train_labels)
            training_time = time.time() - start_time

            # Evaluate model
            start_time = time.time()
            score = eval_func(model, test_items, test_labels)
            eval_time = time.time() - start_time

            scores.append(score)
            fold_results.append(
                {
                    "fold": i + 1,
                    "score": score,
                    "training_time": training_time,
                    "eval_time": eval_time,
                    "test_size": len(test_items),
                    "train_size": len(train_items),
                }
            )

        # Calculate aggregate statistics
        mean_score = np.mean(scores)
        std_score = np.std(scores)

        return {
            "mean_score": mean_score,
            "std_score": std_score,
            "fold_results": fold_results,
            "n_splits": n_splits,
        }

    def parallel_map(
        self, func: Callable[[T], R], items: List[T], batch_size: int = None
    ) -> List[R]:
        """
        Apply a function to all items in parallel batches.

        Args:
            func: Function to apply to each item
            items: List of items to process
            batch_size: Override the default batch size

        Returns:
            List of results
        """
        effective_batch_size = batch_size or self.config.batch_size

        result = process_batch(
            items=items,
            processor_func=func,
            max_workers=self.config.max_workers,
            timeout=self.config.timeout,
        )

        return result.results


# Convenience functions for data analysis batch processing
def batch_extract_features(
    items: List[T],
    feature_extractors: Dict[str, Callable[[T], Any]],
    batch_size: int = 100,
    max_workers: int = None,
) -> Dict[str, List[Any]]:
    """
    Extract multiple features from a dataset in batches.

    Args:
        items: Dataset items to process
        feature_extractors: Dictionary of feature name to extractor function
        batch_size: Size of each batch
        max_workers: Maximum number of workers for parallel processing

    Returns:
        Dictionary of feature name to list of extracted values
    """
    config = AnalysisBatchConfig(batch_size=batch_size, max_workers=max_workers)
    processor = AnalysisBatchProcessor(lambda x: x, config=config)
    return processor.extract_features(items, feature_extractors, batch_size)


def batch_transform(
    transform_func: Callable[[T], R],
    items: List[T],
    batch_size: int = 100,
    max_workers: int = None,
) -> List[R]:
    """
    Transform a dataset in batches.

    Args:
        transform_func: Function to transform each item
        items: Dataset items to transform
        batch_size: Size of each batch
        max_workers: Maximum number of workers for parallel processing

    Returns:
        List of transformed items
    """
    config = AnalysisBatchConfig(batch_size=batch_size, max_workers=max_workers)
    processor = AnalysisBatchProcessor(transform_func, config=config)
    return processor.process_dataset(items, batch_size).results
