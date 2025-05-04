"""
"""
Data analysis batch processing utilities.
Data analysis batch processing utilities.


This module provides utilities for performing batch processing on data analysis tasks,
This module provides utilities for performing batch processing on data analysis tasks,
such as feature extraction, data transformation, and model evaluation.
such as feature extraction, data transformation, and model evaluation.
"""
"""




import logging
import logging
import time
import time
from dataclasses import dataclass
from dataclasses import dataclass


import numpy
import numpy


(
(
Any,
Any,
Callable,
Callable,
Dict,
Dict,
Generic,
Generic,
List,
List,
Tuple,
Tuple,
TypeVar,
TypeVar,
)
)
as np
as np


from .batch_utils import BatchProcessor, BatchResult, process_batch
from .batch_utils import BatchProcessor, BatchResult, process_batch


# Type variables for generic functions
# Type variables for generic functions
T = TypeVar("T")  # Input item type
T = TypeVar("T")  # Input item type
R = TypeVar("R")  # Result item type
R = TypeVar("R")  # Result item type


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




@dataclass
@dataclass
class AnalysisBatchConfig:
    class AnalysisBatchConfig:
    """Configuration for data analysis batch processing."""

    batch_size: int = 100
    max_workers: int = None
    timeout: float = None
    retry_count: int = 0
    include_input_in_result: bool = False


    class AnalysisBatchProcessor(Generic[T, R]):
    """
    """
    Specialized batch processor for data analysis tasks.
    Specialized batch processor for data analysis tasks.
    """
    """


    def __init__(
    def __init__(
    self, processor_func: Callable[[T], R], config: AnalysisBatchConfig = None
    self, processor_func: Callable[[T], R], config: AnalysisBatchConfig = None
    ):
    ):
    """
    """
    Initialize the analysis batch processor.
    Initialize the analysis batch processor.


    Args:
    Args:
    processor_func: Function to process each item
    processor_func: Function to process each item
    config: Configuration for batch processing
    config: Configuration for batch processing
    """
    """
    self.processor_func = processor_func
    self.processor_func = processor_func
    self.config = config or AnalysisBatchConfig()
    self.config = config or AnalysisBatchConfig()
    self.batch_processor = BatchProcessor(
    self.batch_processor = BatchProcessor(
    processor_func=processor_func,
    processor_func=processor_func,
    batch_size=self.config.batch_size,
    batch_size=self.config.batch_size,
    max_workers=self.config.max_workers,
    max_workers=self.config.max_workers,
    timeout=self.config.timeout,
    timeout=self.config.timeout,
    )
    )


    def process_dataset(
    def process_dataset(
    self, items: List[T], batch_size: int = None
    self, items: List[T], batch_size: int = None
    ) -> BatchResult[T, R]:
    ) -> BatchResult[T, R]:
    """
    """
    Process a dataset in batches.
    Process a dataset in batches.


    Args:
    Args:
    items: Dataset items to process
    items: Dataset items to process
    batch_size: Override the default batch size
    batch_size: Override the default batch size


    Returns:
    Returns:
    BatchResult with processing results
    BatchResult with processing results
    """
    """
    effective_batch_size = batch_size or self.config.batch_size
    effective_batch_size = batch_size or self.config.batch_size


    # Process the items
    # Process the items
    result = self.batch_processor.process(items, batch_size=effective_batch_size)
    result = self.batch_processor.process(items, batch_size=effective_batch_size)


    return result
    return result


    def extract_features(
    def extract_features(
    self,
    self,
    items: List[T],
    items: List[T],
    feature_extractors: Dict[str, Callable[[T], Any]],
    feature_extractors: Dict[str, Callable[[T], Any]],
    batch_size: int = None,
    batch_size: int = None,
    ) -> Dict[str, List[Any]]:
    ) -> Dict[str, List[Any]]:
    """
    """
    Extract multiple features from a dataset in batches.
    Extract multiple features from a dataset in batches.


    Args:
    Args:
    items: Dataset items to process
    items: Dataset items to process
    feature_extractors: Dictionary of feature name to extractor function
    feature_extractors: Dictionary of feature name to extractor function
    batch_size: Override the default batch size
    batch_size: Override the default batch size


    Returns:
    Returns:
    Dictionary of feature name to list of extracted values
    Dictionary of feature name to list of extracted values
    """
    """
    effective_batch_size = batch_size or self.config.batch_size
    effective_batch_size = batch_size or self.config.batch_size
    features = {name: [] for name in feature_extractors}
    features = {name: [] for name in feature_extractors}


    # Process each feature extractor
    # Process each feature extractor
    for name, extractor in feature_extractors.items():
    for name, extractor in feature_extractors.items():
    processor = BatchProcessor(
    processor = BatchProcessor(
    processor_func=extractor,
    processor_func=extractor,
    batch_size=effective_batch_size,
    batch_size=effective_batch_size,
    max_workers=self.config.max_workers,
    max_workers=self.config.max_workers,
    timeout=self.config.timeout,
    timeout=self.config.timeout,
    )
    )


    result = processor.process(items)
    result = processor.process(items)
    features[name] = result.results
    features[name] = result.results


    return features
    return features


    def train_test_split(
    def train_test_split(
    self,
    self,
    items: List[T],
    items: List[T],
    labels: List[Any] = None,
    labels: List[Any] = None,
    test_size: float = 0.2,
    test_size: float = 0.2,
    random_state: int = None,
    random_state: int = None,
    ) -> Tuple[List[T], List[T], List[Any], List[Any]]:
    ) -> Tuple[List[T], List[T], List[Any], List[Any]]:
    """
    """
    Split a dataset into training and testing sets.
    Split a dataset into training and testing sets.


    Args:
    Args:
    items: Dataset items
    items: Dataset items
    labels: Optional labels
    labels: Optional labels
    test_size: Proportion of the dataset to include in the test split
    test_size: Proportion of the dataset to include in the test split
    random_state: Seed for random number generator
    random_state: Seed for random number generator


    Returns:
    Returns:
    Tuple of (train_items, test_items, train_labels, test_labels)
    Tuple of (train_items, test_items, train_labels, test_labels)
    """
    """
    if random_state is not None:
    if random_state is not None:
    np.random.seed(random_state)
    np.random.seed(random_state)


    # Create indices and shuffle them
    # Create indices and shuffle them
    indices = np.arange(len(items))
    indices = np.arange(len(items))
    np.random.shuffle(indices)
    np.random.shuffle(indices)


    # Calculate split point
    # Calculate split point
    split_idx = int(len(items) * (1 - test_size))
    split_idx = int(len(items) * (1 - test_size))


    # Split indices
    # Split indices
    train_indices = indices[:split_idx]
    train_indices = indices[:split_idx]
    test_indices = indices[split_idx:]
    test_indices = indices[split_idx:]


    # Split items
    # Split items
    train_items = [items[i] for i in train_indices]
    train_items = [items[i] for i in train_indices]
    test_items = [items[i] for i in test_indices]
    test_items = [items[i] for i in test_indices]


    # Split labels if provided
    # Split labels if provided
    train_labels = None
    train_labels = None
    test_labels = None
    test_labels = None


    if labels is not None:
    if labels is not None:
    train_labels = [labels[i] for i in train_indices]
    train_labels = [labels[i] for i in train_indices]
    test_labels = [labels[i] for i in test_indices]
    test_labels = [labels[i] for i in test_indices]


    return train_items, test_items, train_labels, test_labels
    return train_items, test_items, train_labels, test_labels


    def cross_validation(
    def cross_validation(
    self,
    self,
    items: List[T],
    items: List[T],
    labels: List[Any],
    labels: List[Any],
    model_func: Callable[[List[T], List[Any]], Any],
    model_func: Callable[[List[T], List[Any]], Any],
    eval_func: Callable[[Any, List[T], List[Any]], float],
    eval_func: Callable[[Any, List[T], List[Any]], float],
    n_splits: int = 5,
    n_splits: int = 5,
    random_state: int = None,
    random_state: int = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Perform cross-validation on a dataset.
    Perform cross-validation on a dataset.


    Args:
    Args:
    items: Dataset items
    items: Dataset items
    labels: Labels for the items
    labels: Labels for the items
    model_func: Function that takes (train_items, train_labels) and returns a model
    model_func: Function that takes (train_items, train_labels) and returns a model
    eval_func: Function that takes (model, test_items, test_labels) and returns a score
    eval_func: Function that takes (model, test_items, test_labels) and returns a score
    n_splits: Number of cross-validation splits
    n_splits: Number of cross-validation splits
    random_state: Seed for random number generator
    random_state: Seed for random number generator


    Returns:
    Returns:
    Dictionary with cross-validation results
    Dictionary with cross-validation results
    """
    """
    if random_state is not None:
    if random_state is not None:
    np.random.seed(random_state)
    np.random.seed(random_state)


    # Create indices
    # Create indices
    indices = np.arange(len(items))
    indices = np.arange(len(items))
    np.random.shuffle(indices)
    np.random.shuffle(indices)


    # Calculate fold size
    # Calculate fold size
    fold_size = len(items) // n_splits
    fold_size = len(items) // n_splits


    # Perform cross-validation
    # Perform cross-validation
    scores = []
    scores = []
    fold_results = []
    fold_results = []


    for i in range(n_splits):
    for i in range(n_splits):
    # Create test indices for this fold
    # Create test indices for this fold
    start_idx = i * fold_size
    start_idx = i * fold_size
    end_idx = start_idx + fold_size if i < n_splits - 1 else len(items)
    end_idx = start_idx + fold_size if i < n_splits - 1 else len(items)
    test_indices = indices[start_idx:end_idx]
    test_indices = indices[start_idx:end_idx]


    # Create train indices (all indices not in test)
    # Create train indices (all indices not in test)
    train_indices = np.array(
    train_indices = np.array(
    [idx for idx in indices if idx not in test_indices]
    [idx for idx in indices if idx not in test_indices]
    )
    )


    # Split data
    # Split data
    train_items = [items[i] for i in train_indices]
    train_items = [items[i] for i in train_indices]
    train_labels = [labels[i] for i in train_indices]
    train_labels = [labels[i] for i in train_indices]
    test_items = [items[i] for i in test_indices]
    test_items = [items[i] for i in test_indices]
    test_labels = [labels[i] for i in test_indices]
    test_labels = [labels[i] for i in test_indices]


    # Train model
    # Train model
    start_time = time.time()
    start_time = time.time()
    model = model_func(train_items, train_labels)
    model = model_func(train_items, train_labels)
    training_time = time.time() - start_time
    training_time = time.time() - start_time


    # Evaluate model
    # Evaluate model
    start_time = time.time()
    start_time = time.time()
    score = eval_func(model, test_items, test_labels)
    score = eval_func(model, test_items, test_labels)
    eval_time = time.time() - start_time
    eval_time = time.time() - start_time


    scores.append(score)
    scores.append(score)
    fold_results.append(
    fold_results.append(
    {
    {
    "fold": i + 1,
    "fold": i + 1,
    "score": score,
    "score": score,
    "training_time": training_time,
    "training_time": training_time,
    "eval_time": eval_time,
    "eval_time": eval_time,
    "test_size": len(test_items),
    "test_size": len(test_items),
    "train_size": len(train_items),
    "train_size": len(train_items),
    }
    }
    )
    )


    # Calculate aggregate statistics
    # Calculate aggregate statistics
    mean_score = np.mean(scores)
    mean_score = np.mean(scores)
    std_score = np.std(scores)
    std_score = np.std(scores)


    return {
    return {
    "mean_score": mean_score,
    "mean_score": mean_score,
    "std_score": std_score,
    "std_score": std_score,
    "fold_results": fold_results,
    "fold_results": fold_results,
    "n_splits": n_splits,
    "n_splits": n_splits,
    }
    }


    def parallel_map(
    def parallel_map(
    self, func: Callable[[T], R], items: List[T], batch_size: int = None
    self, func: Callable[[T], R], items: List[T], batch_size: int = None
    ) -> List[R]:
    ) -> List[R]:
    """
    """
    Apply a function to all items in parallel batches.
    Apply a function to all items in parallel batches.


    Args:
    Args:
    func: Function to apply to each item
    func: Function to apply to each item
    items: List of items to process
    items: List of items to process
    batch_size: Override the default batch size
    batch_size: Override the default batch size


    Returns:
    Returns:
    List of results
    List of results
    """
    """


    result = process_batch(
    result = process_batch(
    items=items,
    items=items,
    processor_func=func,
    processor_func=func,
    max_workers=self.config.max_workers,
    max_workers=self.config.max_workers,
    timeout=self.config.timeout,
    timeout=self.config.timeout,
    )
    )


    return result.results
    return result.results




    # Convenience functions for data analysis batch processing
    # Convenience functions for data analysis batch processing
    def batch_extract_features(
    def batch_extract_features(
    items: List[T],
    items: List[T],
    feature_extractors: Dict[str, Callable[[T], Any]],
    feature_extractors: Dict[str, Callable[[T], Any]],
    batch_size: int = 100,
    batch_size: int = 100,
    max_workers: int = None,
    max_workers: int = None,
    ) -> Dict[str, List[Any]]:
    ) -> Dict[str, List[Any]]:
    """
    """
    Extract multiple features from a dataset in batches.
    Extract multiple features from a dataset in batches.


    Args:
    Args:
    items: Dataset items to process
    items: Dataset items to process
    feature_extractors: Dictionary of feature name to extractor function
    feature_extractors: Dictionary of feature name to extractor function
    batch_size: Size of each batch
    batch_size: Size of each batch
    max_workers: Maximum number of workers for parallel processing
    max_workers: Maximum number of workers for parallel processing


    Returns:
    Returns:
    Dictionary of feature name to list of extracted values
    Dictionary of feature name to list of extracted values
    """
    """
    config = AnalysisBatchConfig(batch_size=batch_size, max_workers=max_workers)
    config = AnalysisBatchConfig(batch_size=batch_size, max_workers=max_workers)
    processor = AnalysisBatchProcessor(lambda x: x, config=config)
    processor = AnalysisBatchProcessor(lambda x: x, config=config)
    return processor.extract_features(items, feature_extractors, batch_size)
    return processor.extract_features(items, feature_extractors, batch_size)




    def batch_transform(
    def batch_transform(
    transform_func: Callable[[T], R],
    transform_func: Callable[[T], R],
    items: List[T],
    items: List[T],
    batch_size: int = 100,
    batch_size: int = 100,
    max_workers: int = None,
    max_workers: int = None,
    ) -> List[R]:
    ) -> List[R]:
    """
    """
    Transform a dataset in batches.
    Transform a dataset in batches.


    Args:
    Args:
    transform_func: Function to transform each item
    transform_func: Function to transform each item
    items: Dataset items to transform
    items: Dataset items to transform
    batch_size: Size of each batch
    batch_size: Size of each batch
    max_workers: Maximum number of workers for parallel processing
    max_workers: Maximum number of workers for parallel processing


    Returns:
    Returns:
    List of transformed items
    List of transformed items
    """
    """
    config = AnalysisBatchConfig(batch_size=batch_size, max_workers=max_workers)
    config = AnalysisBatchConfig(batch_size=batch_size, max_workers=max_workers)
    processor = AnalysisBatchProcessor(transform_func, config=config)
    processor = AnalysisBatchProcessor(transform_func, config=config)
    return processor.process_dataset(items, batch_size).results
    return processor.process_dataset(items, batch_size).results