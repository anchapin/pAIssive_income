"""
Fine-tuning module for AI models.

This module provides tools for fine-tuning AI models, including data collection,
fine-tuning workflows, evaluation, and model comparison.
"""

from .data_collector import (
    DataCollector, DataCollectionConfig, DatasetFormat,
    collect_data, prepare_dataset, export_dataset
)

from .fine_tuner import (
    FineTuner, FineTuningConfig, FineTuningMethod,
    fine_tune_model, resume_fine_tuning, stop_fine_tuning
)

from .evaluator import (
    ModelEvaluator, EvaluationConfig, EvaluationMetric,
    evaluate_model, compare_models, generate_evaluation_report
)

from .workflows import (
    FineTuningWorkflow, WorkflowConfig, WorkflowStep,
    create_workflow, run_workflow, save_workflow, load_workflow
)

__all__ = [
    # Data collection
    'DataCollector',
    'DataCollectionConfig',
    'DatasetFormat',
    'collect_data',
    'prepare_dataset',
    'export_dataset',
    
    # Fine-tuning
    'FineTuner',
    'FineTuningConfig',
    'FineTuningMethod',
    'fine_tune_model',
    'resume_fine_tuning',
    'stop_fine_tuning',
    
    # Evaluation
    'ModelEvaluator',
    'EvaluationConfig',
    'EvaluationMetric',
    'evaluate_model',
    'compare_models',
    'generate_evaluation_report',
    
    # Workflows
    'FineTuningWorkflow',
    'WorkflowConfig',
    'WorkflowStep',
    'create_workflow',
    'run_workflow',
    'save_workflow',
    'load_workflow'
]
