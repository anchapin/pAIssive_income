"""
Accuracy metric for benchmarking AI models.

This module provides a metric for measuring the accuracy of AI models.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .base_metric import BaseMetric


class AccuracyMetric(BaseMetric):
    """
    Metric for measuring accuracy.
    """

    def __init__(self, **kwargs):
        """
        Initialize the accuracy metric.

        Args:
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="accuracy", unit="%", **kwargs)
        self.correct = 0
        self.total = 0

    def measure(
        self, func: Callable, inputs: List[Any], labels: List[Any], *args, **kwargs
    ) -> float:
        """
        Measure the accuracy of a function on a dataset.

        Args:
            func: Function to measure
            inputs: List of inputs
            labels: List of expected labels
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Accuracy as a percentage
        """
        if len(inputs) != len(labels):
            raise ValueError("Inputs and labels must have the same length")

        correct = 0
        total = len(inputs)

        for input_data, label in zip(inputs, labels):
            # Get prediction
            prediction = func(input_data, *args, **kwargs)

            # Check if correct
            if prediction == label:
                correct += 1

        # Calculate accuracy
        accuracy = (correct / total) * 100 if total > 0 else 0

        # Update counters
        self.correct += correct
        self.total += total

        # Add value
        self.add_value(accuracy)

        return accuracy

    def measure_single(self, prediction: Any, label: Any) -> float:
        """
        Measure the accuracy of a single prediction.

        Args:
            prediction: Predicted value
            label: Expected label

        Returns:
            Accuracy as a percentage (0 or 100)
        """
        # Check if correct
        correct = 1 if prediction == label else 0
        total = 1

        # Calculate accuracy
        accuracy = (correct / total) * 100

        # Update counters
        self.correct += correct
        self.total += total

        # Add value
        self.add_value(accuracy)

        return accuracy

    def get_overall_accuracy(self) -> float:
        """
        Get the overall accuracy across all measurements.

        Returns:
            Overall accuracy as a percentage
        """
        return (self.correct / self.total) * 100 if self.total > 0 else 0

    def reset(self) -> None:
        """
        Reset the metric.
        """
        super().reset()
        self.correct = 0
        self.total = 0

    def get_stats(self) -> Dict[str, float]:
        """
        Get statistics about the accuracy values.

        Returns:
            Dictionary with statistics
        """
        stats = super().get_stats()

        # Add overall accuracy
        stats["overall"] = self.get_overall_accuracy()

        return stats
