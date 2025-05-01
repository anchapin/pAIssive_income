"""
Example usage of the model adapters.

This script demonstrates how to use the different model adapters
(Ollama, LM Studio, OpenAI-compatible, TensorRT) in the AI Models module.
"""

import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Add the parent directory to the path to import the ai_models module
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from ai_models.adapters import LMStudioAdapter, OllamaAdapter, OpenAICompatibleAdapter

# Try to import TensorRT adapter if available
try:
    from ai_models.adapters import TensorRTAdapter

    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_ollama_adapter(base_url: str, model_name: str, prompt: str) -> None:
    """
    Test the Ollama adapter.

    Args:
        base_url: Base URL of the Ollama API
        model_name: Name of the model to use
        prompt: Input prompt for text generation
    """
    print("\n" + "=" * 80)
    print("Testing Ollama Adapter")
    print("=" * 80)

    try:
        # Create Ollama adapter
        adapter = OllamaAdapter(base_url=base_url)

        # List available models
        models = adapter.list_models()
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"- {model['name']} ({model.get('size', 'Unknown')})")

        # Check if the specified model is available
        model_available = any(model["name"] == model_name for model in models)

        if not model_available:
            print(
                f"\nModel {model_name} not found. Please pull it with: ollama pull {model_name}"
            )
            return

        # Get model info
        model_info = adapter.get_model_info(model_name)
        print(f"\nModel info for {model_name}:")
        print(f"- Size: {model_info.get('size', 'Unknown')}")
        print(f"- Modified: {model_info.get('modified_at', 'Unknown')}")
        print(f"- Parameters: {model_info.get('parameters', 'Unknown')}")

        # Generate text
        print(f"\nGenerating text with {model_name} for prompt: {prompt}")
        response = adapter.generate_text(model_name, prompt)
        print(f"Response: {response}")

        # Chat with the model
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        print(f"\nChatting with {model_name}")
        response = adapter.chat(model_name, messages)
        print(f"Response: {response.get('message', {}).get('content', '')}")

        # Create embedding
        print(f"\nCreating embedding with {model_name} for text: {prompt}")
        try:
            embedding = adapter.create_embedding(model_name, prompt)
            print(f"Embedding dimensions: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        except Exception as e:
            print(f"Error creating embedding: {e}")

    except Exception as e:
        print(f"Error testing Ollama adapter: {e}")


def test_lmstudio_adapter(base_url: str, prompt: str) -> None:
    """
    Test the LM Studio adapter.

    Args:
        base_url: Base URL of the LM Studio API
        prompt: Input prompt for text generation
    """
    print("\n" + "=" * 80)
    print("Testing LM Studio Adapter")
    print("=" * 80)

    try:
        # Create LM Studio adapter
        adapter = LMStudioAdapter(base_url=base_url)

        # List available models
        models = adapter.list_models()
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"- {model['id']}")

        # If there are models, use the first one
        if models:
            model_id = models[0]["id"]

            # Generate completions
            print(f"\nGenerating completions with {model_id} for prompt: {prompt}")
            response = adapter.generate_completions(model_id, prompt)
            print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")

            # Generate chat completions
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
            print(f"\nGenerating chat completions with {model_id}")
            response = adapter.generate_chat_completions(model_id, messages)
            print(
                f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
            )

            # Create embeddings
            print(f"\nCreating embeddings with {model_id} for text: {prompt}")
            try:
                response = adapter.create_embeddings(model_id, prompt)
                embeddings = response.get("data", [{}])[0].get("embedding", [])
                print(f"Embedding dimensions: {len(embeddings)}")
                print(f"First 5 values: {embeddings[:5]}")
            except Exception as e:
                print(f"Error creating embeddings: {e}")
        else:
            print("\nNo models available in LM Studio")

    except Exception as e:
        print(f"Error testing LM Studio adapter: {e}")


