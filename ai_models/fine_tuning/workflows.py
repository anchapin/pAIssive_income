"""
Fine-tuning workflows for AI models.

This module provides tools for creating and running fine-tuning workflows,
including data collection, fine-tuning, and evaluation.
"""

import os
import json
import logging
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field

from datasets import Dataset, DatasetDict

from .data_collector import DataCollector, DataCollectionConfig, collect_data, prepare_dataset
from .fine_tuner import FineTuner, FineTuningConfig, fine_tune_model, resume_fine_tuning
from .evaluator import ModelEvaluator, EvaluationConfig, evaluate_model, compare_models

# Configure logger
logger = logging.getLogger(__name__)


class WorkflowStep(Enum):
    """
    Enum for workflow steps.
    """
    DATA_COLLECTION = "data_collection"
    FINE_TUNING = "fine_tuning"
    EVALUATION = "evaluation"
    COMPARISON = "comparison"


@dataclass
class WorkflowConfig:
    """
    Configuration for fine-tuning workflow.
    """
    # Workflow name and output directory
    name: str
    output_dir: str
    
    # Steps to include in the workflow
    steps: List[WorkflowStep] = field(default_factory=lambda: [
        WorkflowStep.DATA_COLLECTION,
        WorkflowStep.FINE_TUNING,
        WorkflowStep.EVALUATION
    ])
    
    # Data collection configuration
    data_collection_config: Optional[DataCollectionConfig] = None
    
    # Fine-tuning configuration
    fine_tuning_config: Optional[FineTuningConfig] = None
    
    # Evaluation configuration
    evaluation_config: Optional[EvaluationConfig] = None
    
    # Comparison configuration
    comparison_models: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validate and process the configuration after initialization.
        """
        # Convert string steps to enum if needed
        processed_steps = []
        for step in self.steps:
            if isinstance(step, str):
                try:
                    step = WorkflowStep(step)
                except ValueError:
                    logger.warning(f"Unknown step: {step}, skipping")
                    continue
            processed_steps.append(step)
        self.steps = processed_steps
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)


class FineTuningWorkflow:
    """
    Class for running fine-tuning workflows.
    """
    
    def __init__(self, config: WorkflowConfig):
        """
        Initialize the workflow.
        
        Args:
            config: Configuration for the workflow
        """
        self.config = config
        self.results = {}
        self.dataset = None
        self.model_path = None
    
    def run(self) -> Dict[str, Any]:
        """
        Run the workflow.
        
        Returns:
            Dictionary with workflow results
        """
        start_time = time.time()
        
        logger.info(f"Starting workflow: {self.config.name}")
        
        # Run each step in the workflow
        for step in self.config.steps:
            logger.info(f"Running step: {step.value}")
            
            if step == WorkflowStep.DATA_COLLECTION:
                self._run_data_collection()
            elif step == WorkflowStep.FINE_TUNING:
                self._run_fine_tuning()
            elif step == WorkflowStep.EVALUATION:
                self._run_evaluation()
            elif step == WorkflowStep.COMPARISON:
                self._run_comparison()
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Save workflow results
        self._save_results(total_time)
        
        logger.info(f"Workflow completed in {total_time:.2f} seconds")
        
        return self.results
    
    def _run_data_collection(self) -> None:
        """
        Run the data collection step.
        """
        if self.config.data_collection_config is None:
            logger.warning("No data collection configuration provided, skipping step")
            return
        
        try:
            logger.info("Collecting data")
            
            # Create data collector
            collector = DataCollector(self.config.data_collection_config)
            
            # Prepare dataset
            self.dataset = collector.prepare()
            
            # Export dataset
            dataset_path = os.path.join(self.config.output_dir, "dataset")
            self.dataset.save_to_disk(dataset_path)
            
            # Store results
            self.results["data_collection"] = {
                "dataset_path": dataset_path,
                "num_samples": {
                    "train": len(self.dataset["train"]),
                    "validation": len(self.dataset["validation"]),
                    "test": len(self.dataset["test"]) if "test" in self.dataset else 0
                }
            }
            
            logger.info(f"Data collection completed, dataset saved to {dataset_path}")
            
        except Exception as e:
            logger.error(f"Error in data collection step: {e}")
            self.results["data_collection"] = {"error": str(e)}
    
    def _run_fine_tuning(self) -> None:
        """
        Run the fine-tuning step.
        """
        if self.config.fine_tuning_config is None:
            logger.warning("No fine-tuning configuration provided, skipping step")
            return
        
        try:
            logger.info("Fine-tuning model")
            
            # Update fine-tuning configuration with dataset if available
            if self.dataset is not None and self.config.fine_tuning_config.dataset is None:
                self.config.fine_tuning_config.dataset = self.dataset
            
            # Create fine-tuner
            fine_tuner = FineTuner(self.config.fine_tuning_config)
            
            # Prepare for fine-tuning
            fine_tuner.prepare()
            
            # Train the model
            train_metrics = fine_tuner.train()
            
            # Save the model
            self.model_path = fine_tuner.save()
            
            # Store results
            self.results["fine_tuning"] = {
                "model_path": self.model_path,
                "train_metrics": train_metrics
            }
            
            logger.info(f"Fine-tuning completed, model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error in fine-tuning step: {e}")
            self.results["fine_tuning"] = {"error": str(e)}
    
    def _run_evaluation(self) -> None:
        """
        Run the evaluation step.
        """
        if self.config.evaluation_config is None:
            logger.warning("No evaluation configuration provided, skipping step")
            return
        
        if self.model_path is None and "fine_tuning" in self.results and "model_path" in self.results["fine_tuning"]:
            self.model_path = self.results["fine_tuning"]["model_path"]
        
        if self.model_path is None:
            logger.warning("No model path available for evaluation, skipping step")
            return
        
        try:
            logger.info(f"Evaluating model: {self.model_path}")
            
            # Update evaluation configuration with model path
            self.config.evaluation_config.model_path = self.model_path
            
            # Update evaluation configuration with dataset if available
            if self.dataset is not None and self.config.evaluation_config.dataset is None:
                self.config.evaluation_config.dataset = self.dataset
            
            # Create evaluator
            evaluator = ModelEvaluator(self.config.evaluation_config)
            
            # Evaluate model
            evaluation_results = evaluator.evaluate()
            
            # Visualize results
            if self.config.evaluation_config.output_dir:
                visualization_path = evaluator.visualize_results()
            else:
                visualization_path = None
            
            # Store results
            self.results["evaluation"] = {
                "results": evaluation_results,
                "visualization_path": visualization_path
            }
            
            logger.info("Evaluation completed")
            
        except Exception as e:
            logger.error(f"Error in evaluation step: {e}")
            self.results["evaluation"] = {"error": str(e)}
    
    def _run_comparison(self) -> None:
        """
        Run the comparison step.
        """
        if not self.config.comparison_models:
            logger.warning("No comparison models provided, skipping step")
            return
        
        if self.model_path is None and "fine_tuning" in self.results and "model_path" in self.results["fine_tuning"]:
            self.model_path = self.results["fine_tuning"]["model_path"]
        
        if self.model_path is None:
            logger.warning("No model path available for comparison, skipping step")
            return
        
        try:
            logger.info("Comparing models")
            
            # Add the fine-tuned model to the comparison list
            model_paths = [self.model_path] + self.config.comparison_models
            
            # Get dataset path
            dataset_path = None
            if self.dataset is not None:
                dataset_path = os.path.join(self.config.output_dir, "dataset")
                self.dataset.save_to_disk(dataset_path)
            elif "data_collection" in self.results and "dataset_path" in self.results["data_collection"]:
                dataset_path = self.results["data_collection"]["dataset_path"]
            
            if dataset_path is None:
                logger.warning("No dataset available for comparison, skipping step")
                return
            
            # Create output directory for comparison results
            comparison_dir = os.path.join(self.config.output_dir, "comparison")
            os.makedirs(comparison_dir, exist_ok=True)
            
            # Compare models
            comparison_results = compare_models(
                model_paths=model_paths,
                dataset_path=dataset_path,
                metrics=self.config.evaluation_config.metrics if self.config.evaluation_config else None,
                output_dir=comparison_dir
            )
            
            # Generate comparison report
            report_path = os.path.join(comparison_dir, "comparison_report.md")
            report_path = ModelEvaluator.generate_evaluation_report(
                results=comparison_results,
                output_path=report_path
            )
            
            # Store results
            self.results["comparison"] = {
                "results": comparison_results,
                "report_path": report_path
            }
            
            logger.info("Comparison completed")
            
        except Exception as e:
            logger.error(f"Error in comparison step: {e}")
            self.results["comparison"] = {"error": str(e)}
    
    def _save_results(self, total_time: float) -> None:
        """
        Save workflow results to disk.
        
        Args:
            total_time: Total time taken by the workflow
        """
        # Create results object
        workflow_results = {
            "name": self.config.name,
            "steps": [step.value for step in self.config.steps],
            "results": self.results,
            "metadata": self.config.metadata,
            "total_time": total_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save results to file
        results_path = os.path.join(self.config.output_dir, "workflow_results.json")
        
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(workflow_results, f, indent=2)
        
        logger.info(f"Saved workflow results to {results_path}")


def create_workflow(config: WorkflowConfig) -> FineTuningWorkflow:
    """
    Create a fine-tuning workflow.
    
    Args:
        config: Configuration for the workflow
        
    Returns:
        Fine-tuning workflow
    """
    return FineTuningWorkflow(config)


def run_workflow(config: WorkflowConfig) -> Dict[str, Any]:
    """
    Run a fine-tuning workflow.
    
    Args:
        config: Configuration for the workflow
        
    Returns:
        Dictionary with workflow results
    """
    workflow = create_workflow(config)
    return workflow.run()


def save_workflow(workflow: FineTuningWorkflow, path: str) -> str:
    """
    Save a workflow configuration to disk.
    
    Args:
        workflow: Workflow to save
        path: Path to save the workflow
        
    Returns:
        Path to the saved workflow
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Convert configuration to dictionary
    config_dict = {
        "name": workflow.config.name,
        "output_dir": workflow.config.output_dir,
        "steps": [step.value for step in workflow.config.steps],
        "metadata": workflow.config.metadata
    }
    
    # Save configuration to file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)
    
    logger.info(f"Saved workflow configuration to {path}")
    return path


def load_workflow(path: str) -> FineTuningWorkflow:
    """
    Load a workflow configuration from disk.
    
    Args:
        path: Path to the workflow configuration
        
    Returns:
        Fine-tuning workflow
    """
    # Load configuration from file
    with open(path, "r", encoding="utf-8") as f:
        config_dict = json.load(f)
    
    # Convert steps to enum
    steps = []
    for step in config_dict.get("steps", []):
        try:
            steps.append(WorkflowStep(step))
        except ValueError:
            logger.warning(f"Unknown step: {step}, skipping")
    
    # Create configuration
    config = WorkflowConfig(
        name=config_dict.get("name", "Loaded Workflow"),
        output_dir=config_dict.get("output_dir", "output"),
        steps=steps,
        metadata=config_dict.get("metadata", {})
    )
    
    # Create workflow
    workflow = create_workflow(config)
    
    logger.info(f"Loaded workflow configuration from {path}")
    return workflow
