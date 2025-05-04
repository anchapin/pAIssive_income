"""
"""
Example usage of the model evaluation tools.
Example usage of the model evaluation tools.


This script demonstrates how to use the model evaluation tools to evaluate
This script demonstrates how to use the model evaluation tools to evaluate
and compare fine-tuned models.
and compare fine-tuned models.
"""
"""




import argparse
import argparse
import logging
import logging
import os
import os
import sys
import sys
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


# Add the parent directory to the path to import the ai_models module
# Add the parent directory to the path to import the ai_models module
sys.path.append(
sys.path.append(
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
)


from ai_models.fine_tuning import (compare_models, evaluate_model,
from ai_models.fine_tuning import (compare_models, evaluate_model,
generate_evaluation_report)
generate_evaluation_report)


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def evaluate_single_model(
def evaluate_single_model(
model_path: str,
model_path: str,
dataset_path: str,
dataset_path: str,
output_dir: str,
output_dir: str,
metrics: List[str] = None,
metrics: List[str] = None,
num_samples: Optional[int] = None,
num_samples: Optional[int] = None,
) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Evaluate a single model.
    Evaluate a single model.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    dataset_path: Path to the dataset
    dataset_path: Path to the dataset
    output_dir: Directory to save the results
    output_dir: Directory to save the results
    metrics: List of metrics to use for evaluation
    metrics: List of metrics to use for evaluation
    num_samples: Number of samples to use for evaluation
    num_samples: Number of samples to use for evaluation


    Returns:
    Returns:
    Dictionary with evaluation results
    Dictionary with evaluation results
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print(f"Evaluating Model: {os.path.basename(model_path)}")
    print(f"Evaluating Model: {os.path.basename(model_path)}")
    print("=" * 80)
    print("=" * 80)


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Convert metrics to EvaluationMetric enum
    # Convert metrics to EvaluationMetric enum
    if metrics is None:
    if metrics is None:
    metrics = ["perplexity", "accuracy"]
    metrics = ["perplexity", "accuracy"]


    # Evaluate model
    # Evaluate model
    results = evaluate_model(
    results = evaluate_model(
    model_path=model_path,
    model_path=model_path,
    dataset_path=dataset_path,
    dataset_path=dataset_path,
    metrics=metrics,
    metrics=metrics,
    output_dir=output_dir,
    output_dir=output_dir,
    num_samples=num_samples,
    num_samples=num_samples,
    )
    )


    # Print results
    # Print results
    print("\nEvaluation Results:")
    print("\nEvaluation Results:")
    for metric_name, metric_results in results.items():
    for metric_name, metric_results in results.items():
    print(f"\n{metric_name.upper()}:")
    print(f"\n{metric_name.upper()}:")
    if isinstance(metric_results, dict):
    if isinstance(metric_results, dict):
    for key, value in metric_results.items():
    for key, value in metric_results.items():
    print(f"  {key}: {value}")
    print(f"  {key}: {value}")
    else:
    else:
    print(f"  {metric_results}")
    print(f"  {metric_results}")


    return results
    return results




    def compare_multiple_models(
    def compare_multiple_models(
    model_paths: List[str],
    model_paths: List[str],
    dataset_path: str,
    dataset_path: str,
    output_dir: str,
    output_dir: str,
    metrics: List[str] = None,
    metrics: List[str] = None,
    num_samples: Optional[int] = None,
    num_samples: Optional[int] = None,
    ) -> Dict[str, Dict[str, Any]]:
    ) -> Dict[str, Dict[str, Any]]:
    """
    """
    Compare multiple models.
    Compare multiple models.


    Args:
    Args:
    model_paths: List of paths to the models
    model_paths: List of paths to the models
    dataset_path: Path to the dataset
    dataset_path: Path to the dataset
    output_dir: Directory to save the results
    output_dir: Directory to save the results
    metrics: List of metrics to use for evaluation
    metrics: List of metrics to use for evaluation
    num_samples: Number of samples to use for evaluation
    num_samples: Number of samples to use for evaluation


    Returns:
    Returns:
    Dictionary with evaluation results for each model
    Dictionary with evaluation results for each model
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print(f"Comparing {len(model_paths)} Models")
    print(f"Comparing {len(model_paths)} Models")
    print("=" * 80)
    print("=" * 80)


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Convert metrics to EvaluationMetric enum
    # Convert metrics to EvaluationMetric enum
    if metrics is None:
    if metrics is None:
    metrics = ["perplexity", "accuracy"]
    metrics = ["perplexity", "accuracy"]


    # Compare models
    # Compare models
    results = compare_models(
    results = compare_models(
    model_paths=model_paths,
    model_paths=model_paths,
    dataset_path=dataset_path,
    dataset_path=dataset_path,
    metrics=metrics,
    metrics=metrics,
    output_dir=output_dir,
    output_dir=output_dir,
    num_samples=num_samples,
    num_samples=num_samples,
    )
    )


    # Generate report
    # Generate report
    report_path = os.path.join(output_dir, "comparison_report.md")
    report_path = os.path.join(output_dir, "comparison_report.md")
    generate_evaluation_report(results, report_path)
    generate_evaluation_report(results, report_path)


    print(f"\nComparison report saved to: {report_path}")
    print(f"\nComparison report saved to: {report_path}")


    return results
    return results




    def main():
    def main():
    """
    """
    Main function.
    Main function.
    """
    """
    parser = argparse.ArgumentParser(
    parser = argparse.ArgumentParser(
    description="Evaluate and compare fine-tuned models"
    description="Evaluate and compare fine-tuned models"
    )
    )


    parser.add_argument("--model", type=str, help="Path to the model to evaluate")
    parser.add_argument("--model", type=str, help="Path to the model to evaluate")
    parser.add_argument(
    parser.add_argument(
    "--models", type=str, nargs="+", help="Paths to the models to compare"
    "--models", type=str, nargs="+", help="Paths to the models to compare"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--dataset", type=str, required=True, help="Path to the dataset"
    "--dataset", type=str, required=True, help="Path to the dataset"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir",
    "--output-dir",
    type=str,
    type=str,
    default="evaluation_results",
    default="evaluation_results",
    help="Directory to save the results",
    help="Directory to save the results",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--metrics",
    "--metrics",
    type=str,
    type=str,
    nargs="+",
    nargs="+",
    default=["perplexity", "accuracy"],
    default=["perplexity", "accuracy"],
    help="Metrics to use for evaluation",
    help="Metrics to use for evaluation",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--num-samples", type=int, help="Number of samples to use for evaluation"
    "--num-samples", type=int, help="Number of samples to use for evaluation"
    )
    )


    args = parser.parse_args()
    args = parser.parse_args()


    if args.model:
    if args.model:
    # Evaluate single model
    # Evaluate single model
    evaluate_single_model(
    evaluate_single_model(
    model_path=args.model,
    model_path=args.model,
    dataset_path=args.dataset,
    dataset_path=args.dataset,
    output_dir=args.output_dir,
    output_dir=args.output_dir,
    metrics=args.metrics,
    metrics=args.metrics,
    num_samples=args.num_samples,
    num_samples=args.num_samples,
    )
    )
    elif args.models:
    elif args.models:
    # Compare multiple models
    # Compare multiple models
    compare_multiple_models(
    compare_multiple_models(
    model_paths=args.models,
    model_paths=args.models,
    dataset_path=args.dataset,
    dataset_path=args.dataset,
    output_dir=args.output_dir,
    output_dir=args.output_dir,
    metrics=args.metrics,
    metrics=args.metrics,
    num_samples=args.num_samples,
    num_samples=args.num_samples,
    )
    )
    else:
    else:
    parser.error("Either --model or --models must be specified")
    parser.error("Either --model or --models must be specified")




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()