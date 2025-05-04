"""
"""
Fine-tuning workflows for AI models.
Fine-tuning workflows for AI models.


This module provides tools for creating and running fine-tuning workflows,
This module provides tools for creating and running fine-tuning workflows,
including data collection, fine-tuning, and evaluation.
including data collection, fine-tuning, and evaluation.
"""
"""




import json
import json
import logging
import logging
import os
import os
import time
import time
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from enum import Enum
from enum import Enum
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .evaluator import EvaluationConfig, ModelEvaluator, compare_models
from .evaluator import EvaluationConfig, ModelEvaluator, compare_models
from .fine_tuner import FineTuner, FineTuningConfig
from .fine_tuner import FineTuner, FineTuningConfig


(
(
DataCollectionConfig,
DataCollectionConfig,
DataCollector,
DataCollector,
)
)
# Configure logger
# Configure logger
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class WorkflowStep(Enum):
    class WorkflowStep(Enum):
    """
    """
    Enum for workflow steps.
    Enum for workflow steps.
    """
    """


    DATA_COLLECTION = "data_collection"
    DATA_COLLECTION = "data_collection"
    FINE_TUNING = "fine_tuning"
    FINE_TUNING = "fine_tuning"
    EVALUATION = "evaluation"
    EVALUATION = "evaluation"
    COMPARISON = "comparison"
    COMPARISON = "comparison"




    @dataclass
    @dataclass
    class WorkflowConfig:
    class WorkflowConfig:
    """
    """
    Configuration for fine-tuning workflow.
    Configuration for fine-tuning workflow.
    """
    """


    # Workflow name and output directory
    # Workflow name and output directory
    name: str
    name: str
    output_dir: str
    output_dir: str


    # Steps to include in the workflow
    # Steps to include in the workflow
    steps: List[WorkflowStep] = field(
    steps: List[WorkflowStep] = field(
    default_factory=lambda: [
    default_factory=lambda: [
    WorkflowStep.DATA_COLLECTION,
    WorkflowStep.DATA_COLLECTION,
    WorkflowStep.FINE_TUNING,
    WorkflowStep.FINE_TUNING,
    WorkflowStep.EVALUATION,
    WorkflowStep.EVALUATION,
    ]
    ]
    )
    )


    # Data collection configuration
    # Data collection configuration
    data_collection_config: Optional[DataCollectionConfig] = None
    data_collection_config: Optional[DataCollectionConfig] = None


    # Fine-tuning configuration
    # Fine-tuning configuration
    fine_tuning_config: Optional[FineTuningConfig] = None
    fine_tuning_config: Optional[FineTuningConfig] = None


    # Evaluation configuration
    # Evaluation configuration
    evaluation_config: Optional[EvaluationConfig] = None
    evaluation_config: Optional[EvaluationConfig] = None


    # Comparison configuration
    # Comparison configuration
    comparison_models: List[str] = field(default_factory=list)
    comparison_models: List[str] = field(default_factory=list)


    # Metadata
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


    def __post_init__(self):
    def __post_init__(self):
    """
    """
    Validate and process the configuration after initialization.
    Validate and process the configuration after initialization.
    """
    """
    # Convert string steps to enum if needed
    # Convert string steps to enum if needed
    processed_steps = []
    processed_steps = []
    for step in self.steps:
    for step in self.steps:
    if isinstance(step, str):
    if isinstance(step, str):
    try:
    try:
    step = WorkflowStep(step)
    step = WorkflowStep(step)
