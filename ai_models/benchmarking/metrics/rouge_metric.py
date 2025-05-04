"""
"""
ROUGE metric for benchmarking AI models.
ROUGE metric for benchmarking AI models.


This module provides a metric for measuring the ROUGE scores of text generation models.
This module provides a metric for measuring the ROUGE scores of text generation models.
"""
"""




from typing import Any, Callable, Dict, List
from typing import Any, Callable, Dict, List


from rouge_score import rouge_scorer
from rouge_score import rouge_scorer


from .base_metric import BaseMetric
from .base_metric import BaseMetric


ROUGE_AVAILABLE
ROUGE_AVAILABLE
import statistics
import statistics


# Try to import optional dependencies
# Try to import optional dependencies
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    ROUGE_AVAILABLE = False
    ROUGE_AVAILABLE = False




    class RougeMetric(BaseMetric):
    class RougeMetric(BaseMetric):
    """
    """
    Metric for measuring ROUGE scores.
    Metric for measuring ROUGE scores.
    """
    """


    def __init__(self, rouge_types: List[str] = None, **kwargs):
    def __init__(self, rouge_types: List[str] = None, **kwargs):
    """
    """
    Initialize the ROUGE metric.
    Initialize the ROUGE metric.


    Args:
    Args:
    rouge_types: List of ROUGE types to compute
    rouge_types: List of ROUGE types to compute
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    super().__init__(name="rouge", unit="", **kwargs)
    super().__init__(name="rouge", unit="", **kwargs)


    if not ROUGE_AVAILABLE:
    if not ROUGE_AVAILABLE:
    raise ImportError("rouge_score is required for ROUGE metrics")
    raise ImportError("rouge_score is required for ROUGE metrics")


    self.rouge_types = rouge_types or ["rouge1", "rouge2", "rougeL"]
    self.rouge_types = rouge_types or ["rouge1", "rouge2", "rougeL"]
    self.scorer = rouge_scorer.RougeScorer(self.rouge_types, use_stemmer=True)
    self.scorer = rouge_scorer.RougeScorer(self.rouge_types, use_stemmer=True)


    # Initialize accumulators
    # Initialize accumulators
    self.scores = {rouge_type: [] for rouge_type in self.rouge_types}
    self.scores = {rouge_type: [] for rouge_type in self.rouge_types}


    def measure(
    def measure(
    self, func: Callable, texts: List[str], references: List[str], *args, **kwargs
    self, func: Callable, texts: List[str], references: List[str], *args, **kwargs
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Measure the ROUGE scores of a model on a dataset.
    Measure the ROUGE scores of a model on a dataset.


    Args:
    Args:
    func: Function that generates text
    func: Function that generates text
    texts: List of input texts
    texts: List of input texts
    references: List of reference texts
    references: List of reference texts
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    Dictionary with ROUGE scores
    Dictionary with ROUGE scores
    """
    """
    if len(texts) != len(references):
    if len(texts) != len(references):
    raise ValueError("Texts and references must have the same length")
    raise ValueError("Texts and references must have the same length")


    # Initialize scores
    # Initialize scores
    batch_scores = {rouge_type: [] for rouge_type in self.rouge_types}
    batch_scores = {rouge_type: [] for rouge_type in self.rouge_types}


    for text, reference in zip(texts, references):
    for text, reference in zip(texts, references):
    # Generate output
    # Generate output
    output = func(text, *args, **kwargs)
    output = func(text, *args, **kwargs)


    # Calculate ROUGE scores
    # Calculate ROUGE scores
    scores = self.scorer.score(reference, output)
    scores = self.scorer.score(reference, output)


    # Extract F1 scores
    # Extract F1 scores
    for rouge_type in self.rouge_types:
    for rouge_type in self.rouge_types:
    batch_scores[rouge_type].append(scores[rouge_type].fmeasure)
    batch_scores[rouge_type].append(scores[rouge_type].fmeasure)


    # Calculate average scores
    # Calculate average scores
    avg_scores = {}
    avg_scores = {}
    for rouge_type in self.rouge_types:
    for rouge_type in self.rouge_types:
    avg_scores[rouge_type] = (
    avg_scores[rouge_type] = (
    sum(batch_scores[rouge_type]) / len(batch_scores[rouge_type])
    sum(batch_scores[rouge_type]) / len(batch_scores[rouge_type])
    if batch_scores[rouge_type]
    if batch_scores[rouge_type]
    else 0
    else 0
    )
    )
    self.scores[rouge_type].extend(batch_scores[rouge_type])
    self.scores[rouge_type].extend(batch_scores[rouge_type])


    # Add value
    # Add value
    self.add_value(avg_scores)
    self.add_value(avg_scores)


    return avg_scores
    return avg_scores


    def measure_single(self, output: str, reference: str) -> Dict[str, float]:
    def measure_single(self, output: str, reference: str) -> Dict[str, float]:
    """
    """
    Measure the ROUGE scores for a single text.
    Measure the ROUGE scores for a single text.


    Args:
    Args:
    output: Generated text
    output: Generated text
    reference: Reference text
    reference: Reference text


    Returns:
    Returns:
    Dictionary with ROUGE scores
    Dictionary with ROUGE scores
    """
    """
    # Calculate ROUGE scores
    # Calculate ROUGE scores
    scores = self.scorer.score(reference, output)
    scores = self.scorer.score(reference, output)


    # Extract F1 scores
    # Extract F1 scores
    rouge_scores = {}
    rouge_scores = {}
    for rouge_type in self.rouge_types:
    for rouge_type in self.rouge_types:
    rouge_scores[rouge_type] = scores[rouge_type].fmeasure
    rouge_scores[rouge_type] = scores[rouge_type].fmeasure
    self.scores[rouge_type].append(scores[rouge_type].fmeasure)
    self.scores[rouge_type].append(scores[rouge_type].fmeasure)


    # Add value
    # Add value
    self.add_value(rouge_scores)
    self.add_value(rouge_scores)


    return rouge_scores
    return rouge_scores


    def get_overall_scores(self) -> Dict[str, float]:
    def get_overall_scores(self) -> Dict[str, float]:
    """
    """
    Get the overall ROUGE scores across all measurements.
    Get the overall ROUGE scores across all measurements.


    Returns:
    Returns:
    Dictionary with overall ROUGE scores
    Dictionary with overall ROUGE scores
    """
    """
    overall_scores = {}
    overall_scores = {}
    for rouge_type in self.rouge_types:
    for rouge_type in self.rouge_types:
    overall_scores[rouge_type] = (
    overall_scores[rouge_type] = (
    sum(self.scores[rouge_type]) / len(self.scores[rouge_type])
    sum(self.scores[rouge_type]) / len(self.scores[rouge_type])
    if self.scores[rouge_type]
    if self.scores[rouge_type]
    else 0
    else 0
    )
    )


    return overall_scores
    return overall_scores


    def reset(self) -> None:
    def reset(self) -> None:
    """
    """
    Reset the metric.
    Reset the metric.
    """
    """
    super().reset()
    super().reset()
    self.scores = {rouge_type: [] for rouge_type in self.rouge_types}
    self.scores = {rouge_type: [] for rouge_type in self.rouge_types}


    def get_stats(self) -> Dict[str, Any]:
    def get_stats(self) -> Dict[str, Any]:
    """
    """
    Get statistics about the ROUGE scores.
    Get statistics about the ROUGE scores.


    Returns:
    Returns:
    Dictionary with statistics
    Dictionary with statistics
    """
    """
    stats = {}
    stats = {}


    # Add overall scores
    # Add overall scores
    stats["overall"] = self.get_overall_scores()
    stats["overall"] = self.get_overall_scores()


    # Add individual statistics for each ROUGE type
    # Add individual statistics for each ROUGE type
    for rouge_type in self.rouge_types:
    for rouge_type in self.rouge_types:
    if self.scores[rouge_type]:
    if self.scores[rouge_type]:




    stats[rouge_type] = {
    stats[rouge_type] = {
    "min": min(self.scores[rouge_type]),
    "min": min(self.scores[rouge_type]),
    "max": max(self.scores[rouge_type]),
    "max": max(self.scores[rouge_type]),
    "mean": statistics.mean(self.scores[rouge_type]),
    "mean": statistics.mean(self.scores[rouge_type]),
    "median": statistics.median(self.scores[rouge_type]),
    "median": statistics.median(self.scores[rouge_type]),
    "std_dev": (
    "std_dev": (
    statistics.stdev(self.scores[rouge_type])
    statistics.stdev(self.scores[rouge_type])
    if len(self.scores[rouge_type]) > 1
    if len(self.scores[rouge_type]) > 1
    else 0
    else 0
    ),
    ),
    }
    }


    return stats
    return stats