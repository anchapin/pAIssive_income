#!/usr/bin/env python3
"""
Example script demonstrating asynchronous model inference with the AI Models module.

This script shows how to use the asynchronous processing features of the AI Models module
to perform parallel inference with AI models, improving throughput for batch processing.
"""

import asyncio
import logging
import os
import sys
import time

# Add the parent directory to the path so we can import from ai_models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai_models import ModelInfo, ModelManager
from ai_models.async_utils import (
    AsyncModelProcessor,
    run_in_thread,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def example_batch_text_generation():
    """
    Example of batch text generation using asynchronous processing.
    """
    print("\n=== Batch Text Generation Example ===")

    # Initialize the model manager
    manager = ModelManager()

    # Create an async model processor
    processor = AsyncModelProcessor(manager)

    # Get available models
    models = manager.get_all_models()

    # Find a text generation model
    text_model_id = None
    for model in models:
        if model.type == "huggingface" or "text-generation" in model.capabilities:
            text_model_id = model.id
            break

    if not text_model_id:
        print("No text generation model found. Creating a default example model.")
        # Register a Hugging Face model
        model_info = ModelInfo(
            id="example-model",
            name="GPT-2",
            type="huggingface",
            path="gpt2",
            description="Example text generation model",
        )
        manager.register_model(model_info)
        text_model_id = model_info.id

    # Prepare a batch of prompts
    prompts = [
        "The future of artificial intelligence is",
        "Climate change solutions include",
        "Space exploration in the next decade will focus on",
        "The most important technological breakthroughs will be in",
        "Renewable energy sources that will dominate are",
    ]

    print(f"Processing {len(prompts)} prompts in parallel using model ID: {text_model_id}")

    # Generate text for all prompts in parallel
    start_time = time.time()
    results = await processor.generate_text_batch(
        model_id=text_model_id,
        prompts=prompts,
        concurrency=5,  # Process all prompts in parallel
        max_tokens=50,  # Generate 50 tokens per prompt
        temperature=0.7,  # Set temperature
    )
    total_time = time.time() - start_time

    # Print results
    print(f"\nCompleted batch processing in {total_time:.2f} seconds")
    print("\nResults:")
    for i, (prompt, result) in enumerate(zip(prompts, results)):
        print(f"\nPrompt {i+1}: {prompt}")
        if result.is_success:
            print(f"Response: {result.result}")
            print(f"Processing time: {result.processing_time:.2f} seconds")
        else:
            print(f"Error: {result.error}")

    return results


async def example_batch_embeddings():
    """
    Example of batch embedding generation using asynchronous processing.
    """
    print("\n=== Batch Embedding Generation Example ===")

    # Initialize the model manager
    manager = ModelManager()

    # Create an async model processor
    processor = AsyncModelProcessor(manager)

    # Get available models
    models = manager.get_all_models()

    # Find an embedding model
    embedding_model_id = None
    for model in models:
        if model.type == "embedding" or "embedding" in model.capabilities:
            embedding_model_id = model.id
            break

    if not embedding_model_id:
        print("No embedding model found. Creating a default example model.")
        # Register an embedding model
        model_info = ModelInfo(
            id="example-embedding-model",
            name="MiniLM",
            type="embedding",
            path="all-MiniLM-L6-v2",
            description="Example embedding model",
        )
        manager.register_model(model_info)
        embedding_model_id = model_info.id

    # Prepare a batch of texts
    texts = [
        "Artificial intelligence is transforming industries",
        "Machine learning enables data-driven decision making",
        "Neural networks model complex relationships in data",
        "Deep learning has revolutionized computer vision",
        "Transformers have advanced natural language processing",
    ]

    print(f"Generating embeddings for {len(texts)} texts using model ID: {embedding_model_id}")

    try:
        # Generate embeddings for all texts in parallel
        start_time = time.time()
        results = await processor.generate_embeddings_batch(
            model_id=embedding_model_id,
            texts=texts,
            concurrency=5,  # Process all texts in parallel
        )
        total_time = time.time() - start_time

        # Print results
        print(f"\nCompleted batch embedding generation in {total_time:.2f} seconds")
        print("\nResults:")
        for i, (text, result) in enumerate(zip(texts, results)):
            print(f"\nText {i+1}: {text[:30]}...")
            if result.is_success:
                embeddings = result.result
                print(f"Embedding dimensions: {len(embeddings)}")
                print(f"First 5 values: {embeddings[:5]}")
                print(f"Processing time: {result.processing_time:.2f} seconds")
            else:
                print(f"Error: {result.error}")

    except Exception as e:
        print(f"Error generating embeddings: {e}")

    return results


async def compare_sync_vs_async_batch():
    """
    Compare synchronous vs asynchronous batch processing.
    """
    print("\n=== Synchronous vs Asynchronous Batch Processing Comparison ===")

    # Initialize the model manager
    manager = ModelManager()

    # Create an async model processor
    processor = AsyncModelProcessor(manager)

    # Get available models
    models = manager.get_all_models()

    # Find a text generation model
    text_model_id = None
    for model in models:
        if model.type == "huggingface" or "text-generation" in model.capabilities:
            text_model_id = model.id
            break

    if not text_model_id:
        print("No text generation model found. Creating a default example model.")
        # Register a Hugging Face model
        model_info = ModelInfo(
            id="example-model",
            name="GPT-2",
            type="huggingface",
            path="gpt2",
            description="Example text generation model",
        )
        manager.register_model(model_info)
        text_model_id = model_info.id

    # Load the model
    model = await run_in_thread(manager.load_model, text_model_id)

    # Prepare a batch of prompts
    prompts = [
        "The future of artificial intelligence is",
        "Climate change solutions include",
        "Space exploration in the next decade will focus on",
        "The most important technological breakthroughs will be in",
        "Renewable energy sources that will dominate are",
    ]

    # Synchronous processing
    print("\nRunning synchronous batch processing...")
    sync_start_time = time.time()

    sync_results = []
    for prompt in prompts:
        try:
            start = time.time()
            if hasattr(model, "generate_text"):
                result = model.generate_text(prompt, max_tokens=50, temperature=0.7)
            else:
                # Try different method names for different model types
                if hasattr(model, "generate"):
                    result = model.generate(prompt, max_tokens=50, temperature=0.7)
                else:
                    result = "Model does not support text generation"

            processing_time = time.time() - start
            sync_results.append(
                {"prompt": prompt, "result": result, "processing_time": processing_time}
            )
        except Exception as e:
            sync_results.append(
                {
                    "prompt": prompt,
                    "error": str(e),
                    "processing_time": time.time() - start,
                }
            )

    sync_total_time = time.time() - sync_start_time

    # Asynchronous processing
    print("\nRunning asynchronous batch processing...")
    async_start_time = time.time()

    async_results = await processor.generate_text_batch(
        model_id=text_model_id,
        prompts=prompts,
        concurrency=5,  # Process all prompts in parallel
        max_tokens=50,
        temperature=0.7,
    )

    async_total_time = time.time() - async_start_time

    # Print comparison
    print("\nPerformance Comparison:")
    print(f"Synchronous processing total time: {sync_total_time:.2f} seconds")
    print(f"Asynchronous processing total time: {async_total_time:.2f} seconds")
    print(f"Speedup factor: {sync_total_time / async_total_time:.2f}x")

    # Print individual results
    print("\nSynchronous Results:")
    for i, result in enumerate(sync_results):
        print(f"\nPrompt {i+1}: {result['prompt']}")
        if "error" not in result:
            print(f"Response: {result['result']}")
            print(f"Processing time: {result['processing_time']:.2f} seconds")
        else:
            print(f"Error: {result['error']}")

    print("\nAsynchronous Results:")
    for i, (prompt, result) in enumerate(zip(prompts, async_results)):
        print(f"\nPrompt {i+1}: {prompt}")
        if result.is_success:
            print(f"Response: {result.result}")
            print(f"Processing time: {result.processing_time:.2f} seconds")
        else:
            print(f"Error: {result.error}")


async def main():
    """
    Run the examples.
    """
    print("Asynchronous Model Inference Examples")
    print("====================================")

    # Run the examples
    await example_batch_text_generation()
    await example_batch_embeddings()
    await compare_sync_vs_async_batch()


if __name__ == "__main__":
    asyncio.run(main())