except ValueError:
except ValueError:
    logger.warning(f"Unknown step: {step}, skipping")
    logger.warning(f"Unknown step: {step}, skipping")
    continue
    continue
    processed_steps.append(step)
    processed_steps.append(step)
    self.steps = processed_steps
    self.steps = processed_steps


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(self.output_dir, exist_ok=True)
    os.makedirs(self.output_dir, exist_ok=True)




    class FineTuningWorkflow:
    class FineTuningWorkflow:
    """
    """
    Class for running fine-tuning workflows.
    Class for running fine-tuning workflows.
    """
    """


    def __init__(self, config: WorkflowConfig):
    def __init__(self, config: WorkflowConfig):
    """
    """
    Initialize the workflow.
    Initialize the workflow.


    Args:
    Args:
    config: Configuration for the workflow
    config: Configuration for the workflow
    """
    """
    self.config = config
    self.config = config
    self.results = {}
    self.results = {}
    self.dataset = None
    self.dataset = None
    self.model_path = None
    self.model_path = None


    def run(self) -> Dict[str, Any]:
    def run(self) -> Dict[str, Any]:
    """
    """
    Run the workflow.
    Run the workflow.


    Returns:
    Returns:
    Dictionary with workflow results
    Dictionary with workflow results
    """
    """
    start_time = time.time()
    start_time = time.time()


    logger.info(f"Starting workflow: {self.config.name}")
    logger.info(f"Starting workflow: {self.config.name}")


    # Run each step in the workflow
    # Run each step in the workflow
    for step in self.config.steps:
    for step in self.config.steps:
    logger.info(f"Running step: {step.value}")
    logger.info(f"Running step: {step.value}")


    if step == WorkflowStep.DATA_COLLECTION:
    if step == WorkflowStep.DATA_COLLECTION:
    self._run_data_collection()
    self._run_data_collection()
    elif step == WorkflowStep.FINE_TUNING:
    elif step == WorkflowStep.FINE_TUNING:
    self._run_fine_tuning()
    self._run_fine_tuning()
    elif step == WorkflowStep.EVALUATION:
    elif step == WorkflowStep.EVALUATION:
    self._run_evaluation()
    self._run_evaluation()
    elif step == WorkflowStep.COMPARISON:
    elif step == WorkflowStep.COMPARISON:
    self._run_comparison()
    self._run_comparison()


    # Calculate total time
    # Calculate total time
    total_time = time.time() - start_time
    total_time = time.time() - start_time


    # Save workflow results
    # Save workflow results
    self._save_results(total_time)
    self._save_results(total_time)


    logger.info(f"Workflow completed in {total_time:.2f} seconds")
    logger.info(f"Workflow completed in {total_time:.2f} seconds")


    return self.results
    return self.results


    def _run_data_collection(self) -> None:
    def _run_data_collection(self) -> None:
    """
    """
    Run the data collection step.
    Run the data collection step.
    """
    """
    if self.config.data_collection_config is None:
    if self.config.data_collection_config is None:
    logger.warning("No data collection configuration provided, skipping step")
    logger.warning("No data collection configuration provided, skipping step")
    return try:
    return try:
    logger.info("Collecting data")
    logger.info("Collecting data")


    # Create data collector
    # Create data collector
    collector = DataCollector(self.config.data_collection_config)
    collector = DataCollector(self.config.data_collection_config)


    # Prepare dataset
    # Prepare dataset
    self.dataset = collector.prepare()
    self.dataset = collector.prepare()


    # Export dataset
    # Export dataset
    dataset_path = os.path.join(self.config.output_dir, "dataset")
    dataset_path = os.path.join(self.config.output_dir, "dataset")
    self.dataset.save_to_disk(dataset_path)
    self.dataset.save_to_disk(dataset_path)


    # Store results
    # Store results
    self.results["data_collection"] = {
    self.results["data_collection"] = {
    "dataset_path": dataset_path,
    "dataset_path": dataset_path,
    "num_samples": {
    "num_samples": {
    "train": len(self.dataset["train"]),
    "train": len(self.dataset["train"]),
    "validation": len(self.dataset["validation"]),
    "validation": len(self.dataset["validation"]),
    "test": len(self.dataset["test"]) if "test" in self.dataset else 0,
    "test": len(self.dataset["test"]) if "test" in self.dataset else 0,
    },
    },
    }
    }


    logger.info(f"Data collection completed, dataset saved to {dataset_path}")
    logger.info(f"Data collection completed, dataset saved to {dataset_path}")


except Exception as e:
except Exception as e:
    logger.error(f"Error in data collection step: {e}")
    logger.error(f"Error in data collection step: {e}")
    self.results["data_collection"] = {"error": str(e)}
    self.results["data_collection"] = {"error": str(e)}


    def _run_fine_tuning(self) -> None:
    def _run_fine_tuning(self) -> None:
    """
    """
    Run the fine-tuning step.
    Run the fine-tuning step.
    """
    """
    if self.config.fine_tuning_config is None:
    if self.config.fine_tuning_config is None:
    logger.warning("No fine-tuning configuration provided, skipping step")
    logger.warning("No fine-tuning configuration provided, skipping step")
    return try:
    return try:
    logger.info("Fine-tuning model")
    logger.info("Fine-tuning model")


    # Update fine-tuning configuration with dataset if available
    # Update fine-tuning configuration with dataset if available
    if (
    if (
    self.dataset is not None
    self.dataset is not None
    and self.config.fine_tuning_config.dataset is None
    and self.config.fine_tuning_config.dataset is None
    ):
    ):
    self.config.fine_tuning_config.dataset = self.dataset
    self.config.fine_tuning_config.dataset = self.dataset


    # Create fine-tuner
    # Create fine-tuner
    fine_tuner = FineTuner(self.config.fine_tuning_config)
    fine_tuner = FineTuner(self.config.fine_tuning_config)


    # Prepare for fine-tuning
    # Prepare for fine-tuning
    fine_tuner.prepare()
    fine_tuner.prepare()


    # Train the model
    # Train the model
    train_metrics = fine_tuner.train()
    train_metrics = fine_tuner.train()


    # Save the model
    # Save the model
    self.model_path = fine_tuner.save()
    self.model_path = fine_tuner.save()


    # Store results
    # Store results
    self.results["fine_tuning"] = {
    self.results["fine_tuning"] = {
    "model_path": self.model_path,
    "model_path": self.model_path,
    "train_metrics": train_metrics,
    "train_metrics": train_metrics,
    }
    }


    logger.info(f"Fine-tuning completed, model saved to {self.model_path}")
    logger.info(f"Fine-tuning completed, model saved to {self.model_path}")


