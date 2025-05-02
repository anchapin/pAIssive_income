"""
Evaluation tools for fine-tuned AI models.

This module provides tools for evaluating fine-tuned AI models, including
performance measurement, comparison, and report generation.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import torch
from datasets import Dataset, DatasetDict, load_dataset, load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer

# Import metrics from benchmarking
from ai_models.benchmarking.metrics import AccuracyMetric, PerplexityMetric, RougeMetric

# Configure logger
logger = logging.getLogger(__name__)


class EvaluationMetric(Enum):
    """
    Enum for evaluation metrics.
    """

    ACCURACY = "accuracy"
    PERPLEXITY = "perplexity"
    ROUGE = "rouge"
    BLEU = "bleu"
    F1 = "f1"
    EXACT_MATCH = "exact_match"
    CUSTOM = "custom"


@dataclass
class EvaluationConfig:
    """
    Configuration for model evaluation.
    """

    # Model information
    model_path: str

    # Dataset information
    dataset_path: Optional[str] = None
    dataset: Optional[Union[Dataset, DatasetDict]] = None

    # Evaluation metrics
    metrics: List[EvaluationMetric] = field(
        default_factory=lambda: [EvaluationMetric.PERPLEXITY]
    )

    # Custom evaluation function
    custom_evaluation_function: Optional[Callable] = None

    # Output configuration
    output_dir: Optional[str] = None
    save_results: bool = True

    # Evaluation parameters
    batch_size: int = 8
    max_length: int = 512
    num_samples: Optional[int] = None

    # Device configuration
    device: str = "auto"

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validate and process the configuration after initialization.
        """
        # Convert string metrics to enum if needed
        processed_metrics = []
        for metric in self.metrics:
            if isinstance(metric, str):
                try:
                    metric = EvaluationMetric(metric)
                except ValueError:
                    logger.warning(
                        f"Unknown metric: {metric}, using PERPLEXITY instead"
                    )
                    metric = EvaluationMetric.PERPLEXITY
            processed_metrics.append(metric)
        self.metrics = processed_metrics

        # Set device
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Create output directory if saving results
        if self.save_results and self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)


