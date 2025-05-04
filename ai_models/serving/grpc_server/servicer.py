"""
"""
gRPC servicer for AI models.
gRPC servicer for AI models.


This module provides a gRPC servicer for handling model requests.
This module provides a gRPC servicer for handling model requests.
"""
"""




import logging
import logging
import time
import time
from typing import Dict, List
from typing import Dict, List


import grpc
import grpc


from .proto import model_pb2
from .proto import model_pb2


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


# Try to import gRPC
# Try to import gRPC
try:
    try:




    GRPC_AVAILABLE = True
    GRPC_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("gRPC is required for gRPC server")
    logger.warning("gRPC is required for gRPC server")
    GRPC_AVAILABLE = False
    GRPC_AVAILABLE = False




    class ModelServicer:
    class ModelServicer:
    """
    """
    gRPC servicer for AI models.
    gRPC servicer for AI models.
    """
    """


    def __init__(self, server):
    def __init__(self, server):
    """
    """
    Initialize the model servicer.
    Initialize the model servicer.


    Args:
    Args:
    server: Server instance
    server: Server instance
    """
    """
    self.server = server
    self.server = server
    self.model = server.model
    self.model = server.model
    self.tokenizer = server.tokenizer
    self.tokenizer = server.tokenizer


    def GenerateText(self, request, context):
    def GenerateText(self, request, context):
    """
    """
    Generate text from a prompt.
    Generate text from a prompt.


    Args:
    Args:
    request: Text generation request
    request: Text generation request
    context: gRPC context
    context: gRPC context


    Returns:
    Returns:
    Text generation response
    Text generation response
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Track request
    # Track request
    self.server.request_count += 1
    self.server.request_count += 1
    start_time = time.time()
    start_time = time.time()


    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    }
    }


    if request.stop_sequences:
    if request.stop_sequences:
    params["stop_sequences"] = list(request.stop_sequences)
    params["stop_sequences"] = list(request.stop_sequences)


    # Generate text
    # Generate text
    result = self.model.generate_text(request.prompt, **params)
    result = self.model.generate_text(request.prompt, **params)


    # Count tokens
    # Count tokens
    prompt_tokens = self.tokenizer(
    prompt_tokens = self.tokenizer(
    request.prompt, return_tensors="pt"
    request.prompt, return_tensors="pt"
    ).input_ids.shape[1]
    ).input_ids.shape[1]
    completion_tokens = self.tokenizer(
    completion_tokens = self.tokenizer(
    result["text"], return_tensors="pt"
    result["text"], return_tensors="pt"
    ).input_ids.shape[1]
    ).input_ids.shape[1]
    total_tokens = prompt_tokens + completion_tokens
    total_tokens = prompt_tokens + completion_tokens


    # Track tokens
    # Track tokens
    self.server.token_count += total_tokens
    self.server.token_count += total_tokens


    # Track latency
    # Track latency
    latency = time.time() - start_time
    latency = time.time() - start_time
    self.server.latencies.append(latency * 1000)  # Convert to ms
    self.server.latencies.append(latency * 1000)  # Convert to ms


    # Create response
    # Create response
    response = model_pb2.GenerateTextResponse(
    response = model_pb2.GenerateTextResponse(
    text=result["text"],
    text=result["text"],
    prompt_tokens=prompt_tokens,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    completion_tokens=completion_tokens,
    total_tokens=total_tokens,
    total_tokens=total_tokens,
    finish_reason=result.get("finish_reason", "stop"),
    finish_reason=result.get("finish_reason", "stop"),
    )
    )


    return response
    return response


