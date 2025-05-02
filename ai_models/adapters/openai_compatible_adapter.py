"""
OpenAI-compatible API adapter for the AI Models module.

This module provides an adapter for connecting to OpenAI-compatible APIs,
including local API servers and cloud services.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Generator

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
    logger.warning("Requests not available. OpenAI-compatible adapter will not work.")
    REQUESTS_AVAILABLE = False

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI Python client not available. Using requests instead.")
    OPENAI_AVAILABLE = False


class OpenAICompatibleAdapter:
    """
    Adapter for connecting to OpenAI-compatible APIs.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: Optional[str] = "sk-",
        organization: Optional[str] = None,
        timeout: int = 60,
        use_client_library: bool = True,
        **kwargs,
    ):
        """
        Initialize the OpenAI-compatible adapter.

        Args:
            base_url: Base URL of the API
            api_key: API key for authentication
            organization: Optional organization ID
            timeout: Timeout for API requests in seconds
            use_client_library: Whether to use the OpenAI client library if available
            **kwargs: Additional parameters for the adapter
        """
        self.base_url = base_url
        self.api_key = api_key
        self.organization = organization
        self.timeout = timeout
        self.use_client_library = use_client_library and OPENAI_AVAILABLE
        self.kwargs = kwargs

        if self.use_client_library:
            # Initialize OpenAI client
            self.client = openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                organization=self.organization,
                timeout=self.timeout,
            )
        else:
            if not REQUESTS_AVAILABLE:
                raise ImportError(
                    "Requests not available. Please install it with: pip install requests"
                )

            # Initialize requests session
            self.session = requests.Session()

            # Set up headers
            self.headers = {"Content-Type": "application/json"}

            if self.api_key:
                self.headers["Authorization"] = f"Bearer {self.api_key}"

            if self.organization:
                self.headers["OpenAI-Organization"] = self.organization

        # Check if the API is available
        self._check_api_status()

    def _check_api_status(self) -> None:
        """
        Check if the API is available.

        Raises:
            ConnectionError: If the API is not available
        """
        try:
            if self.use_client_library:
                # Try to list models
                self.client.models.list()
            else:
                # Try to list models
                response = self.session.get(
                    f"{self.base_url}/models", headers=self.headers, timeout=5
                )
                if response.status_code != 200:
                    logger.warning(f"API returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error connecting to API: {e}")
            raise ConnectionError(
                f"Could not connect to API at {self.base_url}. Make sure the API server is running."
            )

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.

        Returns:
            List of model information dictionaries
        """
        try:
            if self.use_client_library:
                models = self.client.models.list()
                return [model.model_dump() for model in models.data]
            else:
                response = self.session.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()
                return data.get("data", [])

        except Exception as e:
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
            if self.use_client_library:
                model = self.client.models.retrieve(model_id)
                return model.model_dump()
            else:
                response = self.session.get(
                    f"{self.base_url}/models/{model_id}",
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Error getting model info for {model_id}: {e}")
            raise

    def create_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Create a completion.

        Args:
            model: ID of the model
            prompt: Input prompt
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for completion

        Returns:
            Response dictionary or a generator yielding response dictionaries if streaming
        """
        try:
            if self.use_client_library:
                if stream:
                    return self._create_completion_stream_client(
                        model=model,
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        stop=stop,
                        **kwargs,
                    )
                else:
                    return self._create_completion_sync_client(
                        model=model,
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        stop=stop,
                        **kwargs,
                    )
            else:
                # Prepare request data
                request_data = {
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "stream": stream,
                }

                # Add stop sequences if provided
                if stop:
                    request_data["stop"] = stop

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in request_data:
                        request_data[key] = value

                if stream:
                    return self._create_completion_stream_requests(request_data)
                else:
                    return self._create_completion_sync_requests(request_data)

        except Exception as e:
            logger.error(f"Error creating completion with {model}: {e}")
            raise

    def _create_completion_sync_client(
        self,
        model: str,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
        stop: Optional[List[str]],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a completion synchronously using the OpenAI client.

        Args:
            model: ID of the model
            prompt: Input prompt
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters for completion

        Returns:
            Response dictionary
        """
        completion = self.client.completions.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
            **kwargs,
        )

        return completion.model_dump()

    def _create_completion_stream_client(
        self,
        model: str,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
        stop: Optional[List[str]],
        **kwargs,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Create a completion as a stream using the OpenAI client.

        Args:
            model: ID of the model
            prompt: Input prompt
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters for completion

        Returns:
            Generator yielding response dictionaries
        """
        stream = self.client.completions.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            yield chunk.model_dump()

    def _create_completion_sync_requests(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a completion synchronously using requests.

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

    def _create_completion_stream_requests(
        self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Create a completion as a stream using requests.

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

    def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Create a chat completion.

        Args:
            model: ID of the model
            messages: List of message dictionaries with "role" and "content" keys
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for chat completion

        Returns:
            Response dictionary or a generator yielding response dictionaries if streaming
        """
        try:
            if self.use_client_library:
                if stream:
                    return self._create_chat_completion_stream_client(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        stop=stop,
                        **kwargs,
                    )
                else:
                    return self._create_chat_completion_sync_client(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        stop=stop,
                        **kwargs,
                    )
            else:
                # Prepare request data
                request_data = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "stream": stream,
                }

                # Add stop sequences if provided
                if stop:
                    request_data["stop"] = stop

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in request_data:
                        request_data[key] = value

                if stream:
                    return self._create_chat_completion_stream_requests(request_data)
                else:
                    return self._create_chat_completion_sync_requests(request_data)

        except Exception as e:
            logger.error(f"Error creating chat completion with {model}: {e}")
            raise

    def _create_chat_completion_sync_client(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        top_p: float,
        max_tokens: int,
        stop: Optional[List[str]],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a chat completion synchronously using the OpenAI client.

        Args:
            model: ID of the model
            messages: List of message dictionaries with "role" and "content" keys
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters for chat completion

        Returns:
            Response dictionary
        """
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
            **kwargs,
        )

        return completion.model_dump()

    def _create_chat_completion_stream_client(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        top_p: float,
        max_tokens: int,
        stop: Optional[List[str]],
        **kwargs,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Create a chat completion as a stream using the OpenAI client.

        Args:
            model: ID of the model
            messages: List of message dictionaries with "role" and "content" keys
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters for chat completion

        Returns:
            Generator yielding response dictionaries
        """
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            yield chunk.model_dump()

    def _create_chat_completion_sync_requests(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a chat completion synchronously using requests.

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

    def _create_chat_completion_stream_requests(
        self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Create a chat completion as a stream using requests.

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

    def create_embedding(
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
        try:
            if self.use_client_library:
                embedding = self.client.embeddings.create(
                    model=model, input=input, **kwargs
                )

                return embedding.model_dump()
            else:
                # Prepare request data
                request_data = {"model": model, "input": input}

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in request_data:
                        request_data[key] = value

                response = self.session.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json=request_data,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Error creating embeddings with {model}: {e}")
            raise

    def create_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create images from a prompt.

        Args:
            prompt: Text prompt
            model: Optional model ID
            n: Number of images to generate
            size: Size of the images
            response_format: Format of the response (url or b64_json)
            **kwargs: Additional parameters for image generation

        Returns:
            Response dictionary with image data
        """
        try:
            if self.use_client_library:
                # Prepare parameters
                params = {
                    "prompt": prompt,
                    "n": n,
                    "size": size,
                    "response_format": response_format,
                }

                # Add model if provided
                if model:
                    params["model"] = model

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in params:
                        params[key] = value

                image = self.client.images.generate(**params)

                return image.model_dump()
            else:
                # Prepare request data
                request_data = {
                    "prompt": prompt,
                    "n": n,
                    "size": size,
                    "response_format": response_format,
                }

                # Add model if provided
                if model:
                    request_data["model"] = model

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in request_data:
                        request_data[key] = value

                response = self.session.post(
                    f"{self.base_url}/images/generations",
                    headers=self.headers,
                    json=request_data,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Error creating images: {e}")
            raise

    def create_audio_transcription(
        self,
        file: str,
        model: str,
        prompt: Optional[str] = None,
        response_format: str = "json",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            file: Path to the audio file
            model: ID of the model
            prompt: Optional prompt to guide the transcription
            response_format: Format of the response
            **kwargs: Additional parameters for transcription

        Returns:
            Response dictionary with transcription
        """
        try:
            if self.use_client_library:
                # Prepare parameters
                params = {
                    "file": open(file, "rb"),
                    "model": model,
                    "response_format": response_format,
                }

                # Add prompt if provided
                if prompt:
                    params["prompt"] = prompt

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in params:
                        params[key] = value

                transcription = self.client.audio.transcriptions.create(**params)

                # Close the file
                params["file"].close()

                # Return as dictionary
                if isinstance(transcription, str):
                    return {"text": transcription}
                else:
                    return transcription.model_dump()
            else:
                # Prepare files and data
                files = {"file": open(file, "rb")}

                data = {"model": model, "response_format": response_format}

                # Add prompt if provided
                if prompt:
                    data["prompt"] = prompt

                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in data:
                        data[key] = value

                # Remove Content-Type header for multipart/form-data
                headers = self.headers.copy()
                if "Content-Type" in headers:
                    del headers["Content-Type"]

                response = self.session.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=self.timeout,
                )

                # Close the file
                files["file"].close()

                response.raise_for_status()

                # Parse response based on format
                if response_format == "json":
                    return response.json()
                else:
                    return {"text": response.text}

        except Exception as e:
            logger.error(f"Error creating audio transcription: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Create an OpenAI-compatible adapter
    adapter = OpenAICompatibleAdapter()

    # List available models
    try:
        models = adapter.list_models()
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"- {model['id']}")

        # If there are models, get info about the first one
        if models:
            model_id = models[0]["id"]

            # Create a completion
            prompt = "Hello, world!"
            print(f"\nCreating completion with {model_id} for prompt: {prompt}")
            response = adapter.create_completion(model_id, prompt)
            print(f"Response: {response.get('choices', [{}])[0].get('text', '')}")

            # Create a chat completion
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ]
            print(f"\nCreating chat completion with {model_id}")
            response = adapter.create_chat_completion(model_id, messages)
            print(
                f"Response: {response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
            )

    except Exception as e:
        print(f"Error: {e}")
