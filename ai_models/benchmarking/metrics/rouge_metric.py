"""
ROUGE metric for benchmarking AI models.

This module provides a metric for measuring the ROUGE scores of text generation models.
"""

from typing import Dict, Any, Optional, List, Union, Tuple, Callable

from .base_metric import BaseMetric

# Try to import optional dependencies
try:
    from rouge_score import rouge_scorer

    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False


class RougeMetric(BaseMetric):
    """
    Metric for measuring ROUGE scores.
    """

    def __init__(self, rouge_types: List[str] = None, **kwargs):
        """
        Initialize the ROUGE metric.

        Args:
            rouge_types: List of ROUGE types to compute
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="rouge", unit="", **kwargs)

        if not ROUGE_AVAILABLE:
            raise ImportError("rouge_score is required for ROUGE metrics")

        self.rouge_types = rouge_types or ["rouge1", "rouge2", "rougeL"]
        self.scorer = rouge_scorer.RougeScorer(self.rouge_types, use_stemmer=True)

        # Initialize accumulators
        self.scores = {rouge_type: [] for rouge_type in self.rouge_types}

    def measure(
        self, func: Callable, texts: List[str], references: List[str], *args, **kwargs
    ) -> Dict[str, float]:
        """
        Measure the ROUGE scores of a model on a dataset.

        Args:
            func: Function that generates text
            texts: List of input texts
            references: List of reference texts
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Dictionary with ROUGE scores
        """
        if len(texts) != len(references):
            raise ValueError("Texts and references must have the same length")

        # Initialize scores
        batch_scores = {rouge_type: [] for rouge_type in self.rouge_types}

        for text, reference in zip(texts, references):
            # Generate output
            output = func(text, *args, **kwargs)

            # Calculate ROUGE scores
            scores = self.scorer.score(reference, output)

            # Extract F1 scores
            for rouge_type in self.rouge_types:
                batch_scores[rouge_type].append(scores[rouge_type].fmeasure)

        # Calculate average scores
        avg_scores = {}
        for rouge_type in self.rouge_types:
            avg_scores[rouge_type] = (
                sum(batch_scores[rouge_type]) / len(batch_scores[rouge_type])
                if batch_scores[rouge_type]
                else 0
            )
            self.scores[rouge_type].extend(batch_scores[rouge_type])

        # Add value
        self.add_value(avg_scores)

        return avg_scores

    def measure_single(self, output: str, reference: str) -> Dict[str, float]:
        """
        Measure the ROUGE scores for a single text.

        Args:
            output: Generated text
            reference: Reference text

        Returns:
            Dictionary with ROUGE scores
        """
        # Calculate ROUGE scores
        scores = self.scorer.score(reference, output)

        # Extract F1 scores
        rouge_scores = {}
        for rouge_type in self.rouge_types:
            rouge_scores[rouge_type] = scores[rouge_type].fmeasure
            self.scores[rouge_type].append(scores[rouge_type].fmeasure)

        # Add value
        self.add_value(rouge_scores)

        return rouge_scores

    def get_overall_scores(self) -> Dict[str, float]:
        """
        Get the overall ROUGE scores across all measurements.

        Returns:
            Dictionary with overall ROUGE scores
        """
        overall_scores = {}
        for rouge_type in self.rouge_types:
            overall_scores[rouge_type] = (
                sum(self.scores[rouge_type]) / len(self.scores[rouge_type])
                if self.scores[rouge_type]
                else 0
            )

        return overall_scores

    def reset(self) -> None:
        """
        Reset the metric.
        """
        super().reset()
        self.scores = {rouge_type: [] for rouge_type in self.rouge_types}

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the ROUGE scores.

        Returns:
            Dictionary with statistics
        """
        stats = {}

        # Add overall scores
        stats["overall"] = self.get_overall_scores()

        # Add individual statistics for each ROUGE type
        for rouge_type in self.rouge_types:
            if self.scores[rouge_type]:
                import statistics

                stats[rouge_type] = {
                    "min": min(self.scores[rouge_type]),
                    "max": max(self.scores[rouge_type]),
                    "mean": statistics.mean(self.scores[rouge_type]),
                    "median": statistics.median(self.scores[rouge_type]),
                    "std_dev": (
                        statistics.stdev(self.scores[rouge_type])
                        if len(self.scores[rouge_type]) > 1
                        else 0
                    ),
                }

        return stats
