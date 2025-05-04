"""
"""
Example usage of the model adapters.
Example usage of the model adapters.


This script demonstrates how to use the different model adapters
This script demonstrates how to use the different model adapters
(Ollama, LM Studio, OpenAI-compatible, TensorRT) in the AI Models module.
(Ollama, LM Studio, OpenAI-compatible, TensorRT) in the AI Models module.
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


from ai_models.adapters import (LMStudioAdapter, OllamaAdapter,
from ai_models.adapters import (LMStudioAdapter, OllamaAdapter,
OpenAICompatibleAdapter, TensorRTAdapter)
OpenAICompatibleAdapter, TensorRTAdapter)


TENSORRT_AVAILABLE
TENSORRT_AVAILABLE


# Add the parent directory to the path to import the ai_models module
# Add the parent directory to the path to import the ai_models module
sys.path.append(
sys.path.append(
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
)
# Try to import TensorRT adapter if available
# Try to import TensorRT adapter if available
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    TENSORRT_AVAILABLE = False
    TENSORRT_AVAILABLE = False


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




    def test_ollama_adapter(base_url: str, model_name: str, prompt: str) -> None:
    def test_ollama_adapter(base_url: str, model_name: str, prompt: str) -> None:
    """
    """
    Test the Ollama adapter.
    Test the Ollama adapter.


    Args:
    Args:
    base_url: Base URL of the Ollama API
    base_url: Base URL of the Ollama API
    model_name: Name of the model to use
    model_name: Name of the model to use
    prompt: Input prompt for text generation
    prompt: Input prompt for text generation
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing Ollama Adapter")
    print("Testing Ollama Adapter")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create Ollama adapter
    # Create Ollama adapter
    adapter = OllamaAdapter(base_url=base_url)
    adapter = OllamaAdapter(base_url=base_url)


    # List available models
    # List available models
    models = adapter.list_models()
    models = adapter.list_models()
    print(f"Available models: {len(models)}")
    print(f"Available models: {len(models)}")
    for model in models:
    for model in models:
    print(f"- {model['name']} ({model.get('size', 'Unknown')})")
    print(f"- {model['name']} ({model.get('size', 'Unknown')})")


    # Check if the specified model is available
    # Check if the specified model is available
    model_available = any(model["name"] == model_name for model in models)
    model_available = any(model["name"] == model_name for model in models)


    if not model_available:
    if not model_available:
    print(
    print(
    f"\nModel {model_name} not found. Please pull it with: ollama pull {model_name}"
    f"\nModel {model_name} not found. Please pull it with: ollama pull {model_name}"
    )
    )
    return # Get model info
    return # Get model info
    model_info = adapter.get_model_info(model_name)
    model_info = adapter.get_model_info(model_name)
    print(f"\nModel info for {model_name}:")
    print(f"\nModel info for {model_name}:")
    print(f"- Size: {model_info.get('size', 'Unknown')}")
    print(f"- Size: {model_info.get('size', 'Unknown')}")
    print(f"- Modified: {model_info.get('modified_at', 'Unknown')}")
    print(f"- Modified: {model_info.get('modified_at', 'Unknown')}")
    print(f"- Parameters: {model_info.get('parameters', 'Unknown')}")
    print(f"- Parameters: {model_info.get('parameters', 'Unknown')}")


    # Generate text
    # Generate text
    print(f"\nGenerating text with {model_name} for prompt: {prompt}")
    print(f"\nGenerating text with {model_name} for prompt: {prompt}")
    response = adapter.generate_text(model_name, prompt)
    response = adapter.generate_text(model_name, prompt)
    print(f"Response: {response}")
    print(f"Response: {response}")


    # Chat with the model
    # Chat with the model
    messages = [
    messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
    {"role": "user", "content": prompt},
    ]
    ]
    print(f"\nChatting with {model_name}")
    print(f"\nChatting with {model_name}")
    response = adapter.chat(model_name, messages)
    response = adapter.chat(model_name, messages)
    print(f"Response: {response.get('message', {}).get('content', '')}")
    print(f"Response: {response.get('message', {}).get('content', '')}")


    # Create embedding
    # Create embedding
    print(f"\nCreating embedding with {model_name} for text: {prompt}")
    print(f"\nCreating embedding with {model_name} for text: {prompt}")
    try:
    try:
    embedding = adapter.create_embedding(model_name, prompt)
    embedding = adapter.create_embedding(model_name, prompt)
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"First 5 values: {embedding[:5]}")
except Exception as e:
except Exception as e:
    print(f"Error creating embedding: {e}")
    print(f"Error creating embedding: {e}")