except Exception as e:
except Exception as e:
    # Track error
    # Track error
    self.server.error_count += 1
    self.server.error_count += 1


    # Log error
    # Log error
    logger.error(f"Error generating text: {e}")
    logger.error(f"Error generating text: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def GenerateTextStream(self, request, context):
    def GenerateTextStream(self, request, context):
    """
    """
    Stream text generation.
    Stream text generation.


    Args:
    Args:
    request: Text generation request
    request: Text generation request
    context: gRPC context
    context: gRPC context


    Yields:
    Yields:
    Text generation response chunks
    Text generation response chunks
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Track request
    # Track request
    self.server.request_count += 1
    self.server.request_count += 1
    start_time = time.time()
    start_time = time.time()


    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    "stream": True,
    "stream": True,
    }
    }


    if request.stop_sequences:
    if request.stop_sequences:
    params["stop_sequences"] = list(request.stop_sequences)
    params["stop_sequences"] = list(request.stop_sequences)


    # Count prompt tokens
    # Count prompt tokens
    prompt_tokens = self.tokenizer(
    prompt_tokens = self.tokenizer(
    request.prompt, return_tensors="pt"
    request.prompt, return_tensors="pt"
    ).input_ids.shape[1]
    ).input_ids.shape[1]
    completion_tokens = 0
    completion_tokens = 0


    # Stream text generation
    # Stream text generation
    for chunk in self.model.generate_text_stream(request.prompt, **params):
    for chunk in self.model.generate_text_stream(request.prompt, **params):
    completion_tokens += 1
    completion_tokens += 1


    # Create response chunk
    # Create response chunk
    response = model_pb2.GenerateTextResponse(
    response = model_pb2.GenerateTextResponse(
    text=chunk["text"],
    text=chunk["text"],
    prompt_tokens=prompt_tokens,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    completion_tokens=completion_tokens,
    total_tokens=prompt_tokens + completion_tokens,
    total_tokens=prompt_tokens + completion_tokens,
    finish_reason=chunk.get("finish_reason", None),
    finish_reason=chunk.get("finish_reason", None),
    )
    )


    yield response
    yield response


    # Track tokens
    # Track tokens
    self.server.token_count += prompt_tokens + completion_tokens
    self.server.token_count += prompt_tokens + completion_tokens


    # Track latency
    # Track latency
    latency = time.time() - start_time
    latency = time.time() - start_time
    self.server.latencies.append(latency * 1000)  # Convert to ms
    self.server.latencies.append(latency * 1000)  # Convert to ms


except Exception as e:
except Exception as e:
    # Track error
    # Track error
    self.server.error_count += 1
    self.server.error_count += 1


    # Log error
    # Log error
    logger.error(f"Error streaming text generation: {e}")
    logger.error(f"Error streaming text generation: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def GenerateChatCompletion(self, request, context):
    def GenerateChatCompletion(self, request, context):
    """
    """
    Generate a chat completion.
    Generate a chat completion.


    Args:
    Args:
    request: Chat completion request
    request: Chat completion request
    context: gRPC context
    context: gRPC context


    Returns:
    Returns:
    Chat completion response
    Chat completion response
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Track request
    # Track request
    self.server.request_count += 1
    self.server.request_count += 1
    start_time = time.time()
    start_time = time.time()


    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    }
    }


    if request.stop_sequences:
    if request.stop_sequences:
    params["stop_sequences"] = list(request.stop_sequences)
    params["stop_sequences"] = list(request.stop_sequences)


    # Convert messages
    # Convert messages
    messages = []
    messages = []
    for message in request.messages:
    for message in request.messages:
    messages.append({"role": message.role, "content": message.content})
    messages.append({"role": message.role, "content": message.content})


    # Generate chat completion
    # Generate chat completion
    result = self.model.generate_chat_completion(messages, **params)
    result = self.model.generate_chat_completion(messages, **params)


    # Count tokens
    # Count tokens
    prompt_tokens = self._count_tokens_from_messages(messages)
    prompt_tokens = self._count_tokens_from_messages(messages)
    completion_tokens = self.tokenizer(
    completion_tokens = self.tokenizer(
    result["message"]["content"], return_tensors="pt"
    result["message"]["content"], return_tensors="pt"
    ).input_ids.shape[1]
    ).input_ids.shape[1]
    total_tokens = prompt_tokens + completion_tokens
    total_tokens = prompt_tokens + completion_tokens


    # Track tokens
    # Track tokens
    self.server.token_count += total_tokens
    self.server.token_count += total_tokens


    # Track latency
    # Track latency
    latency = time.time() - start_time
    latency = time.time() - start_time
    self.server.latencies.append(latency * 1000)  # Convert to ms
    self.server.latencies.append(latency * 1000)  # Convert to ms


    # Create response message
    # Create response message
    response_message = model_pb2.ChatMessage(
    response_message = model_pb2.ChatMessage(
    role=result["message"]["role"], content=result["message"]["content"]
    role=result["message"]["role"], content=result["message"]["content"]
    )
    )


    # Create response
    # Create response
    response = model_pb2.GenerateChatCompletionResponse(
    response = model_pb2.GenerateChatCompletionResponse(
    message=response_message,
    message=response_message,
    prompt_tokens=prompt_tokens,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    completion_tokens=completion_tokens,
    total_tokens=total_tokens,
    total_tokens=total_tokens,
    finish_reason=result.get("finish_reason", "stop"),
    finish_reason=result.get("finish_reason", "stop"),
    )
    )


    return response
    return response


