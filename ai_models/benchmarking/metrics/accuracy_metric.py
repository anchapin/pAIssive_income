"""
"""
Accuracy metric for benchmarking AI models.
Accuracy metric for benchmarking AI models.


This module provides a metric for measuring the accuracy of AI models.
This module provides a metric for measuring the accuracy of AI models.
"""
"""


from typing import Any, Callable, Dict, List
from typing import Any, Callable, Dict, List


from .base_metric import BaseMetric
from .base_metric import BaseMetric




class AccuracyMetric(BaseMetric):
    class AccuracyMetric(BaseMetric):
    """
    """
    Metric for measuring accuracy.
    Metric for measuring accuracy.
    """
    """


    def __init__(self, **kwargs):
    def __init__(self, **kwargs):
    """
    """
    Initialize the accuracy metric.
    Initialize the accuracy metric.


    Args:
    Args:
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    super().__init__(name="accuracy", unit="%", **kwargs)
    super().__init__(name="accuracy", unit="%", **kwargs)
    self.correct = 0
    self.correct = 0
    self.total = 0
    self.total = 0


    def measure(
    def measure(
    self, func: Callable, inputs: List[Any], labels: List[Any], *args, **kwargs
    self, func: Callable, inputs: List[Any], labels: List[Any], *args, **kwargs
    ) -> float:
    ) -> float:
    """
    """
    Measure the accuracy of a function on a dataset.
    Measure the accuracy of a function on a dataset.


    Args:
    Args:
    func: Function to measure
    func: Function to measure
    inputs: List of inputs
    inputs: List of inputs
    labels: List of expected labels
    labels: List of expected labels
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    Accuracy as a percentage
    Accuracy as a percentage
    """
    """
    if len(inputs) != len(labels):
    if len(inputs) != len(labels):
    raise ValueError("Inputs and labels must have the same length")
    raise ValueError("Inputs and labels must have the same length")


    correct = 0
    correct = 0
    total = len(inputs)
    total = len(inputs)


    for input_data, label in zip(inputs, labels):
    for input_data, label in zip(inputs, labels):
    # Get prediction
    # Get prediction
    prediction = func(input_data, *args, **kwargs)
    prediction = func(input_data, *args, **kwargs)


    # Check if correct
    # Check if correct
    if prediction == label:
    if prediction == label:
    correct += 1
    correct += 1


    # Calculate accuracy
    # Calculate accuracy
    accuracy = (correct / total) * 100 if total > 0 else 0
    accuracy = (correct / total) * 100 if total > 0 else 0


    # Update counters
    # Update counters
    self.correct += correct
    self.correct += correct
    self.total += total
    self.total += total


    # Add value
    # Add value
    self.add_value(accuracy)
    self.add_value(accuracy)


    return accuracy
    return accuracy


    def measure_single(self, prediction: Any, label: Any) -> float:
    def measure_single(self, prediction: Any, label: Any) -> float:
    """
    """
    Measure the accuracy of a single prediction.
    Measure the accuracy of a single prediction.


    Args:
    Args:
    prediction: Predicted value
    prediction: Predicted value
    label: Expected label
    label: Expected label


    Returns:
    Returns:
    Accuracy as a percentage (0 or 100)
    Accuracy as a percentage (0 or 100)
    """
    """
    # Check if correct
    # Check if correct
    correct = 1 if prediction == label else 0
    correct = 1 if prediction == label else 0
    total = 1
    total = 1


    # Calculate accuracy
    # Calculate accuracy
    accuracy = (correct / total) * 100
    accuracy = (correct / total) * 100


    # Update counters
    # Update counters
    self.correct += correct
    self.correct += correct
    self.total += total
    self.total += total


    # Add value
    # Add value
    self.add_value(accuracy)
    self.add_value(accuracy)


    return accuracy
    return accuracy


    def get_overall_accuracy(self) -> float:
    def get_overall_accuracy(self) -> float:
    """
    """
    Get the overall accuracy across all measurements.
    Get the overall accuracy across all measurements.


    Returns:
    Returns:
    Overall accuracy as a percentage
    Overall accuracy as a percentage
    """
    """
    return (self.correct / self.total) * 100 if self.total > 0 else 0
    return (self.correct / self.total) * 100 if self.total > 0 else 0


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
    self.correct = 0
    self.correct = 0
    self.total = 0
    self.total = 0


    def get_stats(self) -> Dict[str, float]:
    def get_stats(self) -> Dict[str, float]:
    """
    """
    Get statistics about the accuracy values.
    Get statistics about the accuracy values.


    Returns:
    Returns:
    Dictionary with statistics
    Dictionary with statistics
    """
    """
    stats = super().get_stats()
    stats = super().get_stats()


    # Add overall accuracy
    # Add overall accuracy
    stats["overall"] = self.get_overall_accuracy()
    stats["overall"] = self.get_overall_accuracy()


    return stats
    return stats

