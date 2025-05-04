"""
"""
Example usage of the model optimization utilities.
Example usage of the model optimization utilities.


This script demonstrates how to use the optimization utilities to quantize
This script demonstrates how to use the optimization utilities to quantize
and prune models for improved performance.
and prune models for improved performance.
"""
"""


try:
    try:
    import torch
    import torch
except ImportError:
except ImportError:
    pass
    pass




    import argparse
    import argparse
    import logging
    import logging
    import os
    import os
    import sys
    import sys
    import time
    import time


    import torch
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers import AutoModelForCausalLM, AutoTokenizer


    TRANSFORMERS_AVAILABLE
    TRANSFORMERS_AVAILABLE


    # Add the parent directory to the path to import the ai_models module
    # Add the parent directory to the path to import the ai_models module
    sys.path.append(
    sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    )


    from ai_models.optimization import (analyze_pruning,  # Quantization; Pruning
    from ai_models.optimization import (analyze_pruning,  # Quantization; Pruning
    analyze_quantization, prune_model,
    analyze_quantization, prune_model,
    quantize_model)
    quantize_model)


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


    # Try to import optional dependencies
    # Try to import optional dependencies
    try:
    try:




    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("PyTorch not available. Some examples will not work.")
    logger.warning("PyTorch not available. Some examples will not work.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning("Transformers not available. Some examples will not work.")
    logger.warning("Transformers not available. Some examples will not work.")
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False




    def test_quantization(
    def test_quantization(
    model_path: str, output_dir: str, method: str = "bitsandbytes-4bit", bits: int = 4
    model_path: str, output_dir: str, method: str = "bitsandbytes-4bit", bits: int = 4
    ) -> None:
    ) -> None:
    """
    """
    Test model quantization.
    Test model quantization.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_dir: Directory to save the quantized model
    output_dir: Directory to save the quantized model
    method: Quantization method
    method: Quantization method
    bits: Number of bits for quantization
    bits: Number of bits for quantization
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print(f"Testing {method.upper()} Quantization")
    print(f"Testing {method.upper()} Quantization")
    print("=" * 80)
    print("=" * 80)


    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    print("PyTorch and Transformers are required for quantization examples")
    print("PyTorch and Transformers are required for quantization examples")
    return # Create output directory
    return # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Determine output path
    # Determine output path
    output_path = os.path.join(output_dir, f"{method}-{bits}bit")
    output_path = os.path.join(output_dir, f"{method}-{bits}bit")


    try:
    try:
    # Quantize the model
    # Quantize the model
    print(f"Quantizing model {model_path} to {output_path}")
    print(f"Quantizing model {model_path} to {output_path}")
    start_time = time.time()
    start_time = time.time()


    quantized_path = quantize_model(
    quantized_path = quantize_model(
    model_path=model_path,
    model_path=model_path,
    output_path=output_path,
    output_path=output_path,
    method=method,
    method=method,
    bits=bits,
    bits=bits,
    model_type="text-generation",
    model_type="text-generation",
    )
    )


    elapsed_time = time.time() - start_time
    elapsed_time = time.time() - start_time
    print(f"Quantization completed in {elapsed_time:.2f} seconds")
    print(f"Quantization completed in {elapsed_time:.2f} seconds")
    print(f"Quantized model saved to {quantized_path}")
    print(f"Quantized model saved to {quantized_path}")


    # Analyze quantization effects
    # Analyze quantization effects
    print("\nAnalyzing quantization effects...")
    print("\nAnalyzing quantization effects...")
    analysis = analyze_quantization(
    analysis = analyze_quantization(
    original_model_path=model_path,
    original_model_path=model_path,
    quantized_model_path=quantized_path,
    quantized_model_path=quantized_path,
    num_samples=2,
    num_samples=2,
    max_tokens=50,
    max_tokens=50,
    )
    )


    # Print analysis results
    # Print analysis results
    print("\nQuantization Analysis:")
    print("\nQuantization Analysis:")
    print(f"Original model size: {analysis['original_model']['size_mb']:.2f} MB")
    print(f"Original model size: {analysis['original_model']['size_mb']:.2f} MB")
    print(f"Quantized model size: {analysis['pruned_model']['size_mb']:.2f} MB")
    print(f"Quantized model size: {analysis['pruned_model']['size_mb']:.2f} MB")
    print(
    print(
    f"Size reduction: {analysis['comparison']['size_reduction_percent']:.2f}%"
    f"Size reduction: {analysis['comparison']['size_reduction_percent']:.2f}%"
    )
    )
    print(
    print(
    f"Speed improvement: {analysis['comparison']['speed_improvement_percent']:.2f}%"
    f"Speed improvement: {analysis['comparison']['speed_improvement_percent']:.2f}%"
    )
    )
    print(f"Output similarity: {analysis['comparison']['output_similarity']:.4f}")
    print(f"Output similarity: {analysis['comparison']['output_similarity']:.4f}")


    # Print sample outputs
    # Print sample outputs
    print("\nSample Outputs:")
    print("\nSample Outputs:")
    for i, (prompt, orig, quant) in enumerate(
    for i, (prompt, orig, quant) in enumerate(
    zip(
    zip(
    analysis["prompts"],
    analysis["prompts"],
    analysis["original_model"]["outputs"],
    analysis["original_model"]["outputs"],
    analysis["pruned_model"]["outputs"],
    analysis["pruned_model"]["outputs"],
    )
    )
    ):
    ):
    print(f"\nPrompt {i+1}: {prompt}")
    print(f"\nPrompt {i+1}: {prompt}")
    print(f"Original: {orig[:100]}...")
    print(f"Original: {orig[:100]}...")
    print(f"Quantized: {quant[:100]}...")
    print(f"Quantized: {quant[:100]}...")


except Exception as e:
except Exception as e:
    print(f"Error during quantization: {e}")
    print(f"Error during quantization: {e}")




    def test_pruning(
    def test_pruning(
    model_path: str, output_dir: str, method: str = "magnitude", sparsity: float = 0.5
    model_path: str, output_dir: str, method: str = "magnitude", sparsity: float = 0.5
    ) -> None:
    ) -> None:
    """
    """
    Test model pruning.
    Test model pruning.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_dir: Directory to save the pruned model
    output_dir: Directory to save the pruned model
    method: Pruning method
    method: Pruning method
    sparsity: Target sparsity (0.0 to 1.0)
    sparsity: Target sparsity (0.0 to 1.0)
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print(f"Testing {method.upper()} Pruning")
    print(f"Testing {method.upper()} Pruning")
    print("=" * 80)
    print("=" * 80)


    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    print("PyTorch and Transformers are required for pruning examples")
    print("PyTorch and Transformers are required for pruning examples")
    return # Create output directory
    return # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Determine output path
    # Determine output path
    output_path = os.path.join(output_dir, f"{method}-{int(sparsity*100)}pct")
    output_path = os.path.join(output_dir, f"{method}-{int(sparsity*100)}pct")


    try:
    try:
    # Prune the model
    # Prune the model
    print(f"Pruning model {model_path} to {output_path}")
    print(f"Pruning model {model_path} to {output_path}")
    start_time = time.time()
    start_time = time.time()


    pruned_path = prune_model(
    pruned_path = prune_model(
    model_path=model_path,
    model_path=model_path,
    output_path=output_path,
    output_path=output_path,
    method=method,
    method=method,
    sparsity=sparsity,
    sparsity=sparsity,
    model_type="text-generation",
    model_type="text-generation",
    )
    )


    elapsed_time = time.time() - start_time
    elapsed_time = time.time() - start_time
    print(f"Pruning completed in {elapsed_time:.2f} seconds")
    print(f"Pruning completed in {elapsed_time:.2f} seconds")
    print(f"Pruned model saved to {pruned_path}")
    print(f"Pruned model saved to {pruned_path}")


    # Analyze pruning effects
    # Analyze pruning effects
    print("\nAnalyzing pruning effects...")
    print("\nAnalyzing pruning effects...")
    analysis = analyze_pruning(
    analysis = analyze_pruning(
    original_model_path=model_path,
    original_model_path=model_path,
    pruned_model_path=pruned_path,
    pruned_model_path=pruned_path,
    num_samples=2,
    num_samples=2,
    max_tokens=50,
    max_tokens=50,
    )
    )


    # Print analysis results
    # Print analysis results
    print("\nPruning Analysis:")
    print("\nPruning Analysis:")
    print(f"Original model size: {analysis['original_model']['size_mb']:.2f} MB")
    print(f"Original model size: {analysis['original_model']['size_mb']:.2f} MB")
    print(f"Original model sparsity: {analysis['original_model']['sparsity']:.4f}")
    print(f"Original model sparsity: {analysis['original_model']['sparsity']:.4f}")
    print(f"Pruned model size: {analysis['pruned_model']['size_mb']:.2f} MB")
    print(f"Pruned model size: {analysis['pruned_model']['size_mb']:.2f} MB")
    print(f"Pruned model sparsity: {analysis['pruned_model']['sparsity']:.4f}")
    print(f"Pruned model sparsity: {analysis['pruned_model']['sparsity']:.4f}")
    print(
    print(
    f"Size reduction: {analysis['comparison']['size_reduction_percent']:.2f}%"
    f"Size reduction: {analysis['comparison']['size_reduction_percent']:.2f}%"
    )
    )
    print(
    print(
    f"Sparsity increase: {analysis['comparison']['sparsity_increase_percent']:.2f}%"
    f"Sparsity increase: {analysis['comparison']['sparsity_increase_percent']:.2f}%"
    )
    )
    print(
    print(
    f"Speed improvement: {analysis['comparison']['speed_improvement_percent']:.2f}%"
    f"Speed improvement: {analysis['comparison']['speed_improvement_percent']:.2f}%"
    )
    )
    print(f"Output similarity: {analysis['comparison']['output_similarity']:.4f}")
    print(f"Output similarity: {analysis['comparison']['output_similarity']:.4f}")


    # Print sample outputs
    # Print sample outputs
    print("\nSample Outputs:")
    print("\nSample Outputs:")
    for i, (prompt, orig, pruned) in enumerate(
    for i, (prompt, orig, pruned) in enumerate(
    zip(
    zip(
    analysis["prompts"],
    analysis["prompts"],
    analysis["original_model"]["outputs"],
    analysis["original_model"]["outputs"],
    analysis["pruned_model"]["outputs"],
    analysis["pruned_model"]["outputs"],
    )
    )
    ):
    ):
    print(f"\nPrompt {i+1}: {prompt}")
    print(f"\nPrompt {i+1}: {prompt}")
    print(f"Original: {orig[:100]}...")
    print(f"Original: {orig[:100]}...")
    print(f"Pruned: {pruned[:100]}...")
    print(f"Pruned: {pruned[:100]}...")


except Exception as e:
except Exception as e:
    print(f"Error during pruning: {e}")
    print(f"Error during pruning: {e}")




    def main():
    def main():
    """
    """
    Main function to demonstrate the model optimization utilities.
    Main function to demonstrate the model optimization utilities.
    """
    """
    parser = argparse.ArgumentParser(description="Test model optimization utilities")
    parser = argparse.ArgumentParser(description="Test model optimization utilities")
    parser.add_argument(
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    "--model-path", type=str, required=True, help="Path to the model"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir",
    "--output-dir",
    type=str,
    type=str,
    default="optimized_models",
    default="optimized_models",
    help="Directory to save optimized models",
    help="Directory to save optimized models",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--optimization",
    "--optimization",
    type=str,
    type=str,
    choices=["quantization", "pruning", "all"],
    choices=["quantization", "pruning", "all"],
    default="all",
    default="all",
    help="Optimization to test",
    help="Optimization to test",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--quant-method",
    "--quant-method",
    type=str,
    type=str,
    choices=["bitsandbytes-4bit", "bitsandbytes-8bit", "awq", "gptq"],
    choices=["bitsandbytes-4bit", "bitsandbytes-8bit", "awq", "gptq"],
    default="bitsandbytes-4bit",
    default="bitsandbytes-4bit",
    help="Quantization method",
    help="Quantization method",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--quant-bits", type=int, default=4, help="Number of bits for quantization"
    "--quant-bits", type=int, default=4, help="Number of bits for quantization"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--prune-method",
    "--prune-method",
    type=str,
    type=str,
    choices=["magnitude", "structured"],
    choices=["magnitude", "structured"],
    default="magnitude",
    default="magnitude",
    help="Pruning method",
    help="Pruning method",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--prune-sparsity",
    "--prune-sparsity",
    type=float,
    type=float,
    default=0.5,
    default=0.5,
    help="Target sparsity for pruning (0.0 to 1.0)",
    help="Target sparsity for pruning (0.0 to 1.0)",
    )
    )


    args = parser.parse_args()
    args = parser.parse_args()


    if args.optimization == "quantization" or args.optimization == "all":
    if args.optimization == "quantization" or args.optimization == "all":
    test_quantization(
    test_quantization(
    model_path=args.model_path,
    model_path=args.model_path,
    output_dir=args.output_dir,
    output_dir=args.output_dir,
    method=args.quant_method,
    method=args.quant_method,
    bits=args.quant_bits,
    bits=args.quant_bits,
    )
    )


    if args.optimization == "pruning" or args.optimization == "all":
    if args.optimization == "pruning" or args.optimization == "all":
    test_pruning(
    test_pruning(
    model_path=args.model_path,
    model_path=args.model_path,
    output_dir=args.output_dir,
    output_dir=args.output_dir,
    method=args.prune_method,
    method=args.prune_method,
    sparsity=args.prune_sparsity,
    sparsity=args.prune_sparsity,
    )
    )




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()