except Exception as e:
except Exception as e:
    # Track error
    # Track error
    self.server.error_count += 1
    self.server.error_count += 1


    # Log error
    # Log error
    logger.error(f"Error generating chat completion: {e}")
    logger.error(f"Error generating chat completion: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def GenerateChatCompletionStream(self, request, context):
    def GenerateChatCompletionStream(self, request, context):
    """
    """
    Stream chat completion.
    Stream chat completion.


    Args:
    Args:
    request: Chat completion request
    request: Chat completion request
    context: gRPC context
    context: gRPC context


    Yields:
    Yields:
    Chat completion response chunks
    Chat completion response chunks
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Track request
    # Track request
    self.server.request_count += 1
    self.server.request_count += 1
    start_time = time.time()
    start_time = time.time()


    # Get generation parameters
    # Get generation parameters
    params = {
    params = {
    "max_tokens": request.max_tokens,
    "max_tokens": request.max_tokens,
    "temperature": request.temperature,
    "temperature": request.temperature,
    "top_p": request.top_p,
    "top_p": request.top_p,
    "top_k": request.top_k,
    "top_k": request.top_k,
    "repetition_penalty": request.repetition_penalty,
    "repetition_penalty": request.repetition_penalty,
    "stream": True,
    "stream": True,
    }
    }


    if request.stop_sequences:
    if request.stop_sequences:
    params["stop_sequences"] = list(request.stop_sequences)
    params["stop_sequences"] = list(request.stop_sequences)


    # Convert messages
    # Convert messages
    messages = []
    messages = []
    for message in request.messages:
    for message in request.messages:
    messages.append({"role": message.role, "content": message.content})
    messages.append({"role": message.role, "content": message.content})


    # Count prompt tokens
    # Count prompt tokens
    prompt_tokens = self._count_tokens_from_messages(messages)
    prompt_tokens = self._count_tokens_from_messages(messages)
    completion_tokens = 0
    completion_tokens = 0


    # Stream chat completion
    # Stream chat completion
    for chunk in self.model.generate_chat_completion_stream(messages, **params):
    for chunk in self.model.generate_chat_completion_stream(messages, **params):
    completion_tokens += 1
    completion_tokens += 1


    # Create response message
    # Create response message
    response_message = model_pb2.ChatMessage(
    response_message = model_pb2.ChatMessage(
    role="assistant", content=chunk["content"]
    role="assistant", content=chunk["content"]
    )
    )


    # Create response chunk
    # Create response chunk
    response = model_pb2.GenerateChatCompletionResponse(
    response = model_pb2.GenerateChatCompletionResponse(
    message=response_message,
    message=response_message,
    prompt_tokens=prompt_tokens,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    completion_tokens=completion_tokens,
    total_tokens=prompt_tokens + completion_tokens,
    total_tokens=prompt_tokens + completion_tokens,
    finish_reason=chunk.get("finish_reason", None),
    finish_reason=chunk.get("finish_reason", None),
    )
    )


    yield response
    yield response


    # Track tokens
    # Track tokens
    self.server.token_count += prompt_tokens + completion_tokens
    self.server.token_count += prompt_tokens + completion_tokens


    # Track latency
    # Track latency
    latency = time.time() - start_time
    latency = time.time() - start_time
    self.server.latencies.append(latency * 1000)  # Convert to ms
    self.server.latencies.append(latency * 1000)  # Convert to ms


except Exception as e:
except Exception as e:
    # Track error
    # Track error
    self.server.error_count += 1
    self.server.error_count += 1


    # Log error
    # Log error
    logger.error(f"Error streaming chat completion: {e}")
    logger.error(f"Error streaming chat completion: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def ClassifyText(self, request, context):
    def ClassifyText(self, request, context):
    """
    """
    Classify text.
    Classify text.


    Args:
    Args:
    request: Text classification request
    request: Text classification request
    context: gRPC context
    context: gRPC context


    Returns:
    Returns:
    Text classification response
    Text classification response
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Track request
    # Track request
    self.server.request_count += 1
    self.server.request_count += 1
    start_time = time.time()
    start_time = time.time()


    # Classify text
    # Classify text
    result = self.model.classify_text(request.text)
    result = self.model.classify_text(request.text)


    # Count tokens
    # Count tokens
    tokens = self.tokenizer(request.text, return_tensors="pt").input_ids.shape[
    tokens = self.tokenizer(request.text, return_tensors="pt").input_ids.shape[
    1
    1
    ]
    ]


    # Track tokens
    # Track tokens
    self.server.token_count += tokens
    self.server.token_count += tokens


    # Track latency
    # Track latency
    latency = time.time() - start_time
    latency = time.time() - start_time
    self.server.latencies.append(latency * 1000)  # Convert to ms
    self.server.latencies.append(latency * 1000)  # Convert to ms


    # Create response labels
    # Create response labels
    response_labels = []
    response_labels = []
    for label in result["labels"]:
    for label in result["labels"]:
    response_label = model_pb2.ClassificationLabel(
    response_label = model_pb2.ClassificationLabel(
    label=label["label"], score=label["score"]
    label=label["label"], score=label["score"]
    )
    )
    response_labels.append(response_label)
    response_labels.append(response_label)


    # Create response
    # Create response
    response = model_pb2.ClassifyTextResponse(
    response = model_pb2.ClassifyTextResponse(
    labels=response_labels, top_label=result["top_label"], tokens=tokens
    labels=response_labels, top_label=result["top_label"], tokens=tokens
    )
    )


    return response
    return response


except Exception as e:
except Exception as e:
    # Track error
    # Track error
    self.server.error_count += 1
    self.server.error_count += 1


    # Log error
    # Log error
    logger.error(f"Error classifying text: {e}")
    logger.error(f"Error classifying text: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def GetEmbeddings(self, request, context):
    def GetEmbeddings(self, request, context):
    """
    """
    Get embeddings for text.
    Get embeddings for text.


    Args:
    Args:
    request: Embedding request
    request: Embedding request
    context: gRPC context
    context: gRPC context


    Returns:
    Returns:
    Embedding response
    Embedding response
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Track request
    # Track request
    self.server.request_count += 1
    self.server.request_count += 1
    start_time = time.time()
    start_time = time.time()


    # Convert input to list if it's a string
    # Convert input to list if it's a string
    if request.HasField("input_text"):
    if request.HasField("input_text"):
    inputs = [request.input_text]
    inputs = [request.input_text]
    else:
    else:
    inputs = list(request.input_texts)
    inputs = list(request.input_texts)


    # Get embeddings
    # Get embeddings
    embeddings = self.model.get_embeddings(inputs)
    embeddings = self.model.get_embeddings(inputs)


    # Count tokens
    # Count tokens
    total_tokens = sum(
    total_tokens = sum(
    self.tokenizer(text, return_tensors="pt").input_ids.shape[1]
    self.tokenizer(text, return_tensors="pt").input_ids.shape[1]
    for text in inputs
    for text in inputs
    )
    )


    # Track tokens
    # Track tokens
    self.server.token_count += total_tokens
    self.server.token_count += total_tokens


    # Track latency
    # Track latency
    latency = time.time() - start_time
    latency = time.time() - start_time
    self.server.latencies.append(latency * 1000)  # Convert to ms
    self.server.latencies.append(latency * 1000)  # Convert to ms


    # Create response data
    # Create response data
    response_data = []
    response_data = []
    for i, embedding in enumerate(embeddings):
    for i, embedding in enumerate(embeddings):
    embedding_data = model_pb2.EmbeddingData(embedding=embedding, index=i)
    embedding_data = model_pb2.EmbeddingData(embedding=embedding, index=i)
    response_data.append(embedding_data)
    response_data.append(embedding_data)


    # Create usage
    # Create usage
    usage = model_pb2.TokenUsage(
    usage = model_pb2.TokenUsage(
    prompt_tokens=total_tokens, total_tokens=total_tokens
    prompt_tokens=total_tokens, total_tokens=total_tokens
    )
    )


    # Create response
    # Create response
    response = model_pb2.GetEmbeddingsResponse(
    response = model_pb2.GetEmbeddingsResponse(
    data=response_data,
    data=response_data,
    model=request.model or self.server.config.model_id,
    model=request.model or self.server.config.model_id,
    usage=usage,
    usage=usage,
    )
    )


    return response
    return response


except Exception as e:
except Exception as e:
    # Track error
    # Track error
    self.server.error_count += 1
    self.server.error_count += 1


    # Log error
    # Log error
    logger.error(f"Error getting embeddings: {e}")
    logger.error(f"Error getting embeddings: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def GetServerInfo(self, request, context):
    def GetServerInfo(self, request, context):
    """
    """
    Get information about the server.
    Get information about the server.


    Args:
    Args:
    request: Server info request
    request: Server info request
    context: gRPC context
    context: gRPC context


    Returns:
    Returns:
    Server info response
    Server info response
    """
    """
    try:
    try:
    # Import proto modules
    # Import proto modules
    # Get server info
    # Get server info
    info = self.server.get_info()
    info = self.server.get_info()


    # Create response
    # Create response
    response = model_pb2.GetServerInfoResponse(
    response = model_pb2.GetServerInfoResponse(
    version=info.get("version", "unknown"),
    version=info.get("version", "unknown"),
    model_id=info.get("model_id", "unknown"),
    model_id=info.get("model_id", "unknown"),
    model_type=info.get("model_type", "unknown"),
    model_type=info.get("model_type", "unknown"),
    uptime=info.get("uptime", 0),
    uptime=info.get("uptime", 0),
    request_count=info.get("request_count", 0),
    request_count=info.get("request_count", 0),
    error_count=info.get("error_count", 0),
    error_count=info.get("error_count", 0),
    token_count=info.get("token_count", 0),
    token_count=info.get("token_count", 0),
    )
    )


    return response
    return response


except Exception as e:
except Exception as e:
    # Log error
    # Log error
    logger.error(f"Error getting server info: {e}")
    logger.error(f"Error getting server info: {e}")


    # Raise gRPC error
    # Raise gRPC error
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(e))
    context.set_details(str(e))
    raise
    raise


    def _count_tokens_from_messages(self, messages: List[Dict[str, str]]) -> int:
    def _count_tokens_from_messages(self, messages: List[Dict[str, str]]) -> int:
    """
    """
    Count tokens in a list of messages.
    Count tokens in a list of messages.


    Args:
    Args:
    messages: List of messages
    messages: List of messages


    Returns:
    Returns:
    Number of tokens
    Number of tokens
    """
    """
    # Concatenate messages
    # Concatenate messages
    text = ""
    text = ""
    for message in messages:
    for message in messages:
    text += f"{message['role']}: {message['content']}\n"
    text += f"{message['role']}: {message['content']}\n"


    # Count tokens
    # Count tokens
    return self.tokenizer(text, return_tensors="pt").input_ids.shape[1]
    return self.tokenizer(text, return_tensors="pt").input_ids.shape[1]