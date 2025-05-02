"""
LM Studio adapter for the AI Models module.

This module provides an adapter for connecting to LM Studio,
a desktop application for running large language models locally.
"""

import json
import logging
from typing import Any, Dict, Generator, List, Optional, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("Requests not available. LM Studio adapter will not work.")
    REQUESTS_AVAILABLE = False


class LMStudioAdapter:
    """
    Adapter for connecting to LM Studio.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        timeout: int = 60,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the LM Studio adapter.

        Args:
            base_url: Base URL of the LM Studio API
            timeout: Timeout for API requests in seconds
            api_key: Optional API key (not required for local LM Studio)
            **kwargs: Additional parameters for the adapter
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "Requests not available. Please install it with: pip install requests"
            )

        self.base_url = base_url
        self.timeout = timeout
        self.api_key = api_key
        self.kwargs = kwargs
        self.session = requests.Session()

        # Set up headers
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

        # Check if LM Studio is running
        self._check_lmstudio_status()

    def _check_lmstudio_status(self) -> None:
        """
        Check if LM Studio is running.

        Raises:
            ConnectionError: If LM Studio is not running
        """
        try:
            response = self.session.get(
                f"{self.base_url}/models", headers=self.headers, timeout=5
            )
            if response.status_code != 200:
                logger.warning(f"LM Studio returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to LM Studio: {e}")
            raise ConnectionError(
                f"Could not connect to LM Studio at {self.base_url}. Make sure LM Studio is running with the API server enabled."
            )

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models in LM Studio.

        Returns:
            List of model information dictionaries
        """
        try:
            response = self.session.get(
                f"{self.base_url}/models", headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return data.get("data", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing models: {e}")
            raise

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            model_id: ID of the model

        Returns:
            Dictionary with model information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/models/{model_id}",
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting model info for {model_id}: {e}")
            raise

    def generate_completions(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Generate completions using an LM Studio model.

        Args:
            model: ID of the model
            prompt: Input prompt
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for generation

        Returns:
            Response dictionary or a generator yielding response dictionaries if streaming
        """
        # Prepare request data
        request_data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        # Add top_k if supported
        if "top_k" in kwargs:
            request_data["top_k"] = top_k

        # Add stop sequences if provided
        if stop:
            request_data["stop"] = stop

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            if stream:
                return self._generate_completions_stream(request_data)
            else:
                return self._generate_completions_sync(request_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating completions with {model}: {e}")
            raise

    def _generate_completions_sync(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate completions synchronously.

        Args:
            request_data: Request data for the API

        Returns:
            Response dictionary
        """
        response = self.session.post(
            f"{self.base_url}/completions",
            headers=self.headers,
            json=request_data,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()

    def _generate_completions_stream(
        self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate completions as a stream.

        Args:
            request_data: Request data for the API

        Returns:
            Generator yielding response dictionaries
        """
        response = self.session.post(
            f"{self.base_url}/completions",
            headers=self.headers,
            json=request_data,
            stream=True,
            timeout=self.timeout,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")

                # Skip empty lines
                if not line.strip():
                    continue

                # Handle SSE format
                if line.startswith("data: "):
                    line = line[6:]  # Remove "data: " prefix

                    # Check for the end of the stream
                    if line == "[DONE]":
                        break

                    try:
                        data = json.loads(line)
                        yield data

                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode JSON: {line}")

    def generate_chat_completions(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Generate chat completions using an LM Studio model.

        Args:
            model: ID of the model
            messages: List of message dictionaries with "role" and "content" keys
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for chat

        Returns:
            Response dictionary or a generator yielding response dictionaries if streaming
        """
        # Prepare request data
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        # Add top_k if supported
        if "top_k" in kwargs:
            request_data["top_k"] = top_k

        # Add stop sequences if provided
        if stop:
            request_data["stop"] = stop

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            if stream:
                return self._generate_chat_completions_stream(request_data)
            else:
                return self._generate_chat_completions_sync(request_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating chat completions with {model}: {e}")
            raise

    def _generate_chat_completions_sync(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate chat completions synchronously.

        Args:
            request_data: Request data for the API

        Returns:
            Response dictionary
        """
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=request_data,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()

    def _generate_chat_completions_stream(
        self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate chat completions as a stream.

        Args:
            request_data: Request data for the API

        Returns:
            Generator yielding response dictionaries
        """
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=request_data,
            stream=True,
            timeout=self.timeout,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")

                # Skip empty lines
                if not line.strip():
                    continue

                # Handle SSE format
                if line.startswith("data: "):
                    line = line[6:]  # Remove "data: " prefix

                    # Check for the end of the stream
                    if line == "[DONE]":
                        break

                    try:
                        data = json.loads(line)
                        yield data

                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode JSON: {line}")

    def create_embeddings(
        self, model: str, input: Union[str, List[str]], **kwargs
    ) -> Dict[str, Any]:
        """
        Create embeddings for text.

        Args:
            model: ID of the model
            input: Input text or list of texts
            **kwargs: Additional parameters for embedding

        Returns:
            Response dictionary with embeddings
        """
        # Prepare request data
        request_data = {"model": model, "input": input}

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            response = self.session.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=request_data,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating embeddings with {model}: {e}")
            raise

    def get_model_parameters(self, model: str) -> Dict[str, Any]:
        """
        Get parameters for a model.

        Args:
            model: ID of the model

        Returns:
            Dictionary with model parameters
        """
        try:
            response = self.session.get(
                f"{self.base_url}/parameters",
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting model parameters for {model}: {e}")
            raise

    def set_model_parameters(
        self, model: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set parameters for a model.

        Args:
            model: ID of the model
            parameters: Dictionary with model parameters

        Returns:
            Dictionary with updated model parameters
        """
        try:
            response = self.session.post(
                f"{self.base_url}/parameters",
                headers=self.headers,
                json=parameters,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error setting model parameters for {model}: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Create an LM Studio adapter
    adapter = LMStudioAdapter()

    # List available models
    try:
        models = adapter.list_models()
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"- {model['id']}")

        # If there are models, get info about the first one
        if models:
            model_id = models[0]["id"]

            # Generate completions
            prompt = "Hello, world!"
            print(f"\nGenerating completions with {model_id} for prompt: {prompt}")
            response = adapter.generate_completions(model_id, prompt)
            print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")

            # Generate chat completions
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ]
            print(f"\nGenerating chat completions with {model_id}")
            response = adapter.generate_chat_completions(model_id, messages)
            print(
                f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
            )

    except Exception as e:
        print(f"Error: {e}")