def test_openai_compatible_adapter(base_url: str, api_key: str, prompt: str) -> None:
    """
    Test the OpenAI-compatible adapter.

    Args:
        base_url: Base URL of the API
        api_key: API key for authentication
        prompt: Input prompt for text generation
    """
    print("\n" + "=" * 80)
    print("Testing OpenAI-Compatible Adapter")
    print("=" * 80)

    try:
        # Create OpenAI-compatible adapter
        adapter = OpenAICompatibleAdapter(base_url=base_url, api_key=api_key)

        # List available models
        models = adapter.list_models()
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"- {model['id']}")

        # If there are models, use the first one
        if models:
            model_id = models[0]["id"]

            # Create a completion
            print(f"\nCreating completion with {model_id} for prompt: {prompt}")
            response = adapter.create_completion(model_id, prompt)
            print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")

            # Create a chat completion
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
            print(f"\nCreating chat completion with {model_id}")
            response = adapter.create_chat_completion(model_id, messages)
            print(
                f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
            )

            # Create embeddings
            print(f"\nCreating embeddings with {model_id} for text: {prompt}")
            try:
                response = adapter.create_embedding(model_id, prompt)
                embeddings = response.get("data", [{}])[0].get("embedding", [])
                print(f"Embedding dimensions: {len(embeddings)}")
                print(f"First 5 values: {embeddings[:5]}")
            except Exception as e:
                print(f"Error creating embeddings: {e}")
        else:
            print("\nNo models available")

    except Exception as e:
        print(f"Error testing OpenAI-compatible adapter: {e}")


def test_tensorrt_adapter(engine_path: str, tokenizer_path: str, prompt: str) -> None:
    """
    Test the TensorRT adapter.

    Args:
        engine_path: Path to the TensorRT engine file
        tokenizer_path: Path to the tokenizer
        prompt: Input prompt for text generation
    """
    if not TENSORRT_AVAILABLE:
        print("\n" + "=" * 80)
        print("TensorRT Adapter Not Available")
        print("=" * 80)
        print(
            "TensorRT or PyCUDA not available. Please install them to use the TensorRT adapter."
        )
        return

    print("\n" + "=" * 80)
    print("Testing TensorRT Adapter")
    print("=" * 80)

    try:
        # Check if engine file exists
        if not os.path.exists(engine_path):
            print(f"Engine file not found: {engine_path}")
            return

        # Create TensorRT adapter
        adapter = TensorRTAdapter(
            engine_path=engine_path,
            model_type="text-generation",
            tokenizer_path=tokenizer_path,
        )

        # Get metadata
        metadata = adapter.get_metadata()
        print("Engine Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # Generate text
        if adapter.tokenizer:
            print(f"\nGenerating text for prompt: {prompt}")
            output = adapter.generate_text(prompt)
            print(f"Output: {output}")
        else:
            print("\nTokenizer not available. Cannot generate text.")

    except Exception as e:
        print(f"Error testing TensorRT adapter: {e}")


def main():
    """
    Main function to demonstrate the model adapters.
    """
    parser = argparse.ArgumentParser(description="Test different model adapters")
    parser.add_argument(
        "--adapter",
        type=str,
        choices=["ollama", "lmstudio", "openai", "tensorrt"],
        help="Type of adapter to test",
    )
    parser.add_argument("--base-url", type=str, help="Base URL for the API")
    parser.add_argument("--model", type=str, help="Model name or ID")
    parser.add_argument("--api-key", type=str, help="API key for authentication")
    parser.add_argument(
        "--engine-path", type=str, help="Path to the TensorRT engine file"
    )
    parser.add_argument("--tokenizer-path", type=str, help="Path to the tokenizer")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Hello, world!",
        help="Input prompt for text generation",
    )

    args = parser.parse_args()

    # If no adapter is specified, show help
    if not args.adapter:
        parser.print_help()
        return

    # Test the specified adapter
    if args.adapter == "ollama":
        base_url = args.base_url or "http://localhost:11434"
        model_name = args.model or "llama2"
        test_ollama_adapter(base_url, model_name, args.prompt)

    elif args.adapter == "lmstudio":
        base_url = args.base_url or "http://localhost:1234/v1"
        test_lmstudio_adapter(base_url, args.prompt)

    elif args.adapter == "openai":
        base_url = args.base_url or "http://localhost:8000/v1"
        api_key = args.api_key or "sk-"
        test_openai_compatible_adapter(base_url, api_key, args.prompt)

    elif args.adapter == "tensorrt":
        if not args.engine_path:
            print("Error: --engine-path is required for TensorRT adapter")
            return

        if not args.tokenizer_path:
            print("Error: --tokenizer-path is required for TensorRT adapter")
            return

        test_tensorrt_adapter(args.engine_path, args.tokenizer_path, args.prompt)


if __name__ == "__main__":
    main()