except Exception as e:
except Exception as e:
    logger.error(f"Error in fine-tuning step: {e}")
    logger.error(f"Error in fine-tuning step: {e}")
    self.results["fine_tuning"] = {"error": str(e)}
    self.results["fine_tuning"] = {"error": str(e)}


    def _run_evaluation(self) -> None:
    def _run_evaluation(self) -> None:
    """
    """
    Run the evaluation step.
    Run the evaluation step.
    """
    """
    if self.config.evaluation_config is None:
    if self.config.evaluation_config is None:
    logger.warning("No evaluation configuration provided, skipping step")
    logger.warning("No evaluation configuration provided, skipping step")
    return if (
    return if (
    self.model_path is None
    self.model_path is None
    and "fine_tuning" in self.results
    and "fine_tuning" in self.results
    and "model_path" in self.results["fine_tuning"]
    and "model_path" in self.results["fine_tuning"]
    ):
    ):
    self.model_path = self.results["fine_tuning"]["model_path"]
    self.model_path = self.results["fine_tuning"]["model_path"]


    if self.model_path is None:
    if self.model_path is None:
    logger.warning("No model path available for evaluation, skipping step")
    logger.warning("No model path available for evaluation, skipping step")
    return try:
    return try:
    logger.info(f"Evaluating model: {self.model_path}")
    logger.info(f"Evaluating model: {self.model_path}")


    # Update evaluation configuration with model path
    # Update evaluation configuration with model path
    self.config.evaluation_config.model_path = self.model_path
    self.config.evaluation_config.model_path = self.model_path


    # Update evaluation configuration with dataset if available
    # Update evaluation configuration with dataset if available
    if (
    if (
    self.dataset is not None
    self.dataset is not None
    and self.config.evaluation_config.dataset is None
    and self.config.evaluation_config.dataset is None
    ):
    ):
    self.config.evaluation_config.dataset = self.dataset
    self.config.evaluation_config.dataset = self.dataset


    # Create evaluator
    # Create evaluator
    evaluator = ModelEvaluator(self.config.evaluation_config)
    evaluator = ModelEvaluator(self.config.evaluation_config)


    # Evaluate model
    # Evaluate model
    evaluation_results = evaluator.evaluate()
    evaluation_results = evaluator.evaluate()


    # Visualize results
    # Visualize results
    if self.config.evaluation_config.output_dir:
    if self.config.evaluation_config.output_dir:
    visualization_path = evaluator.visualize_results()
    visualization_path = evaluator.visualize_results()
    else:
    else:
    visualization_path = None
    visualization_path = None


    # Store results
    # Store results
    self.results["evaluation"] = {
    self.results["evaluation"] = {
    "results": evaluation_results,
    "results": evaluation_results,
    "visualization_path": visualization_path,
    "visualization_path": visualization_path,
    }
    }


    logger.info("Evaluation completed")
    logger.info("Evaluation completed")


