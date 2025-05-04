"""
"""
LM Studio adapter for the AI Models module.
LM Studio adapter for the AI Models module.


This module provides an adapter for connecting to LM Studio,
This module provides an adapter for connecting to LM Studio,
a desktop application for running large language models locally.
a desktop application for running large language models locally.
"""
"""


import json
import json
import logging
import logging
from typing import Any, Dict, Generator, List, Optional, Union
from typing import Any, Dict, Generator, List, Optional, Union


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
    import requests
    import requests


    REQUESTS_AVAILABLE = True
    REQUESTS_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("Requests not available. LM Studio adapter will not work.")
    logger.warning("Requests not available. LM Studio adapter will not work.")
    REQUESTS_AVAILABLE = False
    REQUESTS_AVAILABLE = False




    class LMStudioAdapter:
    class LMStudioAdapter:
    """
    """
    Adapter for connecting to LM Studio.
    Adapter for connecting to LM Studio.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    base_url: str = "http://localhost:1234/v1",
    base_url: str = "http://localhost:1234/v1",
    timeout: int = 60,
    timeout: int = 60,
    api_key: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs,
    **kwargs,
    ):
    ):
    """
    """
    Initialize the LM Studio adapter.
    Initialize the LM Studio adapter.


    Args:
    Args:
    base_url: Base URL of the LM Studio API
    base_url: Base URL of the LM Studio API
    timeout: Timeout for API requests in seconds
    timeout: Timeout for API requests in seconds
    api_key: Optional API key (not required for local LM Studio)
    api_key: Optional API key (not required for local LM Studio)
    **kwargs: Additional parameters for the adapter
    **kwargs: Additional parameters for the adapter
    """
    """
    if not REQUESTS_AVAILABLE:
    if not REQUESTS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Requests not available. Please install it with: pip install requests"
    "Requests not available. Please install it with: pip install requests"
    )
    )


    self.base_url = base_url
    self.base_url = base_url
    self.timeout = timeout
    self.timeout = timeout
    self.api_key = api_key
    self.api_key = api_key
    self.kwargs = kwargs
    self.kwargs = kwargs
    self.session = requests.Session()
    self.session = requests.Session()


    # Set up headers
    # Set up headers
    self.headers = {}
    self.headers = {}
    if self.api_key:
    if self.api_key:
    self.headers["Authorization"] = f"Bearer {self.api_key}"
    self.headers["Authorization"] = f"Bearer {self.api_key}"


    # Check if LM Studio is running
    # Check if LM Studio is running
    self._check_lmstudio_status()
    self._check_lmstudio_status()


    def _check_lmstudio_status(self) -> None:
    def _check_lmstudio_status(self) -> None:
    """
    """
    Check if LM Studio is running.
    Check if LM Studio is running.


    Raises:
    Raises:
    ConnectionError: If LM Studio is not running
    ConnectionError: If LM Studio is not running
    """
    """
    try:
    try:
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/models", headers=self.headers, timeout=5
    f"{self.base_url}/models", headers=self.headers, timeout=5
    )
    )
    if response.status_code != 200:
    if response.status_code != 200:
    logger.warning(f"LM Studio returned status code {response.status_code}")
    logger.warning(f"LM Studio returned status code {response.status_code}")
