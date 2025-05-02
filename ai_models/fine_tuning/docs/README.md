# Fine-Tuning Documentation

This directory contains comprehensive documentation for the fine-tuning module in the pAIssive_income project.

## Contents

- [Fine-Tuning Best Practices](fine_tuning_best_practices.md): Comprehensive guide to best practices for fine-tuning AI models
- [API Reference](api_reference.md): Detailed API documentation for the fine-tuning module
- [Examples](examples.md): Examples of how to use the fine-tuning module

## Quick Start

To get started with fine-tuning, follow these steps:

1. **Prepare your dataset**:
   ```python
   from ai_models.fine_tuning import DataCollectionConfig, DataCollector, DatasetFormat

   config = DataCollectionConfig(
       sources=["path/to/your/data.jsonl"],
       output_format=DatasetFormat.JSONL,
       output_path="prepared_dataset",
       validation_split=0.1,
       test_split=0.1
   )

   collector = DataCollector(config)
   dataset = collector.prepare()
   ```

2. **Fine-tune your model**:
   ```python
   from ai_models.fine_tuning import FineTuningConfig, FineTuningMethod, fine_tune_model

   config = FineTuningConfig(
       model_path="your/base/model",
       output_dir="fine_tuned_model",
       method=FineTuningMethod.LORA,
       dataset_path="prepared_dataset",
       num_train_epochs=3,
       learning_rate=2e-5
   )

   model_path = fine_tune_model(config)
   ```

3. **Evaluate your model**:
   ```python
   from ai_models.fine_tuning import EvaluationConfig, evaluate_model, EvaluationMetric

   results = evaluate_model(
       model_path="fine_tuned_model",
       dataset_path="prepared_dataset",
       metrics=[EvaluationMetric.PERPLEXITY, EvaluationMetric.ACCURACY],
       output_dir="evaluation_results"
   )
   ```

4. **Compare multiple models**:
   ```python
   from ai_models.fine_tuning import compare_models, generate_evaluation_report

   results = compare_models(
       model_paths=["model1", "model2", "model3"],
       dataset_path="prepared_dataset",
       metrics=["perplexity", "accuracy"],
       output_dir="comparison_results"
   )

   generate_evaluation_report(results, "comparison_report.md")
   ```

For more detailed information, refer to the [Fine-Tuning Best Practices](fine_tuning_best_practices.md) guide.
