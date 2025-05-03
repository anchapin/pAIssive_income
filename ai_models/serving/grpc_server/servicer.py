"""
gRPC servicer for AI models.

This module provides a gRPC servicer for handling model requests.
"""


import logging
import time
from typing import Dict, List


    import grpc
            from .proto import model_pb2

            
            from .proto import model_pb2

            
            from .proto import model_pb2

            
            from .proto import model_pb2

            
            from .proto import model_pb2

            
            from .proto import model_pb2

            
            from .proto import model_pb2

            

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import gRPC
try:


    GRPC_AVAILABLE = True
except ImportError:
    logger.warning("gRPC is required for gRPC server")
    GRPC_AVAILABLE = False


class ModelServicer:
    """
    gRPC servicer for AI models.
    """

    def __init__(self, server):
        """
        Initialize the model servicer.

        Args:
            server: Server instance
        """
        self.server = server
        self.model = server.model
        self.tokenizer = server.tokenizer

    def GenerateText(self, request, context):
        """
        Generate text from a prompt.

        Args:
            request: Text generation request
            context: gRPC context

        Returns:
            Text generation response
        """
        try:
            # Import proto modules
# Track request
            self.server.request_count += 1
            start_time = time.time()

            # Get generation parameters
            params = {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
                "repetition_penalty": request.repetition_penalty,
            }

            if request.stop_sequences:
                params["stop_sequences"] = list(request.stop_sequences)

            # Generate text
            result = self.model.generate_text(request.prompt, **params)

            # Count tokens
            prompt_tokens = self.tokenizer(
                request.prompt, return_tensors="pt"
            ).input_ids.shape[1]
            completion_tokens = self.tokenizer(
                result["text"], return_tensors="pt"
            ).input_ids.shape[1]
            total_tokens = prompt_tokens + completion_tokens

            # Track tokens
            self.server.token_count += total_tokens

            # Track latency
            latency = time.time() - start_time
            self.server.latencies.append(latency * 1000)  # Convert to ms

            # Create response
            response = model_pb2.GenerateTextResponse(
                text=result["text"],
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                finish_reason=result.get("finish_reason", "stop"),
            )

            return response

        except Exception as e:
            # Track error
            self.server.error_count += 1

            # Log error
            logger.error(f"Error generating text: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def GenerateTextStream(self, request, context):
        """
        Stream text generation.

        Args:
            request: Text generation request
            context: gRPC context

        Yields:
            Text generation response chunks
        """
        try:
            # Import proto modules
# Track request
            self.server.request_count += 1
            start_time = time.time()

            # Get generation parameters
            params = {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
                "repetition_penalty": request.repetition_penalty,
                "stream": True,
            }

            if request.stop_sequences:
                params["stop_sequences"] = list(request.stop_sequences)

            # Count prompt tokens
            prompt_tokens = self.tokenizer(
                request.prompt, return_tensors="pt"
            ).input_ids.shape[1]
            completion_tokens = 0

            # Stream text generation
            for chunk in self.model.generate_text_stream(request.prompt, **params):
                completion_tokens += 1

                # Create response chunk
                response = model_pb2.GenerateTextResponse(
                    text=chunk["text"],
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    finish_reason=chunk.get("finish_reason", None),
                )

                yield response

            # Track tokens
            self.server.token_count += prompt_tokens + completion_tokens

            # Track latency
            latency = time.time() - start_time
            self.server.latencies.append(latency * 1000)  # Convert to ms

        except Exception as e:
            # Track error
            self.server.error_count += 1

            # Log error
            logger.error(f"Error streaming text generation: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def GenerateChatCompletion(self, request, context):
        """
        Generate a chat completion.

        Args:
            request: Chat completion request
            context: gRPC context

        Returns:
            Chat completion response
        """
        try:
            # Import proto modules
# Track request
            self.server.request_count += 1
            start_time = time.time()

            # Get generation parameters
            params = {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
                "repetition_penalty": request.repetition_penalty,
            }

            if request.stop_sequences:
                params["stop_sequences"] = list(request.stop_sequences)

            # Convert messages
            messages = []
            for message in request.messages:
                messages.append({"role": message.role, "content": message.content})

            # Generate chat completion
            result = self.model.generate_chat_completion(messages, **params)

            # Count tokens
            prompt_tokens = self._count_tokens_from_messages(messages)
            completion_tokens = self.tokenizer(
                result["message"]["content"], return_tensors="pt"
            ).input_ids.shape[1]
            total_tokens = prompt_tokens + completion_tokens

            # Track tokens
            self.server.token_count += total_tokens

            # Track latency
            latency = time.time() - start_time
            self.server.latencies.append(latency * 1000)  # Convert to ms

            # Create response message
            response_message = model_pb2.ChatMessage(
                role=result["message"]["role"], content=result["message"]["content"]
            )

            # Create response
            response = model_pb2.GenerateChatCompletionResponse(
                message=response_message,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                finish_reason=result.get("finish_reason", "stop"),
            )

            return response

        except Exception as e:
            # Track error
            self.server.error_count += 1

            # Log error
            logger.error(f"Error generating chat completion: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def GenerateChatCompletionStream(self, request, context):
        """
        Stream chat completion.

        Args:
            request: Chat completion request
            context: gRPC context

        Yields:
            Chat completion response chunks
        """
        try:
            # Import proto modules
# Track request
            self.server.request_count += 1
            start_time = time.time()

            # Get generation parameters
            params = {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
                "repetition_penalty": request.repetition_penalty,
                "stream": True,
            }

            if request.stop_sequences:
                params["stop_sequences"] = list(request.stop_sequences)

            # Convert messages
            messages = []
            for message in request.messages:
                messages.append({"role": message.role, "content": message.content})

            # Count prompt tokens
            prompt_tokens = self._count_tokens_from_messages(messages)
            completion_tokens = 0

            # Stream chat completion
            for chunk in self.model.generate_chat_completion_stream(messages, **params):
                completion_tokens += 1

                # Create response message
                response_message = model_pb2.ChatMessage(
                    role="assistant", content=chunk["content"]
                )

                # Create response chunk
                response = model_pb2.GenerateChatCompletionResponse(
                    message=response_message,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    finish_reason=chunk.get("finish_reason", None),
                )

                yield response

            # Track tokens
            self.server.token_count += prompt_tokens + completion_tokens

            # Track latency
            latency = time.time() - start_time
            self.server.latencies.append(latency * 1000)  # Convert to ms

        except Exception as e:
            # Track error
            self.server.error_count += 1

            # Log error
            logger.error(f"Error streaming chat completion: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def ClassifyText(self, request, context):
        """
        Classify text.

        Args:
            request: Text classification request
            context: gRPC context

        Returns:
            Text classification response
        """
        try:
            # Import proto modules
# Track request
            self.server.request_count += 1
            start_time = time.time()

            # Classify text
            result = self.model.classify_text(request.text)

            # Count tokens
            tokens = self.tokenizer(request.text, return_tensors="pt").input_ids.shape[
                1
            ]

            # Track tokens
            self.server.token_count += tokens

            # Track latency
            latency = time.time() - start_time
            self.server.latencies.append(latency * 1000)  # Convert to ms

            # Create response labels
            response_labels = []
            for label in result["labels"]:
                response_label = model_pb2.ClassificationLabel(
                    label=label["label"], score=label["score"]
                )
                response_labels.append(response_label)

            # Create response
            response = model_pb2.ClassifyTextResponse(
                labels=response_labels, top_label=result["top_label"], tokens=tokens
            )

            return response

        except Exception as e:
            # Track error
            self.server.error_count += 1

            # Log error
            logger.error(f"Error classifying text: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def GetEmbeddings(self, request, context):
        """
        Get embeddings for text.

        Args:
            request: Embedding request
            context: gRPC context

        Returns:
            Embedding response
        """
        try:
            # Import proto modules
# Track request
            self.server.request_count += 1
            start_time = time.time()

            # Convert input to list if it's a string
            if request.HasField("input_text"):
                inputs = [request.input_text]
            else:
                inputs = list(request.input_texts)

            # Get embeddings
            embeddings = self.model.get_embeddings(inputs)

            # Count tokens
            total_tokens = sum(
                self.tokenizer(text, return_tensors="pt").input_ids.shape[1]
                for text in inputs
            )

            # Track tokens
            self.server.token_count += total_tokens

            # Track latency
            latency = time.time() - start_time
            self.server.latencies.append(latency * 1000)  # Convert to ms

            # Create response data
            response_data = []
            for i, embedding in enumerate(embeddings):
                embedding_data = model_pb2.EmbeddingData(embedding=embedding, index=i)
                response_data.append(embedding_data)

            # Create usage
            usage = model_pb2.TokenUsage(
                prompt_tokens=total_tokens, total_tokens=total_tokens
            )

            # Create response
            response = model_pb2.GetEmbeddingsResponse(
                data=response_data,
                model=request.model or self.server.config.model_id,
                usage=usage,
            )

            return response

        except Exception as e:
            # Track error
            self.server.error_count += 1

            # Log error
            logger.error(f"Error getting embeddings: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def GetServerInfo(self, request, context):
        """
        Get information about the server.

        Args:
            request: Server info request
            context: gRPC context

        Returns:
            Server info response
        """
        try:
            # Import proto modules
# Get server info
            info = self.server.get_info()

            # Create response
            response = model_pb2.GetServerInfoResponse(
                version=info.get("version", "unknown"),
                model_id=info.get("model_id", "unknown"),
                model_type=info.get("model_type", "unknown"),
                uptime=info.get("uptime", 0),
                request_count=info.get("request_count", 0),
                error_count=info.get("error_count", 0),
                token_count=info.get("token_count", 0),
            )

            return response

        except Exception as e:
            # Log error
            logger.error(f"Error getting server info: {e}")

            # Raise gRPC error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def _count_tokens_from_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens in a list of messages.

        Args:
            messages: List of messages

        Returns:
            Number of tokens
        """
        # Concatenate messages
        text = ""
        for message in messages:
            text += f"{message['role']}: {message['content']}\n"

        # Count tokens
        return self.tokenizer(text, return_tensors="pt").input_ids.shape[1]