# Fine-Tuning Best Practices

This document provides comprehensive guidance on best practices for fine-tuning AI models in the pAIssive_income project. Following these guidelines will help you achieve better results with your fine-tuned models while optimizing resource usage and model performance.

## Table of Contents

1. [Data Collection and Preparation](#data-collection-and-preparation)
2. [Choosing the Right Fine-Tuning Method](#choosing-the-right-fine-tuning-method)
3. [Hyperparameter Selection](#hyperparameter-selection)
4. [Training Process](#training-process)
5. [Evaluation and Comparison](#evaluation-and-comparison)
6. [Optimization for Deployment](#optimization-for-deployment)
7. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
8. [Advanced Techniques](#advanced-techniques)

## Data Collection and Preparation

The quality and preparation of your training data are the most critical factors for successful fine-tuning.

### Data Quality Guidelines

- **Relevance**: Ensure your data is directly relevant to the target task. Irrelevant data can lead to poor performance or unexpected behaviors.
- **Diversity**: Include a diverse range of examples that cover the full spectrum of inputs your model will encounter in production.
- **Balance**: Maintain a balanced dataset that doesn't over-represent certain categories or patterns.
- **Accuracy**: Verify that your data is accurate and free from errors, as the model will learn from and potentially amplify any mistakes.
- **Consistency**: Maintain consistent formatting and structure throughout your dataset.

### Data Quantity Recommendations

| Model Size | Minimum Recommended Samples | Ideal Range |
|------------|----------------------------|-------------|
| Small (<1B parameters) | 500-1,000 | 1,000-5,000 |
| Medium (1B-10B parameters) | 1,000-2,000 | 2,000-10,000 |
| Large (>10B parameters) | 2,000-5,000 | 5,000-20,000+ |

### Data Preparation Steps

1. **Cleaning**:
   - Remove duplicate examples
   - Fix formatting issues
   - Correct errors in labels or responses
   - Normalize text (e.g., consistent capitalization, spacing)

2. **Formatting**:
   - Structure your data according to the model's expected format
   - For instruction-tuning, use a consistent format like:
     ```
     <instruction>
     Your instruction here
     </instruction>
     <response>
     The expected response
     </response>
     ```

3. **Splitting**:
   - Training set: 80-90% of your data
   - Validation set: 10-15% of your data
   - Test set: 5-10% of your data
   - Ensure each split has a representative distribution of your data

4. **Augmentation** (when appropriate):
   - Paraphrasing instructions or responses
   - Generating variations with different wording
   - Adding controlled noise to create robustness

### Using the DataCollector

Our `DataCollector` class provides tools for preparing your dataset:

```python
from ai_models.fine_tuning import DataCollectionConfig, DataCollector, DatasetFormat

# Create configuration
config = DataCollectionConfig(
    sources=["path/to/your/data.jsonl"],
    output_format=DatasetFormat.JSONL,
    output_path="prepared_dataset",
    shuffle=True,
    validation_split=0.1,
    test_split=0.1
)

# Create collector and prepare dataset
collector = DataCollector(config)
dataset = collector.prepare()

# Export the dataset
collector.export(dataset)
```

## Choosing the Right Fine-Tuning Method

Different fine-tuning methods are appropriate for different scenarios. Here's a guide to help you choose:

### Full Fine-Tuning

**When to use**:
- You have a large, high-quality dataset
- You need maximum performance
- You have sufficient computational resources
- The target task is significantly different from the model's pre-training

**Advantages**:
- Maximum adaptation to your task
- Best performance potential

**Disadvantages**:
- Requires significant computational resources
- Risk of catastrophic forgetting
- Longer training time

### Parameter-Efficient Fine-Tuning (PEFT)

#### LoRA (Low-Rank Adaptation)

**When to use**:
- Limited computational resources
- Need to fine-tune large models
- Want to maintain most of the model's general capabilities

**Advantages**:
- Much lower memory requirements
- Faster training
- Multiple adapters can be combined
- Preserves general knowledge

**Disadvantages**:
- Slightly lower performance than full fine-tuning
- May not adapt as well to drastically different tasks

#### QLoRA (Quantized LoRA)

**When to use**:
- Very limited computational resources
- Need to fine-tune very large models
- Consumer-grade hardware

**Advantages**:
- Extremely low memory requirements
- Can fine-tune large models on consumer hardware
- Preserves most performance

**Disadvantages**:
- Some performance degradation
- Slower inference if kept quantized

#### Prefix Tuning

**When to use**:
- Need to control the model's behavior without changing weights
- Want to easily switch between different behaviors

**Advantages**:
- Very parameter-efficient
- Easy to switch between different tasks
- Preserves original model capabilities

**Disadvantages**:
- Less effective for complex adaptations
- May require careful prompt engineering

### Method Selection Guide

| Scenario | Recommended Method | Alternative |
|----------|-------------------|------------|
| Limited GPU memory (<12GB) | QLoRA | Prefix Tuning |
| Medium GPU memory (12-24GB) | LoRA | QLoRA |
| High GPU memory (>24GB) | Full Fine-Tuning | LoRA |
| Multiple related tasks | LoRA with multiple adapters | Prefix Tuning |
| Slight domain adaptation | LoRA with low rank | Prefix Tuning |
| Complete task change | Full Fine-Tuning | LoRA with high rank |

## Hyperparameter Selection

Choosing the right hyperparameters is crucial for effective fine-tuning.

### General Hyperparameters

| Hyperparameter | Typical Range | Notes |
|----------------|--------------|-------|
| Learning Rate | 1e-5 to 5e-5 | Smaller for larger models |
| Batch Size | 1 to 8 | Limited by GPU memory |
| Training Epochs | 2 to 5 | More for smaller datasets |
| Weight Decay | 0.01 to 0.1 | Helps prevent overfitting |
| Warmup Steps | 10% of total steps | Helps stabilize training |

### LoRA-Specific Hyperparameters

| Hyperparameter | Typical Range | Notes |
|----------------|--------------|-------|
| LoRA Rank (r) | 4 to 32 | Higher for more complex tasks |
| LoRA Alpha | 16 to 64 | Usually 2x the rank |
| Target Modules | ["q_proj", "v_proj"] | Model-dependent |
| LoRA Dropout | 0.05 to 0.1 | Helps prevent overfitting |

### QLoRA-Specific Hyperparameters

| Hyperparameter | Typical Range | Notes |
|----------------|--------------|-------|
| Quantization Bits | 4 or 8 | 4-bit for maximum memory savings |
| Quantization Method | "nf4" or "fp4" | "nf4" often works better |
| Double Quantization | True | Further reduces memory usage |

### Recommended Starting Points

For a balanced approach, start with:

```python
from ai_models.fine_tuning import FineTuningConfig, FineTuningMethod

config = FineTuningConfig(
    model_path="your/base/model",
    output_dir="fine_tuned_model",
    method=FineTuningMethod.LORA,
    
    # Dataset parameters
    dataset_path="your/dataset/path",
    
    # Training parameters
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_steps=100,
    
    # LoRA parameters
    lora_r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    lora_target_modules=["q_proj", "v_proj"],
    
    # Early stopping
    early_stopping_patience=3
)
```

## Training Process

### Monitoring Training

Effective monitoring during training helps catch issues early and optimize results.

**Key Metrics to Monitor**:
- **Training Loss**: Should steadily decrease
- **Validation Loss**: Should decrease without diverging from training loss
- **Learning Rate**: Track how it changes with schedulers
- **Gradient Norms**: Can indicate training stability

### Early Stopping

Implement early stopping to prevent overfitting:

```python
# Early stopping is built into our FineTuner
config = FineTuningConfig(
    # ... other parameters ...
    early_stopping_patience=3  # Stop if no improvement for 3 evaluations
)
```

### Checkpointing

Save checkpoints regularly to resume training if interrupted:

```python
# Checkpointing is handled automatically by our FineTuner
config = FineTuningConfig(
    # ... other parameters ...
    save_strategy="steps",
    save_steps=500
)
```

### Handling Training Issues

| Issue | Signs | Solution |
|-------|-------|----------|
| Overfitting | Validation loss increases while training loss decreases | Increase regularization, reduce model size, add more data |
| Underfitting | Both losses plateau at high values | Train longer, increase model capacity, reduce regularization |
| Unstable Training | Loss spikes or NaN values | Reduce learning rate, check for data issues, use gradient clipping |
| Memory Issues | OOM errors | Reduce batch size, use gradient accumulation, switch to QLoRA |

## Evaluation and Comparison

Thorough evaluation is essential to understand your model's performance.

### Key Evaluation Metrics

| Metric | Use Case | Interpretation |
|--------|----------|---------------|
| Perplexity | Language modeling | Lower is better; measures prediction quality |
| Accuracy | Classification | Higher is better; percentage of correct predictions |
| ROUGE | Summarization | Higher is better; measures summary quality |
| BLEU | Translation | Higher is better; measures translation quality |
| F1 Score | Information extraction | Higher is better; balance of precision and recall |

### Evaluation Best Practices

1. **Use a Dedicated Test Set**: Evaluate on data not seen during training
2. **Compare to Baseline**: Always compare to the base model
3. **Evaluate on Multiple Metrics**: Different metrics capture different aspects
4. **Human Evaluation**: Supplement automatic metrics with human judgment
5. **Real-world Testing**: Test in scenarios similar to production

### Using the ModelEvaluator

Our `ModelEvaluator` class provides tools for comprehensive evaluation:

```python
from ai_models.fine_tuning import EvaluationConfig, ModelEvaluator, EvaluationMetric

# Create configuration
config = EvaluationConfig(
    model_path="your/fine_tuned/model",
    dataset_path="your/test/dataset",
    metrics=[EvaluationMetric.PERPLEXITY, EvaluationMetric.ACCURACY],
    output_dir="evaluation_results"
)

# Create evaluator and evaluate
evaluator = ModelEvaluator(config)
results = evaluator.evaluate()

# Visualize results
evaluator.visualize_results()
```

### Comparing Multiple Models

To compare different fine-tuning approaches:

```python
from ai_models.fine_tuning import compare_models, generate_evaluation_report

# Compare models
results = compare_models(
    model_paths=["model1", "model2", "model3"],
    dataset_path="test_dataset",
    metrics=["perplexity", "accuracy"],
    output_dir="comparison_results"
)

# Generate report
generate_evaluation_report(results, "comparison_report.md")
```

## Optimization for Deployment

After fine-tuning, optimize your model for deployment.

### Quantization

Reduce model size and increase inference speed:

```python
from ai_models.optimization import quantize_model, QuantizationConfig, QuantizationMethod

# Quantize model
quantized_model_path = quantize_model(
    model_path="your/fine_tuned/model",
    output_dir="quantized_model",
    config=QuantizationConfig(
        method=QuantizationMethod.BITSANDBYTES,
        bits=4
    )
)
```

### Pruning

Remove unnecessary weights to reduce size:

```python
from ai_models.optimization import prune_model, PruningConfig, PruningMethod

# Prune model
pruned_model_path = prune_model(
    model_path="your/fine_tuned/model",
    output_dir="pruned_model",
    config=PruningConfig(
        method=PruningMethod.MAGNITUDE,
        target_sparsity=0.3
    )
)
```

### Distillation

Create a smaller model that mimics your fine-tuned model:

```python
# Distillation implementation to be added in future updates
```

### Deployment Considerations

- **Memory Usage**: Balance between model size and performance
- **Latency Requirements**: Consider batch processing for throughput
- **Scaling**: Plan for increased usage with load balancing
- **Monitoring**: Implement performance tracking in production

## Common Pitfalls and Solutions

| Pitfall | Signs | Solution |
|---------|-------|----------|
| Catastrophic Forgetting | Model loses general capabilities | Use PEFT methods like LoRA instead of full fine-tuning |
| Data Leakage | Unrealistically good performance | Ensure strict separation between train/validation/test sets |
| Overfitting to Quirks | Model learns dataset artifacts | Increase data diversity, use regularization |
| Training Instability | Loss spikes, NaN values | Reduce learning rate, use gradient clipping |
| Poor Generalization | Works on test set but fails in production | Test on diverse, real-world examples |

## Advanced Techniques

### Instruction Tuning

Fine-tune models to follow instructions:

1. Format data as instruction-response pairs
2. Include diverse instruction types
3. Use consistent formatting
4. Include system prompts if applicable

### Chain-of-Thought Fine-Tuning

Improve reasoning capabilities:

1. Include intermediate reasoning steps in responses
2. Format as: instruction → reasoning → answer
3. Ensure reasoning is explicit and logical

### Reinforcement Learning from Human Feedback (RLHF)

Advanced technique for aligning with human preferences:

1. Fine-tune a base model with supervised learning
2. Collect human preference data
3. Train a reward model
4. Use reinforcement learning to optimize the model

Note: RLHF implementation will be added in future updates.

### Continual Learning

Keep improving your model over time:

1. Collect new data from production
2. Periodically fine-tune on combined old and new data
3. Implement A/B testing for new model versions
4. Monitor for performance regression

## Conclusion

Fine-tuning is both an art and a science. These best practices provide a foundation, but don't hesitate to experiment and adapt them to your specific use case. Document your experiments, learn from both successes and failures, and iterate to achieve the best results.

For more detailed information, refer to the API documentation for the fine-tuning module and the example scripts in the `ai_models/examples` directory.
