"""
Ollama adapter for the AI Models module.

This module provides an adapter for connecting to Ollama,
a local API server for running large language models.
"""

import json
import logging
import aiohttp
from typing import Dict, List, Any, Optional, Union, Generator, AsyncGenerator

from .base_adapter import BaseModelAdapter

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
    logger.warning("Requests not available. Ollama adapter will not work.")
    REQUESTS_AVAILABLE = False

# Check for aiohttp availability for async operations
try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    logger.warning("aiohttp not available. Async operations will not work.")
    AIOHTTP_AVAILABLE = False


class OllamaAdapter(BaseModelAdapter):
    """
    Adapter for connecting to Ollama.
    """

    def __init__(
        self, base_url: str = "http://localhost:11434", timeout: int = 60, **kwargs
    ):
        """
        Initialize the Ollama adapter.

        Args:
            base_url: Base URL of the Ollama API
            timeout: Timeout for API requests in seconds
            **kwargs: Additional parameters for the adapter
        """
        super().__init__(
            name="Ollama",
            description="Adapter for connecting to Ollama, a local API server for running large language models",
        )

        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "Requests not available. Please install it with: pip install requests"
            )

        self.base_url = base_url
        self.timeout = timeout
        self.kwargs = kwargs
        self.session = requests.Session()
        self._async_session = None

        # Check if Ollama is running
        self._check_ollama_status()

    def _check_ollama_status(self) -> None:
        """
        Check if Ollama is running.

        Raises:
            ConnectionError: If Ollama is not running
        """
        try:
            response = self.session.get(f"{self.base_url}", timeout=5)
            if response.status_code != 200:
                logger.warning(f"Ollama returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama: {e}")
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
            )

    def connect(self, **kwargs) -> bool:
        """
        Connect to the adapter.

        Args:
            **kwargs: Connection parameters

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to connect to the Ollama API
            response = self.session.get(f"{self.base_url}", timeout=5)
            if response.status_code != 200:
                logger.warning(f"Ollama returned status code {response.status_code}")
                self._connected = False
                return False

            self._connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from the adapter.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.session.close()
            self._connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Ollama: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models in Ollama.

        Returns:
            List of model information dictionaries
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags", timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return data.get("models", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing models: {e}")
            raise

    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from the adapter.

        Returns:
            List of model dictionaries
        """
        try:
            models = self.list_models()

            # Transform the model data to a standard format
            standardized_models = []
            for model in models:
                standardized_models.append(
                    {
                        "id": model.get("name", ""),
                        "name": model.get("name", "").split(":")[0],
                        "description": f"Ollama model: {model.get('name', '')}",
                        "type": "llm",
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", ""),
                        "adapter": "ollama",
                    }
                )

            return standardized_models

        except Exception as e:
            self._handle_error(
                e, "Failed to get models from Ollama", operation="get_models"
            )
            return []

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name},
                timeout=self.timeout,
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting model info for {model_name}: {e}")
            raise

    def generate_text(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[str, Generator[str, None, None]]:
        """
        Generate text using an Ollama model.

        Args:
            model_name: Name of the model
            prompt: Input prompt
            system_prompt: Optional system prompt
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for generation

        Returns:
            Generated text or a generator yielding text chunks if streaming
        """
        # Prepare request data
        request_data = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": max_tokens,
            "stream": stream,
        }

        # Add system prompt if provided
        if system_prompt:
            request_data["system"] = system_prompt

        # Add stop sequences if provided
        if stop:
            request_data["stop"] = stop

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            if stream:
                return self._generate_text_stream(request_data)
            else:
                return self._generate_text_sync(request_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating text with {model_name}: {e}")
            raise

    def _generate_text_sync(self, request_data: Dict[str, Any]) -> str:
        """
        Generate text synchronously.

        Args:
            request_data: Request data for the API

        Returns:
            Generated text
        """
        response = self.session.post(
            f"{self.base_url}/api/generate", json=request_data, timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    def _generate_text_stream(
        self, request_data: Dict[str, Any]
    ) -> Generator[str, None, None]:
        """
        Generate text as a stream.

        Args:
            request_data: Request data for the API

        Returns:
            Generator yielding text chunks
        """
        response = self.session.post(
            f"{self.base_url}/api/generate",
            json=request_data,
            stream=True,
            timeout=self.timeout,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

                    # Check if this is the last chunk
                    if data.get("done", False):
                        break

                except json.JSONDecodeError:
                    logger.warning(f"Could not decode JSON: {line}")

    def chat(
        self,
        model_name: str,
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
        Chat with an Ollama model.

        Args:
            model_name: Name of the model
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
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": max_tokens,
            "stream": stream,
        }

        # Add stop sequences if provided
        if stop:
            request_data["stop"] = stop

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            if stream:
                return self._chat_stream(request_data)
            else:
                return self._chat_sync(request_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error chatting with {model_name}: {e}")
            raise

    def _chat_sync(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chat synchronously.

        Args:
            request_data: Request data for the API

        Returns:
            Response dictionary
        """
        response = self.session.post(
            f"{self.base_url}/api/chat", json=request_data, timeout=self.timeout
        )
        response.raise_for_status()

        return response.json()

    def _chat_stream(
        self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Chat as a stream.

        Args:
            request_data: Request data for the API

        Returns:
            Generator yielding response dictionaries
        """
        response = self.session.post(
            f"{self.base_url}/api/chat",
            json=request_data,
            stream=True,
            timeout=self.timeout,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    yield data

                    # Check if this is the last chunk
                    if data.get("done", False):
                        break

                except json.JSONDecodeError:
                    logger.warning(f"Could not decode JSON: {line}")

    def create_embedding(self, model_name: str, prompt: str, **kwargs) -> List[float]:
        """
        Create an embedding for a text.

        Args:
            model_name: Name of the model
            prompt: Input text
            **kwargs: Additional parameters for embedding

        Returns:
            List of embedding values
        """
        # Prepare request data
        request_data = {"model": model_name, "prompt": prompt}

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json=request_data,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            return data.get("embedding", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating embedding with {model_name}: {e}")
            raise

    def pull_model(
        self,
        model_name: str,
        insecure: bool = False,
        callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Pull a model from the Ollama library.

        Args:
            model_name: Name of the model
            insecure: Whether to allow insecure connections
            callback: Optional callback function for progress updates

        Returns:
            Dictionary with pull status
        """
        # Prepare request data
        request_data = {"name": model_name, "insecure": insecure}

        try:
            if callback:
                return self._pull_model_with_callback(request_data, callback)
            else:
                response = self.session.post(
                    f"{self.base_url}/api/pull",
                    json=request_data,
                    timeout=None,  # No timeout for model pulling
                )
                response.raise_for_status()

                return {"status": "success", "model": model_name}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            raise

    def _pull_model_with_callback(
        self, request_data: Dict[str, Any], callback: callable
    ) -> Dict[str, Any]:
        """
        Pull a model with progress updates.

        Args:
            request_data: Request data for the API
            callback: Callback function for progress updates

        Returns:
            Dictionary with pull status
        """
        response = self.session.post(
            f"{self.base_url}/api/pull",
            json=request_data,
            stream=True,
            timeout=None,  # No timeout for model pulling
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    callback(data)

                    # Check if this is the last chunk
                    if "status" in data and data["status"] == "success":
                        return data

                except json.JSONDecodeError:
                    logger.warning(f"Could not decode JSON: {line}")

        return {"status": "success", "model": request_data["name"]}

    def push_model(
        self,
        model_name: str,
        insecure: bool = False,
        callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Push a model to a registry.

        Args:
            model_name: Name of the model
            insecure: Whether to allow insecure connections
            callback: Optional callback function for progress updates

        Returns:
            Dictionary with push status
        """
        # Prepare request data
        request_data = {"name": model_name, "insecure": insecure}

        try:
            if callback:
                return self._push_model_with_callback(request_data, callback)
            else:
                response = self.session.post(
                    f"{self.base_url}/api/push",
                    json=request_data,
                    timeout=None,  # No timeout for model pushing
                )
                response.raise_for_status()

                return {"status": "success", "model": model_name}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error pushing model {model_name}: {e}")
            raise

    def _push_model_with_callback(
        self, request_data: Dict[str, Any], callback: callable
    ) -> Dict[str, Any]:
        """
        Push a model with progress updates.

        Args:
            request_data: Request data for the API
            callback: Callback function for progress updates

        Returns:
            Dictionary with push status
        """
        response = self.session.post(
            f"{self.base_url}/api/push",
            json=request_data,
            stream=True,
            timeout=None,  # No timeout for model pushing
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    callback(data)

                    # Check if this is the last chunk
                    if "status" in data and data["status"] == "success":
                        return data

                except json.JSONDecodeError:
                    logger.warning(f"Could not decode JSON: {line}")

        return {"status": "success", "model": request_data["name"]}

    def create_model(
        self, model_name: str, modelfile: str, callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Create a model from a Modelfile.

        Args:
            model_name: Name of the model
            modelfile: Content of the Modelfile
            callback: Optional callback function for progress updates

        Returns:
            Dictionary with creation status
        """
        # Prepare request data
        request_data = {"name": model_name, "modelfile": modelfile}

        try:
            if callback:
                return self._create_model_with_callback(request_data, callback)
            else:
                response = self.session.post(
                    f"{self.base_url}/api/create",
                    json=request_data,
                    timeout=None,  # No timeout for model creation
                )
                response.raise_for_status()

                return {"status": "success", "model": model_name}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating model {model_name}: {e}")
            raise

    def _create_model_with_callback(
        self, request_data: Dict[str, Any], callback: callable
    ) -> Dict[str, Any]:
        """
        Create a model with progress updates.

        Args:
            request_data: Request data for the API
            callback: Callback function for progress updates

        Returns:
            Dictionary with creation status
        """
        response = self.session.post(
            f"{self.base_url}/api/create",
            json=request_data,
            stream=True,
            timeout=None,  # No timeout for model creation
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    callback(data)

                    # Check if this is the last chunk
                    if "status" in data and data["status"] == "success":
                        return data

                except json.JSONDecodeError:
                    logger.warning(f"Could not decode JSON: {line}")

        return {"status": "success", "model": request_data["name"]}

    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """
        Delete a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with deletion status
        """
        # Prepare request data
        request_data = {"name": model_name}

        try:
            response = self.session.delete(
                f"{self.base_url}/api/delete", json=request_data, timeout=self.timeout
            )
            response.raise_for_status()

            return {"status": "success", "model": model_name}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting model {model_name}: {e}")
            raise

    def copy_model(self, source_model: str, target_model: str) -> Dict[str, Any]:
        """
        Copy a model.

        Args:
            source_model: Name of the source model
            target_model: Name of the target model

        Returns:
            Dictionary with copy status
        """
        # Prepare request data
        request_data = {"source": source_model, "destination": target_model}

        try:
            response = self.session.post(
                f"{self.base_url}/api/copy", json=request_data, timeout=self.timeout
            )
            response.raise_for_status()

            return {"status": "success", "source": source_model, "target": target_model}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error copying model {source_model} to {target_model}: {e}")
            raise

    async def connect_async(self, **kwargs) -> bool:
        """
        Connect to the adapter asynchronously.

        Args:
            **kwargs: Connection parameters

        Returns:
            True if successful, False otherwise
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp not available. Please install it with: pip install aiohttp"
            )

        try:
            # Create async session if needed
            if self._async_session is None:
                self._async_session = aiohttp.ClientSession()

            # Try to connect to the Ollama API
            async with self._async_session.get(
                f"{self.base_url}", timeout=5
            ) as response:
                if response.status != 200:
                    logger.warning(f"Ollama returned status code {response.status}")
                    self._connected = False
                    return False

            self._connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama asynchronously: {e}")
            self._connected = False
            return False

    async def disconnect_async(self) -> bool:
        """
        Disconnect from the adapter asynchronously.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self._async_session is not None:
                await self._async_session.close()
                self._async_session = None
            self._connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Ollama asynchronously: {e}")
            return False

    async def list_models_async(self) -> List[Dict[str, Any]]:
        """
        List available models in Ollama asynchronously.

        Returns:
            List of model information dictionaries
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp not available. Please install it with: pip install aiohttp"
            )

        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        try:
            async with self._async_session.get(
                f"{self.base_url}/api/tags", timeout=self.timeout
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("models", [])

        except aiohttp.ClientError as e:
            logger.error(f"Error listing models asynchronously: {e}")
            raise

    async def get_models_async(self) -> List[Dict[str, Any]]:
        """
        Get available models from the adapter asynchronously.

        Returns:
            List of model dictionaries
        """
        try:
            models = await self.list_models_async()

            # Transform the model data to a standard format
            standardized_models = []
            for model in models:
                standardized_models.append(
                    {
                        "id": model.get("name", ""),
                        "name": model.get("name", "").split(":")[0],
                        "description": f"Ollama model: {model.get('name', '')}",
                        "type": "llm",
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", ""),
                        "adapter": "ollama",
                    }
                )

            return standardized_models

        except Exception as e:
            logger.error(f"Failed to get models from Ollama asynchronously: {e}")
            return []

    async def get_model_info_async(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model asynchronously.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp not available. Please install it with: pip install aiohttp"
            )

        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        try:
            async with self._async_session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name},
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(
                f"Error getting model info for {model_name} asynchronously: {e}"
            )
            raise

    async def generate_text_async(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text using an Ollama model asynchronously.

        Args:
            model_name: Name of the model
            prompt: Input prompt
            system_prompt: Optional system prompt
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for generation

        Returns:
            Generated text or an async generator yielding text chunks if streaming
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp not available. Please install it with: pip install aiohttp"
            )

        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        # Prepare request data
        request_data = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": max_tokens,
            "stream": stream,
        }

        # Add system prompt if provided
        if system_prompt:
            request_data["system"] = system_prompt

        # Add stop sequences if provided
        if stop:
            request_data["stop"] = stop

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            if stream:
                return self._generate_text_stream_async(request_data)
            else:
                return await self._generate_text_sync_async(request_data)

        except aiohttp.ClientError as e:
            logger.error(f"Error generating text with {model_name} asynchronously: {e}")
            raise

    async def _generate_text_sync_async(self, request_data: Dict[str, Any]) -> str:
        """
        Generate text synchronously but using async API.

        Args:
            request_data: Request data for the API

        Returns:
            Generated text
        """
        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        async with self._async_session.post(
            f"{self.base_url}/api/generate", json=request_data, timeout=self.timeout
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("response", "")

    async def _generate_text_stream_async(
        self, request_data: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Generate text as an async stream.

        Args:
            request_data: Request data for the API

        Returns:
            Async generator yielding text chunks
        """
        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        async with self._async_session.post(
            f"{self.base_url}/api/generate", json=request_data, timeout=self.timeout
        ) as response:
            response.raise_for_status()

            # Process the stream line by line
            async for line in response.content:
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

                        # Check if this is the last chunk
                        if data.get("done", False):
                            break

                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode JSON: {line}")

    async def chat_async(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Chat with an Ollama model asynchronously.

        Args:
            model_name: Name of the model
            messages: List of message dictionaries with "role" and "content" keys
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            max_tokens: Maximum number of tokens to generate
            stop: Optional list of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters for chat

        Returns:
            Response dictionary or an async generator yielding response dictionaries if streaming
        """
        # Prepare request data
        request_data = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": max_tokens,
            "stream": stream,
        }

        # Add stop sequences if provided
        if stop:
            request_data["stop"] = stop

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            if stream:
                return self._chat_stream_async(request_data)
            else:
                return await self._chat_sync_async(request_data)

        except aiohttp.ClientError as e:
            logger.error(f"Error chatting with {model_name} asynchronously: {e}")
            raise

    async def _chat_sync_async(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chat synchronously but using async API.

        Args:
            request_data: Request data for the API

        Returns:
            Response dictionary
        """
        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        async with self._async_session.post(
            f"{self.base_url}/api/chat", json=request_data, timeout=self.timeout
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def _chat_stream_async(
        self, request_data: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Chat as an async stream.

        Args:
            request_data: Request data for the API

        Returns:
            Async generator yielding response dictionaries
        """
        # Create async session if needed
        if self._async_session is None:
            self._async_session = aiohttp.ClientSession()

        async with self._async_session.post(
            f"{self.base_url}/api/chat", json=request_data, timeout=self.timeout
        ) as response:
            response.raise_for_status()

            # Process the stream line by line
            async for line in response.content:
                if line:
                    try:
                        data = json.loads(line)
                        yield data

                        # Check if this is the last chunk
                        if data.get("done", False):
                            break

                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode JSON: {line}")

    async def create_embedding_async(
        self, model_name: str, prompt: str, **kwargs
    ) -> List[float]:
        """
        Create an embedding for a text asynchronously.

        Args:
            model_name: Name of the model
            prompt: Input text
            **kwargs: Additional parameters for embedding

        Returns:
            List of embedding values
        """
        # Prepare request data
        request_data = {"model": model_name, "prompt": prompt}

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value

        try:
            async with self._async_session.post(
                f"{self.base_url}/api/embeddings",
                json=request_data,
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("embedding", [])

        except aiohttp.ClientError as e:
            logger.error(
                f"Error creating embedding with {model_name} asynchronously: {e}"
            )
            raise

    async def pull_model_async(
        self,
        model_name: str,
        insecure: bool = False,
    ) -> Dict[str, Any]:
        """
        Pull a model from the Ollama library asynchronously.

        Args:
            model_name: Name of the model
            insecure: Whether to allow insecure connections

        Returns:
            Dictionary with pull status
        """
        # Prepare request data
        request_data = {"name": model_name, "insecure": insecure}

        try:
            async with self._async_session.post(
                f"{self.base_url}/api/pull",
                json=request_data,
                timeout=None,  # No timeout for model pulling
            ) as response:
                response.raise_for_status()

                return {"status": "success", "model": model_name}

        except aiohttp.ClientError as e:
            logger.error(f"Error pulling model {model_name} asynchronously: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Create an Ollama adapter
    adapter = OllamaAdapter()

    # List available models
    try:
        models = adapter.list_models()
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"- {model['name']} ({model['size']})")

        # If there are models, get info about the first one
        if models:
            model_name = models[0]["name"]
            model_info = adapter.get_model_info(model_name)
            print(f"\nModel info for {model_name}:")
            print(f"- Size: {model_info.get('size', 'Unknown')}")
            print(f"- Modified: {model_info.get('modified_at', 'Unknown')}")
            print(f"- Parameters: {model_info.get('parameters', 'Unknown')}")

            # Generate text
            prompt = "Hello, world!"
            print(f"\nGenerating text with {model_name} for prompt: {prompt}")
            response = adapter.generate_text(model_name, prompt)
            print(f"Response: {response}")

    except Exception as e:
        print(f"Error: {e}")