except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error connecting to LM Studio: {e}")
    logger.error(f"Error connecting to LM Studio: {e}")
    raise ConnectionError(
    raise ConnectionError(
    f"Could not connect to LM Studio at {self.base_url}. Make sure LM Studio is running with the API server enabled."
    f"Could not connect to LM Studio at {self.base_url}. Make sure LM Studio is running with the API server enabled."
    )
    )


    def list_models(self) -> List[Dict[str, Any]]:
    def list_models(self) -> List[Dict[str, Any]]:
    """
    """
    List available models in LM Studio.
    List available models in LM Studio.


    Returns:
    Returns:
    List of model information dictionaries
    List of model information dictionaries
    """
    """
    try:
    try:
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/models", headers=self.headers, timeout=self.timeout
    f"{self.base_url}/models", headers=self.headers, timeout=self.timeout
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    data = response.json()
    data = response.json()
    return data.get("data", [])
    return data.get("data", [])


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error listing models: {e}")
    logger.error(f"Error listing models: {e}")
    raise
    raise


    def get_model_info(self, model_id: str) -> Dict[str, Any]:
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
    """
    """
    Get information about a specific model.
    Get information about a specific model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    Dictionary with model information
    Dictionary with model information
    """
    """
    try:
    try:
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/models/{model_id}",
    f"{self.base_url}/models/{model_id}",
    headers=self.headers,
    headers=self.headers,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    return response.json()
    return response.json()


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error getting model info for {model_id}: {e}")
    logger.error(f"Error getting model info for {model_id}: {e}")
    raise
    raise


    def generate_completions(
    def generate_completions(
    self,
    self,
    model: str,
    model: str,
    prompt: str,
    prompt: str,
    temperature: float = 0.7,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_p: float = 0.9,
    top_k: int = 40,
    top_k: int = 40,
    max_tokens: int = 2048,
    max_tokens: int = 2048,
    stop: Optional[List[str]] = None,
    stop: Optional[List[str]] = None,
    stream: bool = False,
    stream: bool = False,
    **kwargs,
    **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    """
    """
    Generate completions using an LM Studio model.
    Generate completions using an LM Studio model.


    Args:
    Args:
    model: ID of the model
    model: ID of the model
    prompt: Input prompt
    prompt: Input prompt
    temperature: Temperature for sampling
    temperature: Temperature for sampling
    top_p: Top-p sampling parameter
    top_p: Top-p sampling parameter
    top_k: Top-k sampling parameter
    top_k: Top-k sampling parameter
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    stop: Optional list of stop sequences
    stop: Optional list of stop sequences
    stream: Whether to stream the response
    stream: Whether to stream the response
    **kwargs: Additional parameters for generation
    **kwargs: Additional parameters for generation


    Returns:
    Returns:
    Response dictionary or a generator yielding response dictionaries if streaming
    Response dictionary or a generator yielding response dictionaries if streaming
    """
    """
    # Prepare request data
    # Prepare request data
    request_data = {
    request_data = {
    "model": model,
    "model": model,
    "prompt": prompt,
    "prompt": prompt,
    "temperature": temperature,
    "temperature": temperature,
    "top_p": top_p,
    "top_p": top_p,
    "max_tokens": max_tokens,
    "max_tokens": max_tokens,
    "stream": stream,
    "stream": stream,
    }
    }


    # Add top_k if supported
    # Add top_k if supported
    if "top_k" in kwargs:
    if "top_k" in kwargs:
    request_data["top_k"] = top_k
    request_data["top_k"] = top_k


    # Add stop sequences if provided
    # Add stop sequences if provided
    if stop:
    if stop:
    request_data["stop"] = stop
    request_data["stop"] = stop


    # Add any additional parameters
    # Add any additional parameters
    for key, value in kwargs.items():
    for key, value in kwargs.items():
    if key not in request_data:
    if key not in request_data:
    request_data[key] = value
    request_data[key] = value


    try:
    try:
    if stream:
    if stream:
    return self._generate_completions_stream(request_data)
    return self._generate_completions_stream(request_data)
    else:
    else:
    return self._generate_completions_sync(request_data)
    return self._generate_completions_sync(request_data)


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error generating completions with {model}: {e}")
    logger.error(f"Error generating completions with {model}: {e}")
    raise
    raise


    def _generate_completions_sync(
    def _generate_completions_sync(
    self, request_data: Dict[str, Any]
    self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Generate completions synchronously.
    Generate completions synchronously.


    Args:
    Args:
    request_data: Request data for the API
    request_data: Request data for the API


    Returns:
    Returns:
    Response dictionary
    Response dictionary
    """
    """
    response = self.session.post(
    response = self.session.post(
    f"{self.base_url}/completions",
    f"{self.base_url}/completions",
    headers=self.headers,
    headers=self.headers,
    json=request_data,
    json=request_data,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    return response.json()
    return response.json()


    def _generate_completions_stream(
    def _generate_completions_stream(
    self, request_data: Dict[str, Any]
    self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
    ) -> Generator[Dict[str, Any], None, None]:
    """
    """
    Generate completions as a stream.
    Generate completions as a stream.


    Args:
    Args:
    request_data: Request data for the API
    request_data: Request data for the API


    Returns:
    Returns:
    Generator yielding response dictionaries
    Generator yielding response dictionaries
    """
    """
    response = self.session.post(
    response = self.session.post(
    f"{self.base_url}/completions",
    f"{self.base_url}/completions",
    headers=self.headers,
    headers=self.headers,
    json=request_data,
    json=request_data,
    stream=True,
    stream=True,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    for line in response.iter_lines():
    for line in response.iter_lines():
    if line:
    if line:
    line = line.decode("utf-8")
    line = line.decode("utf-8")


    # Skip empty lines
    # Skip empty lines
    if not line.strip():
    if not line.strip():
    continue
    continue


    # Handle SSE format
    # Handle SSE format
    if line.startswith("data: "):
    if line.startswith("data: "):
    line = line[6:]  # Remove "data: " prefix
    line = line[6:]  # Remove "data: " prefix


    # Check for the end of the stream
    # Check for the end of the stream
    if line == "[DONE]":
    if line == "[DONE]":
    break
    break


    try:
    try:
    data = json.loads(line)
    data = json.loads(line)
    yield data
    yield data


except json.JSONDecodeError:
except json.JSONDecodeError:
    logger.warning(f"Could not decode JSON: {line}")
    logger.warning(f"Could not decode JSON: {line}")


    def generate_chat_completions(
    def generate_chat_completions(
    self,
    self,
    model: str,
    model: str,
    messages: List[Dict[str, str]],
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_p: float = 0.9,
    top_k: int = 40,
    top_k: int = 40,
    max_tokens: int = 2048,
    max_tokens: int = 2048,
    stop: Optional[List[str]] = None,
    stop: Optional[List[str]] = None,
    stream: bool = False,
    stream: bool = False,
    **kwargs,
    **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    """
    """
    Generate chat completions using an LM Studio model.
    Generate chat completions using an LM Studio model.


    Args:
    Args:
    model: ID of the model
    model: ID of the model
    messages: List of message dictionaries with "role" and "content" keys
    messages: List of message dictionaries with "role" and "content" keys
    temperature: Temperature for sampling
    temperature: Temperature for sampling
    top_p: Top-p sampling parameter
    top_p: Top-p sampling parameter
    top_k: Top-k sampling parameter
    top_k: Top-k sampling parameter
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    stop: Optional list of stop sequences
    stop: Optional list of stop sequences
    stream: Whether to stream the response
    stream: Whether to stream the response
    **kwargs: Additional parameters for chat
    **kwargs: Additional parameters for chat


    Returns:
    Returns:
    Response dictionary or a generator yielding response dictionaries if streaming
    Response dictionary or a generator yielding response dictionaries if streaming
    """
    """
    # Prepare request data
    # Prepare request data
    request_data = {
    request_data = {
    "model": model,
    "model": model,
    "messages": messages,
    "messages": messages,
    "temperature": temperature,
    "temperature": temperature,
    "top_p": top_p,
    "top_p": top_p,
    "max_tokens": max_tokens,
    "max_tokens": max_tokens,
    "stream": stream,
    "stream": stream,
    }
    }


    # Add top_k if supported
    # Add top_k if supported
    if "top_k" in kwargs:
    if "top_k" in kwargs:
    request_data["top_k"] = top_k
    request_data["top_k"] = top_k


    # Add stop sequences if provided
    # Add stop sequences if provided
    if stop:
    if stop:
    request_data["stop"] = stop
    request_data["stop"] = stop


    # Add any additional parameters
    # Add any additional parameters
    for key, value in kwargs.items():
    for key, value in kwargs.items():
    if key not in request_data:
    if key not in request_data:
    request_data[key] = value
    request_data[key] = value


    try:
    try:
    if stream:
    if stream:
    return self._generate_chat_completions_stream(request_data)
    return self._generate_chat_completions_stream(request_data)
    else:
    else:
    return self._generate_chat_completions_sync(request_data)
    return self._generate_chat_completions_sync(request_data)


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error generating chat completions with {model}: {e}")
    logger.error(f"Error generating chat completions with {model}: {e}")
    raise
    raise


    def _generate_chat_completions_sync(
    def _generate_chat_completions_sync(
    self, request_data: Dict[str, Any]
    self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Generate chat completions synchronously.
    Generate chat completions synchronously.


    Args:
    Args:
    request_data: Request data for the API
    request_data: Request data for the API


    Returns:
    Returns:
    Response dictionary
    Response dictionary
    """
    """
    response = self.session.post(
    response = self.session.post(
    f"{self.base_url}/chat/completions",
    f"{self.base_url}/chat/completions",
    headers=self.headers,
    headers=self.headers,
    json=request_data,
    json=request_data,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    return response.json()
    return response.json()


    def _generate_chat_completions_stream(
    def _generate_chat_completions_stream(
    self, request_data: Dict[str, Any]
    self, request_data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
    ) -> Generator[Dict[str, Any], None, None]:
    """
    """
    Generate chat completions as a stream.
    Generate chat completions as a stream.


    Args:
    Args:
    request_data: Request data for the API
    request_data: Request data for the API


    Returns:
    Returns:
    Generator yielding response dictionaries
    Generator yielding response dictionaries
    """
    """
    response = self.session.post(
    response = self.session.post(
    f"{self.base_url}/chat/completions",
    f"{self.base_url}/chat/completions",
    headers=self.headers,
    headers=self.headers,
    json=request_data,
    json=request_data,
    stream=True,
    stream=True,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    for line in response.iter_lines():
    for line in response.iter_lines():
    if line:
    if line:
    line = line.decode("utf-8")
    line = line.decode("utf-8")


    # Skip empty lines
    # Skip empty lines
    if not line.strip():
    if not line.strip():
    continue
    continue


    # Handle SSE format
    # Handle SSE format
    if line.startswith("data: "):
    if line.startswith("data: "):
    line = line[6:]  # Remove "data: " prefix
    line = line[6:]  # Remove "data: " prefix


    # Check for the end of the stream
    # Check for the end of the stream
    if line == "[DONE]":
    if line == "[DONE]":
    break
    break


    try:
    try:
    data = json.loads(line)
    data = json.loads(line)
    yield data
    yield data


except json.JSONDecodeError:
except json.JSONDecodeError:
    logger.warning(f"Could not decode JSON: {line}")
    logger.warning(f"Could not decode JSON: {line}")


    def create_embeddings(
    def create_embeddings(
    self, model: str, input: Union[str, List[str]], **kwargs
    self, model: str, input: Union[str, List[str]], **kwargs
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create embeddings for text.
    Create embeddings for text.


    Args:
    Args:
    model: ID of the model
    model: ID of the model
    input: Input text or list of texts
    input: Input text or list of texts
    **kwargs: Additional parameters for embedding
    **kwargs: Additional parameters for embedding


    Returns:
    Returns:
    Response dictionary with embeddings
    Response dictionary with embeddings
    """
    """
    # Prepare request data
    # Prepare request data
    request_data = {"model": model, "input": input}
    request_data = {"model": model, "input": input}


    # Add any additional parameters
    # Add any additional parameters
    for key, value in kwargs.items():
    for key, value in kwargs.items():
    if key not in request_data:
    if key not in request_data:
    request_data[key] = value
    request_data[key] = value


    try:
    try:
    response = self.session.post(
    response = self.session.post(
    f"{self.base_url}/embeddings",
    f"{self.base_url}/embeddings",
    headers=self.headers,
    headers=self.headers,
    json=request_data,
    json=request_data,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    return response.json()
    return response.json()


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error creating embeddings with {model}: {e}")
    logger.error(f"Error creating embeddings with {model}: {e}")
    raise
    raise


    def get_model_parameters(self, model: str) -> Dict[str, Any]:
    def get_model_parameters(self, model: str) -> Dict[str, Any]:
    """
    """
    Get parameters for a model.
    Get parameters for a model.


    Args:
    Args:
    model: ID of the model
    model: ID of the model


    Returns:
    Returns:
    Dictionary with model parameters
    Dictionary with model parameters
    """
    """
    try:
    try:
    response = self.session.get(
    response = self.session.get(
    f"{self.base_url}/parameters",
    f"{self.base_url}/parameters",
    headers=self.headers,
    headers=self.headers,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    return response.json()
    return response.json()


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error getting model parameters for {model}: {e}")
    logger.error(f"Error getting model parameters for {model}: {e}")
    raise
    raise


    def set_model_parameters(
    def set_model_parameters(
    self, model: str, parameters: Dict[str, Any]
    self, model: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Set parameters for a model.
    Set parameters for a model.


    Args:
    Args:
    model: ID of the model
    model: ID of the model
    parameters: Dictionary with model parameters
    parameters: Dictionary with model parameters


    Returns:
    Returns:
    Dictionary with updated model parameters
    Dictionary with updated model parameters
    """
    """
    try:
    try:
    response = self.session.post(
    response = self.session.post(
    f"{self.base_url}/parameters",
    f"{self.base_url}/parameters",
    headers=self.headers,
    headers=self.headers,
    json=parameters,
    json=parameters,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )
    response.raise_for_status()
    response.raise_for_status()


    return response.json()
    return response.json()


except requests.exceptions.RequestException as e:
except requests.exceptions.RequestException as e:
    logger.error(f"Error setting model parameters for {model}: {e}")
    logger.error(f"Error setting model parameters for {model}: {e}")
    raise
    raise




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create an LM Studio adapter
    # Create an LM Studio adapter
    adapter = LMStudioAdapter()
    adapter = LMStudioAdapter()


    # List available models
    # List available models
    try:
    try:
    models = adapter.list_models()
    models = adapter.list_models()
    print(f"Available models: {len(models)}")
    print(f"Available models: {len(models)}")
    for model in models:
    for model in models:
    print(f"- {model['id']}")
    print(f"- {model['id']}")


    # If there are models, get info about the first one
    # If there are models, get info about the first one
    if models:
    if models:
    model_id = models[0]["id"]
    model_id = models[0]["id"]


    # Generate completions
    # Generate completions
    prompt = "Hello, world!"
    prompt = "Hello, world!"
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
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "user", "content": "Hello, how are you?"},
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


except Exception as e:
except Exception as e:
    print(f"Error: {e}")
    print(f"Error: {e}")