class ModelEvaluator:
    """
    Class for evaluating fine-tuned models.
    """

    def __init__(self, config: EvaluationConfig):
        """
        Initialize the model evaluator.

        Args:
            config: Configuration for evaluation
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.dataset = None
        self.metrics = {}
        self.results = {}

        # Initialize metrics
        self._initialize_metrics()

    def prepare(self) -> None:
        """
        Prepare for evaluation by loading the model, tokenizer, and dataset.
        """
        # Load model and tokenizer
        self._load_model_and_tokenizer()

        # Load dataset
        self._load_dataset()

    def _initialize_metrics(self) -> None:
        """
        Initialize metrics based on the configuration.
        """
        for metric_type in self.config.metrics:
            if metric_type == EvaluationMetric.ACCURACY:
                self.metrics[metric_type] = AccuracyMetric()
            elif metric_type == EvaluationMetric.PERPLEXITY:
                self.metrics[metric_type] = PerplexityMetric()
            elif metric_type == EvaluationMetric.ROUGE:
                self.metrics[metric_type] = RougeMetric()
            elif metric_type == EvaluationMetric.BLEU:
                # Initialize BLEU metric (to be implemented)
                pass
            elif metric_type == EvaluationMetric.F1:
                # Initialize F1 metric (to be implemented)
                pass
            elif metric_type == EvaluationMetric.EXACT_MATCH:
                # Initialize Exact Match metric (to be implemented)
                pass

        logger.info(f"Initialized metrics: {list(self.metrics.keys())}")

    def _load_model_and_tokenizer(self) -> None:
        """
        Load the model and tokenizer for evaluation.
        """
        try:
            logger.info(f"Loading model from {self.config.model_path}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path, device_map=self.config.device
            )

            logger.info(f"Model loaded successfully on {self.config.device}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def _load_dataset(self) -> None:
        """
        Load the dataset for evaluation.
        """
        # If dataset is already provided, use it
        if self.config.dataset is not None:
            self.dataset = self.config.dataset
            logger.info("Using provided dataset")
            return

        # If dataset path is provided, load it
        if self.config.dataset_path is not None:
            try:
                logger.info(f"Loading dataset from {self.config.dataset_path}")

                # Check if it's a Hugging Face dataset or a local path
                if os.path.exists(self.config.dataset_path):
                    # Try to load from disk
                    self.dataset = load_from_disk(self.config.dataset_path)
                else:
                    # Try to load from Hugging Face
                    self.dataset = load_dataset(self.config.dataset_path)

                logger.info("Dataset loaded successfully")
            except Exception as e:
                logger.error(f"Error loading dataset: {e}")
                raise
        else:
            logger.warning("No dataset provided for evaluation")

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate the model using the configured metrics.

        Returns:
            Dictionary with evaluation results
        """
        if self.model is None or self.tokenizer is None:
            self.prepare()

        if self.dataset is None:
            raise ValueError("No dataset available for evaluation")

        results = {}

        # Determine which split to use for evaluation
        eval_split = "test" if "test" in self.dataset else "validation"
        if eval_split not in self.dataset:
            # Use the first available split
            eval_split = list(self.dataset.keys())[0]

        logger.info(f"Evaluating model using {eval_split} split")

        # Limit number of samples if specified
        eval_dataset = self.dataset[eval_split]
        if self.config.num_samples and len(eval_dataset) > self.config.num_samples:
            eval_dataset = eval_dataset.select(range(self.config.num_samples))
            logger.info(f"Using {self.config.num_samples} samples for evaluation")

        # Evaluate using each metric
        for metric_type, metric in self.metrics.items():
            logger.info(f"Evaluating using {metric_type.value} metric")

            if metric_type == EvaluationMetric.PERPLEXITY:
                metric_result = self._evaluate_perplexity(eval_dataset)
            elif metric_type == EvaluationMetric.ACCURACY:
                metric_result = self._evaluate_accuracy(eval_dataset)
            elif metric_type == EvaluationMetric.ROUGE:
                metric_result = self._evaluate_rouge(eval_dataset)
            elif metric_type == EvaluationMetric.BLEU:
                metric_result = self._evaluate_bleu(eval_dataset)
            elif metric_type == EvaluationMetric.F1:
                metric_result = self._evaluate_f1(eval_dataset)
            elif metric_type == EvaluationMetric.EXACT_MATCH:
                metric_result = self._evaluate_exact_match(eval_dataset)
            elif (
                metric_type == EvaluationMetric.CUSTOM
                and self.config.custom_evaluation_function
            ):
                metric_result = self._evaluate_custom(eval_dataset)
            else:
                logger.warning(f"Skipping unsupported metric: {metric_type.value}")
                continue

            results[metric_type.value] = metric_result
            logger.info(f"{metric_type.value} evaluation result: {metric_result}")

        # Store results
        self.results = results

        # Save results if configured
        if self.config.save_results and self.config.output_dir:
            self._save_results()

        return results

    def _evaluate_perplexity(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using perplexity.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with perplexity results
        """
        # Set up perplexity calculation
        perplexity_metric = self.metrics.get(EvaluationMetric.PERPLEXITY)
        if perplexity_metric is None:
            perplexity_metric = PerplexityMetric()

        # Create a function to calculate loss for a text
        def calculate_loss(text):
            # Tokenize the text
            inputs = self.tokenizer(text, return_tensors="pt").to(self.config.device)

            # Calculate loss
            with torch.no_grad():
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss.item()

            # Return loss and number of tokens
            return loss, inputs["input_ids"].numel()

        # Find the text field in the dataset
        text_field = None
        for field in ["text", "content", "input", "prompt", "question"]:
            if field in dataset.features:
                text_field = field
                break

        if text_field is None:
            raise ValueError("No text field found in the dataset")

        # Calculate perplexity on the dataset
        texts = dataset[text_field]
        if isinstance(texts, list):
            # Measure perplexity on the dataset
            perplexity = perplexity_metric.measure(calculate_loss, texts)

            # Get overall perplexity
            overall_perplexity = perplexity_metric.get_overall_perplexity()

            return {"perplexity": perplexity, "overall_perplexity": overall_perplexity}
        else:
            logger.warning(
                f"Text field {text_field} is not a list, skipping perplexity evaluation"
            )
            return {"perplexity": float("inf")}

    def _evaluate_accuracy(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using accuracy.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with accuracy results
        """
        # Set up accuracy calculation
        accuracy_metric = self.metrics.get(EvaluationMetric.ACCURACY)
        if accuracy_metric is None:
            accuracy_metric = AccuracyMetric()

        # Find input and label fields in the dataset
        input_field = None
        label_field = None

        for input_candidate in ["input", "prompt", "question", "text"]:
            if input_candidate in dataset.features:
                input_field = input_candidate
                break

        for label_candidate in ["output", "completion", "answer", "label", "target"]:
            if label_candidate in dataset.features:
                label_field = label_candidate
                break

        if input_field is None or label_field is None:
            raise ValueError("Could not find input and label fields in the dataset")

        # Create a function to generate predictions
        def generate_prediction(input_text):
            # Tokenize the input
            inputs = self.tokenizer(input_text, return_tensors="pt").to(
                self.config.device
            )

            # Generate prediction
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=self.config.max_length,
                    num_return_sequences=1,
                )

            # Decode prediction
            prediction = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return prediction

        # Calculate accuracy on the dataset
        inputs = dataset[input_field]
        labels = dataset[label_field]

        if isinstance(inputs, list) and isinstance(labels, list):
            # Measure accuracy on the dataset
            accuracy = accuracy_metric.measure(generate_prediction, inputs, labels)

            # Get overall accuracy
            overall_accuracy = accuracy_metric.get_overall_accuracy()

            return {"accuracy": accuracy, "overall_accuracy": overall_accuracy}
        else:
            logger.warning(
                "Input or label fields are not lists, skipping accuracy evaluation"
            )
            return {"accuracy": 0.0}

    def _evaluate_rouge(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using ROUGE scores.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with ROUGE results
        """
        # Set up ROUGE calculation
        rouge_metric = self.metrics.get(EvaluationMetric.ROUGE)
        if rouge_metric is None:
            rouge_metric = RougeMetric()

        # Find input and reference fields in the dataset
        input_field = None
        reference_field = None

        for input_candidate in ["input", "prompt", "question", "text"]:
            if input_candidate in dataset.features:
                input_field = input_candidate
                break

        for reference_candidate in [
            "output",
            "completion",
            "answer",
            "label",
            "target",
            "reference",
        ]:
            if reference_candidate in dataset.features:
                reference_field = reference_candidate
                break

        if input_field is None or reference_field is None:
            raise ValueError("Could not find input and reference fields in the dataset")

        # Create a function to generate predictions
        def generate_prediction(input_text):
            # Tokenize the input
            inputs = self.tokenizer(input_text, return_tensors="pt").to(
                self.config.device
            )

            # Generate prediction
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=self.config.max_length,
                    num_return_sequences=1,
                )

            # Decode prediction
            prediction = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return prediction

        # Calculate ROUGE on the dataset
        inputs = dataset[input_field]
        references = dataset[reference_field]

        if isinstance(inputs, list) and isinstance(references, list):
            # Generate predictions
            predictions = []
            for input_text in inputs:
                prediction = generate_prediction(input_text)
                predictions.append(prediction)

            # Measure ROUGE scores
            rouge_scores = rouge_metric.measure_batch(predictions, references)

            return rouge_scores
        else:
            logger.warning(
                "Input or reference fields are not lists, skipping ROUGE evaluation"
            )
            return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}

    def _evaluate_bleu(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using BLEU score.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with BLEU results
        """
        # BLEU evaluation to be implemented
        logger.warning("BLEU evaluation not yet implemented")
        return {"bleu": 0.0}

    def _evaluate_f1(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using F1 score.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with F1 results
        """
        # F1 evaluation to be implemented
        logger.warning("F1 evaluation not yet implemented")
        return {"f1": 0.0}

    def _evaluate_exact_match(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using exact match.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with exact match results
        """
        # Exact match evaluation to be implemented
        logger.warning("Exact match evaluation not yet implemented")
        return {"exact_match": 0.0}

    def _evaluate_custom(self, dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate the model using a custom evaluation function.

        Args:
            dataset: Dataset to evaluate on

        Returns:
            Dictionary with custom evaluation results
        """
        if self.config.custom_evaluation_function is None:
            logger.warning("No custom evaluation function provided")
            return {"custom": 0.0}

        try:
            # Call the custom evaluation function
            custom_results = self.config.custom_evaluation_function(
                model=self.model,
                tokenizer=self.tokenizer,
                dataset=dataset,
                device=self.config.device,
            )

            return custom_results
        except Exception as e:
            logger.error(f"Error in custom evaluation function: {e}")
            return {"custom": 0.0, "error": str(e)}

    def _save_results(self) -> None:
        """
        Save evaluation results to disk.
        """
        if not self.config.output_dir:
            return

        # Create results directory
        results_dir = os.path.join(self.config.output_dir, "evaluation_results")
        os.makedirs(results_dir, exist_ok=True)

        # Save results as JSON
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        results_path = os.path.join(results_dir, f"results_{timestamp}.json")

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "model_path": self.config.model_path,
                    "metrics": [metric.value for metric in self.config.metrics],
                    "results": self.results,
                    "metadata": self.config.metadata,
                    "timestamp": timestamp,
                },
                f,
                indent=2,
            )

        logger.info(f"Saved evaluation results to {results_path}")

    def visualize_results(self, output_path: Optional[str] = None) -> str:
        """
        Visualize evaluation results.

        Args:
            output_path: Path to save the visualization

        Returns:
            Path to the saved visualization
        """
        if not self.results:
            logger.warning("No results to visualize")
            return ""

        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns

            # Create output directory if it doesn't exist
            if output_path is None and self.config.output_dir:
                output_dir = os.path.join(self.config.output_dir, "visualizations")
                os.makedirs(output_dir, exist_ok=True)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                output_path = os.path.join(
                    output_dir, f"evaluation_viz_{timestamp}.png"
                )

            if output_path is None:
                logger.warning("No output path provided for visualization")
                return ""

            # Prepare data for visualization
            viz_data = []

            for metric_name, metric_results in self.results.items():
                if isinstance(metric_results, dict):
                    for result_name, result_value in metric_results.items():
                        if isinstance(result_value, (int, float)) and not isinstance(
                            result_value, bool
                        ):
                            viz_data.append(
                                {
                                    "Metric": f"{metric_name}_{result_name}",
                                    "Value": result_value,
                                }
                            )

            if not viz_data:
                logger.warning("No numeric results to visualize")
                return ""

            # Create dataframe
            df = pd.DataFrame(viz_data)

            # Create visualization
            plt.figure(figsize=(10, 6))
            sns.set_style("whitegrid")

            # Create bar plot
            sns.barplot(x="Metric", y="Value", data=df)

            # Add labels and title
            plt.title(
                f"Evaluation Results for {os.path.basename(self.config.model_path)}"
            )
            plt.xlabel("Metric")
            plt.ylabel("Value")

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha="right")

            # Adjust layout
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path)
            plt.close()

            logger.info(f"Saved visualization to {output_path}")
            return output_path

        except ImportError as e:
            logger.warning(f"Could not create visualization: {e}")
            logger.warning(
                "Install matplotlib, pandas, and seaborn for visualization support"
            )
            return ""
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return ""

    @staticmethod
    def compare_models(
        model_paths: List[str],
        dataset_path: str,
        metrics: List[Union[str, EvaluationMetric]] = None,
        output_dir: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple models using the same evaluation metrics.

        Args:
            model_paths: List of paths to the models
            dataset_path: Path to the dataset
            metrics: List of metrics to use for evaluation
            output_dir: Directory to save the results
            **kwargs: Additional parameters for evaluation

        Returns:
            Dictionary with evaluation results for each model
        """
        if metrics is None:
            metrics = [EvaluationMetric.PERPLEXITY]

        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Evaluate each model
        results = {}

        for model_path in model_paths:
            logger.info(f"Evaluating model: {model_path}")

            try:
                # Create configuration
                config = EvaluationConfig(
                    model_path=model_path,
                    dataset_path=dataset_path,
                    metrics=metrics,
                    output_dir=output_dir,
                    **kwargs,
                )

                # Create evaluator
                evaluator = ModelEvaluator(config)

                # Evaluate model
                model_results = evaluator.evaluate()

                # Store results
                results[model_path] = model_results

                # Visualize results if output directory is provided
                if output_dir:
                    model_name = os.path.basename(model_path)
                    viz_path = os.path.join(output_dir, f"evaluation_{model_name}.png")
                    evaluator.visualize_results(viz_path)

            except Exception as e:
                logger.error(f"Error evaluating model {model_path}: {e}")
                results[model_path] = {"error": str(e)}

        # Generate comparison visualization if output directory is provided
        if output_dir and len(results) > 1:
            try:
                ModelEvaluator.visualize_comparison(results, output_dir)
            except Exception as e:
                logger.error(f"Error creating comparison visualization: {e}")

        return results

    @staticmethod
    def visualize_comparison(
        results: Dict[str, Dict[str, Any]], output_dir: str
    ) -> str:
        """
        Visualize comparison of multiple models.

        Args:
            results: Dictionary with evaluation results for each model
            output_dir: Directory to save the visualization

        Returns:
            Path to the saved visualization
        """
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Prepare data for visualization
            viz_data = []

            for model_path, model_results in results.items():
                model_name = os.path.basename(model_path)

                for metric_name, metric_results in model_results.items():
                    if isinstance(metric_results, dict):
                        for result_name, result_value in metric_results.items():
                            if isinstance(
                                result_value, (int, float)
                            ) and not isinstance(result_value, bool):
                                viz_data.append(
                                    {
                                        "Model": model_name,
                                        "Metric": f"{metric_name}_{result_name}",
                                        "Value": result_value,
                                    }
                                )

            if not viz_data:
                logger.warning("No numeric results to visualize")
                return ""

            # Create dataframe
            df = pd.DataFrame(viz_data)

            # Create visualization
            plt.figure(figsize=(12, 8))
            sns.set_style("whitegrid")

            # Create grouped bar plot
            sns.catplot(
                x="Metric",
                y="Value",
                hue="Model",
                data=df,
                kind="bar",
                height=6,
                aspect=1.5,
            )

            # Add labels and title
            plt.title("Model Comparison")
            plt.xlabel("Metric")
            plt.ylabel("Value")

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha="right")

            # Adjust layout
            plt.tight_layout()

            # Save figure
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_path = os.path.join(output_dir, f"model_comparison_{timestamp}.png")
            plt.savefig(output_path)
            plt.close()

            logger.info(f"Saved comparison visualization to {output_path}")
            return output_path

        except ImportError as e:
            logger.warning(f"Could not create visualization: {e}")
            logger.warning(
                "Install matplotlib, pandas, and seaborn for visualization support"
            )
            return ""
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return ""

    @staticmethod
    def generate_evaluation_report(
        results: Dict[str, Dict[str, Any]],
        output_path: str,
        include_visualizations: bool = True,
    ) -> str:
        """
        Generate a comprehensive evaluation report.

        Args:
            results: Dictionary with evaluation results for each model
            output_path: Path to save the report
            include_visualizations: Whether to include visualizations in the report

        Returns:
            Path to the saved report
        """
        try:
            import pandas as pd
            from tabulate import tabulate

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Prepare report content
            report_content = []

            # Add header
            report_content.append("# Model Evaluation Report")
            report_content.append(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append("")

            # Add summary
            report_content.append("## Summary")
            report_content.append(f"Number of models evaluated: {len(results)}")
            report_content.append("")

            # Create summary table
            summary_data = []

            for model_path, model_results in results.items():
                model_name = os.path.basename(model_path)
                model_summary = {"Model": model_name}

                # Extract key metrics
                for metric_name, metric_results in model_results.items():
                    if isinstance(metric_results, dict):
                        for result_name, result_value in metric_results.items():
                            if isinstance(
                                result_value, (int, float)
                            ) and not isinstance(result_value, bool):
                                model_summary[f"{metric_name}_{result_name}"] = (
                                    result_value
                                )

                summary_data.append(model_summary)

            if summary_data:
                # Convert to DataFrame
                summary_df = pd.DataFrame(summary_data)

                # Add summary table
                report_content.append(
                    tabulate(
                        summary_df, headers="keys", tablefmt="pipe", showindex=False
                    )
                )
                report_content.append("")

            # Add detailed results for each model
            report_content.append("## Detailed Results")
            report_content.append("")

            for model_path, model_results in results.items():
                model_name = os.path.basename(model_path)
                report_content.append(f"### {model_name}")
                report_content.append(f"Model path: {model_path}")
                report_content.append("")

                # Add metrics
                for metric_name, metric_results in model_results.items():
                    report_content.append(f"#### {metric_name}")

                    if isinstance(metric_results, dict):
                        # Create table for metric results
                        metric_data = []

                        for result_name, result_value in metric_results.items():
                            metric_data.append(
                                {"Metric": result_name, "Value": result_value}
                            )

                        if metric_data:
                            # Convert to DataFrame
                            metric_df = pd.DataFrame(metric_data)

                            # Add metric table
                            report_content.append(
                                tabulate(
                                    metric_df,
                                    headers="keys",
                                    tablefmt="pipe",
                                    showindex=False,
                                )
                            )
                    else:
                        report_content.append(f"Value: {metric_results}")

                    report_content.append("")

            # Add visualizations if requested
            if include_visualizations:
                report_content.append("## Visualizations")
                report_content.append("")

                # Generate comparison visualization
                viz_dir = os.path.join(os.path.dirname(output_path), "visualizations")
                os.makedirs(viz_dir, exist_ok=True)

                comparison_viz_path = ModelEvaluator.visualize_comparison(
                    results, viz_dir
                )

                if comparison_viz_path:
                    # Add comparison visualization
                    report_content.append("### Model Comparison")
                    report_content.append(
                        f"![Model Comparison]({os.path.relpath(comparison_viz_path, os.path.dirname(output_path))})"
                    )
                    report_content.append("")

            # Write report to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(report_content))

            logger.info(f"Saved evaluation report to {output_path}")
            return output_path

        except ImportError as e:
            logger.warning(f"Could not generate report: {e}")
            logger.warning("Install pandas and tabulate for report generation support")
            return ""
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return ""


# Helper functions


def evaluate_model(
    model_path: str,
    dataset_path: str,
    metrics: List[Union[str, EvaluationMetric]] = None,
    output_dir: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Evaluate a fine-tuned model.

    Args:
        model_path: Path to the model
        dataset_path: Path to the dataset
        metrics: List of metrics to use for evaluation
        output_dir: Directory to save the results
        **kwargs: Additional parameters for evaluation

    Returns:
        Dictionary with evaluation results
    """
    # Create configuration
    config = EvaluationConfig(
        model_path=model_path,
        dataset_path=dataset_path,
        metrics=metrics or [EvaluationMetric.PERPLEXITY],
        output_dir=output_dir,
        **kwargs,
    )

    # Create evaluator
    evaluator = ModelEvaluator(config)

    # Evaluate model
    results = evaluator.evaluate()

    # Visualize results if output directory is provided
    if output_dir:
        evaluator.visualize_results()

    return results


def compare_models(
    model_paths: List[str],
    dataset_path: str,
    metrics: List[Union[str, EvaluationMetric]] = None,
    output_dir: Optional[str] = None,
    **kwargs,
) -> Dict[str, Dict[str, Any]]:
    """
    Compare multiple fine-tuned models.

    Args:
        model_paths: List of paths to the models
        dataset_path: Path to the dataset
        metrics: List of metrics to use for evaluation
        output_dir: Directory to save the results
        **kwargs: Additional parameters for evaluation

    Returns:
        Dictionary with evaluation results for each model
    """
    return ModelEvaluator.compare_models(
        model_paths=model_paths,
        dataset_path=dataset_path,
        metrics=metrics,
        output_dir=output_dir,
        **kwargs,
    )


def generate_evaluation_report(
    results: Dict[str, Dict[str, Any]],
    output_path: str,
    include_visualizations: bool = True,
) -> str:
    """
    Generate a comprehensive evaluation report.

    Args:
        results: Dictionary with evaluation results for each model
        output_path: Path to save the report
        include_visualizations: Whether to include visualizations in the report

    Returns:
        Path to the saved report
    """
    return ModelEvaluator.generate_evaluation_report(
        results=results,
        output_path=output_path,
        include_visualizations=include_visualizations,
    )