except Exception as e:
except Exception as e:
    logger.error(f"Error in evaluation step: {e}")
    logger.error(f"Error in evaluation step: {e}")
    self.results["evaluation"] = {"error": str(e)}
    self.results["evaluation"] = {"error": str(e)}


    def _run_comparison(self) -> None:
    def _run_comparison(self) -> None:
    """
    """
    Run the comparison step.
    Run the comparison step.
    """
    """
    if not self.config.comparison_models:
    if not self.config.comparison_models:
    logger.warning("No comparison models provided, skipping step")
    logger.warning("No comparison models provided, skipping step")
    return if (
    return if (
    self.model_path is None
    self.model_path is None
    and "fine_tuning" in self.results
    and "fine_tuning" in self.results
    and "model_path" in self.results["fine_tuning"]
    and "model_path" in self.results["fine_tuning"]
    ):
    ):
    self.model_path = self.results["fine_tuning"]["model_path"]
    self.model_path = self.results["fine_tuning"]["model_path"]


    if self.model_path is None:
    if self.model_path is None:
    logger.warning("No model path available for comparison, skipping step")
    logger.warning("No model path available for comparison, skipping step")
    return try:
    return try:
    logger.info("Comparing models")
    logger.info("Comparing models")


    # Add the fine-tuned model to the comparison list
    # Add the fine-tuned model to the comparison list
    model_paths = [self.model_path] + self.config.comparison_models
    model_paths = [self.model_path] + self.config.comparison_models


    # Get dataset path
    # Get dataset path
    dataset_path = None
    dataset_path = None
    if self.dataset is not None:
    if self.dataset is not None:
    dataset_path = os.path.join(self.config.output_dir, "dataset")
    dataset_path = os.path.join(self.config.output_dir, "dataset")
    self.dataset.save_to_disk(dataset_path)
    self.dataset.save_to_disk(dataset_path)
    elif (
    elif (
    "data_collection" in self.results
    "data_collection" in self.results
    and "dataset_path" in self.results["data_collection"]
    and "dataset_path" in self.results["data_collection"]
    ):
    ):
    dataset_path = self.results["data_collection"]["dataset_path"]
    dataset_path = self.results["data_collection"]["dataset_path"]


    if dataset_path is None:
    if dataset_path is None:
    logger.warning("No dataset available for comparison, skipping step")
    logger.warning("No dataset available for comparison, skipping step")
    return # Create output directory for comparison results
    return # Create output directory for comparison results
    comparison_dir = os.path.join(self.config.output_dir, "comparison")
    comparison_dir = os.path.join(self.config.output_dir, "comparison")
    os.makedirs(comparison_dir, exist_ok=True)
    os.makedirs(comparison_dir, exist_ok=True)


    # Compare models
    # Compare models
    comparison_results = compare_models(
    comparison_results = compare_models(
    model_paths=model_paths,
    model_paths=model_paths,
    dataset_path=dataset_path,
    dataset_path=dataset_path,
    metrics=(
    metrics=(
    self.config.evaluation_config.metrics
    self.config.evaluation_config.metrics
    if self.config.evaluation_config
    if self.config.evaluation_config
    else None
    else None
    ),
    ),
    output_dir=comparison_dir,
    output_dir=comparison_dir,
    )
    )


    # Generate comparison report
    # Generate comparison report
    report_path = os.path.join(comparison_dir, "comparison_report.md")
    report_path = os.path.join(comparison_dir, "comparison_report.md")
    report_path = ModelEvaluator.generate_evaluation_report(
    report_path = ModelEvaluator.generate_evaluation_report(
    results=comparison_results, output_path=report_path
    results=comparison_results, output_path=report_path
    )
    )


    # Store results
    # Store results
    self.results["comparison"] = {
    self.results["comparison"] = {
    "results": comparison_results,
    "results": comparison_results,
    "report_path": report_path,
    "report_path": report_path,
    }
    }


    logger.info("Comparison completed")
    logger.info("Comparison completed")