except Exception as e:
except Exception as e:
    print(f"Error testing Ollama adapter: {e}")
    print(f"Error testing Ollama adapter: {e}")




    def test_lmstudio_adapter(base_url: str, prompt: str) -> None:
    def test_lmstudio_adapter(base_url: str, prompt: str) -> None:
    """
    """
    Test the LM Studio adapter.
    Test the LM Studio adapter.


    Args:
    Args:
    base_url: Base URL of the LM Studio API
    base_url: Base URL of the LM Studio API
    prompt: Input prompt for text generation
    prompt: Input prompt for text generation
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing LM Studio Adapter")
    print("Testing LM Studio Adapter")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create LM Studio adapter
    # Create LM Studio adapter
    adapter = LMStudioAdapter(base_url=base_url)
    adapter = LMStudioAdapter(base_url=base_url)


    # List available models
    # List available models
    models = adapter.list_models()
    models = adapter.list_models()
    print(f"Available models: {len(models)}")
    print(f"Available models: {len(models)}")
    for model in models:
    for model in models:
    print(f"- {model['id']}")
    print(f"- {model['id']}")


    # If there are models, use the first one
    # If there are models, use the first one
    if models:
    if models:
    model_id = models[0]["id"]
    model_id = models[0]["id"]


    # Generate completions
    # Generate completions
    print(f"\nGenerating completions with {model_id} for prompt: {prompt}")
    print(f"\nGenerating completions with {model_id} for prompt: {prompt}")
    response = adapter.generate_completions(model_id, prompt)
    response = adapter.generate_completions(model_id, prompt)
    print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")
    print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")


    # Generate chat completions
    # Generate chat completions
    messages = [
    messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
    {"role": "user", "content": prompt},
    ]
    ]
    print(f"\nGenerating chat completions with {model_id}")
    print(f"\nGenerating chat completions with {model_id}")
    response = adapter.generate_chat_completions(model_id, messages)
    response = adapter.generate_chat_completions(model_id, messages)
    print(
    print(
    f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
    f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
    )
    )


    # Create embeddings
    # Create embeddings
    print(f"\nCreating embeddings with {model_id} for text: {prompt}")
    print(f"\nCreating embeddings with {model_id} for text: {prompt}")
    try:
    try:
    response = adapter.create_embeddings(model_id, prompt)
    response = adapter.create_embeddings(model_id, prompt)
    embeddings = response.get("data", [{}])[0].get("embedding", [])
    embeddings = response.get("data", [{}])[0].get("embedding", [])
    print(f"Embedding dimensions: {len(embeddings)}")
    print(f"Embedding dimensions: {len(embeddings)}")
    print(f"First 5 values: {embeddings[:5]}")
    print(f"First 5 values: {embeddings[:5]}")
except Exception as e:
except Exception as e:
    print(f"Error creating embeddings: {e}")
    print(f"Error creating embeddings: {e}")
    else:
    else:
    print("\nNo models available in LM Studio")
    print("\nNo models available in LM Studio")


except Exception as e:
except Exception as e:
    print(f"Error testing LM Studio adapter: {e}")
    print(f"Error testing LM Studio adapter: {e}")




    def test_openai_compatible_adapter(base_url: str, api_key: str, prompt: str) -> None:
    def test_openai_compatible_adapter(base_url: str, api_key: str, prompt: str) -> None:
    """
    """
    Test the OpenAI-compatible adapter.
    Test the OpenAI-compatible adapter.


    Args:
    Args:
    base_url: Base URL of the API
    base_url: Base URL of the API
    api_key: API key for authentication
    api_key: API key for authentication
    prompt: Input prompt for text generation
    prompt: Input prompt for text generation
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing OpenAI-Compatible Adapter")
    print("Testing OpenAI-Compatible Adapter")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create OpenAI-compatible adapter
    # Create OpenAI-compatible adapter
    adapter = OpenAICompatibleAdapter(base_url=base_url, api_key=api_key)
    adapter = OpenAICompatibleAdapter(base_url=base_url, api_key=api_key)


    # List available models
    # List available models
    models = adapter.list_models()
    models = adapter.list_models()
    print(f"Available models: {len(models)}")
    print(f"Available models: {len(models)}")
    for model in models:
    for model in models:
    print(f"- {model['id']}")
    print(f"- {model['id']}")


    # If there are models, use the first one
    # If there are models, use the first one
    if models:
    if models:
    model_id = models[0]["id"]
    model_id = models[0]["id"]


    # Create a completion
    # Create a completion
    print(f"\nCreating completion with {model_id} for prompt: {prompt}")
    print(f"\nCreating completion with {model_id} for prompt: {prompt}")
    response = adapter.create_completion(model_id, prompt)
    response = adapter.create_completion(model_id, prompt)
    print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")
    print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")


    # Create a chat completion
    # Create a chat completion
    messages = [
    messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
    {"role": "user", "content": prompt},
    ]
    ]
    print(f"\nCreating chat completion with {model_id}")
    print(f"\nCreating chat completion with {model_id}")
    response = adapter.create_chat_completion(model_id, messages)
    response = adapter.create_chat_completion(model_id, messages)
    print(
    print(
    f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
    f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
    )
    )


    # Create embeddings
    # Create embeddings
    print(f"\nCreating embeddings with {model_id} for text: {prompt}")
    print(f"\nCreating embeddings with {model_id} for text: {prompt}")
    try:
    try:
    response = adapter.create_embedding(model_id, prompt)
    response = adapter.create_embedding(model_id, prompt)
    embeddings = response.get("data", [{}])[0].get("embedding", [])
    embeddings = response.get("data", [{}])[0].get("embedding", [])
    print(f"Embedding dimensions: {len(embeddings)}")
    print(f"Embedding dimensions: {len(embeddings)}")
    print(f"First 5 values: {embeddings[:5]}")
    print(f"First 5 values: {embeddings[:5]}")
except Exception as e:
except Exception as e:
    print(f"Error creating embeddings: {e}")
    print(f"Error creating embeddings: {e}")
    else:
    else:
    print("\nNo models available")
    print("\nNo models available")


except Exception as e:
except Exception as e:
    print(f"Error testing OpenAI-compatible adapter: {e}")
    print(f"Error testing OpenAI-compatible adapter: {e}")




    def test_tensorrt_adapter(engine_path: str, tokenizer_path: str, prompt: str) -> None:
    def test_tensorrt_adapter(engine_path: str, tokenizer_path: str, prompt: str) -> None:
    """
    """
    Test the TensorRT adapter.
    Test the TensorRT adapter.


    Args:
    Args:
    engine_path: Path to the TensorRT engine file
    engine_path: Path to the TensorRT engine file
    tokenizer_path: Path to the tokenizer
    tokenizer_path: Path to the tokenizer
    prompt: Input prompt for text generation
    prompt: Input prompt for text generation
    """
    """
    if not TENSORRT_AVAILABLE:
    if not TENSORRT_AVAILABLE:
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("TensorRT Adapter Not Available")
    print("TensorRT Adapter Not Available")
    print("=" * 80)
    print("=" * 80)
    print(
    print(
    "TensorRT or PyCUDA not available. Please install them to use the TensorRT adapter."
    "TensorRT or PyCUDA not available. Please install them to use the TensorRT adapter."
    )
    )
    return print("\n" + "=" * 80)
    return print("\n" + "=" * 80)
    print("Testing TensorRT Adapter")
    print("Testing TensorRT Adapter")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Check if engine file exists
    # Check if engine file exists
    if not os.path.exists(engine_path):
    if not os.path.exists(engine_path):
    print(f"Engine file not found: {engine_path}")
    print(f"Engine file not found: {engine_path}")
    return # Create TensorRT adapter
    return # Create TensorRT adapter
    adapter = TensorRTAdapter(
    adapter = TensorRTAdapter(
    engine_path=engine_path,
    engine_path=engine_path,
    model_type="text-generation",
    model_type="text-generation",
    tokenizer_path=tokenizer_path,
    tokenizer_path=tokenizer_path,
    )
    )


    # Get metadata
    # Get metadata
    metadata = adapter.get_metadata()
    metadata = adapter.get_metadata()
    print("Engine Metadata:")
    print("Engine Metadata:")
    for key, value in metadata.items():
    for key, value in metadata.items():
    print(f"  {key}: {value}")
    print(f"  {key}: {value}")


    # Generate text
    # Generate text
    if adapter.tokenizer:
    if adapter.tokenizer:
    print(f"\nGenerating text for prompt: {prompt}")
    print(f"\nGenerating text for prompt: {prompt}")
    output = adapter.generate_text(prompt)
    output = adapter.generate_text(prompt)
    print(f"Output: {output}")
    print(f"Output: {output}")
    else:
    else:
    print("\nTokenizer not available. Cannot generate text.")
    print("\nTokenizer not available. Cannot generate text.")