except Exception as e:
except Exception as e:
    logger.error(f"Error in comparison step: {e}")
    logger.error(f"Error in comparison step: {e}")
    self.results["comparison"] = {"error": str(e)}
    self.results["comparison"] = {"error": str(e)}


    def _save_results(self, total_time: float) -> None:
    def _save_results(self, total_time: float) -> None:
    """
    """
    Save workflow results to disk.
    Save workflow results to disk.


    Args:
    Args:
    total_time: Total time taken by the workflow
    total_time: Total time taken by the workflow
    """
    """
    # Create results object
    # Create results object
    workflow_results = {
    workflow_results = {
    "name": self.config.name,
    "name": self.config.name,
    "steps": [step.value for step in self.config.steps],
    "steps": [step.value for step in self.config.steps],
    "results": self.results,
    "results": self.results,
    "metadata": self.config.metadata,
    "metadata": self.config.metadata,
    "total_time": total_time,
    "total_time": total_time,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    }


    # Save results to file
    # Save results to file
    results_path = os.path.join(self.config.output_dir, "workflow_results.json")
    results_path = os.path.join(self.config.output_dir, "workflow_results.json")


    with open(results_path, "w", encoding="utf-8") as f:
    with open(results_path, "w", encoding="utf-8") as f:
    json.dump(workflow_results, f, indent=2)
    json.dump(workflow_results, f, indent=2)


    logger.info(f"Saved workflow results to {results_path}")
    logger.info(f"Saved workflow results to {results_path}")




    def create_workflow(config: WorkflowConfig) -> FineTuningWorkflow:
    def create_workflow(config: WorkflowConfig) -> FineTuningWorkflow:
    """
    """
    Create a fine-tuning workflow.
    Create a fine-tuning workflow.


    Args:
    Args:
    config: Configuration for the workflow
    config: Configuration for the workflow


    Returns:
    Returns:
    Fine-tuning workflow
    Fine-tuning workflow
    """
    """
    return FineTuningWorkflow(config)
    return FineTuningWorkflow(config)




    def run_workflow(config: WorkflowConfig) -> Dict[str, Any]:
    def run_workflow(config: WorkflowConfig) -> Dict[str, Any]:
    """
    """
    Run a fine-tuning workflow.
    Run a fine-tuning workflow.


    Args:
    Args:
    config: Configuration for the workflow
    config: Configuration for the workflow


    Returns:
    Returns:
    Dictionary with workflow results
    Dictionary with workflow results
    """
    """
    workflow = create_workflow(config)
    workflow = create_workflow(config)
    return workflow.run()
    return workflow.run()




    def save_workflow(workflow: FineTuningWorkflow, path: str) -> str:
    def save_workflow(workflow: FineTuningWorkflow, path: str) -> str:
    """
    """
    Save a workflow configuration to disk.
    Save a workflow configuration to disk.


    Args:
    Args:
    workflow: Workflow to save
    workflow: Workflow to save
    path: Path to save the workflow
    path: Path to save the workflow


    Returns:
    Returns:
    Path to the saved workflow
    Path to the saved workflow
    """
    """
    # Create directory if it doesn't exist
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    os.makedirs(os.path.dirname(path), exist_ok=True)


    # Convert configuration to dictionary
    # Convert configuration to dictionary
    config_dict = {
    config_dict = {
    "name": workflow.config.name,
    "name": workflow.config.name,
    "output_dir": workflow.config.output_dir,
    "output_dir": workflow.config.output_dir,
    "steps": [step.value for step in workflow.config.steps],
    "steps": [step.value for step in workflow.config.steps],
    "metadata": workflow.config.metadata,
    "metadata": workflow.config.metadata,
    }
    }


    # Save configuration to file
    # Save configuration to file
    with open(path, "w", encoding="utf-8") as f:
    with open(path, "w", encoding="utf-8") as f:
    json.dump(config_dict, f, indent=2)
    json.dump(config_dict, f, indent=2)


    logger.info(f"Saved workflow configuration to {path}")
    logger.info(f"Saved workflow configuration to {path}")
    return path
    return path




    def load_workflow(path: str) -> FineTuningWorkflow:
    def load_workflow(path: str) -> FineTuningWorkflow:
    """
    """
    Load a workflow configuration from disk.
    Load a workflow configuration from disk.


    Args:
    Args:
    path: Path to the workflow configuration
    path: Path to the workflow configuration


    Returns:
    Returns:
    Fine-tuning workflow
    Fine-tuning workflow
    """
    """
    # Load configuration from file
    # Load configuration from file
    with open(path, "r", encoding="utf-8") as f:
    with open(path, "r", encoding="utf-8") as f:
    config_dict = json.load(f)
    config_dict = json.load(f)


    # Convert steps to enum
    # Convert steps to enum
    steps = []
    steps = []
    for step in config_dict.get("steps", []):
    for step in config_dict.get("steps", []):
    try:
    try:
    steps.append(WorkflowStep(step))
    steps.append(WorkflowStep(step))
except ValueError:
except ValueError:
    logger.warning(f"Unknown step: {step}, skipping")
    logger.warning(f"Unknown step: {step}, skipping")


    # Create configuration
    # Create configuration
    config = WorkflowConfig(
    config = WorkflowConfig(
    name=config_dict.get("name", "Loaded Workflow"),
    name=config_dict.get("name", "Loaded Workflow"),
    output_dir=config_dict.get("output_dir", "output"),
    output_dir=config_dict.get("output_dir", "output"),
    steps=steps,
    steps=steps,
    metadata=config_dict.get("metadata", {}),
    metadata=config_dict.get("metadata", {}),
    )
    )


    # Create workflow
    # Create workflow
    workflow = create_workflow(config)
    workflow = create_workflow(config)


    logger.info(f"Loaded workflow configuration from {path}")
    logger.info(f"Loaded workflow configuration from {path}")
    return workflow
    return workflow