except Exception as e:
except Exception as e:
    print(f"Error testing TensorRT adapter: {e}")
    print(f"Error testing TensorRT adapter: {e}")




    def main():
    def main():
    """
    """
    Main function to demonstrate the model adapters.
    Main function to demonstrate the model adapters.
    """
    """
    parser = argparse.ArgumentParser(description="Test different model adapters")
    parser = argparse.ArgumentParser(description="Test different model adapters")
    parser.add_argument(
    parser.add_argument(
    "--adapter",
    "--adapter",
    type=str,
    type=str,
    choices=["ollama", "lmstudio", "openai", "tensorrt"],
    choices=["ollama", "lmstudio", "openai", "tensorrt"],
    help="Type of adapter to test",
    help="Type of adapter to test",
    )
    )
    parser.add_argument("--base-url", type=str, help="Base URL for the API")
    parser.add_argument("--base-url", type=str, help="Base URL for the API")
    parser.add_argument("--model", type=str, help="Model name or ID")
    parser.add_argument("--model", type=str, help="Model name or ID")
    parser.add_argument("--api-key", type=str, help="API key for authentication")
    parser.add_argument("--api-key", type=str, help="API key for authentication")
    parser.add_argument(
    parser.add_argument(
    "--engine-path", type=str, help="Path to the TensorRT engine file"
    "--engine-path", type=str, help="Path to the TensorRT engine file"
    )
    )
    parser.add_argument("--tokenizer-path", type=str, help="Path to the tokenizer")
    parser.add_argument("--tokenizer-path", type=str, help="Path to the tokenizer")
    parser.add_argument(
    parser.add_argument(
    "--prompt",
    "--prompt",
    type=str,
    type=str,
    default="Hello, world!",
    default="Hello, world!",
    help="Input prompt for text generation",
    help="Input prompt for text generation",
    )
    )


    args = parser.parse_args()
    args = parser.parse_args()


    # If no adapter is specified, show help
    # If no adapter is specified, show help
    if not args.adapter:
    if not args.adapter:
    parser.print_help()
    parser.print_help()
    return # Test the specified adapter
    return # Test the specified adapter
    if args.adapter == "ollama":
    if args.adapter == "ollama":
    base_url = args.base_url or "http://localhost:11434"
    base_url = args.base_url or "http://localhost:11434"
    model_name = args.model or "llama2"
    model_name = args.model or "llama2"
    test_ollama_adapter(base_url, model_name, args.prompt)
    test_ollama_adapter(base_url, model_name, args.prompt)


    elif args.adapter == "lmstudio":
    elif args.adapter == "lmstudio":
    base_url = args.base_url or "http://localhost:1234/v1"
    base_url = args.base_url or "http://localhost:1234/v1"
    test_lmstudio_adapter(base_url, args.prompt)
    test_lmstudio_adapter(base_url, args.prompt)


    elif args.adapter == "openai":
    elif args.adapter == "openai":
    base_url = args.base_url or "http://localhost:8000/v1"
    base_url = args.base_url or "http://localhost:8000/v1"
    api_key = args.api_key or "sk-"
    api_key = args.api_key or "sk-"
    test_openai_compatible_adapter(base_url, api_key, args.prompt)
    test_openai_compatible_adapter(base_url, api_key, args.prompt)


    elif args.adapter == "tensorrt":
    elif args.adapter == "tensorrt":
    if not args.engine_path:
    if not args.engine_path:
    print("Error: --engine-path is required for TensorRT adapter")
    print("Error: --engine-path is required for TensorRT adapter")
    return if not args.tokenizer_path:
    return if not args.tokenizer_path:
    print("Error: --tokenizer-path is required for TensorRT adapter")
    print("Error: --tokenizer-path is required for TensorRT adapter")
    return test_tensorrt_adapter(args.engine_path, args.tokenizer_path, args.prompt)
    return test_tensorrt_adapter(args.engine_path, args.tokenizer_path, args.prompt)




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()